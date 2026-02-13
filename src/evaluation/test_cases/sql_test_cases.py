"""
FILE: sql_test_cases.py
STATUS: Active
RESPONSIBILITY: SQL evaluation test cases (80 curated, deduplicated, gap-filled cases)
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu
"""

from src.evaluation.models.sql_models import QueryType, SQLEvaluationTestCase

# ============================================================================
# SIMPLE SQL QUERIES (13 cases)
# Single-table queries with JOIN, straightforward retrieval
# Reduced from 17 → 12, then +1 win/loss query = 13
# ============================================================================

SIMPLE_SQL_CASES = [
    # Top N queries (5 cases - kept most diverse)
    SQLEvaluationTestCase(
        question="Who scored the most points this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander scored the most points with 2485 PTS.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="Who are the top 3 rebounders in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.reb DESC LIMIT 3",
        ground_truth_answer="Top 3 rebounders: Ivica Zubac (1008), Domantas Sabonis (973), Karl-Anthony Towns (922).",
        ground_truth_data=[
            {"name": "Ivica Zubac", "reb": 1008},
            {"name": "Domantas Sabonis", "reb": 973},
            {"name": "Karl-Anthony Towns", "reb": 922}
        ],
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="Who are the top 5 players in steals?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.stl FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.stl DESC LIMIT 5",
        ground_truth_answer="Top 5 steals: Dyson Daniels (228), Shai Gilgeous-Alexander (129), Nikola Jokić (126), Kris Dunn (126), Cason Wallace (122).",
        ground_truth_data=[
            {"name": "Dyson Daniels", "stl": 228},
            {"name": "Shai Gilgeous-Alexander", "stl": 129},
            {"name": "Nikola Jokić", "stl": 126},
            {"name": "Kris Dunn", "stl": 126},
            {"name": "Cason Wallace", "stl": 122},
        ],
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="Who has the best free throw percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ft_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ft_pct IS NOT NULL ORDER BY ps.ft_pct DESC LIMIT 1",
        ground_truth_answer="Sam Hauser has the best free throw percentage at 100%.",
        ground_truth_data={"name": "Sam Hauser", "ft_pct": 100.0},
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="Who has the highest true shooting percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ts_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ts_pct IS NOT NULL AND ps.gp > 20 ORDER BY ps.ts_pct DESC LIMIT 1",
        ground_truth_answer="Kai Jones has the highest true shooting percentage at 80.4%.",
        ground_truth_data={"name": "Kai Jones", "ts_pct": 80.4},
        category="simple_sql_top_n",
    ),

    # Individual player stat lookups (4 cases - kept diverse stats)
    SQLEvaluationTestCase(
        question="What is LeBron James' average points per game?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ROUND(ps.pts*1.0/ps.gp, 1) as ppg FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%LeBron%'",
        ground_truth_answer="LeBron James averages 24.4 points per game.",
        ground_truth_data={"name": "LeBron James", "ppg": 24.4},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="What is Stephen Curry's 3-point percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Stephen Curry%'",
        ground_truth_answer="Stephen Curry's 3-point percentage is 39.7%.",
        ground_truth_data={"name": "Stephen Curry", "three_pct": 39.7},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="What is Nikola Jokić's total rebounds?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Jokić%'",
        ground_truth_answer="Nikola Jokić has 889 rebounds.",
        ground_truth_data={"name": "Nikola Jokić", "reb": 889},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="How many assists did Chris Paul record?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Chris Paul%'",
        ground_truth_answer="Chris Paul recorded 607 assists.",
        ground_truth_data={"name": "Chris Paul", "ast": 607},
        category="simple_sql_player_stats",
    ),

    # Team roster queries (2 cases)
    SQLEvaluationTestCase(
        question="How many players on the Lakers roster?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM players WHERE team_abbr = 'LAL'",
        ground_truth_answer="There are 20 players on the Lakers roster.",
        ground_truth_data={"player_count": 20},
        category="simple_sql_team_roster",
    ),
    SQLEvaluationTestCase(
        question="List all players on the Golden State Warriors.",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name FROM players WHERE team_abbr = 'GSW' ORDER BY name",
        ground_truth_answer="Warriors roster: Brandin Podziemski, Braxton Key, Buddy Hield, Draymond Green, Gary Payton II, Gui Santos, Jackson Rowe, Jimmy Butler III, Jonathan Kuminga, Kevon Looney, Kevin Knox II, Moses Moody, Pat Spencer, Quinten Post, Stephen Curry, Trayce Jackson-Davis, Yuri Collins (17 players).",
        ground_truth_data=[
            {"name": "Brandin Podziemski"}, {"name": "Braxton Key"}, {"name": "Buddy Hield"}, {"name": "Draymond Green"},
            {"name": "Gary Payton II"}, {"name": "Gui Santos"}, {"name": "Jackson Rowe"}, {"name": "Jimmy Butler III"},
            {"name": "Jonathan Kuminga"}, {"name": "Kevin Knox II"}, {"name": "Kevon Looney"}, {"name": "Moses Moody"},
            {"name": "Pat Spencer"}, {"name": "Quinten Post"}, {"name": "Stephen Curry"}, {"name": "Trayce Jackson-Davis"},
            {"name": "Yuri Collins"}
        ],
        category="simple_sql_team_roster",
    ),

    # Win/loss record query (1 case)
    SQLEvaluationTestCase(
        question="Which player has the most wins this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.w FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.w DESC LIMIT 1",
        ground_truth_answer="Jarrett Allen has the most wins with 64.",
        ground_truth_data={"name": "Jarrett Allen", "w": 64},
        category="simple_sql_top_n",
    ),

    # League average (1 case)
    SQLEvaluationTestCase(
        question="What is the average player age in the NBA?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(age) as avg_age FROM players WHERE age IS NOT NULL",
        ground_truth_answer="The average player age in the NBA is 26.15 years.",
        ground_truth_data={"avg_age": 26.15},
        category="aggregation_sql_league",
    ),
]

