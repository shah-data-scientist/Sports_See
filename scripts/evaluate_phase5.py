"""
FILE: evaluate_phase5.py
STATUS: Active
RESPONSIBILITY: Phase 5 evaluation with extended hybrid test cases
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

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
from src.evaluation.hybrid_test_cases import HYBRID_TEST_CASES
from src.services.chat import ChatService

logger = logging.getLogger(__name__)

# Combine existing + new hybrid test cases
ALL_TEST_CASES = EVALUATION_TEST_CASES + HYBRID_TEST_CASES


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
    if settings.google_api_key:
        from google import genai

        logger.info("Using Gemini for sample generation")
        return genai.Client(api_key=settings.google_api_key)
    return None


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
                return chat_service.generate_response(query=query, context=context)
        except Exception as e:
            is_retryable = (
                "429" in str(e)
                or "rate" in str(e).lower()
                or "ResourceExhausted" in type(e).__name__
                or "resource_exhausted" in str(e).lower()
            )
            if is_retryable and attempt < max_retries - 1:
                wait = 15 * (2 ** attempt)
                logger.warning("Rate limited, waiting %ds (attempt %d/%d)", wait, attempt + 1, max_retries)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("All retries exhausted")


CHECKPOINT_PATH = Path("evaluation_checkpoint_phase5.json")
BATCH_SIZE = 10
BATCH_COOLDOWN = 60


def _save_checkpoint(samples: list[EvaluationSample]) -> None:
    """Save checkpoint."""
    data = [s.model_dump() for s in samples]
    CHECKPOINT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Checkpoint saved: %d samples", len(samples))


def _load_checkpoint() -> list[EvaluationSample]:
    """Load checkpoint."""
    if not CHECKPOINT_PATH.exists():
        return []
    data = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
    samples = [EvaluationSample(**item) for item in data]
    logger.info("Checkpoint loaded: %d samples", len(samples))
    return samples


@logfire.instrument("generate_phase5_samples")
def generate_samples(chat_service: ChatService) -> list[EvaluationSample]:
    """Generate samples with extended hybrid test cases.

    Args:
        chat_service: ChatService with SQL enabled.

    Returns:
        List of evaluation samples.
    """
    gemini_client = _build_generation_client()
    use_gemini = gemini_client is not None

    samples = _load_checkpoint()
    start_idx = len(samples)
    total = len(ALL_TEST_CASES)

    if start_idx >= total:
        logger.info("All %d samples already generated", total)
        return samples

    logger.info("Starting from sample %d/%d (Extended test cases)", start_idx + 1, total)

    for i in range(start_idx, total):
        tc = ALL_TEST_CASES[i]
        batch_pos = (i - start_idx) % BATCH_SIZE

        if batch_pos == 0 and i > start_idx:
            logger.info("Batch complete. Cooling down %ds...", BATCH_COOLDOWN)
            time.sleep(BATCH_COOLDOWN)

        logger.info("Sample %d/%d: %s", i + 1, total, tc.question[:60])

        try:
            search_results = chat_service.search(query=tc.question, k=settings.search_k)
            contexts = [r.text for r in search_results]
            context_str = "\n\n---\n\n".join(
                f"Source: {r.source} (Score: {r.score:.1f}%)\n{r.text}"
                for r in search_results
            )

            prompt = (
                f"Tu es '{settings.app_name} Analyst AI', un assistant expert.\n"
                f"Réponds à la question en te basant sur le contexte fourni.\n\n"
                f"CONTEXTE:\n---\n{context_str}\n---\n\n"
                f"QUESTION:\n{tc.question}\n\n"
                f"INSTRUCTIONS:\n"
                f"- Réponds de manière précise et concise\n"
                f"- Si le contexte ne contient pas l'information, dis-le\n"
                f"- Cite les sources si possible\n"
            )

            answer = _generate_with_retry(
                gemini_client, prompt,
                use_gemini=use_gemini,
                chat_service=chat_service,
                query=tc.question,
                context=context_str,
            )

            samples.append(
                EvaluationSample(
                    user_input=tc.question,
                    response=answer,
                    retrieved_contexts=contexts,
                    reference=tc.ground_truth,
                    category=tc.category,
                )
            )

            _save_checkpoint(samples)

        except Exception as e:
            logger.error("Failed on sample %d: %s", i + 1, e)
            _save_checkpoint(samples)
            raise

        if i < total - 1:
            time.sleep(3)

    logger.info("All %d samples generated", total)
    return samples


@logfire.instrument("run_phase5_evaluation")
def run_evaluation(samples: list[EvaluationSample]) -> EvaluationReport:
    """Run RAGAS evaluation."""
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import (
        Faithfulness,
        LLMContextPrecisionWithoutReference,
        LLMContextRecall,
        ResponseRelevancy,
    )

    evaluator_llm = _build_evaluator_llm()
    evaluator_embeddings = _build_evaluator_embeddings()

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

    metrics = [
        Faithfulness(llm=evaluator_llm),
        ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings),
        LLMContextPrecisionWithoutReference(llm=evaluator_llm),
        LLMContextRecall(llm=evaluator_llm),
    ]

    logger.info("Running RAGAS evaluation with %d samples...", len(samples))
    result = evaluate(dataset=eval_dataset, metrics=metrics)

    return _build_report(result, samples)


def _build_report(result, samples: list[EvaluationSample]) -> EvaluationReport:
    """Build evaluation report."""
    df = result.to_pandas()

    metric_cols = {
        "faithfulness": "faithfulness",
        "answer_relevancy": "answer_relevancy",
        "context_precision": "llm_context_precision_without_reference",
        "context_recall": "context_recall",
    }

    def _safe_mean(series):
        valid = series.dropna()
        return float(valid.mean()) if len(valid) > 0 else None

    overall = MetricScores(
        faithfulness=_safe_mean(df.get(metric_cols["faithfulness"], [])),
        answer_relevancy=_safe_mean(df.get(metric_cols["answer_relevancy"], [])),
        context_precision=_safe_mean(df.get(metric_cols["context_precision"], [])),
        context_recall=_safe_mean(df.get(metric_cols["context_recall"], [])),
    )

    categories = [s.category for s in samples]
    df["category"] = categories

    category_results: list[CategoryResult] = []
    for cat in TestCategory:
        cat_df = df[df["category"] == cat]
        if len(cat_df) == 0:
            continue
        category_results.append(
            CategoryResult(
                category=cat,
                count=len(cat_df),
                avg_faithfulness=_safe_mean(cat_df.get(metric_cols["faithfulness"], [])),
                avg_answer_relevancy=_safe_mean(cat_df.get(metric_cols["answer_relevancy"], [])),
                avg_context_precision=_safe_mean(cat_df.get(metric_cols["context_precision"], [])),
                avg_context_recall=_safe_mean(cat_df.get(metric_cols["context_recall"], [])),
            )
        )

    return EvaluationReport(
        overall_scores=overall,
        category_results=category_results,
        sample_count=len(samples),
        model_used="gemini-2.0-flash-lite" if settings.google_api_key else settings.chat_model,
    )


def print_comparison_table(report: EvaluationReport) -> None:
    """Print evaluation results."""
    def _fmt(val: float | None) -> str:
        return f"{val:.3f}" if val is not None else "N/A"

    print("\n" + "=" * 80)
    print(f"  PHASE 5 EVALUATION REPORT (Extended Test Cases)")
    print(f"  Model: {report.model_used}  |  Samples: {report.sample_count}")
    print(f"  SQL Integration: ENABLED  |  Test Cases: Existing + Hybrid")
    print("=" * 80)

    print("\n  OVERALL SCORES")
    print("  " + "-" * 60)
    o = report.overall_scores
    print(f"  {'Metric':<25} {'Score':>10}")
    print(f"  {'Faithfulness':<25} {_fmt(o.faithfulness):>10}")
    print(f"  {'Answer Relevancy':<25} {_fmt(o.answer_relevancy):>10}")
    print(f"  {'Context Precision':<25} {_fmt(o.context_precision):>10}")
    print(f"  {'Context Recall':<25} {_fmt(o.context_recall):>10}")

    print("\n  SCORES BY CATEGORY")
    print("  " + "-" * 76)
    header = (
        f"  {'Category':<10} {'Count':>5} {'Faithful':>10} "
        f"{'Relevancy':>10} {'Precision':>10} {'Recall':>10}"
    )
    print(header)
    print("  " + "-" * 76)

    for cr in report.category_results:
        row = (
            f"  {cr.category.value:<10} {cr.count:>5} "
            f"{_fmt(cr.avg_faithfulness):>10} "
            f"{_fmt(cr.avg_answer_relevancy):>10} "
            f"{_fmt(cr.avg_context_precision):>10} "
            f"{_fmt(cr.avg_context_recall):>10}"
        )
        print(row)

    print("  " + "-" * 76)
    print("=" * 80 + "\n")


def main() -> int:
    """Run Phase 5 evaluation with extended test cases.

    Returns:
        Exit code (0 for success).
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    configure_observability()

    logger.info("Initializing ChatService with SQL enabled (Phase 5)...")
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    logger.info("Total test cases: %d (Existing: %d + Hybrid: %d)",
                len(ALL_TEST_CASES), len(EVALUATION_TEST_CASES), len(HYBRID_TEST_CASES))

    logger.info("Generating evaluation samples with hybrid RAG...")
    try:
        samples = generate_samples(chat_service)
    except Exception:
        logger.error("Sample generation interrupted. Re-run to continue.")
        return 1

    logger.info("Running RAGAS evaluation...")
    report = run_evaluation(samples)

    print_comparison_table(report)

    # Save Phase 5 results
    report_path = Path("evaluation_results/ragas_phase5_extended.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "phase": "Phase 5 - Extended Hybrid Test Cases",
                "model": report.model_used,
                "sample_count": report.sample_count,
                "test_cases": {
                    "existing": len(EVALUATION_TEST_CASES),
                    "hybrid": len(HYBRID_TEST_CASES),
                    "total": len(ALL_TEST_CASES),
                },
                "sql_enabled": True,
                "overall_scores": {
                    "faithfulness": report.overall_scores.faithfulness,
                    "answer_relevancy": report.overall_scores.answer_relevancy,
                    "context_precision": report.overall_scores.context_precision,
                    "context_recall": report.overall_scores.context_recall,
                },
                "category_scores": [
                    {
                        "category": result.category.value,
                        "count": result.count,
                        "faithfulness": result.avg_faithfulness,
                        "answer_relevancy": result.avg_answer_relevancy,
                        "context_precision": result.avg_context_precision,
                        "context_recall": result.avg_context_recall,
                    }
                    for result in report.category_results
                ],
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    logger.info(f"Phase 3 report saved to {report_path}")

    # Clean up checkpoint
    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        logger.info("Checkpoint removed")

    return 0


if __name__ == "__main__":
    sys.exit(main())
