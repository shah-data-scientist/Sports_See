"""
FILE: evaluate_phase9_subset.py
STATUS: Active
RESPONSIBILITY: Phase 9 subset evaluation - Hybrid category-aware prompts (12 samples)
LAST MAJOR UPDATE: 2026-02-08
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

from src.core.config import settings
from src.core.observability import configure_observability, logfire
from src.evaluation.models import (
    CategoryResult,
    EvaluationReport,
    EvaluationSample,
    MetricScores,
    TestCategory,
)
from src.evaluation.test_cases import EVALUATION_TEST_CASES
from src.services.chat import ChatService

logger = logging.getLogger(__name__)


# Phase 9: Category-Aware Hybrid Prompts
PHASE9_SIMPLE_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

CONTEXT:
---
{context}
---

QUESTION:
{question}

INSTRUCTIONS:
- Answer directly and concisely
- Use only information from the context above
- If information is missing, say so briefly

ANSWER:"""


PHASE9_COMPLEX_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

You MUST follow these rules:
- Answer ONLY using information from the CONTEXT below
- When stating a fact or statistic, cite it as: [Source: <source_name>]
- If unsure or information is missing, say: "The available data doesn't specify this."
- Never infer or extrapolate beyond what's explicitly stated
- Keep answers factual and concise

CONTEXT:
---
{context}
---

QUESTION:
{question}

ANSWER WITH CITATIONS:"""


PHASE9_NOISY_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

You MUST follow these rules:
- Answer ONLY using information from the CONTEXT below
- When stating a fact or statistic, cite it as: [Source: <source_name>]
- If unsure or information is missing, say: "The available data doesn't specify this."
- Never infer or extrapolate beyond what's explicitly stated
- Keep answers factual and concise

CONTEXT:
---
{context}
---

QUESTION:
{question}

ANSWER WITH CITATIONS:"""


PHASE9_CONVERSATIONAL_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

CONTEXT:
---
{context}
---

QUESTION:
{question}

INSTRUCTIONS:
- Answer naturally and conversationally
- Base your answer on the context above
- Be concise and helpful
- If information isn't in the context, say so clearly

ANSWER:"""


def get_prompt_for_category(category: TestCategory) -> str:
    """Get the appropriate prompt template for a given category.

    Args:
        category: Test case category

    Returns:
        Prompt template string
    """
    if category == TestCategory.SIMPLE:
        return PHASE9_SIMPLE_PROMPT
    elif category == TestCategory.COMPLEX:
        return PHASE9_COMPLEX_PROMPT
    elif category == TestCategory.NOISY:
        return PHASE9_NOISY_PROMPT
    elif category == TestCategory.CONVERSATIONAL:
        return PHASE9_CONVERSATIONAL_PROMPT
    else:
        # Fallback to complex prompt
        return PHASE9_COMPLEX_PROMPT


def _build_gemini_client():
    """Build Gemini client for sample generation."""
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY required for Phase 9 evaluation (uses Gemini)")

    from google import genai
    logger.info("Using Gemini 2.0 Flash Lite for sample generation")
    return genai.Client(api_key=settings.google_api_key)


def _generate_with_retry(client, prompt: str, max_retries: int = 6) -> str:
    """Generate response with retry logic for rate limits."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "resource" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt * 10, 120)  # Exponential backoff, max 2min
                    logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries}), waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {max_retries} retries: {error_msg}")
                    raise
            else:
                logger.error(f"Generation error: {error_msg}")
                raise