# ============================================================================
# COMPARISON SQL QUERIES (7 cases)
# Multi-player comparisons with JOIN, WHERE IN clauses
# Reduced from 14 → 8 → 7 by removing similar comparisons (top 2 TS% dup)
# ============================================================================

COMPARISON_SQL_CASES = [
    # Two-player direct comparisons (5 cases - kept most diverse stat types)
    SQLEvaluationTestCase(
        question="Compare Jokić and Embiid's stats",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Joel Embiid')",
        ground_truth_answer=(
            "Nikola Jokić: 2072 PTS, 889 REB, 714 AST. "
            "Joel Embiid: 452 PTS, 156 REB, 86 AST."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714},
            {"name": "Joel Embiid", "pts": 452, "reb": 156, "ast": 86},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who shoots better from 3, Curry or Lillard?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Stephen Curry', 'Damian Lillard') ORDER BY ps.three_pct DESC",
        ground_truth_answer="Stephen Curry shoots better (39.7%) than Damian Lillard (37.6%).",
        ground_truth_data=[
            {"name": "Stephen Curry", "three_pct": 39.7},
            {"name": "Damian Lillard", "three_pct": 37.6},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who is more efficient goal maker, Jokić or Embiid?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.fg_pct, ps.efg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Joel Embiid') ORDER BY ps.fg_pct DESC",
        ground_truth_answer="Nikola Jokić is more efficient: FG% 57.6, EFG% 62.7 vs Joel Embiid FG% 44.4, EFG% 48.1.",
        ground_truth_data=[
            {"name": "Nikola Jokić", "fg_pct": 57.6, "efg_pct": 62.7},
            {"name": "Joel Embiid", "fg_pct": 44.4, "efg_pct": 48.1},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare Jayson Tatum and Kevin Durant scoring efficiency",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts, ps.fg_pct, ps.efg_pct, ps.ts_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Jayson Tatum', 'Kevin Durant') ORDER BY ps.pts DESC",
        ground_truth_answer="Jayson Tatum: 1930 PTS, 45.2% FG, 53.7% EFG, 58.2% TS. Kevin Durant: 1649 PTS, 52.7% FG, 59.8% EFG, 64.2% TS.",
        ground_truth_data=[
            {"name": "Jayson Tatum", "pts": 1930, "fg_pct": 45.2, "efg_pct": 53.7, "ts_pct": 58.2},
            {"name": "Kevin Durant", "pts": 1649, "fg_pct": 52.7, "efg_pct": 59.8, "ts_pct": 64.2},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who has more assists, James Harden or Chris Paul?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Harden%' OR p.name LIKE '%Chris Paul%' ORDER BY ps.ast DESC LIMIT 2",
        ground_truth_answer="James Harden has more assists (687) than Chris Paul (607).",
        ground_truth_data=[
            {"name": "James Harden", "ast": 687},
            {"name": "Chris Paul", "ast": 607},
        ],
        category="comparison_sql_players",
    ),

    # Top N comparisons (3 cases)
    SQLEvaluationTestCase(
        question="Compare the top 2 steals leaders",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.stl FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.stl DESC LIMIT 2",
        ground_truth_answer="Top 2 steals: Dyson Daniels (228), Shai Gilgeous-Alexander (129).",
        ground_truth_data=[
            {"name": "Dyson Daniels", "stl": 228},
            {"name": "Shai Gilgeous-Alexander", "stl": 129},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare blocks between the top 2 leaders",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.blk FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.blk DESC LIMIT 2",
        ground_truth_answer="Victor Wembanyama (175 BLK) leads, followed by Brook Lopez (152 BLK).",
        ground_truth_data=[
            {"name": "Victor Wembanyama", "blk": 175},
            {"name": "Brook Lopez", "blk": 152},
        ],
        category="comparison_sql_players",
    ),
]

# ============================================================================
# AGGREGATION SQL QUERIES (10 cases)
# League-wide stats, AVG/COUNT/MAX, calculations
# Reduced from 17 → 10 by consolidating similar aggregations
# ============================================================================

AGGREGATION_SQL_CASES = [
    # League averages (4 cases - diverse metrics)
    SQLEvaluationTestCase(
        question="What is the average 3-point percentage for all players?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(three_pct) as avg_3p_pct FROM player_stats WHERE three_pct IS NOT NULL",
        ground_truth_answer="The average 3-point percentage across all players is 29.9%.",
        ground_truth_data={"avg_3p_pct": 29.9},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="What is the average field goal percentage in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT ROUND(AVG(fg_pct), 1) as avg_fg_pct FROM player_stats WHERE fg_pct IS NOT NULL",
        ground_truth_answer="The average field goal percentage is 44.6%.",
        ground_truth_data={"avg_fg_pct": 44.6},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="What is the average PIE in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT ROUND(AVG(pie), 1) as avg_pie FROM player_stats WHERE pie IS NOT NULL",
        ground_truth_answer="The average PIE is 8.9.",
        ground_truth_data={"avg_pie": 8.9},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="What is the average rebounds per game league-wide?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(CAST(reb AS REAL) / gp) as avg_rpg FROM player_stats WHERE gp > 0",
        ground_truth_answer="The average rebounds per game is 3.60 RPG.",
        ground_truth_data={"avg_rpg": 3.60},
        category="aggregation_sql_league",
    ),

    # Count queries (4 cases - diverse thresholds)
    SQLEvaluationTestCase(
        question="How many players scored over 1000 points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts > 1000",
        ground_truth_answer="84 players scored over 1000 points this season.",
        ground_truth_data={"player_count": 84},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="How many players have a true shooting percentage over 60%?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE ts_pct > 60 AND gp >= 20",
        ground_truth_answer="118 players (with 20+ games played) have a true shooting percentage over 60%.",
        ground_truth_data={"player_count": 118},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="How many players have more than 500 assists?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as count FROM player_stats WHERE ast > 500",
        ground_truth_answer="10 players have more than 500 assists.",
        ground_truth_data={"count": 10},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="How many players played more than 50 games?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as count FROM player_stats WHERE gp > 50",
        ground_truth_answer="282 players played more than 50 games.",
        ground_truth_data={"count": 282},
        category="aggregation_sql_count",
    ),

    # Min/Max queries (2 cases)
    SQLEvaluationTestCase(
        question="What is the highest PIE in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT MAX(pie) as max_pie FROM player_stats",
        ground_truth_answer="The highest PIE is 40.0.",
        ground_truth_data={"max_pie": 40.0},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="What is the maximum number of blocks recorded by any player?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT MAX(blk) as max_blocks FROM player_stats",
        ground_truth_answer="Victor Wembanyama has the maximum blocks with 175.",
        ground_truth_data={"max_blocks": 175},
        category="aggregation_sql_league",
    ),

    # Team-specific aggregation (1 case)
    SQLEvaluationTestCase(
        question="What is the average field goal percentage for the Lakers?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT ROUND(AVG(ps.fg_pct), 1) as avg_fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.team_abbr = 'LAL' AND ps.fg_pct IS NOT NULL",
        ground_truth_answer="The average field goal percentage for the Lakers is 44.6%.",
        ground_truth_data={"avg_fg_pct": 44.6},
        category="aggregation_sql_team",
    ),
]

# ============================================================================
# COMPLEX SQL QUERIES (14 cases)
# Subqueries, multiple joins, calculated fields, advanced filtering
# 10 original + 1 GROUP BY + 3 new (team comparison, HAVING, BETWEEN)
# ============================================================================

COMPLEX_SQL_CASES = [
    # Subquery comparisons (1 case)
    SQLEvaluationTestCase(
        question="Which players score more points per game than the league average?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 0 AND ps.pts*1.0/ps.gp > (SELECT AVG(pts*1.0/gp) FROM player_stats WHERE gp > 0) "
            "ORDER BY ppg DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 above-avg PPG: Shai Gilgeous-Alexander (32.7), Giannis Antetokounmpo (30.4), Nikola Jokić (29.6), Luka Dončić (28.2), Anthony Edwards (27.6).",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "ppg": 32.7},
            {"name": "Giannis Antetokounmpo", "ppg": 30.4},
            {"name": "Nikola Jokić", "ppg": 29.6},
            {"name": "Luka Dončić", "ppg": 28.2},
            {"name": "Anthony Edwards", "ppg": 27.6},
        ],
        category="complex_sql_subquery",
    ),

    # Multiple conditions (3 cases)
    SQLEvaluationTestCase(
        question="Find players with both high scoring (1500+ points) and high assists (300+ assists)",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts >= 1500 AND ps.ast >= 300 "
            "ORDER BY ps.pts DESC LIMIT 4"
        ),
        ground_truth_answer="Top 4 dual-threat players: Shai Gilgeous-Alexander (2485 PTS, 486 AST), Anthony Edwards (2180 PTS, 356 AST), Nikola Jokić (2072 PTS, 714 AST), Giannis Antetokounmpo (2037 PTS, 436 AST).",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "ast": 486},
            {"name": "Anthony Edwards", "pts": 2180, "ast": 356},
            {"name": "Nikola Jokić", "pts": 2072, "ast": 714},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "ast": 436},
        ],
        category="complex_sql_multiple_conditions",
    ),
    SQLEvaluationTestCase(
        question="Which players have better than 50% field goal percentage AND 35%+ from three?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.fg_pct, ps.three_pct FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.fg_pct >= 50 AND ps.three_pct >= 35 AND ps.gp >= 50 "
            "ORDER BY ps.fg_pct DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 with FG>50% AND 3P>35% (50+ games): Dwight Powell (68.9 FG%, 40.0 3P%), Drew Eubanks (59.3 FG%, 50.0 3P%), Domantas Sabonis (59.0 FG%, 41.7 3P%), Christian Braun (58.0 FG%, 39.7 3P%), Nikola Jokić (57.6 FG%, 41.7 3P%).",
        ground_truth_data=[
            {"name": "Dwight Powell", "fg_pct": 68.9, "three_pct": 40.0},
            {"name": "Drew Eubanks", "fg_pct": 59.3, "three_pct": 50.0},
            {"name": "Domantas Sabonis", "fg_pct": 59.0, "three_pct": 41.7},
            {"name": "Christian Braun", "fg_pct": 58.0, "three_pct": 39.7},
            {"name": "Nikola Jokić", "fg_pct": 57.6, "three_pct": 41.7},
        ],
        category="complex_sql_multiple_conditions",
    ),
    SQLEvaluationTestCase(
        question="Find players averaging double-digits in points, rebounds, and assists",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, "
            "ROUND(ps.pts*1.0/ps.gp, 1) as ppg, "
            "ROUND(ps.reb*1.0/ps.gp, 1) as rpg, "
            "ROUND(ps.ast*1.0/ps.gp, 1) as apg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 0 "
            "AND ps.pts*1.0/ps.gp >= 10 "
            "AND ps.reb*1.0/ps.gp >= 10 "
            "AND ps.ast*1.0/ps.gp >= 10"
        ),
        ground_truth_answer="Rare players averaging 10+ PPG, RPG, and APG (triple-double averages).",
        ground_truth_data=[
            {"name": "Nikola Jokić", "ppg": 29.6, "rpg": 12.7, "apg": 10.2},
        ],
        category="complex_sql_calculated_triple_condition",
    ),

    # Calculated fields (3 cases)
    SQLEvaluationTestCase(
        question="Find the top 5 players by total defensive actions (steals + blocks)",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.stl, ps.blk, (ps.stl + ps.blk) as defensive_actions "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY (ps.stl + ps.blk) DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 defenders: Dyson Daniels (281), Victor Wembanyama (226), Shai Gilgeous-Alexander (205), Myles Turner (202), Jaren Jackson Jr. (200).",
        ground_truth_data=[
            {"name": "Dyson Daniels", "stl": 228, "blk": 53, "defensive_actions": 281},
            {"name": "Victor Wembanyama", "stl": 51, "blk": 175, "defensive_actions": 226},
            {"name": "Shai Gilgeous-Alexander", "stl": 129, "blk": 76, "defensive_actions": 205},
            {"name": "Myles Turner", "stl": 58, "blk": 144, "defensive_actions": 202},
            {"name": "Jaren Jackson Jr,", "stl": 89, "blk": 111, "defensive_actions": 200},
        ],
        category="complex_sql_calculated_field",
    ),
    SQLEvaluationTestCase(
        question="Which players have the best assist-to-turnover ratio among those with 300+ assists?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.ast, ps.tov, ROUND(ps.ast*1.0/ps.tov, 2) as ast_to_ratio "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.ast >= 300 AND ps.tov > 0 "
            "ORDER BY (ps.ast*1.0/ps.tov) DESC LIMIT 5"
        ),
        ground_truth_answer="Best AST/TO (300+ AST): Tyrese Haliburton (5.74), Tyus Jones (4.82), Chris Paul (4.63), Mike Conley (4.10), Fred VanVleet (3.73).",
        ground_truth_data=[
            {"name": "Tyrese Haliburton", "ast": 672, "tov": 117, "ast_to_ratio": 5.74},
            {"name": "Tyus Jones", "ast": 429, "tov": 89, "ast_to_ratio": 4.82},
            {"name": "Chris Paul", "ast": 607, "tov": 131, "ast_to_ratio": 4.63},
            {"name": "Mike Conley", "ast": 320, "tov": 78, "ast_to_ratio": 4.10},
            {"name": "Fred VanVleet", "ast": 336, "tov": 90, "ast_to_ratio": 3.73},
        ],
        category="complex_sql_ratio_calculation",
    ),
    SQLEvaluationTestCase(
        question="What percentage of players have a true shooting percentage above 60%?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT "
            "ROUND(100.0 * COUNT(CASE WHEN ts_pct > 60 THEN 1 END) / COUNT(*), 1) as pct_above_60 "
            "FROM player_stats WHERE ts_pct IS NOT NULL AND gp >= 20"
        ),
        ground_truth_answer="25.9% of players (118 out of 456 with 20+ games) have a true shooting percentage above 60%.",
        ground_truth_data={"pct_above_60": 25.9},
        category="complex_sql_percentage_calculation",
    ),

    # Advanced filtering (3 cases)
    SQLEvaluationTestCase(
        question="Who are the most efficient scorers among players with 50+ games played?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.efg_pct, ps.pts, ps.gp FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp >= 50 AND ps.efg_pct IS NOT NULL "
            "ORDER BY ps.efg_pct DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 most efficient (EFG%, 50+ GP): Jaxson Hayes (72.2), Jarrett Allen (70.6), Dwight Powell (70.5), Adem Bona (70.3), Daniel Gafford (70.2).",
        ground_truth_data=[
            {"name": "Jaxson Hayes", "efg_pct": 72.2},
            {"name": "Jarrett Allen", "efg_pct": 70.6},
            {"name": "Dwight Powell", "efg_pct": 70.5},
            {"name": "Adem Bona", "efg_pct": 70.3},
            {"name": "Daniel Gafford", "efg_pct": 70.2},
        ],
        category="complex_sql_filtering",
    ),
    SQLEvaluationTestCase(
        question="Who are the top 3 players in points per game among those who played at least 70 games?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp >= 70 "
            "ORDER BY (ps.pts*1.0/ps.gp) DESC LIMIT 3"
        ),
        ground_truth_answer="Top 3 PPG (70+ GP): Shai Gilgeous-Alexander (32.7), Nikola Jokić (29.6), Anthony Edwards (27.6).",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "gp": 76, "ppg": 32.7},
            {"name": "Nikola Jokić", "pts": 2072, "gp": 70, "ppg": 29.6},
            {"name": "Anthony Edwards", "pts": 2180, "gp": 79, "ppg": 27.6},
        ],
        category="complex_sql_filtering_calculation",
    ),
    SQLEvaluationTestCase(
        question="Find the most versatile players with at least 1000 points, 400 rebounds, and 200 assists",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts >= 1000 AND ps.reb >= 400 AND ps.ast >= 200 "
            "ORDER BY (ps.pts + ps.reb + ps.ast) DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 versatile (1000+ PTS, 400+ REB, 200+ AST): Nikola Jokić (2072/889/714), Giannis Antetokounmpo (2037/797/436), Jayson Tatum (1930/626/432), Anthony Edwards (2180/450/356), James Harden (1801/458/687).",
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "reb": 797, "ast": 436},
            {"name": "Jayson Tatum", "pts": 1930, "reb": 626, "ast": 432},
            {"name": "Anthony Edwards", "pts": 2180, "reb": 450, "ast": 356},
            {"name": "James Harden", "pts": 1801, "reb": 458, "ast": 687},
        ],
        category="complex_sql_versatility",
    ),

    # GROUP BY query (1 case)
    SQLEvaluationTestCase(
        question="Which team has the highest average points per player?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.team_abbr, ROUND(AVG(ps.pts), 1) as avg_pts "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "GROUP BY p.team_abbr ORDER BY avg_pts DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 teams by avg points per player: DEN (582.3), SAS (566.6), CLE (565.6), BOS (561.8), OKC (548.9).",
        ground_truth_data=[
            {"team_abbr": "DEN", "avg_pts": 582.3},
            {"team_abbr": "SAS", "avg_pts": 566.6},
            {"team_abbr": "CLE", "avg_pts": 565.6},
            {"team_abbr": "BOS", "avg_pts": 561.8},
            {"team_abbr": "OKC", "avg_pts": 548.9},
        ],
        category="complex_sql_group_by",
    ),

    # Team comparison with GROUP BY (1 case)
    SQLEvaluationTestCase(
        question="Compare the average points per player between the Celtics and Lakers",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.team_abbr, ROUND(AVG(ps.pts), 1) as avg_pts, COUNT(*) as player_count "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr IN ('BOS', 'LAL') "
            "GROUP BY p.team_abbr ORDER BY avg_pts DESC"
        ),
        ground_truth_answer="Celtics average 561.8 points per player (17 players) vs Lakers 434.6 (20 players).",
        ground_truth_data=[
            {"team_abbr": "BOS", "avg_pts": 561.8, "player_count": 17},
            {"team_abbr": "LAL", "avg_pts": 434.6, "player_count": 20},
        ],
        category="complex_sql_team_comparison",
    ),

    # HAVING clause query (1 case)
    SQLEvaluationTestCase(
        question="Which teams have at least 3 players with more than 1000 points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.team_abbr, COUNT(*) as high_scorers "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts > 1000 "
            "GROUP BY p.team_abbr HAVING COUNT(*) >= 3 "
            "ORDER BY high_scorers DESC LIMIT 5"
        ),
        ground_truth_answer="Teams with 3+ high scorers (1000+ pts): SAS (5), NYK (5), CLE (5), SAC (4), IND (4).",
        ground_truth_data=[
            {"team_abbr": "SAS", "high_scorers": 5},
            {"team_abbr": "NYK", "high_scorers": 5},
            {"team_abbr": "CLE", "high_scorers": 5},
            {"team_abbr": "SAC", "high_scorers": 4},
            {"team_abbr": "IND", "high_scorers": 4},
        ],
        category="complex_sql_having",
    ),

    # Range query with BETWEEN (1 case)
    SQLEvaluationTestCase(
        question="Find players between 25 and 30 years old with more than 1500 points",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.age BETWEEN 25 AND 30 AND ps.pts > 1500 "
            "ORDER BY ps.pts DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 scorers aged 25-30: Shai Gilgeous-Alexander (26, 2485), Nikola Jokić (30, 2072), Giannis Antetokounmpo (30, 2037), Jayson Tatum (27, 1930), Devin Booker (28, 1920).",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "age": 26, "pts": 2485},
            {"name": "Nikola Jokić", "age": 30, "pts": 2072},
            {"name": "Giannis Antetokounmpo", "age": 30, "pts": 2037},
            {"name": "Jayson Tatum", "age": 27, "pts": 1930},
            {"name": "Devin Booker", "age": 28, "pts": 1920},
        ],
        category="complex_sql_range",
    ),
]

