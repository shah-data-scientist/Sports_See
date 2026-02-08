"""
FILE: sql_only_test_cases.py
STATUS: Active
RESPONSIBILITY: SQL-only test cases with ACTUAL database ground truth (21 cases)
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

from src.evaluation.sql_evaluation import QueryType, SQLEvaluationTestCase

# ============================================================================
# SIMPLE SQL QUERIES (7 cases)
# Single-table queries with JOIN, straightforward retrieval
# ============================================================================

SIMPLE_SQL_CASES = [
    SQLEvaluationTestCase(
        question="Who scored the most points this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander scored the most points with 2485 PTS.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="What is LeBron James' average points per game?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ROUND(ps.pts*1.0/ps.gp, 1) as ppg FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%LeBron%'",
        ground_truth_answer="LeBron James averages 24.4 points per game.",
        ground_truth_data={"name": "LeBron James", "ppg": 24.4},
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
    SQLEvaluationTestCase(
        question="What is Stephen Curry's 3-point percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Curry%'",
        ground_truth_answer="Stephen Curry's 3-point percentage is 39.7%.",
        ground_truth_data={"name": "Stephen Curry", "three_pct": 39.7},
        category="simple_sql_player_stats",
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
        question="How many games did Damian Lillard play?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Lillard%'",
        ground_truth_answer="Damian Lillard played 58 games.",
        ground_truth_data={"name": "Damian Lillard", "gp": 58},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="What is Kevin Durant's field goal percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Durant%'",
        ground_truth_answer="Kevin Durant's field goal percentage is 52.7%.",
        ground_truth_data={"name": "Kevin Durant", "fg_pct": 52.7},
        category="simple_sql_player_stats",
    ),
]

# ============================================================================
# COMPARISON SQL QUERIES (7 cases)
# Multi-player comparisons with JOIN, WHERE IN clauses
# ============================================================================

COMPARISON_SQL_CASES = [
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
        question="Who has more rebounds, Giannis or Anthony Davis?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name IN ('Giannis Antetokounmpo', 'Anthony Davis') "
            "ORDER BY ps.reb DESC"
        ),
        ground_truth_answer="Giannis Antetokounmpo has more rebounds (797) than Anthony Davis (592).",
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "reb": 797},
            {"name": "Anthony Davis", "reb": 592},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare LeBron James and Kevin Durant's scoring",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('LeBron James', 'Kevin Durant')",
        ground_truth_answer="LeBron James: 1708 PTS. Kevin Durant: 1649 PTS.",
        ground_truth_data=[
            {"name": "LeBron James", "pts": 1708},
            {"name": "Kevin Durant", "pts": 1649},
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
        question="Compare Trae Young and Luka Dončić's assists",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Trae Young', 'Luka Dončić') ORDER BY ps.ast DESC",
        ground_truth_answer="Trae Young: 882 AST. Luka Dončić: 385 AST.",
        ground_truth_data=[
            {"name": "Trae Young", "ast": 882},
            {"name": "Luka Dončić", "ast": 385},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who is more efficient, Jokić or Embiid?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Joel Embiid') ORDER BY ps.pie DESC",
        ground_truth_answer="Nikola Jokić has higher PIE (20.6) than Joel Embiid (16.9).",
        ground_truth_data=[
            {"name": "Nikola Jokić", "pie": 20.6},
            {"name": "Joel Embiid", "pie": 16.9},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare blocks: Giannis vs Brook Lopez",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.blk FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Giannis Antetokounmpo', 'Brook Lopez') ORDER BY ps.blk DESC",
        ground_truth_answer="Brook Lopez has more blocks than Giannis Antetokounmpo.",
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "blk": 80},
        ],
        category="comparison_sql_players",
    ),
]

# ============================================================================
# AGGREGATION SQL QUERIES (7 cases)
# League-wide stats, AVG/COUNT/MAX, no JOIN needed
# ============================================================================

AGGREGATION_SQL_CASES = [
    SQLEvaluationTestCase(
        question="What is the average 3-point percentage for all players?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(three_pct) as avg_3p_pct FROM player_stats WHERE three_pct IS NOT NULL",
        ground_truth_answer="The average 3-point percentage across all players is 29.9%.",
        ground_truth_data={"avg_3p_pct": 29.9},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players scored over 1000 points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts > 1000",
        ground_truth_answer="84 players scored over 1000 points this season.",
        ground_truth_data={"player_count": 84},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the average field goal percentage in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(fg_pct) as avg_fg_pct FROM player_stats WHERE fg_pct IS NOT NULL",
        ground_truth_answer="The average field goal percentage is 44.6%.",
        ground_truth_data={"avg_fg_pct": 44.6},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players average over 20 points per game?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts*1.0/gp > 20",
        ground_truth_answer="50 players average over 20 points per game.",
        ground_truth_data={"player_count": 50},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the highest PIE in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT MAX(pie) as max_pie FROM player_stats",
        ground_truth_answer="The highest PIE is 40.0.",
        ground_truth_data={"max_pie": 40.0},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players have a true shooting percentage over 60%?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE ts_pct > 60",
        ground_truth_answer="142 players have a true shooting percentage over 60%.",
        ground_truth_data={"player_count": 142},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the average number of assists per game league-wide?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(ast*1.0/gp) as avg_apg FROM player_stats WHERE gp > 0",
        ground_truth_answer="The average number of assists per game league-wide is 2.09 APG.",
        ground_truth_data={"avg_apg": 2.09},
        category="aggregation_sql_league",
    ),
]

# ============================================================================
# SIMPLE SQL QUERIES - PART 2 (7 additional cases)
# ============================================================================

SIMPLE_SQL_CASES_PART2 = [
    SQLEvaluationTestCase(
        question="Who has the most assists this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.ast DESC LIMIT 1",
        ground_truth_answer="Trae Young has the most assists with 882 AST.",
        ground_truth_data={"name": "Trae Young", "ast": 882},
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="How many points did Giannis Antetokounmpo score?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Giannis%'",
        ground_truth_answer="Giannis Antetokounmpo scored 2037 points.",
        ground_truth_data={"name": "Giannis Antetokounmpo", "pts": 2037},
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
        question="Who has the best free throw percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ft_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ft_pct IS NOT NULL ORDER BY ps.ft_pct DESC LIMIT 1",
        ground_truth_answer="Sam Hauser has the best free throw percentage at 100%.",
        ground_truth_data={"name": "Sam Hauser", "ft_pct": 100.0},
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
        question="How many games did Anthony Edwards play?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Anthony Edwards%'",
        ground_truth_answer="Anthony Edwards played 79 games.",
        ground_truth_data={"name": "Anthony Edwards", "gp": 79},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="Who has the highest true shooting percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ts_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ts_pct IS NOT NULL AND ps.gp > 20 ORDER BY ps.ts_pct DESC LIMIT 1",
        ground_truth_answer="Kai Jones has the highest true shooting percentage at 80.4%.",
        ground_truth_data={"name": "Kai Jones", "ts_pct": 80.4},
        category="simple_sql_top_n",
    ),
]

# ============================================================================
# COMPARISON SQL QUERIES - PART 2 (7 additional cases)
# ============================================================================

COMPARISON_SQL_CASES_PART2 = [
    SQLEvaluationTestCase(
        question="Compare Shai Gilgeous-Alexander and Anthony Edwards scoring",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Shai Gilgeous-Alexander', 'Anthony Edwards') ORDER BY ps.pts DESC",
        ground_truth_answer="Shai Gilgeous-Alexander: 2485 PTS. Anthony Edwards: 2180 PTS.",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485},
            {"name": "Anthony Edwards", "pts": 2180},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who has more rebounds, Jokić or Sabonis?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Domantas Sabonis') ORDER BY ps.reb DESC",
        ground_truth_answer="Domantas Sabonis has more rebounds (973) than Nikola Jokić (889).",
        ground_truth_data=[
            {"name": "Domantas Sabonis", "reb": 973},
            {"name": "Nikola Jokić", "reb": 889},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare Jayson Tatum and Kevin Durant scoring efficiency",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts, ps.fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Jayson Tatum', 'Kevin Durant') ORDER BY ps.pts DESC",
        ground_truth_answer="Jayson Tatum: 1930 PTS, 45.2% FG. Kevin Durant: 1649 PTS, 52.7% FG.",
        ground_truth_data=[
            {"name": "Jayson Tatum", "pts": 1930, "fg_pct": 45.2},
            {"name": "Kevin Durant", "pts": 1649, "fg_pct": 52.7},
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
        question="Who are the top 2 players by true shooting percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ts_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.gp > 20 ORDER BY ps.ts_pct DESC LIMIT 2",
        ground_truth_answer="Top 2 TS%: Kai Jones (80.4%), Jarrett Allen (72.4%).",
        ground_truth_data=[
            {"name": "Kai Jones", "ts_pct": 80.4},
            {"name": "Jarrett Allen", "ts_pct": 72.4},
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
# AGGREGATION SQL QUERIES - PART 2 (7 additional cases)
# ============================================================================

AGGREGATION_SQL_CASES_PART2 = [
    SQLEvaluationTestCase(
        question="What is the average rebounds per game league-wide?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(CAST(reb AS REAL) / gp) as avg_rpg FROM player_stats WHERE gp > 0",
        ground_truth_answer="The average rebounds per game is 3.60 RPG.",
        ground_truth_data={"avg_rpg": 3.60},
        category="aggregation_sql_league",
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
        question="What is the average free throw percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(ft_pct) as avg FROM player_stats WHERE ft_pct IS NOT NULL",
        ground_truth_answer="The average free throw percentage is 72.0%.",
        ground_truth_data={"avg": 72.0},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players played more than 50 games?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as count FROM player_stats WHERE gp > 50",
        ground_truth_answer="282 players played more than 50 games.",
        ground_truth_data={"count": 282},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the minimum points scored (excluding zeros)?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT MIN(pts) as min_pts FROM player_stats WHERE pts > 0",
        ground_truth_answer="The minimum points scored is 1.",
        ground_truth_data={"min_pts": 1},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players have more than 100 blocks?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as count FROM player_stats WHERE blk > 100",
        ground_truth_answer="12 players have more than 100 blocks.",
        ground_truth_data={"count": 12},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the average PIE in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(pie) as avg_pie FROM player_stats WHERE pie IS NOT NULL",
        ground_truth_answer="The average PIE is 8.9.",
        ground_truth_data={"avg_pie": 8.9},
        category="aggregation_sql_league",
    ),
]

# ============================================================================
# COMBINED TEST SUITE (42 TOTAL)
# ============================================================================

SQL_ONLY_TEST_CASES = (
    SIMPLE_SQL_CASES + SIMPLE_SQL_CASES_PART2 +
    COMPARISON_SQL_CASES + COMPARISON_SQL_CASES_PART2 +
    AGGREGATION_SQL_CASES + AGGREGATION_SQL_CASES_PART2
)

# Verify count
assert len(SQL_ONLY_TEST_CASES) == 42, f"Expected 42 cases, got {len(SQL_ONLY_TEST_CASES)}"
assert len(SIMPLE_SQL_CASES) + len(SIMPLE_SQL_CASES_PART2) == 14, f"Expected 14 simple cases"
assert len(COMPARISON_SQL_CASES) + len(COMPARISON_SQL_CASES_PART2) == 14, f"Expected 14 comparison cases"
assert len(AGGREGATION_SQL_CASES) + len(AGGREGATION_SQL_CASES_PART2) == 14, f"Expected 14 aggregation cases"
