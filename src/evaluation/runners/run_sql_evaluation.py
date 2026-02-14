"""
FILE: run_sql_evaluation.py
STATUS: Active
RESPONSIBILITY: Execute SQL evaluation tests via API; delegate analysis to sql_quality_analysis module
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import json
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from starlette.testclient import TestClient

from src.api.main import create_app
from src.core.config import settings
from src.core.observability import logger
from src.evaluation.analysis.sql_quality_analysis import (
    analyze_column_selection,
    analyze_error_taxonomy,
    analyze_fallback_patterns,
    analyze_query_complexity,
    analyze_query_structure,
    analyze_response_quality,
    analyze_results,  # NEW: Unified interface
)
from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES

# Rate limiting configuration for Gemini free tier (15 RPM)
# SQL queries consume ~2 Gemini calls each (SQL gen + LLM response)
# At 20s delay = 3 queries/min = ~6 Gemini calls/min (well under 15 RPM)
RATE_LIMIT_DELAY_SECONDS = 20
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 30  # Wait 30s on 429 before retry
BATCH_SIZE = 10  # Extra cooldown every N queries
BATCH_COOLDOWN_SECONDS = 30  # Extra pause between batches


# ============================================================================
# INLINE: SQLOracle - Ground truth validation
# ============================================================================
class SQLOracle:
    """Ground truth oracle for validating SQL evaluation results."""

    def __init__(self):
        """Initialize oracle with ground truth from test cases."""
        self.oracle = self._build_oracle()

    def _build_oracle(self) -> dict[str, dict[str, Any]]:
        """Build oracle from test case ground truth."""
        oracle = {}
        for test_case in SQL_TEST_CASES:
            key = test_case.question.strip().lower()
            oracle[key] = {
                "expected_answer": test_case.ground_truth_answer,
                "expected_data": test_case.ground_truth_data,
                "category": getattr(test_case, "category", "unknown"),
            }
        return oracle

    def get_oracle_entry(self, question: str) -> dict[str, Any] | None:
        """Retrieve oracle entry for a question."""
        key = question.strip().lower()
        return self.oracle.get(key)

    def validate_result(self, question: str, actual_response: str) -> bool:
        """Validate if response is semantically correct."""
        if not actual_response or not actual_response.strip():
            return False
        oracle_entry = self.get_oracle_entry(question)
        if oracle_entry is None:
            return False
        # Simple validation: check if key numeric values appear in response
        response_lower = actual_response.lower()
        expected_data = oracle_entry.get("expected_data")
        if isinstance(expected_data, dict):
            for value in expected_data.values():
                if isinstance(value, (int, float)):
                    if str(value) not in response_lower and str(int(value)) not in response_lower:
                        return False
        return True


# ============================================================================
# INLINE: Comprehensive analysis functions
# ============================================================================
def analyze_sql_results(results: list[dict], oracle: SQLOracle) -> dict[str, Any]:
    """Generate comprehensive SQL evaluation analysis."""
    successful = [r for r in results if r.get("success", False)]

    # Calculate accuracy
    correct_count = sum(
        1 for r in successful
        if oracle.validate_result(r.get("question", ""), r.get("response", ""))
    )
    accuracy_rate = (correct_count / len(successful) * 100) if successful else 0

    # Calculate latencies
    times = [r.get("processing_time_ms", 0) for r in successful if isinstance(r.get("processing_time_ms"), (int, float))]
    if times:
        p50 = statistics.median(times)
        p95 = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
        p99 = statistics.quantiles(times, n=100)[98] if len(times) >= 100 else max(times)
    else:
        p50 = p95 = p99 = 0

    # Analyze by category
    by_category = defaultdict(lambda: {"count": 0, "correct": 0, "times": []})
    for r in results:
        cat = r.get("category", "unknown")
        by_category[cat]["count"] += 1
        if r.get("success") and oracle.validate_result(r.get("question", ""), r.get("response", "")):
            by_category[cat]["correct"] += 1
        if isinstance(r.get("processing_time_ms"), (int, float)):
            by_category[cat]["times"].append(r["processing_time_ms"])

    return {
        "overall": {
            "total_queries": len(results),
            "successful": len(successful),
            "correct_count": correct_count if successful else 0,
            "accuracy_rate": round(accuracy_rate, 2),
            "p50_ms": round(p50, 2),
            "p95_ms": round(p95, 2),
            "p99_ms": round(p99, 2),
        },
        "by_category": {
            cat: {
                "count": data["count"],
                "accuracy_rate": round(data["correct"] / data["count"] * 100 if data["count"] > 0 else 0, 2),
                "avg_time_ms": round(statistics.mean(data["times"]) if data["times"] else 0, 2),
            }
            for cat, data in by_category.items()
        },
    }


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context."""
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him",
        "which of them", "how many games did he"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def _is_conversational_case(test_case) -> bool:
    """Check if test case is conversational."""
    if hasattr(test_case, 'category') and isinstance(test_case.category, str):
        return "conversational" in test_case.category.lower()
    return False