# ============================================================================
# CONVERSATIONAL SQL QUERIES (25 cases)
# Follow-up questions, context-dependent, pronouns, informal language
# Enhanced with noisy/conversational variations + 5 multi-turn threads
# ============================================================================

CONVERSATIONAL_SQL_CASES = [
    # Initial conversational queries (4 cases - varied formality)
    SQLEvaluationTestCase(
        question="Show me the top scorer",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander is the top scorer with 2485 points.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="conversational_initial",
    ),
    SQLEvaluationTestCase(
        question="Who's the best rebounder?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.reb DESC LIMIT 1",
        ground_truth_answer="Ivica Zubac is the top rebounder with 1008 rebounds.",
        ground_truth_data={"name": "Ivica Zubac", "reb": 1008},
        category="conversational_casual",
    ),
    SQLEvaluationTestCase(
        question="Tell me about LeBron's stats",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%LeBron%'",
        ground_truth_answer="LeBron James: 1708 PTS, 546 REB, 574 AST.",
        ground_truth_data={"name": "LeBron James", "pts": 1708, "reb": 546, "ast": 574},
        category="conversational_casual",
    ),
    SQLEvaluationTestCase(
        question="gimme the assist leaders plz",  # Noisy: informal slang
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.ast DESC LIMIT 5",
        ground_truth_answer="Top 5 assist leaders: Trae Young (882), Nikola Jokić (714), James Harden (687), Tyrese Haliburton (672), Cade Cunningham (637).",
        ground_truth_data=[
            {"name": "Trae Young", "ast": 882},
            {"name": "Nikola Jokić", "ast": 714},
            {"name": "James Harden", "ast": 687},
            {"name": "Tyrese Haliburton", "ast": 672},
            {"name": "Cade Cunningham", "ast": 637},
        ],
        category="conversational_casual",
    ),

    # Follow-up questions with pronouns (4 cases)
    SQLEvaluationTestCase(
        question="What about his assists?",  # Follow-up after "Show me the top scorer"
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Shai%'",
        ground_truth_answer="Shai Gilgeous-Alexander has 486 assists (follow-up).",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "ast": 486},
        category="conversational_followup",
    ),
    SQLEvaluationTestCase(
        question="How many games did he play?",  # Follow-up after "Who's the best rebounder?"
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Zubac%'",
        ground_truth_answer="Ivica Zubac played 80 games (contextual follow-up).",
        ground_truth_data={"name": "Ivica Zubac", "gp": 80},
        category="conversational_followup",
    ),
    SQLEvaluationTestCase(
        question="Compare him to Curry",  # Follow-up after "Tell me about LeBron's stats"
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('LeBron James', 'Stephen Curry')",
        ground_truth_answer="LeBron James: 1708 PTS, 546 REB, 574 AST. Stephen Curry: 1715 PTS, 308 REB, 420 AST.",
        ground_truth_data=[
            {"name": "LeBron James", "pts": 1708, "reb": 546, "ast": 574},
            {"name": "Stephen Curry", "pts": 1715, "reb": 308, "ast": 420},
        ],
        category="conversational_comparison",
    ),
    SQLEvaluationTestCase(
        question="Which of them plays for the Hawks?",  # Follow-up after "Show the assist leaders"
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, p.team_abbr, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.team_abbr = 'ATL' ORDER BY ps.ast DESC LIMIT 1",
        ground_truth_answer="Trae Young plays for the Hawks with 882 assists.",
        ground_truth_data={"name": "Trae Young", "ast": 882},
        category="conversational_filter_followup",
    ),

    # Stat abbreviation handling (1 case)
    SQLEvaluationTestCase(
        question="Show me the pts leaders this season",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 5",
        ground_truth_answer="Top pts leaders: Shai Gilgeous-Alexander (2485), Anthony Edwards (2180), Nikola Jokić (2072), Giannis Antetokounmpo (2037), Jayson Tatum (1930).",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485},
            {"name": "Anthony Edwards", "pts": 2180},
            {"name": "Nikola Jokić", "pts": 2072},
            {"name": "Giannis Antetokounmpo", "pts": 2037},
            {"name": "Jayson Tatum", "pts": 1930},
        ],
        category="conversational_stat_abbreviation",
    ),

    # Ambiguous intent query (1 case)
    SQLEvaluationTestCase(
        question="Who is the MVP this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pie, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.gp > 50 ORDER BY ps.pie DESC LIMIT 1",
        ground_truth_answer="Giannis Antetokounmpo leads in PIE (21.0) with 2037 points, making him a top MVP candidate.",
        ground_truth_data={"name": "Giannis Antetokounmpo", "pie": 21.0, "pts": 2037},
        category="conversational_ambiguous",
    ),

    # --- Thread: Progressive Filtering (3 turns) ---
    # Turn 1: broad query → Turn 2: team filter → Turn 3: sort refinement
    SQLEvaluationTestCase(
        question="Show me players with good three-point shooting",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.three_pct FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.three_pct > 38 AND ps.gp >= 50 "
            "ORDER BY ps.three_pct DESC LIMIT 5"
        ),
        ground_truth_answer="Top 3P shooters (>38%, 50+ GP): Drew Eubanks (50.0%), Seth Curry (45.6%), Zach LaVine (44.6%), Ty Jerome (43.9%), Taurean Prince (43.9%).",
        ground_truth_data=[
            {"name": "Drew Eubanks", "three_pct": 50.0},
            {"name": "Seth Curry", "three_pct": 45.6},
            {"name": "Zach LaVine", "three_pct": 44.6},
            {"name": "Ty Jerome", "three_pct": 43.9},
            {"name": "Taurean Prince", "three_pct": 43.9},
        ],
        category="conversational_progressive_filtering",
    ),
    SQLEvaluationTestCase(
        question="Only from the Lakers",  # Refines previous to LAL
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.three_pct FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'LAL' AND ps.three_pct IS NOT NULL "
            "ORDER BY ps.three_pct DESC LIMIT 5"
        ),
        ground_truth_answer="Lakers 3P shooters: Rui Hachimura (41.3%), Dorian Finney-Smith (41.1%), Jordan Goodwin (38.2%), Austin Reaves (37.7%), LeBron James (37.6%).",
        ground_truth_data=[
            {"name": "Rui Hachimura", "three_pct": 41.3},
            {"name": "Dorian Finney-Smith", "three_pct": 41.1},
            {"name": "Jordan Goodwin", "three_pct": 38.2},
            {"name": "Austin Reaves", "three_pct": 37.7},
            {"name": "LeBron James", "three_pct": 37.6},
        ],
        category="conversational_progressive_filtering",
    ),
    SQLEvaluationTestCase(
        question="Sort them by attempts",  # Further refines to ORDER BY three_pa DESC
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.three_pct, ps.three_pa FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'LAL' AND ps.three_pct IS NOT NULL "
            "ORDER BY ps.three_pa DESC LIMIT 5"
        ),
        ground_truth_answer=(
            "Lakers 3P by attempts: Austin Reaves (37.7%, 533 3PA), Luka Dončić (36.8%, 480 3PA), "
            "LeBron James (37.6%, 399 3PA), Dalton Knecht (37.6%, 343 3PA), Dorian Finney-Smith (41.1%, 315 3PA)."
        ),
        ground_truth_data=[
            {"name": "Austin Reaves", "three_pct": 37.7, "three_pa": 533},
            {"name": "Luka Dončić", "three_pct": 36.8, "three_pa": 480},
            {"name": "LeBron James", "three_pct": 37.6, "three_pa": 399},
            {"name": "Dalton Knecht", "three_pct": 37.6, "three_pa": 343},
            {"name": "Dorian Finney-Smith", "three_pct": 41.1, "three_pa": 315},
        ],
        category="conversational_progressive_filtering",
    ),

    # --- Thread: User Correction (3 turns) ---
    # Turn 1: Warriors → Turn 2: correction to Celtics → Turn 3: pronoun to Celtics
    SQLEvaluationTestCase(
        question="Show me stats for the Warriors",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'GSW' ORDER BY ps.pts DESC LIMIT 3"
        ),
        ground_truth_answer="Warriors top 3: Stephen Curry (1715 PTS, 308 REB, 420 AST), Jimmy Butler III (963 PTS, 297 REB, 297 AST), Buddy Hield (910 PTS, 262 REB, 131 AST).",
        ground_truth_data=[
            {"name": "Stephen Curry", "pts": 1715, "reb": 308, "ast": 420},
            {"name": "Jimmy Butler III", "pts": 963, "reb": 297, "ast": 297},
            {"name": "Buddy Hield", "pts": 910, "reb": 262, "ast": 131},
        ],
        category="conversational_correction",
    ),
    SQLEvaluationTestCase(
        question="Actually, I meant the Celtics",  # Corrects team
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'BOS' ORDER BY ps.pts DESC LIMIT 3"
        ),
        ground_truth_answer="Celtics top 3: Jayson Tatum (1930 PTS, 626 REB, 432 AST), Jaylen Brown (1399 PTS, 365 REB, 284 AST), Derrick White (1246 PTS, 342 REB, 365 AST).",
        ground_truth_data=[
            {"name": "Jayson Tatum", "pts": 1930, "reb": 626, "ast": 432},
            {"name": "Jaylen Brown", "pts": 1399, "reb": 365, "ast": 284},
            {"name": "Derrick White", "pts": 1246, "reb": 342, "ast": 365},
        ],
        category="conversational_correction",
    ),
    SQLEvaluationTestCase(
        question="Who is their top scorer?",  # "their" = Celtics (not Warriors)
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'BOS' ORDER BY ps.pts DESC LIMIT 1"
        ),
        ground_truth_answer="Jayson Tatum is the Celtics' top scorer with 1930 points.",
        ground_truth_data={"name": "Jayson Tatum", "pts": 1930},
        category="conversational_correction",
    ),

    # --- Thread: Implicit Category Continuation (3 turns) ---
    # Turn 1: steals → Turn 2: "And blocks?" → Turn 3: "What about turnovers?"
    SQLEvaluationTestCase(
        question="Who leads in steals?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.stl FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY ps.stl DESC LIMIT 1"
        ),
        ground_truth_answer="Dyson Daniels leads in steals with 228.",
        ground_truth_data={"name": "Dyson Daniels", "stl": 228},
        category="conversational_implicit_continuation",
    ),
    SQLEvaluationTestCase(
        question="And blocks?",  # Implicitly: who leads in blocks
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.blk FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY ps.blk DESC LIMIT 1"
        ),
        ground_truth_answer="Victor Wembanyama leads in blocks with 175.",
        ground_truth_data={"name": "Victor Wembanyama", "blk": 175},
        category="conversational_implicit_continuation",
    ),
    SQLEvaluationTestCase(
        question="What about turnovers?",  # Still: who leads in turnovers
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.tov FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY ps.tov DESC LIMIT 1"
        ),
        ground_truth_answer="Trae Young leads in turnovers with 357.",
        ground_truth_data={"name": "Trae Young", "tov": 357},
        category="conversational_implicit_continuation",
    ),

    # --- Thread: Multi-Entity Tracking (3 turns) ---
    # Turn 1: Tatum → Turn 2: LeBron compare → Turn 3: "Between the two"
    SQLEvaluationTestCase(
        question="Tell me about Jayson Tatum's scoring",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name LIKE '%Tatum%'"
        ),
        ground_truth_answer="Jayson Tatum: 1930 PTS in 72 GP (26.8 PPG).",
        ground_truth_data={"name": "Jayson Tatum", "pts": 1930, "gp": 72, "ppg": 26.8},
        category="conversational_multi_entity",
    ),
    SQLEvaluationTestCase(
        question="How does LeBron James compare?",  # Introduces second entity
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name IN ('Jayson Tatum', 'LeBron James')"
        ),
        ground_truth_answer="Jayson Tatum: 1930 PTS (26.8 PPG). LeBron James: 1708 PTS (24.4 PPG).",
        ground_truth_data=[
            {"name": "Jayson Tatum", "pts": 1930, "gp": 72, "ppg": 26.8},
            {"name": "LeBron James", "pts": 1708, "gp": 70, "ppg": 24.4},
        ],
        category="conversational_multi_entity",
    ),
    SQLEvaluationTestCase(
        question="Between the two, who has more rebounds?",  # References both entities
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.reb FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name IN ('Jayson Tatum', 'LeBron James') ORDER BY ps.reb DESC"
        ),
        ground_truth_answer="Jayson Tatum has more rebounds (626) than LeBron James (546).",
        ground_truth_data=[
            {"name": "Jayson Tatum", "reb": 626},
            {"name": "LeBron James", "reb": 546},
        ],
        category="conversational_multi_entity",
    ),

    # --- Thread: Team-Level Pronoun Resolution (3 turns) ---
    # Turn 1: team query → Turn 2: "their" scorers → Turn 3: "their" avg age
    SQLEvaluationTestCase(
        question="Which team has the highest total points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "GROUP BY p.team_abbr ORDER BY total_pts DESC LIMIT 1"
        ),
        ground_truth_answer="The Detroit Pistons (DET) have the highest total points with 10292.",
        ground_truth_data={"team_abbr": "DET", "total_pts": 10292},
        category="conversational_team_pronoun",
    ),
    SQLEvaluationTestCase(
        question="Who are their top scorers?",  # "their" = DET
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'DET' ORDER BY ps.pts DESC LIMIT 3"
        ),
        ground_truth_answer="Pistons top scorers: Cade Cunningham (1827), Malik Beasley (1337), Tobias Harris (1000).",
        ground_truth_data=[
            {"name": "Cade Cunningham", "pts": 1827},
            {"name": "Malik Beasley", "pts": 1337},
            {"name": "Tobias Harris", "pts": 1000},
        ],
        category="conversational_team_pronoun",
    ),
    SQLEvaluationTestCase(
        question="What is the average age of their players?",  # "their" still = DET
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT ROUND(AVG(p.age), 1) as avg_age FROM players p "
            "WHERE p.team_abbr = 'DET' AND p.age IS NOT NULL"
        ),
        ground_truth_answer="The average age of the Pistons players is 25.3 years.",
        ground_truth_data={"avg_age": 25.3},
        category="conversational_team_pronoun",
    ),
]

