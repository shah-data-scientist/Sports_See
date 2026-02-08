"""
FILE: evaluate_phase9_full.py
STATUS: Active
RESPONSIBILITY: Full RAGAS evaluation with Phase 9 hybrid category-aware prompts (47 samples)
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


def generate_samples(
    test_cases: list,
    checkpoint_file: Path | None = None,
) -> list[EvaluationSample]:
    """Generate evaluation samples for RAGAS with Phase 9 hybrid prompts.

    Args:
        test_cases: List of evaluation test cases
        checkpoint_file: Path to checkpoint file for incremental evaluation

    Returns:
        List of evaluation samples
    """
    logger.info(f"Generating samples for {len(test_cases)} test cases")
    logger.info("Using Phase 9 hybrid category-aware prompts")

    # Initialize services
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()
    gemini_client = _build_gemini_client()

    # Load checkpoint if exists
    completed_samples = []
    if checkpoint_file and checkpoint_file.exists():
        logger.info(f"Loading checkpoint from {checkpoint_file}")
        checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
        completed_samples = checkpoint_data.get("samples", [])
        logger.info(f"Resuming from {len(completed_samples)} completed samples")

    samples = []
    for i, test_case in enumerate(test_cases):
        # Skip if already in checkpoint
        if i < len(completed_samples):
            logger.info(f"[{i+1}/{len(test_cases)}] Skipping (from checkpoint): {test_case.question[:60]}...")
            samples.append(EvaluationSample(**completed_samples[i]))
            continue

        logger.info(f"[{i+1}/{len(test_cases)}] Processing ({test_case.category.value}): {test_case.question[:60]}...")

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

        # Save checkpoint
        if checkpoint_file:
            checkpoint_data = {
                "samples": [s.model_dump() for s in samples],
                "completed": len(samples),
                "total": len(test_cases),
            }
            checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"Checkpoint saved: {len(samples)}/{len(test_cases)}")

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
    llm = _build_evaluator_llm()
    embeddings = _build_evaluator_embeddings()

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
    """Compute per-category metric scores.

    Args:
        samples: List of evaluation samples
        ragas_result: RAGAS evaluation result

    Returns:
        List of category results
    """
    # Group samples by category
    category_samples = {}
    for i, test_case in enumerate(EVALUATION_TEST_CASES):
        category = test_case.category.value
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

        # Get first test case in this category for the category enum
        first_idx = indices[0]
        category_enum = EVALUATION_TEST_CASES[first_idx].category

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
    """Run full Phase 9 evaluation."""
    print("\n" + "=" * 80)
    print("  PHASE 9: FULL RAGAS EVALUATION (47 SAMPLES)")
    print("  Strategy: Hybrid Category-Aware Prompts")
    print("    - Simple prompt for SIMPLE/CONVERSATIONAL")
    print("    - Citation prompt for COMPLEX/NOISY")
    print("  LLM: Gemini 2.0 Flash Lite")
    print("=" * 80 + "\n")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Configure observability (optional)
    configure_observability()

    # Setup checkpoint
    checkpoint_file = Path("evaluation_checkpoint_phase9.json")

    # Generate samples with Phase 9 hybrid prompts
    print("Step 1/3: Generating samples with hybrid category-aware prompts...")
    samples = generate_samples(
        test_cases=EVALUATION_TEST_CASES,
        checkpoint_file=checkpoint_file,
    )

    # Run RAGAS evaluation
    print("\nStep 2/3: Running RAGAS evaluation...")
    ragas_result = run_evaluation(samples)

    # Compute overall and category scores
    print("\nStep 3/3: Computing scores...")
    df = ragas_result.to_pandas()

    # Log available columns for debugging
    logger.info(f"RAGAS result columns: {list(df.columns)}")
    print(f"Available columns: {list(df.columns)}")

    # RAGAS metric names (check which ones exist)
    relevancy_col = "answer_relevancy" if "answer_relevancy" in df.columns else "response_relevancy"

    overall_scores = MetricScores(
        faithfulness=float(df["faithfulness"].mean()),
        answer_relevancy=float(df[relevancy_col].mean()),
        context_precision=float(df["llm_context_precision_without_reference"].mean()),
        context_recall=float(df["context_recall"].mean()),
    )

    category_scores = compute_category_scores(samples, ragas_result)

    # Create evaluation report
    report = EvaluationReport(
        sample_count=len(samples),
        model_used="gemini-2.0-flash-lite",
        overall_scores=overall_scores,
        category_results=category_scores,
    )

    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "ragas_phase9.json"
    output_file.write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    # Clean up checkpoint
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        logger.info("Checkpoint file deleted")

    # Print results
    print("\n" + "=" * 80)
    print("  PHASE 9 EVALUATION COMPLETE")
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

    # Compare to Phase 8
    phase8_file = output_dir / "ragas_phase8.json"
    if phase8_file.exists():
        print("\n" + "=" * 80)
        print("  PHASE 8 vs PHASE 9 COMPARISON")
        print("=" * 80)

        phase8_data = json.loads(phase8_file.read_text(encoding="utf-8"))
        p8_scores = phase8_data["overall_scores"]

        print("\nOverall Changes:")
        metric_mapping = {
            "faithfulness": "faithfulness",
            "answer_relevancy": "answer_relevancy",
            "context_precision": "context_precision",
            "context_recall": "context_recall"
        }
        for p8_metric, p9_attr in metric_mapping.items():
            p8 = p8_scores[p8_metric]
            p9 = getattr(overall_scores, p9_attr)
            change = ((p9 / p8) - 1) * 100 if p8 > 0 else 0
            symbol = "+" if change > 0 else "-" if change < 0 else "="
            print(f"  {p8_metric:20s}: {p8:.3f} -> {p9:.3f} ({change:+.1f}%) {symbol}")

        # Category-level comparison
        print("\nCategory-Level Changes:")
        p8_categories = {cat["category"]: cat for cat in phase8_data["category_results"]}

        for cat in category_scores:
            cat_name = cat.category.value
            if cat_name in p8_categories:
                p8_cat = p8_categories[cat_name]
                print(f"\n  {cat_name.upper()}:")

                p8_faith = p8_cat["avg_faithfulness"]
                p9_faith = cat.avg_faithfulness
                faith_change = ((p9_faith / p8_faith) - 1) * 100 if p8_faith > 0 else 0
                faith_symbol = "+" if faith_change > 0 else "-" if faith_change < 0 else "="
                print(f"    Faithfulness:     {p8_faith:.3f} -> {p9_faith:.3f} ({faith_change:+.1f}%) {faith_symbol}")

                p8_rel = p8_cat["avg_answer_relevancy"]
                p9_rel = cat.avg_answer_relevancy
                rel_change = ((p9_rel / p8_rel) - 1) * 100 if p8_rel > 0 else 0
                rel_symbol = "+" if rel_change > 0 else "-" if rel_change < 0 else "="
                print(f"    Ans Relevancy:    {p8_rel:.3f} -> {p9_rel:.3f} ({rel_change:+.1f}%) {rel_symbol}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
