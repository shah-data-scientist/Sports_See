import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "sql" / "nba_stats.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

sql = """
SELECT p.name, ps.fg_pct, ps.three_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.fg_pct >= 50 AND ps.three_pct >= 35
ORDER BY ps.fg_pct DESC LIMIT 5
"""

cursor.execute(sql)
results = cursor.fetchall()

print("Top 5 players with FG% >= 50 AND 3P% >= 35 (ordered by FG%):")
for i, row in enumerate(results, 1):
    r = dict(row)
    print(f"{i}. {r['name']}: FG% {r['fg_pct']}, 3P% {r['three_pct']}")

conn.close()