# ============================================================================
# NOISY SQL QUERIES (7 cases)
# Typos, slang, abbreviations — tests classifier + SQL gen robustness
# ============================================================================

NOISY_SQL_CASES = [
    SQLEvaluationTestCase(
        question="whos got da most pts this szn",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander has the most points with 2485.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="noisy_sql_typo",
    ),
    SQLEvaluationTestCase(
        question="show me currys 3 pt pct",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Stephen Curry%'",
        ground_truth_answer="Stephen Curry's 3-point percentage is 39.7%.",
        ground_truth_data={"name": "Stephen Curry", "three_pct": 39.7},
        category="noisy_sql_abbreviation",
    ),
    SQLEvaluationTestCase(
        question="how many playas got more than 1k points??",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts > 1000",
        ground_truth_answer="84 players scored over 1000 points.",
        ground_truth_data={"player_count": 84},
        category="noisy_sql_slang",
    ),
    SQLEvaluationTestCase(
        question="jokic rebounds total plzz",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Jokić%'",
        ground_truth_answer="Nikola Jokić has 889 total rebounds.",
        ground_truth_data={"name": "Nikola Jokić", "reb": 889},
        category="noisy_sql_informal",
    ),
    SQLEvaluationTestCase(
        question="compare lebron n harden assists",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('LeBron James', 'James Harden') ORDER BY ps.ast DESC",
        ground_truth_answer="James Harden has 687 assists vs LeBron James with 574.",
        ground_truth_data=[
            {"name": "James Harden", "ast": 687},
            {"name": "LeBron James", "ast": 574},
        ],
        category="noisy_sql_abbreviation",
    ),
    SQLEvaluationTestCase(
        question="whats the avg fg% in da league lol",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT ROUND(AVG(fg_pct), 1) as avg_fg_pct FROM player_stats WHERE fg_pct IS NOT NULL",
        ground_truth_answer="The average field goal percentage in the league is 44.6%.",
        ground_truth_data={"avg_fg_pct": 44.6},
        category="noisy_sql_slang",
    ),
    SQLEvaluationTestCase(
        question="top 3 reb guys??",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.reb DESC LIMIT 3",
        ground_truth_answer="Top 3 rebounders: Ivica Zubac (1008), Domantas Sabonis (973), Karl-Anthony Towns (922).",
        ground_truth_data=[
            {"name": "Ivica Zubac", "reb": 1008},
            {"name": "Domantas Sabonis", "reb": 973},
            {"name": "Karl-Anthony Towns", "reb": 922},
        ],
        category="noisy_sql_informal",
    ),
]

