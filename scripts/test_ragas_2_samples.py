"""
FILE: test_ragas_2_samples.py
STATUS: Active
RESPONSIBILITY: Quick 2-sample RAGAS validation
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Test RAGAS metrics on 2 samples to verify the fix works.
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

def test_ragas_2_samples():
    """Test RAGAS on 2 samples with fixed context extraction."""
    print("\n" + "="*80)
    print("  TESTING RAGAS ON 2 SAMPLES")
    print("="*80 + "\n")

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
            print(f"\n[{i}/2] Collecting data for: {test_case.question[:60]}...")

            response = client.post(
                "/api/v1/chat",
                json={"query": test_case.question, "k": 5, "include_sources": True},
                timeout=30,
            )

            if response.status_code != 200:
                print(f"  ✗ API call failed: {response.status_code}")
                continue

            api_result = response.json()

            # Extract contexts using FIXED method
            question = test_case.question
            answer = api_result.get("answer", "")
            retrieved_contexts = [src.get("text", "") for src in api_result.get("sources", [])]
            gold_contexts = gold_contexts_map.get(question, [])

            results.append({
                "question": question,
                "answer": answer,
                "contexts": retrieved_contexts,
                "reference": test_case.ground_truth,
                "reference_contexts": gold_contexts,
            })

            print(f"  ✓ Retrieved contexts: {len(retrieved_contexts)}")
            print(f"  ✓ Gold contexts: {len(gold_contexts)}")
            print(f"  ✓ Non-empty retrieved: {len([c for c in retrieved_contexts if c])}")

    # Now calculate RAGAS
    print("\n" + "="*80)
    print("  CALCULATING RAGAS METRICS (2 samples)")
    print("="*80 + "\n")

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

    # Configure Gemini LLM + Mistral embeddings
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

        print("\n" + "="*80)
        print("  RAGAS RESULTS (2 samples)")
        print("="*80)

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

        print(f"  Faithfulness:        {scores['faithfulness']:.3f}")
        print(f"  Answer Relevancy:    {scores['answer_relevancy']:.3f}")
        print(f"  Context Precision:   {scores['context_precision']:.3f}")
        print(f"  Context Recall:      {scores['context_recall']:.3f}")
        print("="*80 + "\n")

        print("✅ RAGAS is working with corrected contexts!")
        return 0

    except Exception as e:
        print(f"ERROR during RAGAS evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_ragas_2_samples())
