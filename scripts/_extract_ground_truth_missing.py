"""
FILE: _extract_ground_truth_missing.py
STATUS: Experimental
RESPONSIBILITY: Extract ground truth from NBA database for test cases missing data
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Extract ground truth from NBA database for the 14 test cases missing ground truth data.
"""
import io
import sqlite3
import sys
import json

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB_PATH = "data/sql/nba_stats.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

results = {}

# ── 1. How many players on the Lakers roster?
c.execute("SELECT COUNT(*) as player_count FROM players WHERE team_abbr = 'LAL'")
row = c.fetchone()
results["lakers_count"] = {"player_count": row["player_count"]}
print(f"1. Lakers roster count: {dict(row)}")

# ── 2. List all players on the Golden State Warriors
c.execute("SELECT name FROM players WHERE team_abbr = 'GSW' ORDER BY name")
rows = c.fetchall()
gsw_players = [dict(r)["name"] for r in rows]
results["gsw_players"] = gsw_players
print(f"2. GSW players ({len(gsw_players)}): {gsw_players[:5]}...")

# ── 3. What is the average player age in the NBA?
c.execute("SELECT ROUND(AVG(age), 2) as avg_age FROM players WHERE age IS NOT NULL")
row = c.fetchone()
results["avg_age"] = {"avg_age": row["avg_age"]}
print(f"3. Average age: {dict(row)}")

# ── 4. Which players score more points per game than the league average?
c.execute("""
    SELECT p.name, ROUND(ps.pts*1.0/ps.gp, 1) as ppg
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE ps.gp > 0 AND ps.pts*1.0/ps.gp > (SELECT AVG(pts*1.0/gp) FROM player_stats WHERE gp > 0)
    ORDER BY ppg DESC LIMIT 5
""")
rows = c.fetchall()
results["above_avg_ppg"] = [dict(r) for r in rows]
print(f"4. Above-avg PPG (top 5): {results['above_avg_ppg']}")

# ── 5. Which players have better than 50% FG AND 35%+ from three?
c.execute("""
    SELECT p.name, ps.fg_pct, ps.three_pct
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE ps.fg_pct >= 50 AND ps.three_pct >= 35
    ORDER BY ps.fg_pct DESC LIMIT 10
""")
rows = c.fetchall()
results["fg50_3p35"] = [dict(r) for r in rows]
print(f"5. FG>50% AND 3P>35% (top 10): {json.dumps(results['fg50_3p35'], indent=2)}")

# ── 6. Which players have the best assist-to-turnover ratio (300+ assists)?
c.execute("""
    SELECT p.name, ps.ast, ps.tov, ROUND(ps.ast*1.0/ps.tov, 2) as ast_to_ratio
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE ps.ast >= 300 AND ps.tov > 0
    ORDER BY (ps.ast*1.0/ps.tov) DESC LIMIT 5
""")
rows = c.fetchall()
results["best_ast_to"] = [dict(r) for r in rows]
print(f"6. Best AST/TO (300+ AST): {json.dumps(results['best_ast_to'], indent=2)}")

# ── 7. What percentage of players have TS% above 60%?
c.execute("""
    SELECT
        ROUND(100.0 * COUNT(CASE WHEN ts_pct > 60 THEN 1 END) / COUNT(*), 1) as pct_above_60,
        COUNT(CASE WHEN ts_pct > 60 THEN 1 END) as count_above,
        COUNT(*) as total
    FROM player_stats WHERE ts_pct IS NOT NULL
""")
row = c.fetchone()
results["ts_pct_above_60"] = dict(row)
print(f"7. TS% > 60%: {results['ts_pct_above_60']}")

# ── 8. Most efficient scorers (50+ games, top 10 by FG%)
c.execute("""
    SELECT p.name, ps.efg_pct, ps.gp
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE ps.gp >= 50 AND ps.efg_pct IS NOT NULL
    ORDER BY ps.efg_pct DESC LIMIT 5
""")
rows = c.fetchall()
results["efficient_scorers_50gp"] = [dict(r) for r in rows]
print(f"8. Efficient scorers (50+ GP): {json.dumps(results['efficient_scorers_50gp'], indent=2)}")

# ── 9. Top 3 PPG among those with 70+ games
c.execute("""
    SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE ps.gp >= 70
    ORDER BY (ps.pts*1.0/ps.gp) DESC LIMIT 3
""")
rows = c.fetchall()
results["top3_ppg_70gp"] = [dict(r) for r in rows]
print(f"9. Top 3 PPG (70+ GP): {json.dumps(results['top3_ppg_70gp'], indent=2)}")

# ── 10. Most versatile: 1000+ PTS, 400+ REB, 200+ AST (top 5)
c.execute("""
    SELECT p.name, ps.pts, ps.reb, ps.ast
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE ps.pts >= 1000 AND ps.reb >= 400 AND ps.ast >= 200
    ORDER BY (ps.pts + ps.reb + ps.ast) DESC LIMIT 5
""")
rows = c.fetchall()
results["versatile_1000_400_200"] = [dict(r) for r in rows]
print(f"10. Versatile (top 5): {json.dumps(results['versatile_1000_400_200'], indent=2)}")

# ── 11. Maximum blocks by any player
c.execute("""
    SELECT p.name, ps.blk as max_blocks
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    ORDER BY ps.blk DESC LIMIT 1
""")
row = c.fetchone()
results["max_blocks"] = dict(row)
print(f"11. Max blocks: {results['max_blocks']}")

# ── 12. Assist leaders (top 5)
c.execute("""
    SELECT p.name, ps.ast
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    ORDER BY ps.ast DESC LIMIT 5
""")
rows = c.fetchall()
results["assist_leaders"] = [dict(r) for r in rows]
print(f"12. Assist leaders: {json.dumps(results['assist_leaders'], indent=2)}")

# ── 13. Compare LeBron to Curry (follow-up context)
c.execute("""
    SELECT p.name, ps.pts, ps.reb, ps.ast
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE p.name IN ('LeBron James', 'Stephen Curry')
    ORDER BY ps.pts DESC
""")
rows = c.fetchall()
results["lebron_vs_curry"] = [dict(r) for r in rows]
print(f"13. LeBron vs Curry: {json.dumps(results['lebron_vs_curry'], indent=2)}")

# ── 14. Which assist leader plays for the Hawks?
c.execute("""
    SELECT p.name, p.team_abbr, ps.ast
    FROM players p JOIN player_stats ps ON p.id = ps.player_id
    WHERE p.team_abbr = 'ATL'
    ORDER BY ps.ast DESC LIMIT 1
""")
row = c.fetchone()
results["hawks_assist_leader"] = dict(row)
print(f"14. Hawks assist leader: {results['hawks_assist_leader']}")

conn.close()

# Save all results
with open("evaluation_results/_ground_truth_missing_14.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\nAll results saved to evaluation_results/_ground_truth_missing_14.json")
