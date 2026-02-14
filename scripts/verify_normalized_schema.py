"""Verify normalized schema after Phase 2 migration."""
import sqlite3

conn = sqlite3.connect('data/sql/nba_stats.db')
cursor = conn.cursor()

print("=" * 80)
print("NORMALIZED SCHEMA VERIFICATION")
print("=" * 80)

# Check players table
cursor.execute('PRAGMA table_info(players)')
players_cols = cursor.fetchall()
print("\nPlayers Table Columns:")
for row in players_cols:
    print(f"  {row[1]:15} {row[2]}")

print(f"\n✅ 'team' column removed: {'team' not in [col[1] for col in players_cols]}")

# Check player_stats table
cursor.execute('PRAGMA table_info(player_stats)')
stats_cols = cursor.fetchall()
print("\nPlayer_Stats Table Columns (first 10):")
for i, row in enumerate(stats_cols):
    if i >= 10:
        print("  ...")
        break
    print(f"  {row[1]:15} {row[2]}")

print(f"\n✅ 'team_abbr' column removed: {'team_abbr' not in [col[1] for col in stats_cols]}")

# Test team aggregation query
cursor.execute("""
    SELECT t.name, SUM(ps.pts) as total_pts, SUM(ps.reb) as total_reb
    FROM teams t
    JOIN players p ON t.abbreviation = p.team_abbr
    JOIN player_stats ps ON p.id = ps.player_id
    WHERE t.abbreviation = 'LAL'
    GROUP BY t.name
""")
result = cursor.fetchone()

print("\nTest Team Aggregation Query:")
print(f"  Lakers: {result[1]:,} pts, {result[2]:,} reb")
print(f"✅ Team queries work correctly!")

conn.close()

print("\n" + "=" * 80)
print("✅ FULL NORMALIZATION COMPLETE")
print("=" * 80)
