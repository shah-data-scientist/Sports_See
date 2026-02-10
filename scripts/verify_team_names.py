"""
FILE: verify_team_names.py
STATUS: Active
RESPONSIBILITY: Verify team names are populated correctly in players table
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import sys
import io
import sqlite3

# Force UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.repositories.nba_database import NBADatabase

db = NBADatabase()
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

print("=" * 80)
print("VERIFYING TEAM NAMES IN PLAYERS TABLE")
print("=" * 80)

# Sample players
cursor.execute("SELECT name, team, team_abbr FROM players LIMIT 15")
rows = cursor.fetchall()

print("\nSample players with team names:")
print("-" * 80)
print(f"{'Player':<30} | {'Team':<30} | {'Abbr'}")
print("-" * 80)
for name, team, abbr in rows:
    print(f"{name:<30} | {team:<30} | {abbr}")

# Check for any abbreviations that weren't mapped
cursor.execute("SELECT DISTINCT team FROM players ORDER BY team")
all_teams = cursor.fetchall()

print("\n" + "=" * 80)
print(f"Total unique teams: {len(all_teams)}")
print("=" * 80)
for (team,) in all_teams:
    print(f"  - {team}")

# Check if any team names are still abbreviations (fallback case)
cursor.execute("SELECT COUNT(*) FROM players WHERE length(team) <= 5")
count_abbr_only = cursor.fetchone()[0]

print("\n" + "=" * 80)
if count_abbr_only == 0:
    print("[+] SUCCESS: All players have full team names (no abbreviations)")
else:
    print(f"[-] WARNING: {count_abbr_only} players still have abbreviations as team names")
print("=" * 80)

conn.close()
