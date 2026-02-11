"""
FILE: verify_all_sql_ground_truth.py
STATUS: Active
RESPONSIBILITY: Comprehensive SQL ground truth verification for all test cases
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Compares expected ground_truth_data against actual database results.
"""
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "sql" / "nba_stats.db"


def query_db(sql: str) -> list[dict]:
    """Execute SQL and return results as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except Exception as e:
        return [{"__error__": str(e)}]
    finally:
        conn.close()


def normalize_value(val: Any) -> Any:
    """Normalize values for comparison (handle float precision)."""
    if isinstance(val, float):
        return round(val, 2)  # Round to 2 decimals for comparison
    return val


def compare_results(expected: Any, actual: list[dict]) -> tuple[bool, str]:
    """Compare expected ground truth with actual results."""
    if expected is None:
        return True, "No ground truth specified (analysis query)"

    # Handle list vs single dict
    if isinstance(expected, dict):
        expected = [expected]

    if len(actual) != len(expected):
        return False, f"Count mismatch: expected {len(expected)}, got {len(actual)}"

    # Check if actual contains errors
    if any("__error__" in row for row in actual):
        return False, f"SQL error: {actual[0]['__error__']}"

    # Sort both by first key to handle ordering differences
    if actual and expected:
        first_key = list(expected[0].keys())[0]
        try:
            actual_sorted = sorted(actual, key=lambda x: (x.get(first_key) is None, x.get(first_key)))
            expected_sorted = sorted(expected, key=lambda x: (x.get(first_key) is None, x.get(first_key)))
        except (TypeError, KeyError):
            # If sorting fails, use original order
            actual_sorted = actual
            expected_sorted = expected

        # Compare each row
        for exp_row, act_row in zip(expected_sorted, actual_sorted):
            for key in exp_row:
                if key not in act_row:
                    return False, f"Missing key '{key}' in actual results"

                exp_val = normalize_value(exp_row[key])
                act_val = normalize_value(act_row[key])

                if exp_val != act_val:
                    return False, f"{key}: expected {exp_val}, got {act_val}"

    return True, "Match"


print("=" * 80)
print(f"COMPREHENSIVE SQL GROUND TRUTH VERIFICATION ({len(SQL_TEST_CASES)} test cases)")
print("=" * 80)

results = {
    "passed": [],
    "failed": [],
    "errors": [],
}

for i, test_case in enumerate(SQL_TEST_CASES, 1):
    question = test_case.question
    expected_data = test_case.ground_truth_data
    sql = test_case.expected_sql

    print(f"\n[{i}/{len(SQL_TEST_CASES)}] {question}")

    # Query database
    actual_data = query_db(sql)

    # Compare
    is_match, message = compare_results(expected_data, actual_data)

    if is_match:
        print(f"  ✅ PASS: {message}")
        results["passed"].append(test_case)
    else:
        print(f"  ❌ FAIL: {message}")
        print(f"     Expected: {expected_data}")
        print(f"     Actual:   {actual_data}")
        results["failed"].append((test_case, actual_data, message))

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Passed:  {len(results['passed'])}/{len(SQL_TEST_CASES)}")
print(f"❌ Failed:  {len(results['failed'])}/{len(SQL_TEST_CASES)}")

if results["failed"]:
    print(f"\n⚠️  FAILED TEST CASES:")
    for test_case, actual, message in results["failed"]:
        print(f"  - {test_case.question}")
        print(f"    Reason: {message}")

success_rate = len(results['passed']) / len(SQL_TEST_CASES) * 100
print(f"\n📊 Success Rate: {success_rate:.1f}%")

if len(results['failed']) == 0:
    print("\n✅ ALL SQL GROUND TRUTH IS CORRECT!")
else:
    print(f"\n⚠️  {len(results['failed'])} test cases need ground truth correction")

print("=" * 80)
