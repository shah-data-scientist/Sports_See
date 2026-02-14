"""Test if statistical abbreviations vs full names produce identical results.

CRITICAL: Database uses specific column names (pts, reb, ast, stl, blk, etc.)
Users may ask using:
- Abbreviations: "PTS", "REB", "AST", "3P%", "FG%"
- Full names: "points", "rebounds", "assists", "three point percentage"
- Mixed: "three pointers made", "field goal percentage"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.sql_tool import NBAGSQLTool

def test_stat_abbreviations():
    """Test if stat abbreviations and full names produce identical results."""
    print("=" * 80)
    print("TESTING: STATISTICAL ABBREVIATIONS VS FULL NAMES")
    print("=" * 80)

    sql_tool = NBAGSQLTool()

    # Test cases: (abbreviation query, full name query, description, expected_column)
    test_pairs = [
        # Scoring stats
        ("Who has the most PTS?", "Who has the most points?", "Points (PTS)", "pts"),
        ("Who has the highest FG%?", "Who has the highest field goal percentage?", "Field Goal % (FG%)", "fg_pct"),
        ("Who made the most 3PM?", "Who made the most three pointers?", "Three Pointers Made (3PM)", "three_pm"),
        ("Best 3P%?", "Best three point percentage?", "Three Point % (3P%)", "three_pct"),
        ("Who has the best FT%?", "Who has the best free throw percentage?", "Free Throw % (FT%)", "ft_pct"),

        # Other stats
        ("Top 3 in REB", "Top 3 in rebounds", "Rebounds (REB)", "reb"),
        ("Most AST", "Most assists", "Assists (AST)", "ast"),
        ("Top STL", "Top steals", "Steals (STL)", "stl"),
        ("Most BLK", "Most blocks", "Blocks (BLK)", "blk"),
        ("Highest TOV", "Highest turnovers", "Turnovers (TOV)", "tov"),

        # Advanced stats
        ("Best TS%?", "Best true shooting percentage?", "True Shooting % (TS%)", "ts_pct"),
        ("Highest PIE", "Highest player impact estimate", "Player Impact Estimate (PIE)", "pie"),
        ("Top eFG%", "Top effective field goal percentage", "Effective FG% (eFG%)", "efg_pct"),
    ]

    results = []
    for i, (abbr_query, full_query, description, expected_col) in enumerate(test_pairs, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {description}")
        print(f"{'=' * 80}")

        print(f"Abbreviation: '{abbr_query}'")
        print(f"Full Name:    '{full_query}'")
        print(f"Expected DB Column: {expected_col}")

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
            print(f"   {abbr_sql[:150]}...")
            print(f"\n📊 Full Name SQL:")
            print(f"   {full_sql[:150]}...")

            # Check if expected column appears in SQL
            abbr_has_col = expected_col.lower() in abbr_sql.lower()
            full_has_col = expected_col.lower() in full_sql.lower()

            print(f"\n🔍 Column Check:")
            print(f"   Abbreviation uses '{expected_col}': {'✅' if abbr_has_col else '❌'}")
            print(f"   Full name uses '{expected_col}':    {'✅' if full_has_col else '❌'}")

            # Compare results
            match = False
            same_player = False
            if len(abbr_results) > 0 and len(full_results) > 0:
                abbr_first = abbr_results[0]
                full_first = full_results[0]

                # Get player names
                abbr_name = abbr_first.get('name', '')
                full_name = full_first.get('name', '')
                same_player = abbr_name == full_name

                # Get stat values (first non-name numeric value)
                abbr_stat = next((v for k, v in abbr_first.items() if k != 'name' and isinstance(v, (int, float))), None)
                full_stat = next((v for k, v in full_first.items() if k != 'name' and isinstance(v, (int, float))), None)

                match = (same_player and abbr_stat == full_stat)

                print(f"\n📈 Results:")
                print(f"   Abbreviation: {abbr_name} = {abbr_stat}")
                print(f"   Full name:    {full_name} = {full_stat}")

            elif len(abbr_results) == 0 and len(full_results) == 0:
                match = True  # Both empty
                print(f"\n📈 Results: Both queries returned empty")

            if match:
                print(f"\n✅ RESULTS MATCH! (Same player, same stat value)")
            elif same_player and not match:
                print(f"\n⚠️  SAME PLAYER, DIFFERENT STAT VALUES")
            else:
                print(f"\n❌ RESULTS DIFFER! (Different players or values)")

            results.append({
                "description": description,
                "abbr_query": abbr_query,
                "full_query": full_query,
                "match": match,
                "abbr_has_col": abbr_has_col,
                "full_has_col": full_has_col,
                "success": True
            })

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                "description": description,
                "abbr_query": abbr_query,
                "full_query": full_query,
                "match": False,
                "abbr_has_col": False,
                "full_has_col": False,
                "success": False
            })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    matched = sum(1 for r in results if r["match"])
    both_use_correct_col = sum(1 for r in results if r.get("abbr_has_col", False) and r.get("full_has_col", False))

    print(f"\n✅ Queries Executed:           {successful}/{len(test_pairs)}")
    print(f"✅ Results Match:              {matched}/{len(test_pairs)}")
    print(f"✅ Both use correct DB column: {both_use_correct_col}/{len(test_pairs)}")

    if matched == len(test_pairs):
        print("\n🎉 VERIFICATION PASSED!")
        print("   Statistical abbreviations and full names produce IDENTICAL results.")
    elif matched >= len(test_pairs) * 0.8:
        print("\n⚠️  MOSTLY CONSISTENT (>80% match rate)")
        print("   Some variations in how stats are interpreted")
    else:
        print("\n❌ INCONSISTENT RESULTS")
        print("   The SQL tool may not handle stat names consistently")

    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result["match"] else "❌"
        col_status = "✅" if (result.get("abbr_has_col") and result.get("full_has_col")) else "⚠️"
        print(f"{i}. {status} {col_status} {result['description']}")
        if not result["match"]:
            print(f"     Abbr: {result['abbr_query']}")
            print(f"     Full: {result['full_query']}")

    # Critical failures (wrong column used)
    print("\n" + "=" * 80)
    print("COLUMN USAGE ANALYSIS")
    print("=" * 80)

    wrong_column_cases = [r for r in results if not (r.get("abbr_has_col", False) and r.get("full_has_col", False))]
    if wrong_column_cases:
        print(f"\n⚠️  {len(wrong_column_cases)} cases where incorrect DB column was used:")
        for r in wrong_column_cases:
            print(f"   - {r['description']}")
            if not r.get("abbr_has_col", False):
                print(f"     ❌ Abbreviation query didn't use correct column")
            if not r.get("full_has_col", False):
                print(f"     ❌ Full name query didn't use correct column")
    else:
        print("\n✅ All queries used the correct database columns!")

if __name__ == "__main__":
    test_stat_abbreviations()
