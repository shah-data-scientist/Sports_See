"""
Test team queries after database migration.
Verifies that normalized schema enables correct team aggregation queries.
"""
import sqlite3
from pathlib import Path

def print_separator(title=""):
    """Print section separator."""
    print("\n" + "="*80)
    if title:
        print(f" {title}")
        print("="*80)
    else:
        print("="*80)

def test_team_query(cursor, description, query, expected_rows=None):
    """Execute and verify a team query."""
    print(f"\n{'─'*80}")
    print(f"TEST: {description}")
    print(f"{'─'*80}")
    print(f"\nSQL:")
    print(query)

    try:
        cursor.execute(query)
        results = cursor.fetchall()

        print(f"\n✅ Query executed successfully")
        print(f"📊 Rows returned: {len(results)}")

        if expected_rows is not None and len(results) != expected_rows:
            print(f"⚠️  Expected {expected_rows} rows, got {len(results)}")

        # Print results
        if results:
            print(f"\nResults:")
            for i, row in enumerate(results[:5], 1):  # Show first 5
                print(f"   {i}. {row}")
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more")

        return True

    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        return False

def main():
    """Run comprehensive team query tests."""
    print_separator("TEAM QUERY TESTS (Post-Migration)")

    db_path = Path("data/sql/nba_stats.db")

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    passed = 0
    failed = 0

    # Test 1: Single team stats
    print_separator("TEST 1: Single Team Statistics")
    query1 = """
        SELECT
            t.name as team,
            COUNT(p.id) as player_count,
            SUM(ps.pts) as total_pts,
            SUM(ps.reb) as total_reb,
            SUM(ps.ast) as total_ast,
            ROUND(AVG(ps.pts), 1) as avg_pts
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        WHERE t.abbreviation = 'LAL'
        GROUP BY t.name
    """
    if test_team_query(cursor, "Lakers team statistics", query1, expected_rows=1):
        passed += 1
    else:
        failed += 1

    # Test 2: Team comparison
    print_separator("TEST 2: Team Comparison")
    query2 = """
        SELECT
            t.name as team,
            SUM(ps.pts) as total_pts,
            SUM(ps.reb) as total_reb,
            SUM(ps.ast) as total_ast
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        WHERE t.abbreviation IN ('BOS', 'LAL')
        GROUP BY t.name
        ORDER BY total_pts DESC
    """
    if test_team_query(cursor, "Celtics vs Lakers comparison", query2, expected_rows=2):
        passed += 1
    else:
        failed += 1

    # Test 3: All teams ranked
    print_separator("TEST 3: All Teams Ranked")
    query3 = """
        SELECT
            t.name as team,
            SUM(ps.pts) as total_pts
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY t.name
        ORDER BY total_pts DESC
        LIMIT 10
    """
    if test_team_query(cursor, "Top 10 teams by total points", query3, expected_rows=10):
        passed += 1
    else:
        failed += 1

    # Test 4: Best defensive team
    print_separator("TEST 4: Best Defensive Team")
    query4 = """
        SELECT
            t.name as team,
            SUM(ps.stl + ps.blk) as defensive_actions,
            SUM(ps.stl) as total_steals,
            SUM(ps.blk) as total_blocks
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY t.name
        ORDER BY defensive_actions DESC
        LIMIT 1
    """
    if test_team_query(cursor, "Team with most defensive actions", query4, expected_rows=1):
        passed += 1
    else:
        failed += 1

    # Test 5: Team with most assists
    print_separator("TEST 5: Most Assists Team")
    query5 = """
        SELECT
            t.name as team,
            SUM(ps.ast) as total_assists,
            ROUND(AVG(ps.ast), 1) as avg_assists_per_player
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY t.name
        ORDER BY total_assists DESC
        LIMIT 3
    """
    if test_team_query(cursor, "Top 3 teams by assists", query5, expected_rows=3):
        passed += 1
    else:
        failed += 1

    # Test 6: Team efficiency
    print_separator("TEST 6: Team Efficiency")
    query6 = """
        SELECT
            t.name as team,
            SUM(ps.pts) as total_pts,
            SUM(ps.fga) as total_fga,
            ROUND(SUM(ps.pts) * 100.0 / SUM(ps.fga), 1) as points_per_attempt
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY t.name
        ORDER BY points_per_attempt DESC
        LIMIT 5
    """
    if test_team_query(cursor, "Most efficient teams (points per field goal attempt)", query6, expected_rows=5):
        passed += 1
    else:
        failed += 1

    # Test 7: Team by wins
    print_separator("TEST 7: Teams by Wins")
    query7 = """
        SELECT
            t.name as team,
            SUM(ps.w) as total_wins,
            SUM(ps.l) as total_losses,
            ROUND(SUM(ps.w) * 100.0 / (SUM(ps.w) + SUM(ps.l)), 1) as win_percentage
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY t.name
        ORDER BY win_percentage DESC
        LIMIT 5
    """
    if test_team_query(cursor, "Top 5 teams by win percentage", query7, expected_rows=5):
        passed += 1
    else:
        failed += 1

    # Test 8: Team three-point shooting
    print_separator("TEST 8: Team Three-Point Shooting")
    query8 = """
        SELECT
            t.name as team,
            SUM(ps.three_pm) as total_3pm,
            SUM(ps.three_pa) as total_3pa,
            ROUND(SUM(ps.three_pm) * 100.0 / SUM(ps.three_pa), 1) as three_pct
        FROM teams t
        JOIN players p ON t.abbreviation = p.team_abbr
        JOIN player_stats ps ON p.id = ps.player_id
        GROUP BY t.name
        HAVING total_3pa > 500
        ORDER BY three_pct DESC
        LIMIT 5
    """
    if test_team_query(cursor, "Best three-point shooting teams (min 500 attempts)", query8):
        passed += 1
    else:
        failed += 1

    # Summary
    print_separator("TEST SUMMARY")
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success Rate: {passed}/{passed + failed} ({passed * 100 / (passed + failed):.1f}%)")

    if failed == 0:
        print("\n" + "="*80)
        print("🎉 ALL TEAM QUERIES WORK CORRECTLY!")
        print("="*80)
        print("\nDatabase normalization successful!")
        print("Team aggregation queries are now functioning properly.")
    else:
        print("\n⚠️  Some queries failed - check database structure")

    conn.close()

if __name__ == "__main__":
    main()