# ============================================================================
# ADVERSARIAL SQL QUERIES (3 cases)
# SQL injection, raw SQL input, path traversal — tests sanitization
# ============================================================================

ADVERSARIAL_SQL_CASES = [
    SQLEvaluationTestCase(
        question="'; DROP TABLE players; -- Who scored the most points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander scored the most with 2485 points.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="adversarial_sql_injection",
    ),
    SQLEvaluationTestCase(
        question="SELECT * FROM players; Who has the most assists?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.ast DESC LIMIT 1",
        ground_truth_answer="Trae Young leads in assists with 882.",
        ground_truth_data={"name": "Trae Young", "ast": 882},
        category="adversarial_raw_sql",
    ),
    SQLEvaluationTestCase(
        question="../../etc/passwd What is Curry's three point percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Stephen Curry%'",
        ground_truth_answer="Stephen Curry's 3-point percentage is 39.7%.",
        ground_truth_data={"name": "Stephen Curry", "three_pct": 39.7},
        category="adversarial_path_traversal",
    ),
]

# ============================================================================
# COMBINED TEST SUITE
# Total: 80 SQL cases (13 simple + 7 comparison + 11 aggregation + 14 complex
#                       + 25 conversational + 7 noisy + 3 adversarial)
# ============================================================================

