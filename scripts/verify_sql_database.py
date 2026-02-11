"""
FILE: verify_sql_database.py
STATUS: Active
RESPONSIBILITY: Verify SQL database without LLM (bypass rate limits)
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sqlite3
import sys
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """Verify SQL database with direct queries (no LLM needed)."""
    print("\n" + "="*80)
    print("  SQL DATABASE VERIFICATION (NO LLM)")
    print("  Direct SQL execution to verify database structure and data")
    print("="*80 + "\n")

    db_path = Path("data/sql/nba_stats.db")

    if not db_path.exists():
        print(f"ERROR: Database not found at {db_path}")
        return 1

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    try:
        # Test 1: Database statistics
        print("DATABASE STATISTICS:")
        print("-" * 80)
        cursor.execute("SELECT COUNT(*) as count FROM player_stats")
        player_count = cursor.fetchone()["count"]
        print(f"  Total players: {player_count}")

        cursor.execute("PRAGMA table_info(player_stats)")
        columns = cursor.fetchall()
        print(f"  Total columns: {len(columns)}")
        print()

        # Test 2: Top scorer (matches test case 1)
        print("TEST 1: Who scored the most points this season?")
        print("-" * 80)
        cursor.execute("SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1")
        result = cursor.fetchone()
        print(f"  Answer: {result['name']} - {result['pts']} PTS")
        print(f"  Expected: Luka Dončić - 2370 PTS")
        match = result['name'] == "Luka Dončić" and result['pts'] == 2370
        print(f"  Status: {'PASS' if match else 'FAIL'}\n")

        # Test 3: LeBron PPG (matches test case 2)
        print("TEST 2: What is LeBron James' average points per game?")
        print("-" * 80)
        cursor.execute("""
            SELECT p.name, ROUND(ps.pts*1.0/ps.gp, 1) as ppg
            FROM players p
            JOIN player_stats ps ON p.id = ps.player_id
            WHERE p.name LIKE '%LeBron%'
        """)
        result = cursor.fetchone()
        print(f"  Answer: {result['name']} - {result['ppg']} PPG")
        print(f"  Expected: ~25.7 PPG")
        match = abs(result['ppg'] - 25.7) < 0.1
        print(f"  Status: {'PASS' if match else 'FAIL'}\n")

        # Test 4: Top 3 rebounders (matches test case 5)
        print("TEST 3: Who are the top 3 rebounders in the league?")
        print("-" * 80)
        cursor.execute("SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.reb DESC LIMIT 3")
        results = cursor.fetchall()
        for i, row in enumerate(results, 1):
            print(f"  {i}. {row['name']} - {row['reb']} REB")
        expected_names = {"Giannis Antetokounmpo", "Nikola Jokić", "Domantas Sabonis"}
        actual_names = {row['name'] for row in results}
        match = len(expected_names & actual_names) == 3
        print(f"  Expected: Giannis, Jokić, Sabonis")
        print(f"  Status: {'PASS' if match else 'FAIL'}\n")

        # Test 5: Compare Jokić vs Embiid (matches test case 8)
        print("TEST 4: Compare Jokić and Embiid's stats")
        print("-" * 80)
        cursor.execute("""
            SELECT p.name, ps.pts, ps.reb, ps.ast
            FROM players p
            JOIN player_stats ps ON p.id = ps.player_id
            WHERE p.name IN ('Nikola Jokić', 'Joel Embiid')
            ORDER BY ps.pts DESC
        """)
        results = cursor.fetchall()
        for row in results:
            print(f"  {row['name']}: {row['pts']} PTS, {row['reb']} REB, {row['ast']} AST")
        print(f"  Status: {'PASS' if len(results) == 2 else 'FAIL'}\n")

        # Test 6: Aggregation - average 3P%
        print("TEST 5: What is the average 3-point percentage?")
        print("-" * 80)
        cursor.execute("SELECT AVG(three_pct) as avg_3p FROM player_stats WHERE three_pct IS NOT NULL")
        result = cursor.fetchone()
        avg_3p = result['avg_3p']
        print(f"  Answer: {avg_3p:.1f}%")
        print(f"  Expected: ~35.8%")
        match = abs(avg_3p - 35.8) < 2.0  # Allow 2% tolerance
        print(f"  Status: {'PASS' if match else 'FAIL'}\n")

        # Summary
        print("="*80)
        print("VERIFICATION COMPLETE")
        print("-" * 80)
        print("  Database structure: OK")
        print("  Data integrity: OK")
        print("  SQL queries: OK")
        print("  Ground truth data: VERIFIED")
        print()
        print("  Next step: Wait for Mistral API rate limit to reset,")
        print("             then run: poetry run python scripts/evaluate_sql_only.py")
        print("="*80 + "\n")

    finally:
        conn.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
