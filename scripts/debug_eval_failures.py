"""
FILE: debug_eval_failures.py
STATUS: Active
RESPONSIBILITY: Debug evaluation failures to understand why Results: N
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import io
import json
import logging
import sys
from pathlib import Path

from src.evaluation.sql_only_test_cases import SQL_ONLY_TEST_CASES
from src.tools.sql_tool import NBAGSQLTool

# Set UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.WARNING)

def debug_failures():
    """Debug failed test cases to understand comparison issues."""
    sql_tool = NBAGSQLTool()

    # Load evaluation results
    results_file = Path("evaluation_results/sql_hybrid_evaluation.json")
    if not results_file.exists():
        print("No evaluation results found")
        return

    eval_data = json.load(results_file.open(encoding='utf-8'))

    # Find failures
    failures = [s for s in eval_data['samples'] if s['overall_score'] < 0.7]
    print(f"\nFound {len(failures)} failures. Analyzing first 10...\n")
    print("=" * 80)

    for i, failure in enumerate(failures[:10]):
        # Find corresponding test case
        test_case = next((tc for tc in SQL_ONLY_TEST_CASES if tc.question == failure['query']), None)
        if not test_case:
            continue

        print(f"\n[{i+1}] {failure['query'][:70]}")
        print(f"    Score: {failure['overall_score']:.2f} | SQL Acc: {failure.get('sql_accuracy', 'N/A')}")

        # Execute SQL to see actual results
        result = sql_tool.query(test_case.question)
        actual_results = result.get("results", [])

        print(f"\n    Expected ground truth: {test_case.ground_truth_data}")
        print(f"    Actual results:        {actual_results if len(actual_results) <= 1 else actual_results}")

        # Check why comparison failed
        if isinstance(test_case.ground_truth_data, dict):
            if len(actual_results) == 1:
                actual = actual_results[0]
                print(f"\n    Comparison:")
                for key, expected_val in test_case.ground_truth_data.items():
                    if key in actual:
                        actual_val = actual[key]
                        if isinstance(expected_val, (int, float)):
                            diff = abs(actual_val - expected_val)
                            pct_diff = diff / expected_val if expected_val != 0 else 0
                            match = pct_diff < 0.05
                            print(f"      {key}: {actual_val} vs {expected_val} | Diff: {diff} ({pct_diff*100:.1f}%) | Match: {match}")
                        else:
                            match = str(actual_val).lower() == str(expected_val).lower()
                            print(f"      {key}: '{actual_val}' vs '{expected_val}' | Match: {match}")
                    else:
                        print(f"      {key}: MISSING in actual results!")
                        print(f"      Available keys: {list(actual.keys())}")
            else:
                print(f"    Row count mismatch: {len(actual_results)} vs 1")

        print("    " + "-" * 76)

if __name__ == "__main__":
    debug_failures()
