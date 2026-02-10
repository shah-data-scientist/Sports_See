"""
FILE: check_database_schema.py
STATUS: Active
RESPONSIBILITY: Check database schema for validation
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import sys
import io

# Force UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sqlite3
from src.repositories.nba_database import NBADatabase

db = NBADatabase()
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

# Check player_stats columns
print("=" * 80)
print("PLAYER_STATS TABLE SCHEMA")
print("=" * 80)
cursor.execute("PRAGMA table_info(player_stats)")
cols = cursor.fetchall()
print(f"\nTotal columns: {len(cols)}\n")
for col in cols:
    print(f"  {col[1]:<20} {col[2]:<15} NULL={col[3]==0} DEFAULT={col[4]} PK={col[5]}")

# Check if TOV exists
tov_exists = any(col[1] == 'tov' for col in cols)
print(f"\n{'[+]' if tov_exists else '[-]'} TOV column exists")

# Check ts_pct range
print("\n" + "=" * 80)
print("TS_PCT VALUE ANALYSIS")
print("=" * 80)
cursor.execute("SELECT MIN(ts_pct), MAX(ts_pct), AVG(ts_pct), COUNT(*) FROM player_stats WHERE ts_pct > 0")
min_val, max_val, avg_val, count = cursor.fetchone()
print(f"\nMin: {min_val}")
print(f"Max: {max_val}")
print(f"Avg: {avg_val:.2f}")
print(f"Count: {count}")

if max_val > 100:
    cursor.execute("SELECT p.name, ps.ts_pct, ps.pts, ps.fga, ps.fta FROM player_stats ps JOIN players p ON ps.player_id = p.id WHERE ps.ts_pct > 100 ORDER BY ps.ts_pct DESC LIMIT 10")
    unusual = cursor.fetchall()
    print(f"\n{len(unusual)} players with TS% > 100:")
    for name, ts, pts, fga, fta in unusual:
        print(f"  {name}: TS%={ts}, PTS={pts}, FGA={fga}, FTA={fta}")

# Check players table
print("\n" + "=" * 80)
print("PLAYERS TABLE SCHEMA")
print("=" * 80)
cursor.execute("PRAGMA table_info(players)")
player_cols = cursor.fetchall()
print(f"\nTotal columns: {len(player_cols)}\n")
for col in player_cols:
    print(f"  {col[1]:<20} {col[2]:<15} NULL={col[3]==0} DEFAULT={col[4]} PK={col[5]}")

# Check if team column exists (not team_abbr)
team_exists = any(col[1] == 'team' for col in player_cols)
team_abbr_exists = any(col[1] == 'team_abbr' for col in player_cols)
print(f"\n{'[+]' if team_exists else '[-]'} 'team' column (full name) exists")
print(f"{'[+]' if team_abbr_exists else '[-]'} 'team_abbr' column exists")

conn.close()
