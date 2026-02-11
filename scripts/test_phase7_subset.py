"""
FILE: test_phase7_subset.py
STATUS: Active
RESPONSIBILITY: Test Phase 7 (Query Expansion) on 12-sample bad-relevancy subset
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import os
# Fix OpenMP conflict before any other imports
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import logging
import time
from pathlib import Path

from src.core.config import settings
from src.core.observability import configure_observability, logfire
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES
from src.services.chat import ChatService

logger = logging.getLogger(__name__)


def _build_generation_client():
    """Build Gemini client for sample generation."""
    if settings.google_api_key:
        from google import genai
        logger.info("Using Gemini for sample generation")
        return genai.Client(api_key=settings.google_api_key)
    return None


def _generate_with_retry(client, prompt: str, max_retries: int = 3) -> str:
    """Generate response with retry logic."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            is_retryable = (
                "429" in str(e)
                or "rate" in str(e).lower()
                or "ResourceExhausted" in type(e).__name__
            )
            if is_retryable and attempt < max_retries - 1:
                wait = 10 * (2 ** attempt)
                logger.warning(f"Rate limited, waiting {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("All retries exhausted")


# Phase 5 prompt (winning prompt from quick test)
PHASE5_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer the question directly and precisely
2. Base your answer on the context provided above
3. Be concise and factual
4. Cite sources when relevant
5. If information is not in the context, briefly state that

ANSWER:"""


@logfire.instrument("test_phase7_subset")
def test_subset(
    chat_service: ChatService,
    subset_indices: list[int],
    phase_name: str,
) -> list[dict]:
    """Test on subset of queries.

    Args:
        chat_service: ChatService instance
        subset_indices: Indices of test cases to run
        phase_name: Name of the phase being tested

    Returns:
        List of sample dicts
    """
    gemini_client = _build_generation_client()
    if not gemini_client:
        raise ValueError("Gemini API key required for testing")

    logger.info(f"Testing {phase_name} on {len(subset_indices)} samples")

    samples = []

    for i, idx in enumerate(subset_indices):
        tc = EVALUATION_TEST_CASES[idx]
        logger.info(f"Sample {i+1}/{len(subset_indices)} (idx={idx}): {tc.question[:60]}")

        try:
            # Search (uses Phase 7: query expansion, no metadata filtering)
            search_results = chat_service.search(query=tc.question, k=settings.search_k)
            contexts = [r.text for r in search_results]
            context_str = "\n\n---\n\n".join(
                f"Source: {r.source} (Score: {r.score:.1f}%)\\n{r.text}"
                for r in search_results
            )

            # Generate answer using Phase 5 prompt
            prompt = PHASE5_PROMPT.format(
                app_name=settings.app_name,
                context=context_str,
                question=tc.question,
            )

            answer = _generate_with_retry(gemini_client, prompt)

            samples.append({
                "index": idx,
                "question": tc.question,
                "answer": answer,
                "contexts": contexts,
                "reference": tc.ground_truth,
                "category": tc.category.value,
            })

            time.sleep(2)  # Rate limiting

        except Exception as e:
            logger.error(f"Failed on sample {idx}: {e}")
            raise

    return samples


def _build_evaluator_llm():
    """Build RAGAS evaluator LLM."""
    from ragas.llms import LangchainLLMWrapper

    if settings.google_api_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        logger.info("Using Gemini as RAGAS evaluator LLM")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=settings.google_api_key,
            temperature=0.0,
        )
    else:
        from langchain_mistralai import ChatMistralAI
        logger.info("Using Mistral as RAGAS evaluator LLM")
        llm = ChatMistralAI(
            model=settings.chat_model,
            api_key=settings.mistral_api_key,
            temperature=0.0,
        )
    return LangchainLLMWrapper(llm)


def _build_evaluator_embeddings():
    """Build embeddings for RAGAS evaluator."""
    from langchain_mistralai import MistralAIEmbeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper

    logger.info("Using Mistral embeddings for RAGAS evaluator")
    embeddings = MistralAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.mistral_api_key,
    )
    return LangchainEmbeddingsWrapper(embeddings)


@logfire.instrument("evaluate_subset")
def evaluate_subset(samples: list[dict]) -> dict:
    """Run RAGAS evaluation on subset.

    Args:
        samples: List of sample dicts

    Returns:
        Dict with metrics
    """
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import Faithfulness, ResponseRelevancy

    logger.info(f"Evaluating {len(samples)} samples")

    evaluator_llm = _build_evaluator_llm()
    evaluator_embeddings = _build_evaluator_embeddings()

    # Build dataset
    dataset_dicts = [
        {
            "user_input": s["question"],
            "response": s["answer"],
            "retrieved_contexts": s["contexts"],
            "reference": s["reference"],
        }
        for s in samples
    ]
    eval_dataset = EvaluationDataset.from_list(dataset_dicts)

    # Only evaluate key metrics for speed
    metrics = [
        Faithfulness(llm=evaluator_llm),
        ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings),
    ]

    logger.info("Running RAGAS evaluation...")
    ragas_result = evaluate(dataset=eval_dataset, metrics=metrics)

    df = ragas_result.to_pandas()

    # Calculate metrics
    def _safe_mean(series):
        valid = series.dropna()
        return float(valid.mean()) if len(valid) > 0 else None

    faithfulness = _safe_mean(df.get("faithfulness", []))
    answer_relevancy = _safe_mean(df.get("answer_relevancy", []))

    # Count refusals
    refusal_count = sum(
        1 for s in samples
        if any(phrase in s["answer"].lower() for phrase in [
            "i am sorry", "do not contain", "does not contain",
            "cannot answer", "i don't have"
        ])
    )

    return {
        "sample_count": len(samples),
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "refusal_count": refusal_count,
        "refusal_rate": refusal_count / len(samples) if samples else 0,
    }


def print_comparison(phase5_metrics: dict, phase7_metrics: dict) -> None:
    """Print comparison table."""
    def fmt(val):
        return f"{val:.3f}" if val is not None else "N/A"

    def pct_change(old, new):
        if old is None or new is None or old == 0:
            return "N/A"
        change = ((new - old) / old) * 100
        sign = "+" if change > 0 else ""
        return f"{sign}{change:.1f}%"

    print("\n" + "=" * 80)
    print("  PHASE 7 SUBSET TEST RESULTS (12 samples with worst relevancy)")
    print("=" * 80)

    print("\n  METRICS COMPARISON")
    print("  " + "-" * 76)
    print(f"  {'Metric':<25} {'Phase 5':>12} {'Phase 7':>12} {'Change':>12}")
    print("  " + "-" * 76)

    f5, f7 = phase5_metrics["faithfulness"], phase7_metrics["faithfulness"]
    r5, r7 = phase5_metrics["answer_relevancy"], phase7_metrics["answer_relevancy"]
    rf5, rf7 = phase5_metrics["refusal_count"], phase7_metrics["refusal_count"]

    print(f"  {'Faithfulness':<25} {fmt(f5):>12} {fmt(f7):>12} {pct_change(f5, f7):>12}")
    print(f"  {'Answer Relevancy':<25} {fmt(r5):>12} {fmt(r7):>12} {pct_change(r5, r7):>12}")
    print(f"  {'Refusal Count':<25} {rf5:>12} {rf7:>12} {rf7 - rf5:>12}")
    print(f"  {'Refusal Rate':<25} {phase5_metrics['refusal_rate']:>11.1%} {phase7_metrics['refusal_rate']:>11.1%} {''}")

    print("  " + "-" * 76)
    print("=" * 80 + "\n")


def main() -> int:
    """Run Phase 7 subset testing.

    Returns:
        Exit code (0 for success)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    configure_observability()

    # Load subset
    subset_path = Path("phase6_test_subset.json")
    if not subset_path.exists():
        logger.error("phase6_test_subset.json not found")
        return 1

    subset_data = json.loads(subset_path.read_text(encoding="utf-8"))
    subset_indices = subset_data["subset_indices"]

    logger.info(f"Testing on {len(subset_indices)} problematic queries")

    # Initialize ChatService with Phase 7 (query expansion enabled, metadata filtering disabled)
    logger.info("Initializing ChatService with Phase 7 improvements...")
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    # Test Phase 7
    logger.info("\n=== TESTING PHASE 7 (Query Expansion) ===")
    phase7_samples = test_subset(chat_service, subset_indices, "Phase 7")
    phase7_metrics = evaluate_subset(phase7_samples)

    # Load Phase 5 baseline for comparison
    phase5_results_path = Path("phase6_subset_results.json")
    if phase5_results_path.exists():
        phase5_data = json.loads(phase5_results_path.read_text(encoding="utf-8"))
        phase5_metrics = phase5_data.get("phase5_metrics", {
            "sample_count": 12,
            "faithfulness": 0.35,
            "answer_relevancy": 0.05,
            "refusal_count": 10,
            "refusal_rate": 10/12,
        })
    else:
        # Use estimated Phase 5 values
        phase5_metrics = {
            "sample_count": 12,
            "faithfulness": 0.35,
            "answer_relevancy": 0.05,
            "refusal_count": 10,
            "refusal_rate": 10/12,
        }

    # Print comparison
    print_comparison(phase5_metrics, phase7_metrics)

    # Save results
    output_path = Path("phase7_subset_results.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "Phase 7 Subset Test",
            "subset_size": len(subset_indices),
            "improvements": ["query_expansion", "no_metadata_filtering", "quality_filter"],
            "phase5_metrics": phase5_metrics,
            "phase7_metrics": phase7_metrics,
            "samples": phase7_samples,
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to {output_path}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