SQL_TEST_CASES = (
    SIMPLE_SQL_CASES +
    COMPARISON_SQL_CASES +
    AGGREGATION_SQL_CASES +
    COMPLEX_SQL_CASES +
    CONVERSATIONAL_SQL_CASES +
    NOISY_SQL_CASES +
    ADVERSARIAL_SQL_CASES
)


# ============================================================================
# VERIFICATION & SUMMARY
# ============================================================================

print(f"\n{'='*70}")
print(f"SQL TEST CASES REVIEW - SUMMARY")
print(f"{'='*70}")
print(f"Simple SQL Cases:        {len(SIMPLE_SQL_CASES):2d} (13)")
print(f"Comparison SQL Cases:    {len(COMPARISON_SQL_CASES):2d} (7)")
print(f"Aggregation SQL Cases:   {len(AGGREGATION_SQL_CASES):2d} (11)")
print(f"Complex SQL Cases:       {len(COMPLEX_SQL_CASES):2d} (14)")
print(f"Conversational SQL Cases: {len(CONVERSATIONAL_SQL_CASES):2d} (25)")
print(f"Noisy SQL Cases:         {len(NOISY_SQL_CASES):2d} (7)")
print(f"Adversarial SQL Cases:   {len(ADVERSARIAL_SQL_CASES):2d} (3)")
print(f"{'-'*70}")
print(f"Total SQL Test Cases:    {len(SQL_TEST_CASES):2d} (80)")
print(f"{'='*70}")

