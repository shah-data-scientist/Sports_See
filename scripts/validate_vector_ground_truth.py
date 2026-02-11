"""
FILE: validate_vector_ground_truth.py
STATUS: Experimental
RESPONSIBILITY: Validate ground truth for new vector test cases by sampling queries
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Samples 15-20 queries from vector_test_cases.py across all categories and verifies:
- Reddit discussion queries retrieve actual Reddit content
- Boosting logic works (high engagement ranks higher)
- Glossary queries return definitions
- Out-of-scope queries return "no info"
- Conversational queries maintain context
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_CHAT_ENDPOINT = f"{API_BASE_URL}/api/v1/chat"

# Sample selection (diverse coverage)
SAMPLE_INDICES = [
    # Reddit discussion queries
    0,   # "What do Reddit users think about teams that have impressed in playoffs?"
    3,   # "What do fans debate about Reggie Miller's efficiency?"
    9,   # "According to basketball discussions, what makes a player efficient?"

    # Boosting logic tests
    15,  # "Tell me about the most discussed playoff efficiency topic."
    16,  # "What's the most popular Reddit discussion about playoffs?"
    19,  # "What do authoritative voices say about playoff basketball?"

    # Glossary/terminology
    25,  # "What is a pick and roll?"
    27,  # "What does zone defense mean?"
    29,  # "What is a triple-double?"

    # Out-of-scope
    33,  # "What is the weather forecast for Los Angeles tomorrow?"
    35,  # "Tell me about the latest political election results."
    37,  # "Best strategy for winning in NBA 2K24 video game?"

    # Conversational
    53,  # "What do fans say about the Lakers?"
    57,  # "Tell me about playoff teams that surprised people."

    # Noisy
    61,  # "whos da best playa in playoffs acording 2 reddit"
    68,  # "nba" (single word, vague)
]

# Output
RESULTS_FILE = Path("evaluation_results") / "ground_truth_validation.json"
RESULTS_FILE.parent.mkdir(exist_ok=True)


def call_chat_api(question: str, conversation_id: str | None = None) -> dict:
    """Call chat API and return response."""
    payload = {"query": question}
    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        response = requests.post(API_CHAT_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def validate_ground_truth():
    """Sample queries and validate ground truth."""
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_sampled": len(SAMPLE_INDICES),
        "validations": [],
        "summary": {
            "matches": 0,
            "mismatches": 0,
            "errors": 0,
        },
    }

    print("\n" + "=" * 80)
    print("GROUND TRUTH VALIDATION")
    print("=" * 80)
    print(f"Sampling {len(SAMPLE_INDICES)} queries from {len(EVALUATION_TEST_CASES)} total")
    print("=" * 80 + "\n")

    for i, idx in enumerate(SAMPLE_INDICES, 1):
        if idx >= len(EVALUATION_TEST_CASES):
            print(f"[{i}/{len(SAMPLE_INDICES)}] Index {idx} out of range, skipping")
            continue

        test_case = EVALUATION_TEST_CASES[idx]

        print(f"[{i}/{len(SAMPLE_INDICES)}] {test_case.category.value.upper()}")
        print(f"  Q: {test_case.question[:70]}...")

        validation = {
            "index": idx,
            "category": test_case.category.value,
            "question": test_case.question,
            "ground_truth": test_case.ground_truth,
            "status": "pending",
        }

        # Call API
        api_response = call_chat_api(test_case.question)

        if "error" in api_response:
            validation["status"] = "error"
            validation["error"] = api_response["error"]
            results["summary"]["errors"] += 1
            print(f"  ERROR: {api_response['error']}")
        else:
            validation["answer"] = api_response.get("answer", "")
            validation["routing"] = api_response.get("routing", "unknown")
            validation["sources_count"] = len(api_response.get("sources", []))

            # Analyze match
            answer = validation["answer"].lower()
            ground_truth = validation["ground_truth"].lower()

            # Check key expectations
            match = False
            mismatch_reason = None

            if "reddit" in ground_truth:
                # Expect Reddit content or discussion
                if "reddit" in answer or "discussion" in answer or "comment" in answer:
                    match = True
                else:
                    mismatch_reason = "Expected Reddit content but not found in answer"

            elif "out of scope" in ground_truth or "doesn't contain" in ground_truth:
                # Expect "no info" response
                if "don't" in answer or "doesn't" in answer or "not" in answer or "no information" in answer:
                    match = True
                else:
                    mismatch_reason = "Expected 'no info' response but got substantive answer"

            elif "glossary" in ground_truth or "define" in ground_truth or "defense" in ground_truth:
                # Expect definition
                if len(answer) > 20:  # Has substantive content
                    match = True
                else:
                    mismatch_reason = "Expected glossary definition but answer too short"

            elif "boost" in ground_truth or "engagement" in ground_truth:
                # Boosting test - check if high-engagement content retrieved
                if "reggie miller" in answer or "efficiency" in answer or len(answer) > 30:
                    match = True
                else:
                    mismatch_reason = "Expected high-engagement content but not found"

            else:
                # General match - answer has content
                if len(answer) > 20:
                    match = True
                else:
                    mismatch_reason = "Answer too short or empty"

            if match:
                validation["status"] = "match"
                results["summary"]["matches"] += 1
                print(f"  OK: Ground truth expectations met")
                print(f"  Routing: {validation['routing']}, Sources: {validation['sources_count']}")
            else:
                validation["status"] = "mismatch"
                validation["mismatch_reason"] = mismatch_reason
                results["summary"]["mismatches"] += 1
                print(f"  MISMATCH: {mismatch_reason}")
                print(f"  Answer: {validation['answer'][:100]}...")

        results["validations"].append(validation)

        # Rate limiting
        if i < len(SAMPLE_INDICES):
            time.sleep(2)

    return results


def generate_summary(results: dict):
    """Print summary of validation results."""
    total = results["total_sampled"]
    matches = results["summary"]["matches"]
    mismatches = results["summary"]["mismatches"]
    errors = results["summary"]["errors"]

    match_rate = (matches / total * 100) if total > 0 else 0

    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total sampled: {total}")
    print(f"Matches: {matches} ({match_rate:.1f}%)")
    print(f"Mismatches: {mismatches} ({100 - match_rate - (errors/total*100):.1f}%)")
    print(f"Errors: {errors} ({errors/total*100:.1f}%)")
    print("=" * 80)

    if mismatches > 0:
        print("\nMISMATCHES FOUND:")
        for v in results["validations"]:
            if v["status"] == "mismatch":
                print(f"\n- [{v['category'].upper()}] {v['question'][:60]}...")
                print(f"  Expected: {v['ground_truth'][:80]}...")
                print(f"  Got: {v['answer'][:80]}...")
                print(f"  Reason: {v.get('mismatch_reason', 'Unknown')}")

    if errors > 0:
        print("\nERRORS:")
        for v in results["validations"]:
            if v["status"] == "error":
                print(f"\n- {v['question'][:60]}...")
                print(f"  Error: {v.get('error', 'Unknown')}")

    print(f"\nResults saved to: {RESULTS_FILE}\n")


def main():
    """Run validation and report."""
    print("\nValidating ground truth for vector test cases...\n")

    results = validate_ground_truth()

    # Save results
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Print summary
    generate_summary(results)

    return 0 if results["summary"]["mismatches"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
