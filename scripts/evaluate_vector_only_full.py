"""
FILE: evaluate_vector_only_full.py
STATUS: Active
RESPONSIBILITY: Full evaluation of vector-only search (FAISS + Mistral) - NO RATE LIMITING
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import os
# Fix OpenMP conflict before any other imports
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime

from src.core.config import settings
from src.core.observability import configure_observability
from src.evaluation.models import (
    CategoryResult,
    EvaluationSample,
    MetricScores,
    TestCategory,
)
from src.evaluation.test_cases import EVALUATION_TEST_CASES
from src.services.chat import ChatService
from src.core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)


# Simple prompt template for vector-only evaluation
VECTOR_ONLY_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

CONTEXT:
---
{context}
---

QUESTION:
{question}

INSTRUCTIONS:
- Answer directly and concisely using the context
- Be factual and helpful
- If information is missing, briefly state so

ANSWER:"""


def _build_gemini_client():
    """Build Gemini client for response generation."""
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY required for evaluation (uses Gemini)")

    from google import genai
    logger.info("Using Gemini 2.0 Flash Lite for response generation")
    return genai.Client(api_key=settings.google_api_key)


def _generate_response(client, prompt: str) -> str:
    """Generate response WITHOUT retry delays - fail fast on errors."""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Generation error: {error_msg}")
        # Return error indicator instead of failing completely
        return f"[ERROR: {error_msg[:100]}]"


def generate_all_samples() -> list[EvaluationSample]:
    """Generate evaluation samples for ALL test cases using vector-only search.

    With automatic retry on rate limits.

    Returns:
        List of evaluation samples
    """
    logger.info(f"Generating samples for ALL {len(EVALUATION_TEST_CASES)} test cases (Vector-only)")

    # Initialize services - DISABLE SQL
    chat_service = ChatService(enable_sql=False)
    chat_service.ensure_ready()
    gemini_client = _build_gemini_client()

    samples = []
    for idx, test_case in enumerate(EVALUATION_TEST_CASES):
        logger.info(f"[{idx+1}/{len(EVALUATION_TEST_CASES)}] Processing ({test_case.category.value}): {test_case.question[:60]}...")

        # VECTOR SEARCH with retry on rate limit
        max_retries = 3
        for attempt in range(max_retries):
            try:
                search_results = chat_service.search(test_case.question, k=5)
                break
            except EmbeddingError as e:
                if "429" in str(e) or "rate" in str(e).lower():
                    if attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)
                        logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Failed after {max_retries} retries")
                        raise
                else:
                    raise

        # Build context from search results
        context = "\n\n".join([
            f"[Source: {result.source}]\n{result.text}"
            for result in search_results
        ])

        # Build prompt
        prompt = VECTOR_ONLY_PROMPT.format(
            app_name=settings.app_name,
            context=context,
            question=test_case.question,
        )

        # Generate response
        response = _generate_response(gemini_client, prompt)

        # Create evaluation sample
        sample = EvaluationSample(
            user_input=test_case.question,
            response=response,
            retrieved_contexts=[result.text for result in search_results],
            reference=test_case.ground_truth,
            category=test_case.category,
        )
        samples.append(sample)

        logger.info(f"  Response length: {len(response)} chars")
        # Small delay to avoid rate limits
        time.sleep(0.5)

    return samples


