"""
FILE: sql_only_test_cases.py
STATUS: Active
RESPONSIBILITY: Comprehensive SQL-only test cases (21 cases, 3x original)
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

from src.evaluation.sql_evaluation import QueryType, SQLEvaluationTestCase

# ============================================================================
# SIMPLE SQL QUERIES (7 cases)
# Single-table queries, straightforward retrieval
# ============================================================================

SIMPLE_SQL_CASES = [
    SQLEvaluationTestCase(
        question="Who scored the most points this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, pts FROM player_stats ORDER BY pts DESC LIMIT 1",
        ground_truth_answer="Luka Dončić scored the most points with 2370 PTS.",
        ground_truth_data={"name": "Luka Dončić", "pts": 2370},
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="What is LeBron James' average points per game?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, pts, gp, ROUND(pts*1.0/gp, 1) as ppg FROM player_stats WHERE name LIKE '%LeBron%'",
        ground_truth_answer="LeBron James averages 25.7 points per game (2082 PTS / 81 GP).",
        ground_truth_data={"name": "LeBron James", "ppg": 25.7},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="How many assists did Chris Paul record?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, ast FROM player_stats WHERE name LIKE '%Chris Paul%'",
        ground_truth_answer="Chris Paul recorded 567 assists.",
        ground_truth_data={"name": "Chris Paul", "ast": 567},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="What is Stephen Curry's 3-point percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, fg3_pct FROM player_stats WHERE name LIKE '%Curry%'",
        ground_truth_answer="Stephen Curry's 3-point percentage is 42.7%.",
        ground_truth_data={"name": "Stephen Curry", "fg3_pct": 0.427},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="Who are the top 3 rebounders in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, reb FROM player_stats ORDER BY reb DESC LIMIT 3",
        ground_truth_answer="Top 3 rebounders: Nikola Jokić (891), Domantas Sabonis (877), Giannis Antetokounmpo (912).",
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "reb": 912},
            {"name": "Nikola Jokić", "reb": 891},
            {"name": "Domantas Sabonis", "reb": 877}
        ],
        category="simple_sql_top_n",
    ),
    SQLEvaluationTestCase(
        question="How many games did Damian Lillard play?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, gp FROM player_stats WHERE name LIKE '%Lillard%'",
        ground_truth_answer="Damian Lillard played 73 games.",
        ground_truth_data={"name": "Damian Lillard", "gp": 73},
        category="simple_sql_player_stats",
    ),
    SQLEvaluationTestCase(
        question="What is Kevin Durant's field goal percentage?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, fg_pct FROM player_stats WHERE name LIKE '%Durant%'",
        ground_truth_answer="Kevin Durant's field goal percentage is 53.7%.",
        ground_truth_data={"name": "Kevin Durant", "fg_pct": 0.537},
        category="simple_sql_player_stats",
    ),
]

# ============================================================================
# COMPARISON SQL QUERIES (7 cases)
# Multi-player/team comparisons, WHERE IN clauses
# ============================================================================

COMPARISON_SQL_CASES = [
    SQLEvaluationTestCase(
        question="Compare Jokić and Embiid's stats",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, pts, reb, ast FROM player_stats WHERE name IN ('Nikola Jokić', 'Joel Embiid')",
        ground_truth_answer=(
            "Nikola Jokić: 2018 PTS, 891 REB, 688 AST. "
            "Joel Embiid: 2159 PTS, 813 REB, 296 AST."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2018, "reb": 891, "ast": 688},
            {"name": "Joel Embiid", "pts": 2159, "reb": 813, "ast": 296},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who has more rebounds, Giannis or Anthony Davis?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT name, reb FROM player_stats "
            "WHERE name IN ('Giannis Antetokounmpo', 'Anthony Davis') "
            "ORDER BY reb DESC"
        ),
        ground_truth_answer="Giannis Antetokounmpo has more rebounds (912) than Anthony Davis (723).",
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "reb": 912},
            {"name": "Anthony Davis", "reb": 723},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare LeBron James and Kevin Durant's scoring",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, pts, ppg FROM player_stats WHERE name IN ('LeBron James', 'Kevin Durant')",
        ground_truth_answer="LeBron James: 2082 PTS (25.7 PPG). Kevin Durant: 2091 PTS (27.4 PPG).",
        ground_truth_data=[
            {"name": "LeBron James", "pts": 2082},
            {"name": "Kevin Durant", "pts": 2091},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who shoots better from 3, Curry or Lillard?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, fg3_pct FROM player_stats WHERE name IN ('Stephen Curry', 'Damian Lillard') ORDER BY fg3_pct DESC",
        ground_truth_answer="Stephen Curry shoots better (42.7%) than Damian Lillard (37.1%).",
        ground_truth_data=[
            {"name": "Stephen Curry", "fg3_pct": 0.427},
            {"name": "Damian Lillard", "fg3_pct": 0.371},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare Trae Young and Luka Dončić's assists",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, ast FROM player_stats WHERE name IN ('Trae Young', 'Luka Dončić') ORDER BY ast DESC",
        ground_truth_answer="Trae Young: 737 AST. Luka Dončić: 580 AST.",
        ground_truth_data=[
            {"name": "Trae Young", "ast": 737},
            {"name": "Luka Dončić", "ast": 580},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Who is more efficient, Jokić or Embiid?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, per FROM player_stats WHERE name IN ('Nikola Jokić', 'Joel Embiid') ORDER BY per DESC",
        ground_truth_answer="Joel Embiid has higher PER (28.5) than Nikola Jokić (27.1).",
        ground_truth_data=[
            {"name": "Joel Embiid", "per": 28.5},
            {"name": "Nikola Jokić", "per": 27.1},
        ],
        category="comparison_sql_players",
    ),
    SQLEvaluationTestCase(
        question="Compare blocks: Giannis vs Jaren Jackson Jr",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, blk FROM player_stats WHERE name IN ('Giannis Antetokounmpo', 'Jaren Jackson Jr.') ORDER BY blk DESC",
        ground_truth_answer="Jaren Jackson Jr.: 94 BLK. Giannis Antetokounmpo: 61 BLK.",
        ground_truth_data=[
            {"name": "Jaren Jackson Jr.", "blk": 94},
            {"name": "Giannis Antetokounmpo", "blk": 61},
        ],
        category="comparison_sql_players",
    ),
]

# ============================================================================
# AGGREGATION SQL QUERIES (7 cases)
# League-wide stats, AVG/COUNT/SUM, GROUP BY
# ============================================================================

AGGREGATION_SQL_CASES = [
    SQLEvaluationTestCase(
        question="What is the average 3-point percentage for all players?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(fg3_pct) as avg_3p_pct FROM player_stats WHERE fg3_pct IS NOT NULL",
        ground_truth_answer="The average 3-point percentage across all players is 35.8%.",
        ground_truth_data={"avg_3p_pct": 0.358},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players scored over 1000 points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts > 1000",
        ground_truth_answer="127 players scored over 1000 points this season.",
        ground_truth_data={"player_count": 127},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the average field goal percentage in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(fg_pct) as avg_fg_pct FROM player_stats WHERE fg_pct IS NOT NULL",
        ground_truth_answer="The average field goal percentage is 46.2%.",
        ground_truth_data={"avg_fg_pct": 0.462},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players average over 20 points per game?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts*1.0/gp > 20",
        ground_truth_answer="43 players average over 20 points per game.",
        ground_truth_data={"player_count": 43},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the highest PER in the league?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT MAX(per) as max_per FROM player_stats",
        ground_truth_answer="The highest PER is 31.2.",
        ground_truth_data={"max_per": 31.2},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players have a true shooting percentage over 60%?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE ts_pct > 0.60",
        ground_truth_answer="89 players have a true shooting percentage over 60%.",
        ground_truth_data={"player_count": 89},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the average number of assists per game league-wide?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(ast*1.0/gp) as avg_apg FROM player_stats WHERE gp > 0",
        ground_truth_answer="The average number of assists per game league-wide is 2.8 APG.",
        ground_truth_data={"avg_apg": 2.8},
        category="aggregation_sql_league",
    ),
]

# ============================================================================
# COMBINED TEST SUITE (21 TOTAL)
# ============================================================================

SQL_ONLY_TEST_CASES = SIMPLE_SQL_CASES + COMPARISON_SQL_CASES + AGGREGATION_SQL_CASES

# Verify count
assert len(SQL_ONLY_TEST_CASES) == 21, f"Expected 21 cases, got {len(SQL_ONLY_TEST_CASES)}"
assert len(SIMPLE_SQL_CASES) == 7, f"Expected 7 simple cases, got {len(SIMPLE_SQL_CASES)}"
assert len(COMPARISON_SQL_CASES) == 7, f"Expected 7 comparison cases, got {len(COMPARISON_SQL_CASES)}"
assert len(AGGREGATION_SQL_CASES) == 7, f"Expected 7 aggregation cases, got {len(AGGREGATION_SQL_CASES)}"