def generate_subset_samples(subset_indices: list[int]) -> list[EvaluationSample]:
    """Generate evaluation samples for Phase 9 subset (category-aware prompts).

    Args:
        subset_indices: Indices of test cases to evaluate

    Returns:
        List of evaluation samples
    """
    logger.info(f"Generating samples for {len(subset_indices)} test cases (Phase 9 hybrid prompts)")

    # Initialize services
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()
    gemini_client = _build_gemini_client()

    samples = []
    for idx in subset_indices:
        test_case = EVALUATION_TEST_CASES[idx]
        logger.info(f"[{idx+1}] Processing ({test_case.category.value}): {test_case.question[:60]}...")

        # Get category-specific prompt
        prompt_template = get_prompt_for_category(test_case.category)

        # Search with Phase 7 query expansion
        search_results = chat_service.search(test_case.question, k=5)

        # Build context from search results
        context = "\n\n".join([
            f"[Source: {result.source}]\n{result.text}"
            for result in search_results
        ])

        # Build prompt with category-aware template
        prompt = prompt_template.format(
            app_name=settings.app_name,
            context=context,
            question=test_case.question,
        )

        # Generate response
        response = _generate_with_retry(gemini_client, prompt)

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
        time.sleep(2)

    return samples


def run_evaluation(samples: list[EvaluationSample]) -> dict:
    """Run RAGAS evaluation on samples.

    Args:
        samples: List of evaluation samples

    Returns:
        Dictionary with RAGAS results
    """
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


def main():
    """Run Phase 9 subset evaluation (12 samples, 3 per category)."""
    print("\n" + "=" * 80)
    print("  PHASE 9: HYBRID CATEGORY-AWARE PROMPTS (SUBSET EVALUATION)")
    print("  Strategy: Simple prompt for SIMPLE/CONVERSATIONAL")
    print("            Citation prompt for COMPLEX/NOISY")
    print("  Samples: 12 (3 per category)")
    print("=" * 80 + "\n")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure observability (optional)
    configure_observability()

    # Select subset: 3 samples per category (first 3 from each)
    subset_indices = []
    category_counts = {cat: 0 for cat in TestCategory}

    for i, test_case in enumerate(EVALUATION_TEST_CASES):
        if category_counts[test_case.category] < 3:
            subset_indices.append(i)
            category_counts[test_case.category] += 1

        if len(subset_indices) == 12:
            break

    print(f"Selected indices: {subset_indices}")
    print(f"Category distribution: {category_counts}\n")

    # Generate samples with Phase 9 hybrid prompts
    print("Step 1/3: Generating samples with category-aware prompts...")
    samples = generate_subset_samples(subset_indices)

    # Run RAGAS evaluation
    print("\nStep 2/3: Running RAGAS evaluation...")
    ragas_result = run_evaluation(samples)

    # Compute overall and category scores
    print("\nStep 3/3: Computing scores...")
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

    # Save results
    output_file = Path("phase9_hybrid_subset.json")
    results_data = {
        "phase": "Phase 9 - Hybrid Category-Aware Prompts (Subset)",
        "strategy": "Simple prompt for SIMPLE/CONVERSATIONAL, Citation prompt for COMPLEX/NOISY",
        "sample_count": len(samples),
        "model": "gemini-2.0-flash-lite",
        "overall_scores": overall_scores.model_dump(),
        "category_scores": [cat.model_dump() for cat in category_scores],
    }
    output_file.write_text(json.dumps(results_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print results
    print("\n" + "=" * 80)
    print("  PHASE 9 SUBSET RESULTS")
    print("=" * 80)
    print(f"\nResults saved to: {output_file}\n")

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

    # Compare to Phase 8 subset results
    phase8_subset_file = Path("phase8_citation_required_subset.json")
    if phase8_subset_file.exists():
        print("\n" + "=" * 80)
        print("  PHASE 8 SUBSET vs PHASE 9 SUBSET COMPARISON")
        print("=" * 80)

        phase8_data = json.loads(phase8_subset_file.read_text(encoding="utf-8"))
        p8_scores = phase8_data["overall_scores"]

        print("\nOverall Changes:")
        for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            p8 = p8_scores[metric]
            p9 = getattr(overall_scores, metric)
            change = ((p9 / p8) - 1) * 100 if p8 > 0 else 0
            symbol = "+" if change > 0 else "-" if change < 0 else "="
            print(f"  {metric:20s}: {p8:.3f} -> {p9:.3f} ({change:+.1f}%) {symbol}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