def run_evaluation(samples: list[EvaluationSample]) -> dict:
    """Run RAGAS evaluation on samples."""
    logger.info("Running RAGAS evaluation...")

    # Lazy import to avoid loading at module level
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import (
        Faithfulness,
        LLMContextPrecisionWithoutReference,
        LLMContextRecall,
        ResponseRelevancy,
    )

    # Build evaluator components
    from ragas.llms import LangchainLLMWrapper
    from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
    from ragas.embeddings import LangchainEmbeddingsWrapper

    if settings.google_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        logger.info("Using Gemini as RAGAS evaluator LLM")
        llm_wrapper = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=settings.google_api_key,
            temperature=0.0,
        )
    else:
        logger.info("Using Mistral as RAGAS evaluator LLM")
        llm_wrapper = ChatMistralAI(
            model=settings.chat_model,
            api_key=settings.mistral_api_key,
            temperature=0.0,
        )

    llm = LangchainLLMWrapper(llm_wrapper)

    logger.info("Using Mistral embeddings for RAGAS evaluator")
    embeddings_wrapper = MistralAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.mistral_api_key,
    )
    embeddings = LangchainEmbeddingsWrapper(embeddings_wrapper)

    # Convert to RAGAS dataset format
    dataset_dicts = [
        {
            "user_input": s.user_input,
            "response": s.response,
            "retrieved_contexts": s.retrieved_contexts,
            "reference": s.reference,
        }
        for s in samples
    ]
    eval_dataset = EvaluationDataset.from_list(dataset_dicts)

    # Run evaluation with all metrics
    metrics = [
        Faithfulness(llm=llm),
        ResponseRelevancy(llm=llm, embeddings=embeddings),
        LLMContextPrecisionWithoutReference(llm=llm),
        LLMContextRecall(llm=llm),
    ]

    logger.info(f"Evaluating {len(samples)} samples with {len(metrics)} metrics...")
    result = evaluate(dataset=eval_dataset, metrics=metrics)

    return result


def compute_category_scores(samples: list[EvaluationSample], ragas_result) -> list[CategoryResult]:
    """Compute per-category metric scores."""
    # Group samples by category
    category_samples = {}
    for i, sample in enumerate(samples):
        category = sample.category.value
        if category not in category_samples:
            category_samples[category] = []
        category_samples[category].append(i)

    # Compute scores per category
    category_results = []
    df = ragas_result.to_pandas()

    # Check which relevancy column name is used
    relevancy_col = "answer_relevancy" if "answer_relevancy" in df.columns else "response_relevancy"

    for category, indices in category_samples.items():
        category_df = df.iloc[indices]

        # Get first sample in this category for the category enum
        first_idx = indices[0]
        category_enum = samples[first_idx].category

        category_result = CategoryResult(
            category=category_enum,
            count=len(indices),
            avg_faithfulness=float(category_df["faithfulness"].mean()),
            avg_answer_relevancy=float(category_df[relevancy_col].mean()),
            avg_context_precision=float(category_df["llm_context_precision_without_reference"].mean()),
            avg_context_recall=float(category_df["context_recall"].mean()),
        )
        category_results.append(category_result)

    return category_results


def analyze_failures(samples: list[EvaluationSample], ragas_result) -> dict:
    """Analyze failure cases and patterns."""
    df = ragas_result.to_pandas()
    relevancy_col = "answer_relevancy" if "answer_relevancy" in df.columns else "response_relevancy"

    # Find low-scoring samples (faithfulness < 0.5 or relevancy < 0.5)
    failures = []
    for i, (sample, row) in enumerate(zip(samples, df.itertuples())):
        faith = row.faithfulness
        relevancy = getattr(row, relevancy_col)

        if faith < 0.5 or relevancy < 0.5:
            failures.append({
                "index": i,
                "category": sample.category.value,
                "question": sample.user_input,
                "response": sample.response[:200],
                "faithfulness": faith,
                "relevancy": relevancy,
                "context_recall": row.context_recall,
            })

    # Sort by lowest faithfulness
    failures.sort(key=lambda x: x["faithfulness"])

    # Analyze patterns
    failure_by_category = {}
    for f in failures:
        cat = f["category"]
        failure_by_category[cat] = failure_by_category.get(cat, 0) + 1

    return {
        "total_failures": len(failures),
        "top_5_failures": failures[:5],
        "failures_by_category": failure_by_category,
    }


