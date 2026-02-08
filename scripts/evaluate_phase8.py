"""
FILE: evaluate_phase8.py
STATUS: Active
RESPONSIBILITY: Full RAGAS evaluation with Phase 8 citation-required prompt
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


# Phase 8 citation-required prompt (winner from 12-sample subset testing)
PHASE8_CITATION_REQUIRED = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

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


def _build_generation_client():
    """Build Gemini client for sample generation."""
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY required for Phase 8 evaluation (uses Gemini)")

    from google import genai
    logger.info("Using Gemini 2.0 Flash Lite for sample generation")
    return genai.Client(api_key=settings.google_api_key)


def _generate_with_retry(client, prompt: str, *, use_gemini: bool, chat_service=None,
                         query: str = "", context: str = "") -> str:
    """Generate response with retry logic."""
    max_retries = 6
    for attempt in range(max_retries):
        try:
            if use_gemini:
                response = client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    contents=prompt,
                )
                return response.text
            else:
                # Fallback to Mistral (not used in Phase 8)
                return chat_service.generate_response(query=query, context=context)
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
    prompt_template: str,
    checkpoint_file: Path | None = None,
    use_gemini: bool = True,
) -> list[EvaluationSample]:
    """Generate evaluation samples for RAGAS.

    Args:
        test_cases: List of evaluation test cases
        prompt_template: Prompt template to use for generation
        checkpoint_file: Path to checkpoint file for incremental evaluation
        use_gemini: Use Gemini for generation (default: True)

    Returns:
        List of evaluation samples
    """
    logger.info(f"Generating samples for {len(test_cases)} test cases")
    logger.info(f"Using Gemini: {use_gemini}")

    # Initialize services
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    gemini_client = _build_generation_client() if use_gemini else None

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

        logger.info(f"[{i+1}/{len(test_cases)}] Processing: {test_case.question[:60]}...")

        # Search with Phase 7 query expansion
        search_results = chat_service.search(test_case.question, k=5)

        # Build context from search results
        context = "\n\n".join([
            f"[Source: {result.source}]\n{result.text}"
            for result in search_results
        ])

        # Build prompt with Phase 8 template
        prompt = prompt_template.format(
            app_name=settings.app_name,
            context=context,
            question=test_case.question,
        )

        # Generate response
        response = _generate_with_retry(
            gemini_client,
            prompt,
            use_gemini=use_gemini,
            chat_service=chat_service,
            query=test_case.question,
            context=context,
        )

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
    """Run full Phase 8 evaluation."""
    print("\n" + "=" * 80)
    print("  PHASE 8: FULL RAGAS EVALUATION (47 SAMPLES)")
    print("  Prompt: citation_required (winner from subset testing)")
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
    checkpoint_file = Path("evaluation_checkpoint_phase8.json")

    # Generate samples with Phase 8 prompt
    print("Step 1/3: Generating samples with citation-required prompt...")
    samples = generate_samples(
        test_cases=EVALUATION_TEST_CASES,
        prompt_template=PHASE8_CITATION_REQUIRED,
        checkpoint_file=checkpoint_file,
        use_gemini=True,
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

    output_file = output_dir / "ragas_phase8.json"
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
    print("  PHASE 8 EVALUATION COMPLETE")
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

    # Compare to Phase 7
    phase7_file = output_dir / "ragas_phase7.json"
    if phase7_file.exists():
        print("\n" + "=" * 80)
        print("  PHASE 7 vs PHASE 8 COMPARISON")
        print("=" * 80)

        phase7_data = json.loads(phase7_file.read_text(encoding="utf-8"))
        p7_scores = phase7_data["overall_scores"]

        print("\nOverall Changes:")
        # Phase 7 uses "answer_relevancy", Phase 8 model uses "answer_relevancy" but RAGAS returns "response_relevancy"
        metric_mapping = {
            "faithfulness": "faithfulness",
            "answer_relevancy": "answer_relevancy",  # P7 file uses this name
            "context_precision": "context_precision",
            "context_recall": "context_recall"
        }
        for p7_metric, p8_attr in metric_mapping.items():
            p7 = p7_scores[p7_metric]
            p8 = getattr(overall_scores, p8_attr)
            change = ((p8 / p7) - 1) * 100 if p7 > 0 else 0
            symbol = "+" if change > 0 else "-" if change < 0 else "="
            print(f"  {p7_metric:20s}: {p7:.3f} -> {p8:.3f} ({change:+.1f}%) {symbol}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
