"""Test 5 random SQL test cases after normalization to verify results unchanged."""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES
from src.tools.sql_tool import NBAGSQLTool

def test_sql_cases():
    """Run 5 random SQL test cases and verify results."""
    print("=" * 80)
    print("TESTING 5 RANDOM SQL CASES AFTER NORMALIZATION")
    print("=" * 80)

    # Select 5 diverse test cases (seed for reproducibility)
    random.seed(42)
    test_cases = random.sample(SQL_TEST_CASES, 5)

    sql_tool = NBAGSQLTool()

    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {test_case.question}")
        print(f"{'─' * 80}")
        print(f"Category: {test_case.category}")

        # Execute query
        try:
            response = sql_tool.query(test_case.question)

            print(f"\n✅ Query executed successfully")
            print(f"\nResponse:")
            # Handle response which might be dict or string
            if isinstance(response, dict):
                response_str = str(response)
            else:
                response_str = str(response)
            print(response_str[:500])  # First 500 chars

            # Check if ground truth data appears in response
            gt_data = test_case.ground_truth_data
            response_lower = response_str.lower()

            match = False
            if isinstance(gt_data, dict):
                # Single result - check if key values appear
                values_found = []
                for key, value in gt_data.items():
                    if key == "name":
                        # Check name appears
                        if str(value).lower() in response_lower:
                            values_found.append(f"{key}={value}")
                    else:
                        # Check numeric value appears
                        if str(value) in response_str or str(int(value)) in response_str:
                            values_found.append(f"{key}={value}")

                match = len(values_found) >= len(gt_data) * 0.7  # 70% of values must appear
                print(f"\nGround Truth Check: {len(values_found)}/{len(gt_data)} values found")
                if values_found:
                    print(f"  Found: {', '.join(values_found)}")

            elif isinstance(gt_data, list):
                # Multiple results - check if at least first result appears
                first_result = gt_data[0]
                values_found = []
                for key, value in first_result.items():
                    if str(value).lower() in response_lower or str(value) in response_str:
                        values_found.append(f"{key}={value}")

                match = len(values_found) >= len(first_result) * 0.5  # 50% of first result values
                print(f"\nGround Truth Check (first result): {len(values_found)}/{len(first_result)} values found")
                if values_found:
                    print(f"  Found: {', '.join(values_found)}")

            results.append({
                "question": test_case.question,
                "category": test_case.category,
                "success": True,
                "match": match
            })

            if match:
                print("\n✅ RESULT MATCHES GROUND TRUTH")
            else:
                print("\n⚠️  RESULT DOESN'T CLEARLY MATCH GROUND TRUTH (may need manual verification)")

        except Exception as e:
            print(f"\n❌ Query failed: {e}")
            results.append({
                "question": test_case.question,
                "category": test_case.category,
                "success": False,
                "match": False
            })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    matched = sum(1 for r in results if r["match"])

    print(f"\n✅ Executed Successfully: {successful}/5")
    print(f"✅ Results Match Ground Truth: {matched}/5")

    if successful == 5 and matched >= 4:
        print("\n🎉 NORMALIZATION VERIFICATION PASSED!")
        print("   SQL queries still work correctly after normalization.")
    elif successful == 5:
        print("\n⚠️  All queries executed but some results need manual verification")
    else:
        print("\n❌ Some queries failed - normalization may have broken queries")

    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        match_status = "✅" if result["match"] else "⚠️"
        print(f"{i}. {status} {match_status} {result['category']}: {result['question'][:60]}...")

if __name__ == "__main__":
    test_sql_cases()