def main():
    """Run full vector-only evaluation (all 47 test cases)."""
    print("\n" + "=" * 80)
    print("  VECTOR-ONLY FULL EVALUATION")
    print("  FAISS + Mistral Embeddings - NO SQL/Hybrid")
    print("  NO RATE LIMITING - Full Speed")
    print(f"  Total samples: {len(EVALUATION_TEST_CASES)}")
    print("=" * 80 + "\n")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure observability (optional)
    configure_observability()

    start_time = datetime.now()

    # Generate samples with vector-only search
    print("Step 1/3: Generating samples with vector-only search...")
    samples = generate_all_samples()

    # Run RAGAS evaluation
    print("\nStep 2/3: Running RAGAS evaluation...")
    ragas_result = run_evaluation(samples)

    # Compute overall and category scores
    print("\nStep 3/3: Computing scores and analyzing failures...")
    df = ragas_result.to_pandas()

    # Check column names
    relevancy_col = "answer_relevancy" if "answer_relevancy" in df.columns else "response_relevancy"

    overall_scores = MetricScores(
        faithfulness=float(df["faithfulness"].mean()),
        answer_relevancy=float(df[relevancy_col].mean()),
        context_precision=float(df["llm_context_precision_without_reference"].mean()),
        context_recall=float(df["context_recall"].mean()),
    )

    category_scores = compute_category_scores(samples, ragas_result)
    failure_analysis = analyze_failures(samples, ragas_result)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Save results
    results_dir = Path("evaluation_results")
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = results_dir / f"vector_only_full_{timestamp}.json"

    results_data = {
        "evaluation_type": "Vector-Only (FAISS + Mistral)",
        "timestamp": timestamp,
        "duration_seconds": duration,
        "sample_count": len(samples),
        "model": "gemini-2.0-flash-lite",
        "search_method": "FAISS vector search (k=5)",
        "sql_enabled": False,
        "overall_scores": overall_scores.model_dump(),
        "category_scores": [cat.model_dump() for cat in category_scores],
        "failure_analysis": failure_analysis,
        "detailed_results": [
            {
                "question": s.user_input,
                "category": s.category.value,
                "response": s.response,
                "faithfulness": float(df.iloc[i]["faithfulness"]),
                "relevancy": float(df.iloc[i][relevancy_col]),
                "context_precision": float(df.iloc[i]["llm_context_precision_without_reference"]),
                "context_recall": float(df.iloc[i]["context_recall"]),
            }
            for i, s in enumerate(samples)
        ],
    }
    output_file.write_text(json.dumps(results_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print results
    print("\n" + "=" * 80)
    print("  VECTOR-ONLY FULL EVALUATION RESULTS")
    print("=" * 80)
    print(f"\nCompleted in: {duration:.1f} seconds")
    print(f"Results saved to: {output_file}\n")

    print("Overall Scores:")
    print(f"  Faithfulness:       {overall_scores.faithfulness:.3f}")
    print(f"  Answer Relevancy:   {overall_scores.answer_relevancy:.3f}")
    print(f"  Context Precision:  {overall_scores.context_precision:.3f}")
    print(f"  Context Recall:     {overall_scores.context_recall:.3f}")

    print("\nCategory Scores:")
    for cat in category_scores:
        print(f"\n  {cat.category.value.upper()} ({cat.count} samples):")
        print(f"    Faithfulness:       {cat.avg_faithfulness:.3f}")
        print(f"    Answer Relevancy:   {cat.avg_answer_relevancy:.3f}")
        print(f"    Context Precision:  {cat.avg_context_precision:.3f}")
        print(f"    Context Recall:     {cat.avg_context_recall:.3f}")

    # Print failure analysis
    print("\n" + "=" * 80)
    print("  FAILURE ANALYSIS")
    print("=" * 80)
    print(f"\nTotal failures (faith<0.5 or rel<0.5): {failure_analysis['total_failures']}")
    print(f"Failures by category: {failure_analysis['failures_by_category']}")

    print("\nTop 5 Failure Cases:")
    for i, failure in enumerate(failure_analysis['top_5_failures'], 1):
        print(f"\n{i}. [{failure['category'].upper()}] Faith={failure['faithfulness']:.3f}, Rel={failure['relevancy']:.3f}")
        print(f"   Q: {failure['question']}")
        print(f"   R: {failure['response']}")

    print("\n" + "=" * 80)
    print("  EVALUATION COMPLETE")
    print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
