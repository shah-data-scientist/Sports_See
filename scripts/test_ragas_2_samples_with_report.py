"""
FILE: test_ragas_2_samples_with_report.py
STATUS: Active
RESPONSIBILITY: 2-sample RAGAS validation with detailed evaluation report
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Test RAGAS metrics on 2 samples with UPDATED retrieval workflow and generate detailed report.
"""

import io
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES

def test_ragas_2_samples_with_report():
    """Test RAGAS on 2 samples with detailed report."""
    print("\n" + "="*100)
    print("  2-SAMPLE RAGAS EVALUATION WITH UPDATED RETRIEVAL WORKFLOW")
    print("="*100)
    print("\n  Workflow: Retrieve 15 candidates → Apply metadata boost → Sort → Return top 5\n")
    print("="*100 + "\n")

    # Load gold contexts
    gold_contexts_file = Path("evaluation_results/vector_gold_contexts.json")
    with open(gold_contexts_file, encoding="utf-8") as f:
        gold_data = json.load(f)

    gold_contexts_map = {item["question"]: item["gold_contexts"] for item in gold_data}

    # Use first 2 test cases
    test_cases = EVALUATION_TEST_CASES[:2]
    results = []

    app = create_app()
    with TestClient(app) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*100}")
            print(f"SAMPLE {i}/2")
            print(f"{'='*100}\n")

            print(f"📋 Question:")
            print(f"   {test_case.question}\n")

            # Call API
            response = client.post(
                "/api/v1/chat",
                json={"query": test_case.question, "k": 5, "include_sources": True},
                timeout=30,
            )

            if response.status_code != 200:
                print(f"  ✗ API call failed: {response.status_code}")
                continue

            api_result = response.json()

            # Extract data
            question = test_case.question
            answer = api_result.get("answer", "")
            retrieved_contexts = [src.get("text", "") for src in api_result.get("sources", [])]
            gold_contexts = gold_contexts_map.get(question, [])

            # Show retrieval results
            print(f"🔍 Retrieval Results (Top 5 after boosting):")
            for j, src in enumerate(api_result.get("sources", []), 1):
                source_name = src.get("source", "unknown")
                score = src.get("score", 0)
                is_reddit = "reddit" in source_name.lower()
                marker = "🔴" if is_reddit else "⚪"
                print(f"   {marker} [{j}] Score: {score:.1f}% | Source: {source_name}")

            print(f"\n💬 LLM Answer ({len(answer)} chars):")
            print(f"   {answer[:300]}...\n")

            print(f"📊 Context Stats:")
            print(f"   Retrieved contexts: {len(retrieved_contexts)}")
            print(f"   Gold contexts:      {len(gold_contexts)}")
            print(f"   Non-empty retrieved: {len([c for c in retrieved_contexts if c])}")
            print(f"   Non-empty gold:      {len([c for c in gold_contexts if c])}")

            results.append({
                "question": question,
                "answer": answer,
                "contexts": retrieved_contexts,
                "reference": test_case.ground_truth,
                "reference_contexts": gold_contexts,
            })

    # Calculate RAGAS
    print("\n\n" + "="*100)
    print("  CALCULATING RAGAS METRICS")
    print("="*100)
    print("  Metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall")
    print("="*100 + "\n")

    try:
        from ragas import evaluate, RunConfig
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_mistralai import MistralAIEmbeddings
        from datasets import Dataset
        from src.core.config import settings
    except ImportError as e:
        print(f"ERROR: ragas dependencies not installed: {e}")
        return 1

    # Configure RAGAS
    print("Configuring RAGAS:")
    print("  LLM: Gemini (gemini-2.0-flash-lite)")
    print("  Embeddings: Mistral (mistral-embed)\n")

    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0,
        google_api_key=settings.google_api_key
    )

    mistral_embeddings = MistralAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.mistral_api_key,
    )
    ragas_embeddings = LangchainEmbeddingsWrapper(mistral_embeddings)

    run_config = RunConfig(max_workers=1, max_wait=180)

    # Prepare dataset
    dataset_dict = {
        "question": [r["question"] for r in results],
        "answer": [r["answer"] for r in results],
        "contexts": [r["contexts"] for r in results],
        "reference": [r["reference"] for r in results],
        "reference_contexts": [r["reference_contexts"] for r in results],
    }

    dataset = Dataset.from_dict(dataset_dict)

    print(f"Evaluating {len(results)} samples...")
    print("(This will take ~30 seconds due to LLM judge calls)\n")

    # Run RAGAS
    try:
        evaluation_result = evaluate(
            dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
            llm=gemini_llm,
            embeddings=ragas_embeddings,
            run_config=run_config,
        )

        # Extract scores
        import numpy as np

        def extract_score(result_obj, key):
            try:
                value = result_obj[key]
            except (KeyError, TypeError):
                value = getattr(result_obj, key, 0)
            if isinstance(value, (list, np.ndarray)):
                return float(np.mean([v for v in value if v is not None]))
            return float(value)

        scores = {
            "faithfulness": extract_score(evaluation_result, "faithfulness"),
            "answer_relevancy": extract_score(evaluation_result, "answer_relevancy"),
            "context_precision": extract_score(evaluation_result, "context_precision"),
            "context_recall": extract_score(evaluation_result, "context_recall"),
        }

        # DETAILED REPORT
        print("\n" + "="*100)
        print("  📊 EVALUATION REPORT")
        print("="*100 + "\n")

        print("🔧 RETRIEVAL WORKFLOW (UPDATED):")
        print("   1. FAISS retrieves 15 candidates based on semantic similarity")
        print("   2. Metadata boost applied to ALL 15 candidates:")
        print("      • Comment upvotes: up to +2%")
        print("      • NBA official account: +4%")
        print("      • Post engagement: up to +2%")
        print("      • Total max boost: +8%")
        print("   3. Sort by boosted scores")
        print("   4. Return top 5 to LLM\n")

        print("📈 RAGAS SCORES:")
        print(f"   Faithfulness:        {scores['faithfulness']:.1%} ({scores['faithfulness']:.3f})")
        print(f"   Answer Relevancy:    {scores['answer_relevancy']:.1%} ({scores['answer_relevancy']:.3f})")
        print(f"   Context Precision:   {scores['context_precision']:.1%} ({scores['context_precision']:.3f})")
        print(f"   Context Recall:      {scores['context_recall']:.1%} ({scores['context_recall']:.3f})\n")

        print("✅ VALIDATION:")
        if scores['context_precision'] >= 0.90 and scores['context_recall'] >= 0.90:
            print("   ✅ Context Precision ≥ 90%")
            print("   ✅ Context Recall ≥ 90%")
            print("   ✅ Retrieval workflow is working correctly!")
        else:
            print("   ⚠️  Context scores below 90%")
            print("   ⚠️  May need further investigation")

        print("\n" + "="*100)

        # Save report
        report = {
            "timestamp": "2026-02-11",
            "workflow": "Retrieve 15 → Boost all → Sort → Top 5",
            "samples_evaluated": 2,
            "ragas_scores": scores,
            "samples": results,
        }

        report_file = Path("evaluation_results/ragas_2_sample_report.json")
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        print(f"\n✓ Report saved to: {report_file}")

        return 0

    except Exception as e:
        print(f"ERROR during RAGAS evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_ragas_2_samples_with_report())
