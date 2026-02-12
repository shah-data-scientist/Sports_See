"""
FILE: run_vector_evaluation.py
STATUS: Active
RESPONSIBILITY: Consolidated vector evaluation system with API-only processing, checkpointing, RAGAS metrics
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Runs comprehensive vector evaluation:
- API-only processing via TestClient (no direct service calls)
- Checkpoint after each query for recovery from failures/rate limits
- RAGAS metrics integration (faithfulness, answer relevancy, context precision/recall)
- 5 comprehensive analysis functions
- 2-file output: JSON (raw data) + MD (comprehensive report)
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from starlette.testclient import TestClient

from src.api.main import create_app
from src.api.dependencies import get_chat_service
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES
from src.evaluation.models import TestCategory
from src.evaluation.analysis.vector_quality_analysis import (
    analyze_category_performance,
    analyze_ragas_metrics,
    analyze_response_patterns,
    analyze_retrieval_performance,
    analyze_source_quality,
)
from src.models.feedback import ChatInteractionCreate
from src.core.config import settings

logger = logging.getLogger(__name__)

# Rate limiting configuration (Gemini free tier: 15 RPM)
# Vector queries consume ~2 Gemini calls each (embedding + LLM response)
RATE_LIMIT_DELAY = 20  # seconds between requests
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 30  # Start with 30s, then 60s, then 120s
BATCH_SIZE = 10  # Extra cooldown every N queries
BATCH_COOLDOWN_SECONDS = 30  # Extra pause between batches


def _load_checkpoint(checkpoint_path: Path) -> dict[str, Any] | None:
    """Load existing checkpoint if present.

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Checkpoint data dict or None if not found
    """
    if checkpoint_path.exists():
        try:
            data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
            logger.info(f"Checkpoint loaded: {data['evaluated_count']}/{data['total_cases']} queries completed")
            return data
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
            return None
    return None


def _save_checkpoint(checkpoint_path: Path, results: list[dict], next_index: int, total_cases: int) -> None:
    """Save checkpoint after each query (atomic write for safety).

    Args:
        checkpoint_path: Path to checkpoint file
        results: List of accumulated results
        next_index: Index of next query to evaluate
        total_cases: Total number of test cases
    """
    checkpoint = {
        "checkpoint_version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "total_cases": total_cases,
        "evaluated_count": len(results),
        "remaining_count": total_cases - len(results),
        "results": results,
        "next_index": next_index
    }

    # Atomic write: write to temp file, then rename
    temp_path = checkpoint_path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8")
    temp_path.replace(checkpoint_path)  # Atomic on Windows/Unix


def _cleanup_checkpoint(checkpoint_path: Path) -> None:
    """Delete checkpoint file after successful completion.

    Args:
        checkpoint_path: Path to checkpoint file
    """
    if checkpoint_path.exists():
        checkpoint_path.unlink()
        logger.info("Checkpoint file deleted after successful completion")


def _retry_api_call(api_call_func, max_retries: int = MAX_RETRIES):
    """Retry API call with exponential backoff on 429 errors.

    Args:
        api_call_func: Function that makes API call
        max_retries: Maximum number of retry attempts

    Returns:
        API response if successful

    Raises:
        Last exception if all retries exhausted
    """
    for attempt in range(max_retries + 1):
        try:
            return api_call_func()
        except Exception as e:
            error_msg = str(e)
            is_rate_limit = "429" in error_msg and ("RESOURCE_EXHAUSTED" in error_msg or "rate" in error_msg.lower())

            if is_rate_limit and attempt < max_retries:
                wait_time = RETRY_BACKOFF_BASE * (2 ** attempt)  # 15s, 30s, 60s
                logger.warning(f"  ⚠️ 429 Rate Limit (attempt {attempt + 1}/{max_retries + 1}). "
                             f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                # Non-rate-limit error or final attempt - re-raise
                raise

    raise RuntimeError("Max retries exhausted")


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context.

    Args:
        question: Question text to analyze

    Returns:
        True if question appears to be a follow-up
    """
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def run_vector_evaluation(resume: bool = True) -> tuple[list[dict], str]:
    """Run vector evaluation with API-only processing and checkpointing.

    Features:
    - API-only: Uses TestClient (no direct service calls)
    - Checkpoint: Saves after EACH query for recovery
    - Resume: Auto-resumes from checkpoint if available
    - RAGAS: Integrates RAGAS metrics calculation
    - Routing verification: Tracks SQL/vector/hybrid classification
    - Conversation support: Manages conversation IDs for follow-up questions
    - Output: JSON + MD comprehensive report

    Args:
        resume: Whether to resume from checkpoint (default: True)

    Returns:
        Tuple of (results list, json_path string)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    checkpoint_path = output_dir / f"vector_evaluation_{timestamp}.checkpoint.json"
    json_path = output_dir / f"vector_evaluation_{timestamp}.json"

    # Step 1: Use all test cases (vector_test_cases.py contains ONLY vector-appropriate cases)
    test_cases = EVALUATION_TEST_CASES

    logger.info(f"Vector evaluation: {len(test_cases)} test cases")

    # Step 2: Check for existing checkpoint
    results = []
    start_index = 0

    if resume:
        checkpoint = _load_checkpoint(checkpoint_path)
        if checkpoint:
            results = checkpoint["results"]
            start_index = checkpoint["next_index"]
            logger.info(f"Resuming from query {start_index + 1}/{len(test_cases)}")

    total_cases = len(test_cases)

    # Step 3: Initialize tracking statistics
    routing_stats = {"sql_only": 0, "vector_only": 0, "hybrid": 0, "unknown": 0}
    misclassifications = []

    if start_index >= total_cases:
        logger.info(f"All {total_cases} queries already evaluated (from checkpoint)")
        # Still proceed to generate report
    else:
        logger.info(f"Starting vector evaluation: {len(test_cases)} test cases")
        logger.info(f"Rate limit delay: {RATE_LIMIT_DELAY}s between queries")

        # Step 4: Evaluate remaining test cases via API
        app = create_app()

        with TestClient(app) as client:
            # Access ChatService for conversation storage
            chat_service = get_chat_service()

            current_conversation_id = None
            current_turn_number = 0

            for i in range(start_index, total_cases):
                test_case = test_cases[i]

                logger.info(f"[{i + 1}/{total_cases}] {test_case.category.value}: {test_case.question[:60]}...")

                # Rate limiting (skip for first query of batch)
                if i > start_index:
                    # Extra batch cooldown every BATCH_SIZE queries
                    queries_done = i - start_index
                    if queries_done > 0 and queries_done % BATCH_SIZE == 0:
                        logger.info(f"  Batch cooldown: {BATCH_COOLDOWN_SECONDS}s (after {queries_done} queries)...")
                        time.sleep(BATCH_COOLDOWN_SECONDS)
                    logger.info(f"  Rate limit delay: {RATE_LIMIT_DELAY}s...")
                    time.sleep(RATE_LIMIT_DELAY)

                # Handle conversational test cases
                if test_case.category == TestCategory.CONVERSATIONAL:
                    if _is_followup_question(test_case.question):
                        if current_conversation_id is None:
                            # Create new conversation
                            conv_resp = client.post("/api/v1/conversations", json={})
                            current_conversation_id = conv_resp.json()["id"]
                            current_turn_number = 1
                        else:
                            current_turn_number += 1
                    else:
                        # New conversation
                        conv_resp = client.post("/api/v1/conversations", json={})
                        current_conversation_id = conv_resp.json()["id"]
                        current_turn_number = 1
                else:
                    # Non-conversational queries don't need conversation context
                    current_conversation_id = None
                    current_turn_number = 0

                try:
                    # Build API request payload
                    payload = {
                        "query": test_case.question,
                        "k": 5,
                        "include_sources": True,
                        "conversation_id": current_conversation_id,
                        "turn_number": current_turn_number if current_conversation_id else 1,
                    }

                    # API call with retry logic
                    def api_call():
                        response = client.post("/api/v1/chat", json=payload, timeout=30)

                        if response.status_code != 200:
                            raise RuntimeError(
                                f"API error {response.status_code}: {response.text[:300]}"
                            )

                        return response.json()

                    api_result = _retry_api_call(api_call)

                    # Store interaction for conversation context
                    if current_conversation_id:
                        interaction = ChatInteractionCreate(
                            query=test_case.question,
                            response=api_result.get("answer", ""),
                            sources=[s.get("source", "") for s in api_result.get("sources", [])],
                            processing_time_ms=int(api_result.get("processing_time_ms", 0)),
                            conversation_id=current_conversation_id,
                            turn_number=current_turn_number,
                        )
                        chat_service.feedback_repository.save_interaction(interaction)

                    # Determine actual routing based on response characteristics
                    has_sql_data = any(
                        kw in api_result.get("answer", "").lower()
                        for kw in ["pts", "reb", "ast", "points", "rebounds", "assists", "ppg", "rpg", "apg"]
                    )
                    has_vector_context = len(api_result.get("sources", [])) > 0

                    if has_sql_data and has_vector_context:
                        actual_routing = "hybrid"
                    elif has_sql_data:
                        actual_routing = "sql_only"
                    elif has_vector_context:
                        actual_routing = "vector_only"
                    else:
                        actual_routing = "unknown"

                    routing_stats[actual_routing] += 1

                    # For Vector test cases, we EXPECT vector_only routing (or hybrid if contextual)
                    expected_routing = "hybrid" if test_case.category == TestCategory.COMPLEX else "vector_only"
                    is_misclassified = actual_routing not in [expected_routing, "hybrid"]

                    if is_misclassified:
                        misclassifications.append({
                            "question": test_case.question,
                            "category": test_case.category.value,
                            "expected": expected_routing,
                            "actual": actual_routing,
                            "response_preview": api_result.get("answer", "")[:150]
                        })

                    # Record result
                    results.append({
                        "question": test_case.question,
                        "category": test_case.category.value,
                        "response": api_result.get("answer", ""),
                        "expected_routing": expected_routing,
                        "actual_routing": actual_routing,
                        "is_misclassified": is_misclassified,
                        "sources": [
                            {
                                "text": s.get("text", "")[:500],  # Truncate for size
                                "score": s.get("score", 0),
                                "source": s.get("source", "unknown")
                            }
                            for s in api_result.get("sources", [])
                        ],
                        "sources_count": len(api_result.get("sources", [])),
                        "processing_time_ms": api_result.get("processing_time_ms", 0),
                        "ground_truth": test_case.ground_truth,
                        "success": True
                    })

                    status = "[PASS]" if not is_misclassified else "[MISCLASS]"
                    logger.info(f"  {status} Expected: {expected_routing} | Actual: {actual_routing} | "
                               f"Sources: {len(api_result.get('sources', []))} | Time: {api_result.get('processing_time_ms', 0)}ms")

                except Exception as e:
                    logger.error(f"  ✗ Failed: {str(e)}")
                    results.append({
                        "question": test_case.question,
                        "category": test_case.category.value,
                        "error": str(e),
                        "success": False
                    })

                # Save checkpoint after EACH query
                _save_checkpoint(checkpoint_path, results, i + 1, total_cases)

        # Print routing summary
        classification_accuracy = (routing_stats['vector_only'] + routing_stats['hybrid']) / total_cases * 100 if total_cases else 0
        logger.info(f"Evaluation complete: {sum(1 for r in results if r['success'])}/{total_cases} successful")
        logger.info(f"Routing accuracy: {classification_accuracy:.1f}% | Misclassifications: {len(misclassifications)}")

    # Step 6: Calculate RAGAS metrics (if we have successful results)
    successful_results = [r for r in results if r.get("success")]

    if successful_results:
        logger.info("Calculating RAGAS metrics...")

        try:
            ragas_scores = calculate_ragas_metrics(results)

            # Merge RAGAS scores back into results
            for i, result in enumerate(results):
                if result.get("success") and i < len(ragas_scores):
                    result["ragas_metrics"] = ragas_scores[i]

            logger.info("✓ RAGAS metrics calculated successfully")

        except Exception as e:
            logger.warning(f"⚠️ RAGAS calculation failed: {e}")
            logger.info("Continuing without RAGAS metrics...")

    # Step 5: Save final JSON results
    classification_accuracy = (routing_stats.get('vector_only', 0) + routing_stats.get('hybrid', 0)) / total_cases * 100 if total_cases else 0

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": "vector_evaluation",
        "total_cases": total_cases,
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "routing_stats": routing_stats,
        "classification_accuracy": classification_accuracy,
        "misclassifications_count": len(misclassifications),
        "misclassifications": misclassifications,
        "results": results
    }

    json_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Results saved to: {json_path}")

    # Step 7: Generate comprehensive MD report
    logger.info("Generating comprehensive report...")
    report_path = generate_comprehensive_report(results, str(json_path), timestamp, routing_stats, misclassifications)
    logger.info(f"Report saved to: {report_path}")

    # Step 8: Cleanup checkpoint
    _cleanup_checkpoint(checkpoint_path)

    return results, str(json_path)


def calculate_ragas_metrics(results: list[dict]) -> list[dict]:
    """Calculate RAGAS metrics for evaluation results.

    Args:
        results: List of evaluation results with responses and sources

    Returns:
        List of RAGAS metric dicts (one per successful result)
    """
    # Lazy import to avoid dependency issues
    try:
        from ragas import evaluate
        from ragas.metrics import (
            Faithfulness,
            ResponseRelevancy,
            LLMContextPrecisionWithoutReference,
            LLMContextRecall,
        )
        from ragas import EvaluationDataset
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_mistralai import MistralAIEmbeddings
    except ImportError as e:
        logger.error(f"RAGAS dependencies not installed: {e}")
        return []

    # Build RAGAS evaluator
    logger.info("Building RAGAS evaluator (Gemini LLM + Mistral embeddings)...")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.google_api_key,
        temperature=0.0
    )
    ragas_llm = LangchainLLMWrapper(llm)

    embeddings = MistralAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.mistral_api_key
    )
    ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

    # Prepare dataset
    successful_results = [r for r in results if r.get("success")]

    if not successful_results:
        logger.warning("No successful results to evaluate")
        return []

    dataset_dicts = [
        {
            "user_input": r["question"],
            "response": r["response"],
            "retrieved_contexts": [s["text"] for s in r.get("sources", [])],
            "reference": r.get("ground_truth", "")
        }
        for r in successful_results
    ]

    eval_dataset = EvaluationDataset.from_list(dataset_dicts)

    # Configure metrics
    metrics = [
        Faithfulness(llm=ragas_llm),
        ResponseRelevancy(llm=ragas_llm, embeddings=ragas_embeddings),
        LLMContextPrecisionWithoutReference(llm=ragas_llm),
        LLMContextRecall(llm=ragas_llm),
    ]

    logger.info(f"Evaluating {len(successful_results)} samples with RAGAS...")

    # Run evaluation
    result = evaluate(dataset=eval_dataset, metrics=metrics)

    # Extract scores
    df = result.to_pandas()

    ragas_scores = []
    for idx in range(len(df)):
        ragas_scores.append({
            "faithfulness": float(df.iloc[idx].get("faithfulness", 0)),
            "answer_relevancy": float(df.iloc[idx].get("answer_relevancy", 0)),
            "context_precision": float(df.iloc[idx].get("llm_context_precision_without_reference", 0)),
            "context_recall": float(df.iloc[idx].get("context_recall", 0))
        })

    return ragas_scores


def generate_comprehensive_report(
    results: list[dict],
    json_path: str,
    timestamp: str,
    routing_stats: dict[str, int] | None = None,
    misclassifications: list[dict] | None = None
) -> str:
    """Generate comprehensive MD report with all analysis sections.

    Args:
        results: List of evaluation results
        json_path: Path to JSON results file
        timestamp: Timestamp string for filename
        routing_stats: Dictionary of routing statistics (optional)
        misclassifications: List of misclassified queries (optional)

    Returns:
        Path to generated MD report
    """
    # Run 5 analysis functions
    ragas_analysis = analyze_ragas_metrics(results)
    source_analysis = analyze_source_quality(results)
    response_analysis = analyze_response_patterns(results)
    retrieval_analysis = analyze_retrieval_performance(results)
    category_analysis = analyze_category_performance(results)

    # Build report content
    report_lines = []

    # Header
    report_lines.extend([
        "# Vector Evaluation Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Dataset:** {len(results)} test cases",
        f"**Results JSON:** `{Path(json_path).name}`",
        "",
        "---",
        "",
    ])

    # Executive Summary
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    success_rate = (successful / len(results) * 100) if results else 0

    overall_ragas = ragas_analysis.get("overall", {})

    report_lines.extend([
        "## Executive Summary",
        "",
        f"- **Total Queries:** {len(results)}",
        f"- **Successful Executions:** {successful} ({success_rate:.1f}%)",
        f"- **Failed Executions:** {failed}",
        "",
    ])

    if overall_ragas:
        report_lines.extend([
            "### Average RAGAS Metrics",
            "",
            f"- **Faithfulness:** {overall_ragas.get('avg_faithfulness', 'N/A')}",
            f"- **Answer Relevancy:** {overall_ragas.get('avg_answer_relevancy', 'N/A')}",
            f"- **Context Precision:** {overall_ragas.get('avg_context_precision', 'N/A')}",
            f"- **Context Recall:** {overall_ragas.get('avg_context_recall', 'N/A')}",
            "",
        ])

    # Performance Metrics
    perf_metrics = retrieval_analysis.get("performance_metrics", {})
    report_lines.extend([
        "### Performance Metrics",
        "",
        f"- **Average Processing Time:** {perf_metrics.get('avg_processing_time_ms', 0):.0f}ms",
        f"- **Average Retrieval Score:** {perf_metrics.get('avg_retrieval_score', 0):.2f}%",
        f"- **Retrieval Success Rate:** {perf_metrics.get('retrieval_success_rate', 0):.1%}",
        "",
    ])

    # Routing Analysis (if available)
    if routing_stats:
        total_routed = sum(routing_stats.values())
        classification_accuracy = ((routing_stats.get('vector_only', 0) + routing_stats.get('hybrid', 0)) / total_routed * 100) if total_routed else 0

        report_lines.extend([
            "### Routing Classification",
            "",
            f"- **SQL Only:** {routing_stats.get('sql_only', 0)} ({routing_stats.get('sql_only', 0) / total_routed * 100:.1f}%)" if total_routed else "- **SQL Only:** 0",
            f"- **Vector Only:** {routing_stats.get('vector_only', 0)} ({routing_stats.get('vector_only', 0) / total_routed * 100:.1f}%)" if total_routed else "- **Vector Only:** 0",
            f"- **Hybrid:** {routing_stats.get('hybrid', 0)} ({routing_stats.get('hybrid', 0) / total_routed * 100:.1f}%)" if total_routed else "- **Hybrid:** 0",
            f"- **Unknown:** {routing_stats.get('unknown', 0)} ({routing_stats.get('unknown', 0) / total_routed * 100:.1f}%)" if total_routed else "- **Unknown:** 0",
            "",
            f"**Classification Accuracy:** {classification_accuracy:.1f}% (vector_only + hybrid expected)",
            "",
        ])

        if misclassifications:
            report_lines.extend([
                f"**Misclassifications:** {len(misclassifications)} queries",
                "",
            ])

    report_lines.extend([
        "---",
        "",
    ])

    # Failure Analysis
    failed_results = [r for r in results if not r.get("success")]
    if failed_results:
        report_lines.extend([
            "## Failure Analysis",
            "",
            f"### Execution Failures ({len(failed_results)} queries)",
            "",
            "| # | Question | Error |",
            "|---|----------|-------|",
        ])

        for i, r in enumerate(failed_results[:10], 1):  # Top 10
            question = r.get("question", "")[:60]
            error = str(r.get("error", ""))[:100]
            report_lines.append(f"| {i} | {question}... | {error}... |")

        report_lines.extend(["", ""])

    # Routing Misclassifications
    if misclassifications:
        report_lines.extend([
            f"### Routing Misclassifications ({len(misclassifications)} queries)",
            "",
            "| # | Question | Category | Expected | Actual | Response Preview |",
            "|---|----------|----------|----------|--------|-----------------|",
        ])

        for i, misc in enumerate(misclassifications[:10], 1):  # Top 10
            question = misc.get("question", "")[:40]
            category = misc.get("category", "unknown")
            expected = misc.get("expected", "")
            actual = misc.get("actual", "")
            preview = misc.get("response_preview", "")[:60]
            report_lines.append(f"| {i} | {question}... | {category} | {expected} | {actual} | {preview}... |")

        report_lines.extend(["", ""])

    # Low-Scoring Queries (RAGAS < 0.7)
    low_scoring = ragas_analysis.get("low_scoring_queries", [])
    if low_scoring:
        report_lines.extend([
            f"### Low-Scoring Queries ({len(low_scoring)} queries with RAGAS < 0.7)",
            "",
            "| # | Question | Min Score | Category |",
            "|---|----------|-----------|----------|",
        ])

        for i, q in enumerate(low_scoring[:10], 1):  # Top 10
            question = q.get("question", "")[:50]
            min_score = q.get("min_score", 0)
            category = q.get("category", "unknown")
            report_lines.append(f"| {i} | {question}... | {min_score:.3f} | {category} |")

        report_lines.extend(["", "---", ""])

    # RAGAS Metrics Analysis
    report_lines.extend([
        "## RAGAS Metrics Analysis",
        "",
        "### Overall Scores",
        "",
    ])

    if overall_ragas:
        report_lines.extend([
            "| Metric | Score |",
            "|--------|-------|",
            f"| Faithfulness | {overall_ragas.get('avg_faithfulness', 'N/A')} |",
            f"| Answer Relevancy | {overall_ragas.get('avg_answer_relevancy', 'N/A')} |",
            f"| Context Precision | {overall_ragas.get('avg_context_precision', 'N/A')} |",
            f"| Context Recall | {overall_ragas.get('avg_context_recall', 'N/A')} |",
            "",
        ])

    # By Category Breakdown
    by_category = ragas_analysis.get("by_category", {})
    if by_category:
        report_lines.extend([
            "### Scores by Category",
            "",
            "| Category | Count | Faithfulness | Answer Relevancy | Context Precision | Context Recall |",
            "|----------|-------|--------------|------------------|-------------------|----------------|",
        ])

        for category, scores in sorted(by_category.items()):
            count = scores.get("count", 0)
            faith = scores.get("avg_faithfulness", "N/A")
            relevancy = scores.get("avg_answer_relevancy", "N/A")
            precision = scores.get("avg_context_precision", "N/A")
            recall = scores.get("avg_context_recall", "N/A")

            report_lines.append(
                f"| {category} | {count} | {faith} | {relevancy} | {precision} | {recall} |"
            )

        report_lines.extend(["", "---", ""])

    # Source Quality Analysis
    retrieval_stats = source_analysis.get("retrieval_stats", {})
    report_lines.extend([
        "## Source Quality Analysis",
        "",
        "### Retrieval Statistics",
        "",
        f"- **Average Sources per Query:** {retrieval_stats.get('avg_sources_per_query', 0)}",
        f"- **Total Unique Sources:** {retrieval_stats.get('total_unique_sources', 0)}",
        f"- **Average Similarity Score:** {retrieval_stats.get('avg_similarity_score', 0):.2f}%",
        f"- **Empty Retrievals:** {source_analysis.get('empty_retrievals', 0)}",
        "",
    ])

    # Top Sources
    top_sources = source_analysis.get("source_diversity", {}).get("top_sources", [])
    if top_sources:
        report_lines.extend([
            "### Top Sources",
            "",
            "| Rank | Source | Count | Avg Score |",
            "|------|--------|-------|-----------|",
        ])

        for i, src in enumerate(top_sources[:10], 1):
            report_lines.append(
                f"| {i} | {src['source'][:40]}... | {src['count']} | {src['avg_score']:.2f}% |"
            )

        report_lines.extend(["", ""])

    # Score Distribution
    score_dist = source_analysis.get("score_analysis", {}).get("score_distribution", {})
    if score_dist:
        report_lines.extend([
            "### Score Distribution",
            "",
            "| Score Range | Count |",
            "|-------------|-------|",
        ])

        for range_label, count in sorted(score_dist.items()):
            report_lines.append(f"| {range_label} | {count} |")

        report_lines.extend(["", "---", ""])

    # Response Quality Analysis
    response_length = response_analysis.get("response_length", {})
    completeness = response_analysis.get("completeness", {})

    report_lines.extend([
        "## Response Quality Analysis",
        "",
        "### Response Length Distribution",
        "",
        f"- **Average Length:** {response_length.get('avg_length', 0):.0f} characters",
        f"- **Min Length:** {response_length.get('min_length', 0)} characters",
        f"- **Max Length:** {response_length.get('max_length', 0)} characters",
        "",
    ])

    length_dist = response_length.get("distribution", {})
    if length_dist:
        report_lines.extend([
            "| Category | Count |",
            "|----------|-------|",
            f"| Very Short (<100 chars) | {length_dist.get('very_short', 0)} |",
            f"| Short (100-200 chars) | {length_dist.get('short', 0)} |",
            f"| Medium (200-400 chars) | {length_dist.get('medium', 0)} |",
            f"| Long (400+ chars) | {length_dist.get('long', 0)} |",
            "",
        ])

    report_lines.extend([
        "### Completeness Analysis",
        "",
        f"- **Complete Answers:** {completeness.get('complete_answers', 0)}",
        f"- **Incomplete Answers:** {completeness.get('incomplete_answers', 0)}",
        f"- **Declined Answers:** {completeness.get('declined_answers', 0)}",
        "",
        "---",
        "",
    ])

    # Retrieval Performance Analysis
    k_value_analysis = retrieval_analysis.get("k_value_analysis", {})
    score_thresholds = retrieval_analysis.get("score_thresholds", {})

    report_lines.extend([
        "## Retrieval Performance Analysis",
        "",
        "### K-Value Analysis",
        "",
        f"- **Configured K:** {k_value_analysis.get('configured_k', 5)}",
        f"- **Actual Average Retrieved:** {k_value_analysis.get('actual_avg_retrieved', 0):.2f}",
        f"- **Queries Below K:** {k_value_analysis.get('queries_below_k', 0)}",
        "",
        "### Score Thresholds",
        "",
        f"- **Above 0.8:** {score_thresholds.get('above_0.8', 0)} sources",
        f"- **0.6 to 0.8:** {score_thresholds.get('0.6_to_0.8', 0)} sources",
        f"- **Below 0.6:** {score_thresholds.get('below_0.6', 0)} sources",
        "",
    ])

    # By Source Type
    by_source_type = retrieval_analysis.get("by_source_type", {})
    if by_source_type:
        report_lines.extend([
            "### Performance by Source Type",
            "",
            "| Source Type | Count | Avg Score |",
            "|-------------|-------|-----------|",
        ])

        for source_type, stats in sorted(by_source_type.items()):
            report_lines.append(
                f"| {source_type} | {stats['count']} | {stats['avg_score']:.2f}% |"
            )

        report_lines.extend(["", "---", ""])

    # Category Performance Analysis
    category_breakdown = category_analysis.get("category_breakdown", {})

    report_lines.extend([
        "## Category Performance Analysis",
        "",
        "### Performance by Category",
        "",
        "| Category | Count | Success Rate | Avg Faithfulness | Avg Answer Relevancy | Avg Sources | Avg Retrieval Score |",
        "|----------|-------|--------------|------------------|----------------------|-------------|---------------------|",
    ])

    for category, stats in sorted(category_breakdown.items()):
        count = stats.get("count", 0)
        success_rate = stats.get("success_rate", 0)
        faith = stats.get("avg_faithfulness", "N/A")
        relevancy = stats.get("avg_answer_relevancy", "N/A")
        sources = stats.get("avg_sources", 0)
        retrieval_score = stats.get("avg_retrieval_score", 0)

        report_lines.append(
            f"| {category} | {count} | {success_rate:.1%} | {faith} | {relevancy} | {sources:.1f} | {retrieval_score:.2f}% |"
        )

    report_lines.extend(["", ""])

    # Comparative Analysis
    comparative = category_analysis.get("comparative_analysis", {})
    if comparative.get("best_category"):
        report_lines.extend([
            "### Comparative Analysis",
            "",
            f"- **Best Performing Category:** {comparative.get('best_category')}",
            f"- **Worst Performing Category:** {comparative.get('worst_category')}",
            f"- **Largest Gap (Faithfulness):** {comparative.get('largest_gap', {}).get('gap', 0):.3f}",
            "",
        ])

    # Recommendations
    recommendations = category_analysis.get("recommendations", [])
    if recommendations:
        report_lines.extend([
            "### Recommendations",
            "",
        ])

        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")

        report_lines.extend(["", "---", ""])

    # Key Findings (automated insights)
    report_lines.extend([
        "## Key Findings",
        "",
    ])

    # Generate automated insights
    insights = []

    if overall_ragas.get("avg_faithfulness") and overall_ragas["avg_faithfulness"] >= 0.8:
        insights.append("✅ High faithfulness score indicates responses are well-grounded in sources")

    if overall_ragas.get("avg_context_recall") and overall_ragas["avg_context_recall"] < 0.7:
        insights.append("⚠️ Low context recall suggests some relevant information may not be retrieved")

    if source_analysis.get("empty_retrievals", 0) > len(results) * 0.1:
        insights.append("⚠️ High rate of empty retrievals - review query preprocessing and index quality")

    if completeness.get("declined_answers", 0) > len(results) * 0.15:
        insights.append("⚠️ High rate of declined answers - may need better source coverage")

    if perf_metrics.get("avg_processing_time_ms", 0) > 2000:
        insights.append("⚠️ High average processing time - consider performance optimization")

    if not insights:
        insights.append("✅ All metrics within acceptable ranges")

    for insight in insights:
        report_lines.append(f"- {insight}")

    report_lines.extend(["", "---", ""])

    # Footer
    report_lines.extend([
        "",
        f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Evaluation Time:** {len(results) * RATE_LIMIT_DELAY / 60:.1f} minutes (estimated)",
        "",
        "---",
        "",
        "Generated by Sports_See Vector Evaluation System",
        ""
    ])

    # Write report to file
    report_path = Path("evaluation_results") / f"vector_evaluation_report_{timestamp}.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    return str(report_path)


if __name__ == "__main__":
    import argparse
    import sys
    import io

    parser = argparse.ArgumentParser(description="Vector evaluation with API-only processing and checkpointing")
    parser.add_argument("--no-resume", action="store_true", help="Start fresh (ignore checkpoint)")
    args = parser.parse_args()

    # Fix Windows charmap encoding
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    try:
        results, json_path = run_vector_evaluation(resume=not args.no_resume)
        print(f"\n✅ Evaluation complete! Results saved to:")
        print(f"   - JSON: {json_path}")
        print(f"   - Report: {json_path.replace('.json', '_report.md')}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Evaluation interrupted by user. Re-run to resume from checkpoint.")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
