"""
FILE: diagnose_scoring.py
STATUS: Active
RESPONSIBILITY: Diagnose why evaluation scores are low despite correct responses
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import sys
import json
from pathlib import Path

# Load evaluation results
results_file = Path("evaluation_results/sql_hybrid_evaluation.json")
with open(results_file, encoding="utf-8") as f:
    data = json.load(f)

# Load test cases to compare
from src.evaluation.sql_test_cases import SQL_TEST_CASES

print("=" * 80)
print("EVALUATION SCORING DIAGNOSTIC")
print("=" * 80)

# Find low-scoring samples that seem correct
low_scores = [
    (i, s) for i, s in enumerate(data["samples"])
    if s["overall_score"] < 0.7 and "cannot find" not in s["response"].lower()
]

print(f"\nFound {len(low_scores)} low-scoring samples with seemingly correct answers\n")

# Analyze first 5 in detail
for i, sample in low_scores[:5]:
    test_case = SQL_TEST_CASES[i]

    print(f"Sample {i+1}: {sample['query'][:60]}")
    print(f"  Overall Score: {sample['overall_score']:.3f}")
    print(f"  SQL Accuracy: {sample['sql_accuracy']:.3f}")
    print(f"  Response: {sample['response'][:80]}...")
    print(f"  Ground Truth: {test_case.ground_truth_answer[:80]}...")

    # Check keyword overlap (answer correctness calculation)
    response_words = set(sample['response'].lower().split())
    ground_truth_words = set(test_case.ground_truth_answer.lower().split())
    overlap = len(response_words & ground_truth_words)
    overlap_ratio = overlap / max(len(ground_truth_words), 1)

    print(f"  Keyword Overlap: {overlap}/{len(ground_truth_words)} = {overlap_ratio:.3f}")
    print(f"  Answer Correctness (estimated): {min(overlap_ratio * 1.5, 1.0):.3f}")

    # SQL accuracy breakdown (4 components, each 0.25)
    # sql_accuracy = 0.75 means 3/4 passed
    if sample['sql_accuracy'] == 0.75:
        print(f"  SQL: 3/4 checks passed (likely: syntax OK, execution OK, semantic OK, results_accurate FAIL)")
    elif sample['sql_accuracy'] == 0.5:
        print(f"  SQL: 2/4 checks passed")

    # Overall score formula for SQL_ONLY:
    # = sql_accuracy * 0.4 + (answer_relevancy + answer_correctness) / 2 * 0.6
    # answer_relevancy = 0.7 (hardcoded)
    estimated_correctness = min(overlap_ratio * 1.5, 1.0)
    estimated_overall = sample['sql_accuracy'] * 0.4 + (0.7 + estimated_correctness) / 2 * 0.6
    print(f"  Expected Overall: {sample['sql_accuracy']:.2f}*0.4 + (0.7+{estimated_correctness:.2f})/2*0.6 = {estimated_overall:.3f}")

    print()

print("=" * 80)
print("CONCLUSION:")
print("Low scores are likely due to:")
print("  1. SQL accuracy at 0.75 (3/4) instead of 1.0 - likely 'results_accurate' check failing")
print("  2. Keyword overlap (answer_correctness) may be low if ground truth uses different wording")
print("  3. Hardcoded answer_relevancy of 0.7 caps the score")
print("=" * 80)