def run_sql_evaluation(test_indices: list[int] | None = None) -> tuple[list[dict[str, Any]], str]:
    """Run SQL evaluation on all test cases using FastAPI API.

    Args:
        test_indices: Optional list of test case indices to run (for mini mode)

    Returns:
        Tuple of (results list, output JSON path)
    """
    logger.info(f"Starting SQL evaluation with {len(SQL_TEST_CASES)} test cases")

    if test_indices is not None:
        selected_cases = [SQL_TEST_CASES[i] for i in test_indices if i < len(SQL_TEST_CASES)]
        logger.info(f"Mini mode: running {len(selected_cases)} of {len(SQL_TEST_CASES)} test cases")
    else:
        selected_cases = list(SQL_TEST_CASES)

    results = []
    success_count = 0
    failure_count = 0

    # Checkpoint file for crash recovery
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    checkpoint_path = output_dir / "sql_evaluation_checkpoint.json"

    # Resume from checkpoint if exists
    start_index = 0
    if checkpoint_path.exists():
        checkpoint_data = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        results = checkpoint_data.get("results", [])
        start_index = len(results)
        success_count = sum(1 for r in results if r.get("success"))
        failure_count = sum(1 for r in results if not r.get("success"))
        logger.info(f"Resuming from checkpoint: {start_index}/{len(selected_cases)} done ({success_count} success, {failure_count} failures)")

    # Create FastAPI app and run evaluation through API
    app = create_app()
    with TestClient(app) as client:
        current_conversation_id = None
        current_turn_number = 0
        current_thread = None  # Track conversation thread

        for i, test_case in enumerate(selected_cases, 1):
            # Skip already-completed cases (checkpoint resume)
            if i <= start_index:
                continue

            logger.info(f"[{i}/{len(selected_cases)}] Evaluating: {test_case.question}")

            # Rate limit delay (skip before first query)
            if i > 1 and i > start_index + 1:
                # Extra batch cooldown every BATCH_SIZE queries
                queries_done = i - start_index - 1
                if queries_done > 0 and queries_done % BATCH_SIZE == 0:
                    logger.info(f"  Batch cooldown: {BATCH_COOLDOWN_SECONDS}s (after {queries_done} queries)...")
                    time.sleep(BATCH_COOLDOWN_SECONDS)
                time.sleep(RATE_LIMIT_DELAY_SECONDS)

            # Handle conversational test cases using conversation_thread field
            if hasattr(test_case, 'conversation_thread') and test_case.conversation_thread:
                # Check if thread changed (new conversation needed)
                if test_case.conversation_thread != current_thread:
                    # Start new conversation for new thread
                    conv_resp = client.post("/api/v1/conversations", json={})
                    current_conversation_id = conv_resp.json()["id"]
                    current_turn_number = 1
                    current_thread = test_case.conversation_thread
                    logger.info(f"  → New conversation thread: {current_thread} (conversation_id: {current_conversation_id})")
                else:
                    # Continue same conversation thread
                    current_turn_number += 1
                    logger.info(f"  → Continue thread: {current_thread} (turn {current_turn_number})")
            else:
                # Isolated query (no conversation)
                current_conversation_id = None
                current_turn_number = 0
                current_thread = None

            try:
                # Build API request payload
                payload = {
                    "query": test_case.question,
                    "k": 5,
                    "include_sources": True,
                    "conversation_id": current_conversation_id,
                }

                # Retry logic for rate limiting
                http_response = None
                last_error = None

                for attempt in range(MAX_RETRIES + 1):
                    http_response = client.post("/api/v1/chat", json=payload)

                    if http_response.status_code == 200:
                        break

                    # Check for rate limit
                    is_rate_limit = (
                        http_response.status_code == 429
                        or (http_response.status_code == 500 and "429" in http_response.text)
                    )

                    if is_rate_limit and attempt < MAX_RETRIES:
                        wait = RETRY_BACKOFF_SECONDS * (attempt + 1)
                        logger.warning(f"  Rate limit hit, retry {attempt + 1}/{MAX_RETRIES} after {wait}s...")
                        time.sleep(wait)
                    else:
                        last_error = f"API error {http_response.status_code}: {http_response.text[:300]}"
                        break

                if http_response is None or http_response.status_code != 200:
                    raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {last_error}")

                # Parse response
                response_data = http_response.json()

                # Determine routing
                sources = response_data.get("sources", [])
                actual_routing = "sql_only" if len(sources) == 0 else "fallback_to_vector"
                expected_routing = test_case.query_type.value

                is_misclassified = (
                    (expected_routing == "sql_only" and actual_routing != "sql_only") or
                    (expected_routing in ["contextual_only", "hybrid"] and actual_routing == "sql_only")
                )

                category = test_case.category if hasattr(test_case, "category") else "unknown"

                results.append({
                    "question": test_case.question,
                    "category": category,
                    "response": response_data.get("answer", ""),
                    "expected_routing": expected_routing,
                    "actual_routing": actual_routing,
                    "is_misclassified": is_misclassified,
                    "sources_count": len(sources),
                    "processing_time_ms": response_data.get("processing_time_ms", 0.0),
                    "generated_sql": response_data.get("generated_sql"),
                    "conversation_id": current_conversation_id,
                    "success": True
                })

                success_count += 1
                logger.info(f"✓ Success (routing: {actual_routing})")

            except Exception as e:
                logger.error(f"✗ Failed: {str(e)}")
                results.append({
                    "question": test_case.question,
                    "category": test_case.category if hasattr(test_case, "category") else "unknown",
                    "response": "",
                    "expected_routing": test_case.query_type.value,
                    "actual_routing": "error",
                    "is_misclassified": True,
                    "sources_count": 0,
                    "processing_time_ms": 0.0,
                    "generated_sql": None,
                    "conversation_id": current_conversation_id,
                    "success": False,
                    "error": str(e)
                })
                failure_count += 1

            # Save checkpoint after each query
            checkpoint_path.write_text(
                json.dumps({"results": results, "completed": i}, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

    logger.info(f"\nEvaluation complete: {success_count} success, {failure_count} failures")

    # Generate comprehensive analysis using unified interface
    logger.info("Generating comprehensive analysis...")
    analysis = analyze_results(results, SQL_TEST_CASES)

    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"sql_evaluation_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Save analysis to separate JSON file
    analysis_path = output_dir / f"sql_evaluation_analysis_{timestamp}.json"
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # Clean up checkpoint after successful save
    if checkpoint_path.exists():
        checkpoint_path.unlink()
        logger.info("Checkpoint file cleaned up")

    logger.info(f"Results saved to: {json_path}")
    logger.info(f"Analysis saved to: {analysis_path}")

    return results, str(json_path)


def generate_comprehensive_report(results: list[dict[str, Any]], json_path: str) -> str:
    """Generate comprehensive evaluation report with all metrics.

    Args:
        results: Evaluation results
        json_path: Path to JSON results file

    Returns:
        Path to generated markdown report
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    report_path = output_dir / f"sql_evaluation_report_{timestamp}.md"

    # Run all analyses
    oracle = SQLOracle()
    analysis = analyze_sql_results(results, oracle)

    error_taxonomy = analyze_error_taxonomy(results)
    fallback_patterns = analyze_fallback_patterns(results)
    response_quality = analyze_response_quality(results)
    query_structure = analyze_query_structure(results)
    query_complexity = analyze_query_complexity(results)
    column_selection = analyze_column_selection(results)

    # Compute accuracy breakdown for report
    correct_count = analysis['overall']['correct_count']
    successful_count = analysis['overall']['successful']
    analysis['accuracy'] = {
        'correct_results': correct_count,
        'incorrect_results': successful_count - correct_count,
        'unknown_results': len(results) - successful_count,
        'accuracy_breakdown': {},
    }

    # Compute SQL quality from query_structure for report
    total_with_sql = query_structure['total_queries']
    joins_count = query_structure['queries_with_join']
    correct_joins = query_structure['correctness']['correct_joins']
    broken_joins = joins_count - correct_joins
    analysis['sql_quality'] = {
        'total_queries_with_sql': total_with_sql,
        'queries_with_joins': joins_count,
        'join_correctness_count': correct_joins,
        'join_correctness_rate': (correct_joins / joins_count * 100) if joins_count > 0 else 100.0,
        'broken_joins_count': broken_joins,
        'broken_joins_rate': (broken_joins / joins_count * 100) if joins_count > 0 else 0.0,
        'missing_joins_estimated': query_structure['correctness']['missing_joins'],
        'broken_joins_sample': query_structure['correctness']['examples'],
    }

    # Enrich by_category with success_rate, fallback_rate, avg_processing_time_ms
    for cat, stats in analysis['by_category'].items():
        cat_results = [r for r in results if r.get("category") == cat]
        cat_successful = sum(1 for r in cat_results if r.get("success"))
        cat_fallbacks = sum(1 for r in cat_results if r.get("actual_routing") == "fallback_to_vector")
        stats['success_rate'] = (cat_successful / len(cat_results) * 100) if cat_results else 0.0
        stats['avg_processing_time_ms'] = stats.pop('avg_time_ms', 0)
        stats['fallback_rate'] = (cat_fallbacks / len(cat_results) * 100) if cat_results else 0.0

    # Calculate summary statistics
    total_queries = len(results)
    successful_queries = sum(1 for r in results if r.get("success", False))
    failed_queries = total_queries - successful_queries
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0

    misclassifications = sum(1 for r in results if r.get("is_misclassified", False))
    classification_accuracy = ((total_queries - misclassifications) / total_queries * 100) if total_queries > 0 else 0

    # Processing times
    processing_times = [r["processing_time_ms"] for r in results if r.get("success", False)]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    min_processing_time = min(processing_times) if processing_times else 0
    max_processing_time = max(processing_times) if processing_times else 0

    # Generate report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# SQL Evaluation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Dataset:** {total_queries} SQL test cases\n\n")
        f.write(f"**Results JSON:** `{json_path}`\n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Queries:** {total_queries}\n")
        f.write(f"- **Successful Executions:** {successful_queries} ({success_rate:.1f}%)\n")
        f.write(f"- **Failed Executions:** {failed_queries}\n")
        f.write(f"- **Result Accuracy:** {analysis['overall']['accuracy_rate']:.1f}% ({analysis['overall']['correct_count']}/{analysis['overall']['successful']})\n")
        f.write(f"- **Classification Accuracy:** {classification_accuracy:.1f}%\n")
        f.write(f"- **Misclassifications:** {misclassifications}\n")
        f.write(f"- **Avg Processing Time:** {avg_processing_time:.0f}ms\n")
        f.write(f"- **p95 Processing Time:** {analysis['overall']['p95_ms']:.0f}ms\n")
        f.write(f"- **p99 Processing Time:** {analysis['overall']['p99_ms']:.0f}ms\n\n")

        # Failure Analysis
        f.write("## Failure Analysis\n\n")

        # Execution failures
        execution_failures = [r for r in results if not r.get("success", True)]
        if execution_failures:
            f.write(f"### Execution Failures ({len(execution_failures)})\n\n")
            f.write("| Question | Category | Error |\n")
            f.write("|----------|----------|-------|\n")
            for failure in execution_failures:
                question = failure["question"][:60] + "..." if len(failure["question"]) > 60 else failure["question"]
                category = failure.get("category", "unknown")
                error = failure.get("error", "Unknown error")[:50]
                f.write(f"| {question} | {category} | {error} |\n")
            f.write("\n")
        else:
            f.write("### Execution Failures\n\n")
            f.write("✓ No execution failures detected.\n\n")

        # Misclassifications
        misclassified = [r for r in results if r.get("is_misclassified", False) and r.get("success", True)]
        if misclassified:
            f.write(f"### Routing Misclassifications ({len(misclassified)})\n\n")
            f.write("| Question | Category | Expected | Actual |\n")
            f.write("|----------|----------|----------|--------|\n")
            for mc in misclassified:
                question = mc["question"][:60] + "..." if len(mc["question"]) > 60 else mc["question"]
                category = mc.get("category", "unknown")
                expected = mc["expected_routing"]
                actual = mc["actual_routing"]
                f.write(f"| {question} | {category} | {expected} | {actual} |\n")
            f.write("\n")
        else:
            f.write("### Routing Misclassifications\n\n")
            f.write("✓ No routing misclassifications detected.\n\n")

        # Result Accuracy Analysis
        f.write("## Result Accuracy Analysis\n\n")
        f.write(f"- **Correct Results:** {analysis['accuracy']['correct_results']}\n")
        f.write(f"- **Incorrect Results:** {analysis['accuracy']['incorrect_results']}\n")
        f.write(f"- **Unknown (Not in Oracle):** {analysis['accuracy']['unknown_results']}\n\n")

        if analysis['accuracy']['accuracy_breakdown']:
            f.write("### Accuracy Breakdown\n\n")
            for accuracy_type, count in analysis['accuracy']['accuracy_breakdown'].items():
                f.write(f"- **{accuracy_type.replace('_', ' ').title()}:** {count}\n")
            f.write("\n")

        # SQL Quality Analysis
        f.write("## SQL Quality Analysis\n\n")
        f.write(f"- **Total Queries with SQL:** {analysis['sql_quality']['total_queries_with_sql']}\n")
        f.write(f"- **Queries with JOINs:** {analysis['sql_quality']['queries_with_joins']}\n")
        f.write(f"- **JOIN Correctness Rate:** {analysis['sql_quality']['join_correctness_rate']:.1f}% ({analysis['sql_quality']['join_correctness_count']}/{analysis['sql_quality']['queries_with_joins']})\n")
        f.write(f"- **Broken JOINs:** {analysis['sql_quality']['broken_joins_count']} ({analysis['sql_quality']['broken_joins_rate']:.1f}%)\n")
        f.write(f"- **Missing JOINs (Estimated):** {analysis['sql_quality']['missing_joins_estimated']}\n\n")

        if analysis['sql_quality']['broken_joins_sample']:
            f.write("### Broken JOINs (Sample)\n\n")
            for i, broken_join in enumerate(analysis['sql_quality']['broken_joins_sample'], 1):
                f.write(f"{i}. **{broken_join['question'][:80]}**\n")
                f.write(f"   - Issue: {broken_join['issue']}\n")
                f.write(f"   - SQL: `{broken_join['sql']}`\n\n")

        # Performance Metrics
        f.write("### Performance Metrics\n\n")
        f.write(f"- **Average Processing Time:** {avg_processing_time:.0f}ms\n")
        f.write(f"- **Min Processing Time:** {min_processing_time:.0f}ms\n")
        f.write(f"- **Max Processing Time:** {max_processing_time:.0f}ms\n")
        f.write(f"- **p50 (Median):** {analysis['overall']['p50_ms']:.0f}ms\n")
        f.write(f"- **p95:** {analysis['overall']['p95_ms']:.0f}ms\n")
        f.write(f"- **p99:** {analysis['overall']['p99_ms']:.0f}ms\n\n")

        # Compute outliers inline (queries > p95 threshold)
        outlier_threshold = analysis['overall']['p95_ms']
        outlier_queries = [
            r for r in results
            if r.get("success") and r.get("processing_time_ms", 0) > outlier_threshold
        ]
        if outlier_queries:
            f.write("### Performance Outliers\n\n")
            f.write(f"Found {len(outlier_queries)} queries exceeding p95 threshold ({outlier_threshold:.0f}ms):\n\n")
            for outlier in outlier_queries:
                f.write(f"- **{outlier['question'][:80]}** ({outlier['processing_time_ms']:.0f}ms) - {outlier.get('category', 'unknown')}\n")
            f.write("\n")

        # Response Quality Analysis
        f.write("## Response Quality Analysis\n\n")

        f.write("### Error Taxonomy\n\n")
        f.write(f"- **Total Errors:** {error_taxonomy['total_errors']}\n")
        f.write(f"- **LLM Declined:** {len(error_taxonomy['llm_declined'])}\n")
        f.write(f"- **Syntax Errors:** {len(error_taxonomy['syntax_error'])}\n")
        f.write(f"- **Empty Responses:** {len(error_taxonomy['empty_response'])}\n\n")

        if error_taxonomy['llm_declined']:
            f.write("#### LLM Declined Examples\n\n")
            for case in error_taxonomy['llm_declined'][:3]:
                f.write(f"**Q:** {case['question']}\n\n")
                f.write(f"**Response:** {case['response']}\n\n")

        f.write("### Fallback Patterns\n\n")
        f.write(f"- **SQL Only:** {fallback_patterns['sql_only']} ({100 - fallback_patterns['fallback_rate']:.1f}%)\n")
        f.write(f"- **Fallback to Vector:** {fallback_patterns['fallback_to_vector']} ({fallback_patterns['fallback_rate']:.1f}%)\n\n")

        f.write("#### Fallback by Category\n\n")
        f.write("| Category | Total | Fallbacks | Rate |\n")
        f.write("|----------|-------|-----------|------|\n")
        for category, stats in fallback_patterns['by_category'].items():
            f.write(f"| {category} | {stats['total']} | {stats['fallbacks']} | {stats['rate']:.1f}% |\n")
        f.write("\n")

        f.write("### Response Quality Metrics\n\n")
        f.write(f"- **Avg Response Length:** {response_quality['verbosity']['avg_length']:.0f} chars\n")
        f.write(f"- **Min/Max Length:** {response_quality['verbosity']['min_length']} / {response_quality['verbosity']['max_length']} chars\n")
        f.write(f"- **Responses with Hedging:** {response_quality['confidence_indicators']['total_with_hedging']}\n")
        f.write(f"- **Complete Responses:** {response_quality['completeness']['complete']}\n")
        f.write(f"- **Incomplete Responses:** {response_quality['completeness']['incomplete']}\n\n")

        # Query Quality Analysis
        f.write("## Query Quality Analysis\n\n")

        f.write("### Query Structure\n\n")
        if query_structure['total_queries'] > 0:
            f.write(f"- **Total SQL Queries Generated:** {query_structure['total_queries']}\n")
            f.write(f"- **Queries with JOIN:** {query_structure['queries_with_join']} ({query_structure['queries_with_join']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with Aggregation:** {query_structure['queries_with_aggregation']} ({query_structure['queries_with_aggregation']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with Filter (WHERE):** {query_structure['queries_with_filter']} ({query_structure['queries_with_filter']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with ORDER BY:** {query_structure['queries_with_ordering']} ({query_structure['queries_with_ordering']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with LIMIT:** {query_structure['queries_with_limit']} ({query_structure['queries_with_limit']/query_structure['total_queries']*100:.1f}%)\n\n")

            f.write("#### JOIN Correctness\n\n")
            f.write(f"- **Correct JOINs:** {query_structure['correctness']['correct_joins']}\n")
            f.write(f"- **Missing JOINs:** {query_structure['correctness']['missing_joins']}\n\n")
        else:
            f.write("No SQL queries were captured for analysis.\n\n")

        f.write("### Query Complexity\n\n")
        if query_complexity['total_queries'] > 0:
            f.write(f"- **Avg JOINs per Query:** {query_complexity['avg_joins_per_query']:.2f}\n")
            f.write(f"- **Avg WHERE Conditions:** {query_complexity['avg_where_conditions']:.2f}\n")
            f.write(f"- **Queries with Subqueries:** {query_complexity['queries_with_subqueries']}\n")
            f.write(f"- **Queries with GROUP BY:** {query_complexity['queries_with_group_by']}\n")
            f.write(f"- **Queries with HAVING:** {query_complexity['queries_with_having']}\n\n")

            f.write("#### Complexity Distribution\n\n")
            f.write("| Level | Count | Percentage |\n")
            f.write("|-------|-------|------------|\n")
            for level, count in query_complexity['complexity_distribution'].items():
                pct = (count / query_complexity['total_queries'] * 100) if query_complexity['total_queries'] > 0 else 0
                f.write(f"| {level.replace('_', ' ').title()} | {count} | {pct:.1f}% |\n")
            f.write("\n")
        else:
            f.write("No SQL queries were captured for complexity analysis.\n\n")

        f.write("### Column Selection\n\n")
        if column_selection['total_queries'] > 0:
            f.write(f"- **Avg Columns Selected:** {column_selection['avg_columns_selected']:.2f}\n")
            f.write(f"- **SELECT * Usage:** {column_selection['select_star_count']} queries\n")
            f.write(f"- **Over-selection Rate:** {column_selection['over_selection_rate']:.1f}%\n")
            f.write(f"- **Under-selection Rate:** {column_selection['under_selection_rate']:.1f}%\n\n")
        else:
            f.write("No SQL queries were captured for column selection analysis.\n\n")

        # Category Performance Analysis
        f.write("## Category Performance Analysis\n\n")
        f.write("| Category | Count | Success | Accuracy | Avg Time | Fallback Rate |\n")
        f.write("|----------|-------|---------|----------|----------|---------------|\n")
        for category, stats in sorted(analysis['by_category'].items()):
            f.write(
                f"| {category} | {stats['count']} | "
                f"{stats['success_rate']:.1f}% | {stats['accuracy_rate']:.1f}% | "
                f"{stats['avg_processing_time_ms']:.0f}ms | {stats['fallback_rate']:.1f}% |\n"
            )
        f.write("\n")

        # Key Findings
        f.write("## Key Findings\n\n")
        findings = []

        if success_rate >= 95:
            findings.append(f"✓ **Excellent execution reliability** ({success_rate:.1f}% success rate)")
        elif success_rate >= 80:
            findings.append(f"⚠ **Good execution reliability** ({success_rate:.1f}% success rate) with room for improvement")
        else:
            findings.append(f"❌ **Poor execution reliability** ({success_rate:.1f}% success rate) - needs attention")

        # Result accuracy finding
        result_accuracy = analysis['overall']['accuracy_rate']
        if result_accuracy >= 90:
            findings.append(f"✓ **Excellent result accuracy** ({result_accuracy:.1f}%) - responses match expected results")
        elif result_accuracy >= 75:
            findings.append(f"⚠ **Good result accuracy** ({result_accuracy:.1f}%) - some errors detected")
        else:
            findings.append(f"❌ **Low result accuracy** ({result_accuracy:.1f}%) - significant improvements needed")

        if classification_accuracy >= 95:
            findings.append(f"✓ **High classification accuracy** ({classification_accuracy:.1f}%)")
        elif classification_accuracy >= 80:
            findings.append(f"⚠ **Moderate classification accuracy** ({classification_accuracy:.1f}%) - could be improved")
        else:
            findings.append(f"❌ **Low classification accuracy** ({classification_accuracy:.1f}%) - needs improvement")

        # JOIN quality finding
        join_correctness = analysis['sql_quality']['join_correctness_rate']
        broken_joins = analysis['sql_quality']['broken_joins_count']
        if join_correctness >= 95:
            findings.append(f"✓ **Excellent JOIN correctness** ({join_correctness:.1f}%) - properly structured queries")
        elif broken_joins > 0:
            findings.append(f"❌ **Critical: {broken_joins} broken JOINs detected** ({analysis['sql_quality']['broken_joins_rate']:.1f}%) - results may be incorrect")
        else:
            findings.append(f"⚠ **Moderate JOIN quality** ({join_correctness:.1f}%)")

        if fallback_patterns['fallback_rate'] < 10:
            findings.append(f"✓ **Low fallback rate** ({fallback_patterns['fallback_rate']:.1f}%) indicates good SQL routing")
        elif fallback_patterns['fallback_rate'] < 25:
            findings.append(f"⚠ **Moderate fallback rate** ({fallback_patterns['fallback_rate']:.1f}%)")
        else:
            findings.append(f"❌ **High fallback rate** ({fallback_patterns['fallback_rate']:.1f}%) suggests classifier needs tuning")

        if error_taxonomy['total_errors'] == 0:
            findings.append("✓ **No LLM errors detected** - excellent response quality")
        elif error_taxonomy['total_errors'] < 5:
            findings.append(f"⚠ **Few LLM errors** ({error_taxonomy['total_errors']}) detected")
        else:
            findings.append(f"❌ **Multiple LLM errors** ({error_taxonomy['total_errors']}) detected - review prompts")

        # Latency finding
        p95_time = analysis['overall']['p95_ms']
        if p95_time < 10000:
            findings.append(f"✓ **Fast performance** (p95: {p95_time:.0f}ms) suitable for interactive use")
        elif p95_time < 30000:
            findings.append(f"⚠ **Moderate performance** (p95: {p95_time:.0f}ms)")
        else:
            findings.append(f"❌ **Slow performance** (p95: {p95_time:.0f}ms) - consider optimization")

        for finding in findings:
            f.write(f"{finding}\n\n")

        # Detailed Test Results
        f.write("## Detailed Test Results\n\n")

        # Group by category
        by_category = defaultdict(list)
        for result in results:
            category = result.get("category", "unknown")
            by_category[category].append(result)

        for category in sorted(by_category.keys()):
            category_results = by_category[category]
            f.write(f"### {category.replace('_', ' ').title()} ({len(category_results)} tests)\n\n")

            for result in category_results:
                status = "✓" if result.get("success", False) and not result.get("is_misclassified", False) else "✗"
                f.write(f"**{status} {result['question']}**\n\n")
                f.write(f"- **Expected Routing:** {result['expected_routing']}\n")
                f.write(f"- **Actual Routing:** {result['actual_routing']}\n")
                f.write(f"- **Processing Time:** {result['processing_time_ms']:.0f}ms\n")

                if result.get("generated_sql"):
                    f.write(f"- **Generated SQL:**\n```sql\n{result['generated_sql']}\n```\n\n")

                if not result.get("success", True):
                    f.write(f"- **Error:** {result.get('error', 'Unknown')}\n\n")

                f.write(f"- **Response:**\n{result['response']}\n\n")

        # Report sections
        f.write("---\n\n")
        f.write("## Report Sections\n\n")
        f.write("1. Executive Summary - Overall metrics and success rates\n")
        f.write("2. Failure Analysis - Execution failures, misclassifications, performance\n")
        f.write("3. Response Quality Analysis - Error patterns, fallback behavior, response metrics\n")
        f.write("4. Query Quality Analysis - SQL structure, complexity, column selection\n")
        f.write("5. Key Findings - Actionable insights and recommendations\n")
        f.write("6. Detailed Test Results - Complete test-by-test breakdown\n\n")

    logger.info(f"Report saved to: {report_path}")
    return str(report_path)


def main():
    """Main entry point for SQL evaluation."""
    import argparse

    parser = argparse.ArgumentParser(description="SQL evaluation runner")
    parser.add_argument("--mini", action="store_true", help="Run mini evaluation with 4 diverse test cases")
    args = parser.parse_args()

    test_indices = None
    if args.mini:
        # Select 4 diverse cases: simple(0), comparison(13), aggregation(20), complex(27)
        test_indices = [0, 13, 20, 27]
        print(f"Mini mode: running indices {test_indices}")

    try:
        # Run evaluation
        results, json_path = run_sql_evaluation(test_indices=test_indices)

        # Generate comprehensive report
        report_path = generate_comprehensive_report(results, json_path)

        print("\n" + "="*80)
        print("SQL EVALUATION COMPLETE" + (" (MINI)" if args.mini else ""))
        print("="*80)
        print(f"\nResults saved to:")
        print(f"  - JSON: {json_path}")
        print(f"  - Report: {report_path}")
        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
