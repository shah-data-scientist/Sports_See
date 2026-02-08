"""
FILE: test_fixed_evaluation.py
STATUS: Active
RESPONSIBILITY: Quick test of fixed evaluation index alignment
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import logging
from src.evaluation.sql_test_cases import SQL_TEST_CASES
from scripts.evaluate_sql_hybrid import run_sql_hybrid_evaluation, compute_metrics

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

# Test with first 10 cases
test_cases = SQL_TEST_CASES[:10]

print("=" * 80)
print("TESTING FIXED EVALUATION (First 10 cases)")
print("=" * 80)

# Run evaluation
results = run_sql_hybrid_evaluation(test_cases, use_sql=True)

# Check alignment
print(f"\nTest cases: {len(test_cases)}")
print(f"Results: {len(results)}")
print("\nAlignment check:")
print("-" * 80)

pass_count = 0
fail_count = 0

for i, (sample, test_case) in enumerate(results):
    if sample is None:
        print(f"{i+1}. [SKIP] {test_case.question[:60]}...")
        continue

    # Verify alignment
    if sample.user_input == test_case.question:
        alignment = "OK"
    else:
        alignment = "MISMATCH!"

    # Compute metrics
    metrics = compute_metrics(sample, test_case)

    # Check score
    status = "PASS" if metrics.overall_score >= 0.7 else "FAIL"
    if status == "PASS":
        pass_count += 1
    else:
        fail_count += 1

    print(f"{i+1}. [{status}] {alignment} | Score: {metrics.overall_score:.3f} | {test_case.question[:50]}...")

    # Show details for failures
    if status == "FAIL" and metrics.sql_accuracy:
        print(f"     SQL: {metrics.sql_accuracy.overall_score:.2f} (syntax: {metrics.sql_accuracy.sql_syntax_correct}, "
              f"semantic: {metrics.sql_accuracy.sql_semantic_correct}, "
              f"results: {metrics.sql_accuracy.results_accurate})")
        print(f"     Answer: {sample.response[:80]}...")

print("\n" + "=" * 80)
print(f"RESULTS: {pass_count} PASS, {fail_count} FAIL out of {pass_count + fail_count} queries")
print(f"Pass rate: {pass_count/(pass_count+fail_count)*100:.1f}%")
print("=" * 80)
