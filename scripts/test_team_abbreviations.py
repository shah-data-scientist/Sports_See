"""Test if 3-letter team abbreviations work consistently.

Users can refer to teams in 3 ways:
1. 3-letter abbreviation: "LAL", "BOS", "GSW"
2. Short name: "Lakers", "Celtics", "Warriors"
3. Full name: "Los Angeles Lakers", "Boston Celtics", "Golden State Warriors"

All should produce IDENTICAL results.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.sql_tool import NBAGSQLTool

def test_team_abbreviations():
    """Test if 3-letter team abbreviations work consistently."""
    print("=" * 80)
    print("TESTING: 3-LETTER TEAM ABBREVIATIONS")
    print("=" * 80)

    sql_tool = NBAGSQLTool()

    # Test cases: (abbreviation, short name, full name, description)
    test_teams = [
        ("LAL", "Lakers", "Los Angeles Lakers", "Los Angeles Lakers"),
        ("BOS", "Celtics", "Boston Celtics", "Boston Celtics"),
        ("GSW", "Warriors", "Golden State Warriors", "Golden State Warriors"),
        ("MIA", "Heat", "Miami Heat", "Miami Heat"),
        ("CHI", "Bulls", "Chicago Bulls", "Chicago Bulls"),
        ("DAL", "Mavericks", "Dallas Mavericks", "Dallas Mavericks"),
    ]

    results = []
    for i, (abbr, short_name, full_name, description) in enumerate(test_teams, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {description}")
        print(f"{'=' * 80}")

        # Create 3 query variations
        abbr_query = f"Show me {abbr} stats"
        short_query = f"Show me {short_name} stats"
        full_query = f"Show me {full_name} stats"

        print(f"\n3-Letter Abbr: '{abbr_query}'")
        print(f"Short Name:    '{short_query}'")
        print(f"Full Name:     '{full_query}'")

        try:
            # Execute all 3 variations
            abbr_response = sql_tool.query(abbr_query)
            abbr_results = abbr_response.get('results', []) if isinstance(abbr_response, dict) else []
            abbr_sql = abbr_response.get('sql', '') if isinstance(abbr_response, dict) else ''

            short_response = sql_tool.query(short_query)
            short_results = short_response.get('results', []) if isinstance(short_response, dict) else []
            short_sql = short_response.get('sql', '') if isinstance(short_response, dict) else ''

            full_response = sql_tool.query(full_query)
            full_results = full_response.get('results', []) if isinstance(full_response, dict) else []
            full_sql = full_response.get('sql', '') if isinstance(full_response, dict) else ''

            print(f"\n📊 SQL Generated:")
            print(f"   Abbr:  {abbr_sql[:100]}...")
            print(f"   Short: {short_sql[:100]}...")
            print(f"   Full:  {full_sql[:100]}...")

            # Check if abbreviation appears in SQL (should be in WHERE clause)
            abbr_in_sql = {
                "abbr": abbr.upper() in abbr_sql.upper() or f"'{abbr}'" in abbr_sql,
                "short": abbr.upper() in short_sql.upper() or f"'{abbr}'" in short_sql,
                "full": abbr.upper() in full_sql.upper() or f"'{abbr}'" in full_sql,
            }

            print(f"\n🔍 Uses 3-letter abbreviation in SQL:")
            print(f"   3-letter query: {'✅' if abbr_in_sql['abbr'] else '❌'}")
            print(f"   Short name:     {'✅' if abbr_in_sql['short'] else '❌'}")
            print(f"   Full name:      {'✅' if abbr_in_sql['full'] else '❌'}")

            # Compare results
            all_match = False
            if len(abbr_results) > 0 and len(short_results) > 0 and len(full_results) > 0:
                # Extract numeric values (ignore team name field)
                abbr_values = [v for k, v in abbr_results[0].items() if k != 'name' and isinstance(v, (int, float))]
                short_values = [v for k, v in short_results[0].items() if k != 'name' and isinstance(v, (int, float))]
                full_values = [v for k, v in full_results[0].items() if k != 'name' and isinstance(v, (int, float))]

                all_match = (abbr_values == short_values == full_values)

                print(f"\n📈 Results:")
                print(f"   3-letter: {abbr_results[0]}")
                print(f"   Short:    {short_results[0]}")
                print(f"   Full:     {full_results[0]}")

            elif len(abbr_results) == 0 and len(short_results) == 0 and len(full_results) == 0:
                all_match = True  # All empty
                print(f"\n📈 Results: All queries returned empty")

            if all_match:
                print(f"\n✅ ALL 3 FORMS PRODUCE IDENTICAL RESULTS!")
            else:
                print(f"\n❌ RESULTS DIFFER ACROSS FORMS!")

            results.append({
                "team": description,
                "abbr": abbr,
                "all_match": all_match,
                "abbr_in_sql": abbr_in_sql,
                "success": True
            })

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                "team": description,
                "abbr": abbr,
                "all_match": False,
                "abbr_in_sql": {"abbr": False, "short": False, "full": False},
                "success": False
            })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    all_matched = sum(1 for r in results if r["all_match"])
    all_use_abbr = sum(1 for r in results if all(r["abbr_in_sql"].values()))

    print(f"\n✅ Teams Tested:               {successful}/{len(test_teams)}")
    print(f"✅ All 3 forms match:          {all_matched}/{len(test_teams)}")
    print(f"✅ All forms use 3-letter SQL: {all_use_abbr}/{len(test_teams)}")

    if all_matched == len(test_teams):
        print("\n🎉 VERIFICATION PASSED!")
        print("   3-letter abbreviations, short names, and full names produce IDENTICAL results.")
    elif all_matched >= len(test_teams) * 0.8:
        print("\n⚠️  MOSTLY CONSISTENT (>80% match rate)")
        print("   Some teams may have inconsistent handling")
    else:
        print("\n❌ INCONSISTENT RESULTS")
        print("   Team name handling is not reliable")

    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["all_match"] else "❌"
        sql_status = "✅" if all(result["abbr_in_sql"].values()) else "⚠️"
        print(f"{i}. {status} {sql_status} {result['team']} ({result['abbr']})")
        if not result["all_match"]:
            print(f"     ❌ Results differ across different name formats")
        if not all(result["abbr_in_sql"].values()):
            print(f"     ⚠️  Not all queries used 3-letter abbreviation in SQL")
            for form, used in result["abbr_in_sql"].items():
                if not used:
                    print(f"        - {form} didn't use {result['abbr']}")

    # Critical analysis
    print("\n" + "=" * 80)
    print("SQL GENERATION ANALYSIS")
    print("=" * 80)

    print("\nDo all query forms use the 3-letter abbreviation in SQL WHERE clause?")
    for result in results:
        if all(result["abbr_in_sql"].values()):
            print(f"  ✅ {result['team']}: All forms use '{result['abbr']}' in SQL")
        else:
            print(f"  ❌ {result['team']}: Inconsistent SQL generation")
            for form, used in result["abbr_in_sql"].items():
                status = "✅" if used else "❌"
                print(f"     {status} {form}")

if __name__ == "__main__":
    test_team_abbreviations()
