"""Quick test script to verify SQL remediation implementations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.sql_tool import NBAGSQLTool
from src.services.chat import ChatService


def test_issue_10_normalization():
    """Test Issue #10: Special character normalization."""
    print("\n" + "=" * 80)
    print("ISSUE #10: Special Character Normalization")
    print("=" * 80)

    test_cases = [
        ("Jokić", "Jokic"),
        ("Dončić", "Doncic"),
        ("Šarić", "Saric"),
        ("Antetokounmpo", "Antetokounmpo"),  # No diacritics
    ]

    passed = 0
    for input_name, expected in test_cases:
        result = NBAGSQLTool.normalize_player_name(input_name)
        status = "✅" if result == expected else "❌"
        if result == expected:
            passed += 1
        print(f"  {status} normalize_player_name('{input_name}') = '{result}' (expected: '{expected}')")

    print(f"\n✅ Issue #10: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def test_issue_3_join_validation():
    """Test Issue #3: Missing JOIN validation."""
    print("\n" + "=" * 80)
    print("ISSUE #3: Missing JOIN Validation")
    print("=" * 80)

    tool = NBAGSQLTool()

    # Test case: SQL missing JOIN when query mentions "players"
    question = "Who has the most rebounds?"
    sql_without_join = "SELECT name, reb FROM player_stats ORDER BY reb DESC LIMIT 1"

    validated_sql = tool._validate_sql_structure(sql_without_join, question)

    has_join = "join" in validated_sql.lower()
    status = "✅" if has_join else "❌"

    print(f"\nOriginal SQL (no JOIN):")
    print(f"  {sql_without_join}")
    print(f"\nValidated SQL:")
    print(f"  {validated_sql}")
    print(f"\n{status} JOIN auto-correction: {'WORKING' if has_join else 'FAILED'}")

    return has_join


def test_issue_6_hedging_removal():
    """Test Issue #6: Hedging removal."""
    print("\n" + "=" * 80)
    print("ISSUE #6: Excessive Hedging Removal")
    print("=" * 80)

    test_cases = [
        (
            "Player X appears to have scored approximately 30 points.",
            "Player X  scored  30 points."
        ),
        (
            "He seems to be around 6 feet tall and possibly weighs 200 pounds.",
            "He  is  6 feet tall and  weighs 200 pounds."
        ),
        (
            "The team may have won 50 games this season.",
            "The team has won 50 games this season."
        ),
    ]

    passed = 0
    for input_text, expected_contains in test_cases:
        result = ChatService._remove_excessive_hedging(input_text)
        # Check if hedging words were removed
        hedging_removed = all(
            word not in result.lower()
            for word in ["appears", "approximately", "seems", "around", "possibly", "may have"]
        )
        status = "✅" if hedging_removed else "❌"
        if hedging_removed:
            passed += 1

        print(f"\n  Original: {input_text}")
        print(f"  Cleaned:  {result}")
        print(f"  {status} Hedging removed: {hedging_removed}")

    print(f"\n✅ Issue #6: {passed}/{len(test_cases)} tests passed")
    return passed == len(test_cases)


def main():
    """Run all remediation tests."""
    print("\n" + "=" * 80)
    print("SQL REMEDIATION VERIFICATION TESTS")
    print("=" * 80)

    results = {
        "Issue #10 (Name Normalization)": test_issue_10_normalization(),
        "Issue #3 (JOIN Validation)": test_issue_3_join_validation(),
        "Issue #6 (Hedging Removal)": test_issue_6_hedging_removal(),
    }

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for issue, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {issue}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 ALL REMEDIATION TESTS PASSED!")
    else:
        print("\n⚠️ Some tests failed - review output above")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
