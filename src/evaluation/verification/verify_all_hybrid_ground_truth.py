"""
FILE: verify_all_hybrid_ground_truth.py
STATUS: Active
RESPONSIBILITY: Comprehensive hybrid ground truth verification for all test cases
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Verifies:
1. SQL queries return correct data from database
2. ground_truth_data matches actual SQL results
3. ground_truth_answer appropriately combines SQL data + context
"""
import sqlite3
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.test_cases.sql_test_cases import HYBRID_TEST_CASES

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
        return round(val, 1)
    return val


def compare_results(expected: Any, actual: list[dict]) -> tuple[bool, str, dict]:
    """Compare expected ground truth with actual results."""
    if expected is None:
        return True, "No ground truth data (analysis query)", {"type": "analysis_only"}

    if actual and "__error__" in actual[0]:
        return False, f"SQL error: {actual[0]['__error__']}", {"error": actual[0]["__error__"]}

    if isinstance(expected, dict):
        expected = [expected]

    if len(actual) != len(expected):
        return False, f"Count mismatch: expected {len(expected)}, got {len(actual)}", {
            "expected_count": len(expected),
            "actual_count": len(actual),
            "expected": expected,
            "actual": actual[:10],
        }

    if actual and expected:
        first_key = list(expected[0].keys())[0]
        try:
            actual_sorted = sorted(actual, key=lambda x: (x.get(first_key) is None, x.get(first_key)))
            expected_sorted = sorted(expected, key=lambda x: (x.get(first_key) is None, x.get(first_key)))
        except (TypeError, KeyError):
            actual_sorted = actual
            expected_sorted = expected

        mismatches = []
        for idx, (exp_row, act_row) in enumerate(zip(expected_sorted, actual_sorted)):
            for key in exp_row:
                if key not in act_row:
                    return False, f"Missing key '{key}' in actual results", {
                        "row": idx,
                        "expected_keys": list(exp_row.keys()),
                        "actual_keys": list(act_row.keys()),
                    }

                exp_val = normalize_value(exp_row[key])
                act_val = normalize_value(act_row[key])

                if exp_val != act_val:
                    mismatches.append({
                        "row": idx,
                        "key": key,
                        "expected": exp_val,
                        "actual": act_val,
                    })

        if mismatches:
            return False, f"Value mismatches found", {"mismatches": mismatches, "expected": expected, "actual": actual}

    return True, "Match", {"expected": expected, "actual": actual}


def verify_answer_mentions_data(answer: str, data: Any) -> tuple[bool, str]:
    """Verify that ground_truth_answer mentions key values from ground_truth_data."""
    if data is None:
        return True, "No specific data to verify (analysis question)"

    if isinstance(data, dict):
        data = [data]

    missing_mentions = []
    for row in data:
        if "name" in row:
            name = row["name"]
            name_parts = name.split()
            if not any(part in answer for part in name_parts):
                missing_mentions.append(f"Player '{name}' not mentioned")

    if missing_mentions:
        return False, "; ".join(missing_mentions[:3])

    return True, "Answer appropriately mentions data"


print("=" * 80)
print(f"HYBRID GROUND TRUTH VERIFICATION ({len(HYBRID_TEST_CASES)} test cases)")
print("=" * 80)

results = {"passed": [], "failed": [], "warnings": []}

for i, test_case in enumerate(HYBRID_TEST_CASES, 1):
    question = test_case.question
    expected_data = test_case.ground_truth_data
    expected_answer = test_case.ground_truth_answer
    sql = test_case.expected_sql
    category = test_case.category

    print(f"\n[{i}/{len(HYBRID_TEST_CASES)}] {category}")
    print(f"Q: {question[:80]}...")

    actual_data = query_db(sql)
    is_match, message, details = compare_results(expected_data, actual_data)

    if not is_match:
        print(f"  ❌ SQL DATA MISMATCH: {message}")
        if "mismatches" in details:
            for mm in details["mismatches"][:3]:
                print(f"     Row {mm['row']}, {mm['key']}: expected {mm['expected']}, got {mm['actual']}")
        results["failed"].append({"test_case": test_case, "message": message, "details": details})
        continue

    answer_ok, answer_msg = verify_answer_mentions_data(expected_answer, expected_data)

    if not answer_ok:
        print(f"  ⚠️  ANSWER WARNING: {answer_msg}")
        results["warnings"].append({"test_case": test_case, "message": answer_msg})

    print(f"  ✅ PASS: {message}")
    results["passed"].append(test_case)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Passed:  {len(results['passed'])}/{len(HYBRID_TEST_CASES)}")
print(f"❌ Failed:  {len(results['failed'])}/{len(HYBRID_TEST_CASES)}")
print(f"⚠️  Warnings: {len(results['warnings'])}/{len(HYBRID_TEST_CASES)}")

if results["failed"]:
    print(f"\n❌ FAILED TEST CASES:")
    for item in results["failed"]:
        tc = item["test_case"]
        print(f"\n  [{tc.category}] {tc.question[:70]}...")
        print(f"  Issue: {item['message']}")
        if "mismatches" in item["details"]:
            for mm in item["details"]["mismatches"][:5]:
                print(f"    - {mm['key']}: expected {mm['expected']}, got {mm['actual']}")

if results["warnings"]:
    print(f"\n⚠️  WARNINGS:")
    for item in results["warnings"]:
        tc = item["test_case"]
        print(f"  - {tc.question[:60]}... | {item['message']}")

success_rate = len(results['passed']) / len(HYBRID_TEST_CASES) * 100
print(f"\n📊 Success Rate: {success_rate:.1f}%")

if len(results['failed']) == 0:
    print("\n✅ ALL HYBRID SQL DATA IS CORRECT!")
else:
    print(f"\n⚠️  {len(results['failed'])} test cases need correction")

print("=" * 80)
