"""Test if team queries work the same with abbreviations vs full names."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.sql_tool import NBAGSQLTool

def test_abbreviation_vs_fullname():
    """Test if abbreviation and full name queries produce identical results."""
    print("=" * 80)
    print("TESTING: ABBREVIATION VS FULL NAME QUERIES")
    print("=" * 80)

    sql_tool = NBAGSQLTool()

    # Test cases: (abbreviation query, full name query, description)
    test_pairs = [
        ("Show me Lakers stats", "Show me Los Angeles Lakers stats", "Single team stats"),
        ("Compare Lakers and Celtics", "Compare Los Angeles Lakers and Boston Celtics", "Team comparison"),
        ("What are the Warriors total points?", "What are the Golden State Warriors total points?", "Team total stat"),
        ("How many assists do the Heat have?", "How many assists do the Miami Heat have?", "Team assists"),
    ]

    results = []
    for i, (abbr_query, full_query, description) in enumerate(test_pairs, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {description}")
        print(f"{'=' * 80}")

        print(f"\nAbbreviation Query: '{abbr_query}'")
        print(f"Full Name Query:    '{full_query}'")

        try:
            # Execute abbreviation query
            abbr_response = sql_tool.query(abbr_query)
            abbr_results = abbr_response.get('results', []) if isinstance(abbr_response, dict) else []
            abbr_sql = abbr_response.get('sql', '') if isinstance(abbr_response, dict) else ''

            # Execute full name query
            full_response = sql_tool.query(full_query)
            full_results = full_response.get('results', []) if isinstance(full_response, dict) else []
            full_sql = full_response.get('sql', '') if isinstance(full_response, dict) else ''

            print(f"\n📊 Abbreviation SQL:")
            print(f"   {abbr_sql[:200]}...")
            print(f"\n📊 Full Name SQL:")
            print(f"   {full_sql[:200]}...")

            # Compare results
            match = False
            if len(abbr_results) == len(full_results):
                if len(abbr_results) == 0:
                    match = True  # Both empty
                else:
                    # Compare first result (should be identical)
                    abbr_first = abbr_results[0]
                    full_first = full_results[0]

                    # Check if numeric values match (allowing for team name differences)
                    abbr_values = [v for k, v in abbr_first.items() if k != 'name' and isinstance(v, (int, float))]
                    full_values = [v for k, v in full_first.items() if k != 'name' and isinstance(v, (int, float))]

                    match = abbr_values == full_values

            if match:
                print(f"\n✅ RESULTS MATCH!")
                print(f"   Abbreviation result: {abbr_results[0] if abbr_results else 'empty'}")
                print(f"   Full name result:    {full_results[0] if full_results else 'empty'}")
            else:
                print(f"\n❌ RESULTS DIFFER!")
                print(f"   Abbreviation result: {abbr_results[0] if abbr_results else 'empty'}")
                print(f"   Full name result:    {full_results[0] if full_results else 'empty'}")

            results.append({
                "description": description,
                "abbr_query": abbr_query,
                "full_query": full_query,
                "match": match,
                "success": True
            })

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                "description": description,
                "abbr_query": abbr_query,
                "full_query": full_query,
                "match": False,
                "success": False
            })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    matched = sum(1 for r in results if r["match"])

    print(f"\n✅ Queries Executed: {successful}/{len(test_pairs)}")
    print(f"✅ Results Match:    {matched}/{len(test_pairs)}")

    if matched == len(test_pairs):
        print("\n🎉 VERIFICATION PASSED!")
        print("   Abbreviations and full names produce IDENTICAL results.")
    else:
        print("\n⚠️  Some queries produced different results")
        print("   The SQL tool may not handle both forms consistently")

    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["match"] else "❌"
        print(f"{i}. {status} {result['description']}")
        if not result["match"]:
            print(f"   Abbr: {result['abbr_query']}")
            print(f"   Full: {result['full_query']}")

if __name__ == "__main__":
    test_abbreviation_vs_fullname()
