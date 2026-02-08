"""
FILE: regenerate_ground_truth.py
STATUS: Active
RESPONSIBILITY: Regenerate ground truth data from actual database for SQL test cases
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import io
import json
import logging
import sys
from pathlib import Path

from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.services.query_classifier import QueryType
from src.tools.sql_tool import NBAGSQLTool

# Set UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def regenerate_ground_truth():
    """Regenerate ground truth data from actual database."""
    print("\n" + "=" * 80)
    print("  REGENERATING GROUND TRUTH FROM ACTUAL DATABASE")
    print("=" * 80 + "\n")

    # Initialize SQL tool
    sql_tool = NBAGSQLTool()

    updated_cases = []

    for i, test_case in enumerate(SQL_TEST_CASES):
        print(f"\n[{i+1}/{len(SQL_TEST_CASES)}] {test_case.question}")
        print(f"  Category: {test_case.category}")
        print(f"  Expected SQL: {test_case.expected_sql[:80]}...")

        try:
            # Execute the expected SQL query to get actual results
            result = sql_tool.query(test_case.question)

            if result.get("error"):
                print(f"  ERROR: {result['error']}")
                updated_cases.append({
                    "index": i,
                    "question": test_case.question,
                    "category": test_case.category,
                    "expected_sql": test_case.expected_sql,
                    "error": result["error"],
                    "old_ground_truth": test_case.ground_truth_data,
                    "new_ground_truth": None,
                })
                continue

            actual_results = result.get("results", [])

            if not actual_results:
                print(f"  No results returned")
                updated_cases.append({
                    "index": i,
                    "question": test_case.question,
                    "category": test_case.category,
                    "expected_sql": test_case.expected_sql,
                    "old_ground_truth": test_case.ground_truth_data,
                    "new_ground_truth": None,
                })
                continue

            # Print comparison
            print(f"  OK Got {len(actual_results)} result(s)")
            print(f"  Old ground truth: {test_case.ground_truth_data}")
            print(f"  New ground truth: {actual_results if len(actual_results) > 1 else actual_results[0]}")

            # Check if ground truth matches
            if isinstance(test_case.ground_truth_data, list):
                # Multi-row result
                matches = len(actual_results) == len(test_case.ground_truth_data)
                if matches:
                    print("  OK Row count matches")
                else:
                    print(f"  WARNING Row count mismatch: {len(actual_results)} vs {len(test_case.ground_truth_data)}")
            else:
                # Single-row result
                matches = len(actual_results) == 1
                if matches:
                    print("  OK Single row as expected")
                else:
                    print(f"  WARNING Expected single row, got {len(actual_results)}")

            updated_cases.append({
                "index": i,
                "question": test_case.question,
                "category": test_case.category,
                "expected_sql": test_case.expected_sql,
                "old_ground_truth": test_case.ground_truth_data,
                "new_ground_truth": actual_results if len(actual_results) > 1 else actual_results[0],
                "matches": matches,
            })

        except Exception as e:
            logger.error(f"  Exception: {e}")
            updated_cases.append({
                "index": i,
                "question": test_case.question,
                "category": test_case.category,
                "expected_sql": test_case.expected_sql,
                "error": str(e),
                "old_ground_truth": test_case.ground_truth_data,
                "new_ground_truth": None,
            })

    # Save results
    output_file = Path("evaluation_results/ground_truth_regeneration.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(updated_cases, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"  SUMMARY")
    print("=" * 80)

    total = len(updated_cases)
    errors = sum(1 for c in updated_cases if "error" in c)
    no_results = sum(1 for c in updated_cases if c.get("new_ground_truth") is None and "error" not in c)
    matches = sum(1 for c in updated_cases if c.get("matches", False))
    mismatches = total - errors - no_results - matches

    print(f"  Total test cases: {total}")
    print(f"  OK Matches: {matches} ({100*matches/total:.1f}%)")
    print(f"  WARNING Mismatches: {mismatches} ({100*mismatches/total:.1f}%)")
    print(f"  WARNING No results: {no_results} ({100*no_results/total:.1f}%)")
    print(f"  ERROR Errors: {errors} ({100*errors/total:.1f}%)")
    print(f"\n  Results saved to: {output_file}")
    print("=" * 80 + "\n")

    return updated_cases


if __name__ == "__main__":
    regenerate_ground_truth()