# Assertions for validation
assert len(SIMPLE_SQL_CASES) == 13, f"Expected 13 simple cases, got {len(SIMPLE_SQL_CASES)}"
assert len(COMPARISON_SQL_CASES) == 7, f"Expected 7 comparison cases, got {len(COMPARISON_SQL_CASES)}"
assert len(AGGREGATION_SQL_CASES) == 11, f"Expected 11 aggregation cases, got {len(AGGREGATION_SQL_CASES)}"
assert len(COMPLEX_SQL_CASES) == 14, f"Expected 14 complex cases, got {len(COMPLEX_SQL_CASES)}"
assert len(CONVERSATIONAL_SQL_CASES) == 25, f"Expected 25 conversational cases, got {len(CONVERSATIONAL_SQL_CASES)}"
assert len(NOISY_SQL_CASES) == 7, f"Expected 7 noisy cases, got {len(NOISY_SQL_CASES)}"
assert len(ADVERSARIAL_SQL_CASES) == 3, f"Expected 3 adversarial cases, got {len(ADVERSARIAL_SQL_CASES)}"
assert len(SQL_TEST_CASES) == 80, f"Expected 80 SQL cases, got {len(SQL_TEST_CASES)}"

print(f"\n[OK] All assertions passed - test suite validated")
print(f"[OK] Total SQL test cases: {len(SQL_TEST_CASES)} (80 total)")
