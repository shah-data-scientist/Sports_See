import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "sql" / "nba_stats.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

print("=" * 80)
print("ISSUE 1: tier3_defensive_styles")
print("=" * 80)
sql1 = """
SELECT p.name, ps.stl, ps.blk, (ps.stl + ps.blk) as def_actions 
FROM players p 
JOIN player_stats ps ON p.id = ps.player_id 
ORDER BY (ps.stl + ps.blk) DESC LIMIT 5
"""
print("SQL has LIMIT 5, but ground_truth_data shows only 2 players")
print("\nActual top 5 results:")
cursor = conn.cursor()
cursor.execute(sql1)
for i, row in enumerate(cursor.fetchall(), 1):
    r = dict(row)
    print(f"{i}. {r['name']}: {r['stl']} STL, {r['blk']} BLK ({r['def_actions']} total)")

print("\n" + "=" * 80)
print("ISSUE 2: tier3_dual_threat_strategy")
print("=" * 80)
sql2 = """
SELECT p.name, ps.pts, ps.ast 
FROM players p 
JOIN player_stats ps ON p.id = ps.player_id 
WHERE ps.pts >= 1500 AND ps.ast >= 300 
ORDER BY ps.pts DESC
"""
print("SQL has no LIMIT, returns all matching players")
print("ground_truth_data shows only 2 players (SGA and Jokic)")
print("\nActual results (all players):")
cursor.execute(sql2)
for i, row in enumerate(cursor.fetchall(), 1):
    r = dict(row)
    print(f"{i}. {r['name']}: {r['pts']} PTS, {r['ast']} AST")

print("\n" + "=" * 80)
print("ISSUE 3: tier4_correlation_analysis")
print("=" * 80)
sql3 = """
SELECT p.name, ps.ast, ps.pie 
FROM players p 
JOIN player_stats ps ON p.id = ps.player_id 
WHERE ps.ast > 500 
ORDER BY ps.ast DESC
"""
print("SQL has no LIMIT, returns all players with 500+ assists")
print("ground_truth_data shows only 1 player (Trae Young)")
print("\nActual results (all players):")
cursor.execute(sql3)
for i, row in enumerate(cursor.fetchall(), 1):
    r = dict(row)
    print(f"{i}. {r['name']}: {r['ast']} AST, PIE {r['pie']}")

conn.close()
