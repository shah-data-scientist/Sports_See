"""
FILE: sql_test_cases.py
STATUS: Active
RESPONSIBILITY: Comprehensive SQL and contextual test cases for evaluation
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

from src.evaluation.sql_evaluation import QueryType, SQLEvaluationTestCase

# ============================================================================
# SIMPLE SQL QUERIES (17 cases)
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
    SQLEvaluationTestCase(
        question="How many players on the Lakers roster?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM players WHERE team_abbr = 'LAL'",
        ground_truth_answer="This query counts the number of Lakers players in the roster.",
        ground_truth_data={"player_count": None},
        category="simple_sql_team_roster",
    ),
    SQLEvaluationTestCase(
        question="List all players on the Golden State Warriors.",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name FROM players WHERE team_abbr = 'GSW' ORDER BY name",
        ground_truth_answer="This query lists all Warriors players by name.",
        ground_truth_data=[],
        category="simple_sql_team_roster",
    ),
    SQLEvaluationTestCase(
        question="What is the average player age in the NBA?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(age) as avg_age FROM players WHERE age IS NOT NULL",
        ground_truth_answer="This calculates the average age across all NBA players.",
        ground_truth_data={"avg_age": None},
        category="aggregation_sql_league",
    ),
]

# ============================================================================
# COMPARISON SQL QUERIES (14 cases)
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
# AGGREGATION SQL QUERIES (17 cases)
# League-wide stats, AVG/COUNT/MAX, calculations
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
    SQLEvaluationTestCase(
        question="What is the total number of three-pointers made by all players combined?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT SUM(three_pm) as total_3pm FROM player_stats",
        ground_truth_answer="This sums all three-pointers made across the entire league.",
        ground_truth_data={"total_3pm": None},
        category="aggregation_sql_league",
    ),
    SQLEvaluationTestCase(
        question="How many players have a Player Impact Estimate (PIE) above 0.15?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pie > 0.15",
        ground_truth_answer="This counts players with PIE greater than 0.15 (15%).",
        ground_truth_data={"player_count": None},
        category="aggregation_sql_count",
    ),
    SQLEvaluationTestCase(
        question="What is the maximum number of blocks recorded by any player?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT MAX(blk) as max_blocks FROM player_stats",
        ground_truth_answer="This finds the highest block total by any single player.",
        ground_truth_data={"max_blocks": None},
        category="aggregation_sql_league",
    ),
]

# ============================================================================
# COMPLEX SQL QUERIES (12 cases)
# Subqueries, multiple joins, calculated fields, advanced filtering
# ============================================================================

COMPLEX_SQL_CASES = [
    SQLEvaluationTestCase(
        question="Which players score more points per game than the league average?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 0 AND ps.pts*1.0/ps.gp > (SELECT AVG(pts*1.0/gp) FROM player_stats WHERE gp > 0)"
        ),
        ground_truth_answer="Players with above-average PPG (subquery comparison).",
        ground_truth_data=None,
        category="complex_sql_subquery",
    ),
    SQLEvaluationTestCase(
        question="Find players with both high scoring (1500+ points) and high assists (300+ assists)",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts >= 1500 AND ps.ast >= 300 "
            "ORDER BY ps.pts DESC"
        ),
        ground_truth_answer="Dual-threat players excelling in both scoring and playmaking.",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "ast": 486},
            {"name": "Nikola Jokić", "pts": 2072, "ast": 714},
            {"name": "Anthony Edwards", "pts": 2180, "ast": 333},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "ast": 436},
        ],
        category="complex_sql_multiple_conditions",
    ),
    SQLEvaluationTestCase(
        question="Who are the most efficient scorers among players with 50+ games played?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.fg_pct, ps.pts, ps.gp FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp >= 50 AND ps.fg_pct IS NOT NULL "
            "ORDER BY ps.fg_pct DESC LIMIT 10"
        ),
        ground_truth_answer="Top 10 most efficient scorers (highest FG%) with 50+ games.",
        ground_truth_data=None,
        category="complex_sql_filtering",
    ),
    SQLEvaluationTestCase(
        question="Which players have triple-digit stats in points, rebounds, and assists?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts >= 100 AND ps.reb >= 100 AND ps.ast >= 100"
        ),
        ground_truth_answer="Versatile players with 100+ in PTS, REB, and AST.",
        ground_truth_data=None,
        category="complex_sql_multiple_conditions",
    ),
    SQLEvaluationTestCase(
        question="Find the top 5 players by total defensive actions (steals + blocks)",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.stl, ps.blk, (ps.stl + ps.blk) as defensive_actions "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY (ps.stl + ps.blk) DESC LIMIT 5"
        ),
        ground_truth_answer="Top 5 defenders by combined steals and blocks.",
        ground_truth_data=[
            {"name": "Dyson Daniels", "stl": 228, "blk": 53, "defensive_actions": 281},
            {"name": "Victor Wembanyama", "stl": 51, "blk": 175, "defensive_actions": 226},
            {"name": "Shai Gilgeous-Alexander", "stl": 129, "blk": 76, "defensive_actions": 205},
        ],
        category="complex_sql_calculated_field",
    ),
    SQLEvaluationTestCase(
        question="Which players have better than 50% field goal percentage AND 35%+ from three?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.fg_pct, ps.three_pct FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.fg_pct >= 50 AND ps.three_pct >= 35"
        ),
        ground_truth_answer="Elite two-way shooters with 50%+ FG and 35%+ 3P%.",
        ground_truth_data=None,
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
    SQLEvaluationTestCase(
        question="Who are the top 3 players in points per game among those who played at least 70 games?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp >= 70 "
            "ORDER BY (ps.pts*1.0/ps.gp) DESC LIMIT 3"
        ),
        ground_truth_answer="Top 3 PPG leaders among players with 70+ games (durability + scoring).",
        ground_truth_data=None,
        category="complex_sql_filtering_calculation",
    ),
    SQLEvaluationTestCase(
        question="Find all players who score more than they assist by at least 10 points per game",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, "
            "ROUND(ps.pts*1.0/ps.gp, 1) as ppg, "
            "ROUND(ps.ast*1.0/ps.gp, 1) as apg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 0 AND (ps.pts*1.0/ps.gp - ps.ast*1.0/ps.gp) >= 10"
        ),
        ground_truth_answer="Score-first players with 10+ point gap between PPG and APG.",
        ground_truth_data=None,
        category="complex_sql_differential",
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
        ground_truth_answer="Best playmakers by AST/TO ratio (300+ assists, low turnovers).",
        ground_truth_data=None,
        category="complex_sql_ratio_calculation",
    ),
    SQLEvaluationTestCase(
        question="Find the most versatile players with at least 1000 points, 400 rebounds, and 200 assists",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p "
            "JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts >= 1000 AND ps.reb >= 400 AND ps.ast >= 200 "
            "ORDER BY (ps.pts + ps.reb + ps.ast) DESC"
        ),
        ground_truth_answer="All-around contributors (1000+ PTS, 400+ REB, 200+ AST).",
        ground_truth_data=None,
        category="complex_sql_versatility",
    ),
    SQLEvaluationTestCase(
        question="What percentage of players have a true shooting percentage above 60%?",
        query_type=QueryType.SQL_ONLY,
        expected_sql=(
            "SELECT "
            "ROUND(100.0 * COUNT(CASE WHEN ts_pct > 60 THEN 1 END) / COUNT(*), 1) as pct_above_60 "
            "FROM player_stats WHERE ts_pct IS NOT NULL"
        ),
        ground_truth_answer="Percentage of players with TS% above 60%.",
        ground_truth_data=None,
        category="complex_sql_percentage_calculation",
    ),
]

# ============================================================================
# CONVERSATIONAL SQL QUERIES (8 cases)
# Follow-up questions, context-dependent, pronouns
# ============================================================================

CONVERSATIONAL_SQL_CASES = [
    SQLEvaluationTestCase(
        question="Show me the top scorer",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander is the top scorer with 2485 points.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="conversational_initial",
    ),
    SQLEvaluationTestCase(
        question="What about his assists?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Shai%'",
        ground_truth_answer="Shai Gilgeous-Alexander has 486 assists (follow-up).",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "ast": 486},
        category="conversational_followup",
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
        question="How many games did he play?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Zubac%'",
        ground_truth_answer="Ivica Zubac played 80 games (contextual follow-up).",
        ground_truth_data={"name": "Ivica Zubac", "gp": 80},
        category="conversational_followup",
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
        question="Compare him to Curry",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('LeBron James', 'Stephen Curry')",
        ground_truth_answer="LeBron vs Curry comparison (contextual).",
        ground_truth_data=None,
        category="conversational_comparison",
    ),
    SQLEvaluationTestCase(
        question="Show the assist leaders",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.ast DESC LIMIT 5",
        ground_truth_answer="Top 5 assist leaders.",
        ground_truth_data=None,
        category="conversational_casual",
    ),
    SQLEvaluationTestCase(
        question="Which of them plays for the Hawks?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT p.name, p.team_abbr, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.team_abbr = 'ATL' ORDER BY ps.ast DESC LIMIT 1",
        ground_truth_answer="Trae Young plays for the Hawks and leads them in assists.",
        ground_truth_data=None,
        category="conversational_filter_followup",
    ),
]

# ============================================================================
# COMBINED TEST SUITE
# ============================================================================

SQL_TEST_CASES = (
    SIMPLE_SQL_CASES +
    COMPARISON_SQL_CASES +
    AGGREGATION_SQL_CASES +
    COMPLEX_SQL_CASES +
    CONVERSATIONAL_SQL_CASES
)

# ============================================================================
# HYBRID QUERIES (SQL + Vector Integration)
# Queries requiring both statistical data AND contextual analysis
# ============================================================================

HYBRID_TEST_CASES = [
    # Tier 1: Simple stat + basic context
    SQLEvaluationTestCase(
        question="Who scored the most points this season and what makes them an effective scorer?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander scored 2485 points. His effectiveness comes from his ability to get to the rim and draw fouls.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="tier1_stat_plus_context",
    ),
    SQLEvaluationTestCase(
        question="Compare LeBron James and Kevin Durant's scoring this season and explain their scoring styles.",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('LeBron James', 'Kevin Durant')",
        ground_truth_answer="LeBron James: 1708 PTS. Kevin Durant: 1649 PTS. LeBron uses strength and playmaking while Durant relies on elite shooting.",
        ground_truth_data=[
            {"name": "LeBron James", "pts": 1708},
            {"name": "Kevin Durant", "pts": 1649},
        ],
        category="tier1_comparison_plus_context",
    ),
    SQLEvaluationTestCase(
        question="What is Nikola Jokić's scoring average and why is he considered an elite offensive player?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Jokić%'",
        ground_truth_answer="Jokić averages 29.6 PPG (2072 PTS in 70 GP). He's elite because of his versatile scoring, exceptional passing, and high basketball IQ.",
        ground_truth_data={"name": "Nikola Jokić", "pts": 2072, "gp": 70},
        category="tier1_stat_plus_explanation",
    ),
    SQLEvaluationTestCase(
        question="Who are the top 3 rebounders and what impact do they have on their teams?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.reb DESC LIMIT 3",
        ground_truth_answer="Top 3: Ivica Zubac (1008), Domantas Sabonis (973), Karl-Anthony Towns (922). They create second-chance opportunities and control the boards.",
        ground_truth_data=[
            {"name": "Ivica Zubac", "reb": 1008},
            {"name": "Domantas Sabonis", "reb": 973},
            {"name": "Karl-Anthony Towns", "reb": 922}
        ],
        category="tier1_leaders_plus_impact",
    ),

    # Tier 2: Moderate complexity with multi-stat analysis
    SQLEvaluationTestCase(
        question="Compare Jokić and Embiid's stats and explain which one is more valuable based on their playing style.",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Joel Embiid')",
        ground_truth_answer="Jokić: 2072 PTS, 889 REB, 714 AST (PIE: 20.6). Embiid: 452 PTS, 156 REB, 86 AST (PIE: 16.9). Jokić excels in playmaking while Embiid dominates with scoring and defense.",
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714, "pie": 20.6},
            {"name": "Joel Embiid", "pts": 452, "reb": 156, "ast": 86, "pie": 16.9},
        ],
        category="tier2_comparison_advanced",
    ),
    SQLEvaluationTestCase(
        question="Who are the most efficient scorers by true shooting percentage and what makes them efficient?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.ts_pct, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.gp > 50 ORDER BY ps.ts_pct DESC LIMIT 5",
        ground_truth_answer="Top efficient scorers have high TS% because of good shot selection, high free throw rates, and effective three-point shooting.",
        ground_truth_data=None,
        category="tier2_efficiency_analysis",
    ),
    SQLEvaluationTestCase(
        question="Compare Giannis and Anthony Davis's rebounds and explain how their rebounding styles differ.",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.reb, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Giannis Antetokounmpo', 'Anthony Davis')",
        ground_truth_answer="Giannis: 797 REB. Davis: 592 REB. Giannis uses length and athleticism for rebounds, while Davis combines timing and positioning.",
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "reb": 797},
            {"name": "Anthony Davis", "reb": 592},
        ],
        category="tier2_style_comparison",
    ),
    SQLEvaluationTestCase(
        question="Who has the best assist-to-turnover ratio among high-volume passers and why is this important?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.ast, ps.tov, ROUND(ps.ast*1.0/ps.tov, 2) as ratio FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ast >= 300 AND ps.tov > 0 ORDER BY (ps.ast*1.0/ps.tov) DESC LIMIT 5",
        ground_truth_answer="High AST/TO ratio indicates excellent decision-making and ball security, crucial for winning basketball by maximizing possessions.",
        ground_truth_data=None,
        category="tier2_efficiency_metric",
    ),

    # Tier 3: Complex multi-dimensional analysis
    SQLEvaluationTestCase(
        question="Find players averaging triple-double stats and explain what makes this achievement so rare and valuable.",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ROUND(ps.pts*1.0/ps.gp,1) as ppg, ROUND(ps.reb*1.0/ps.gp,1) as rpg, ROUND(ps.ast*1.0/ps.gp,1) as apg FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.gp > 0 AND ps.pts*1.0/ps.gp >= 10 AND ps.reb*1.0/ps.gp >= 10 AND ps.ast*1.0/ps.gp >= 10",
        ground_truth_answer="Nikola Jokić averages 29.6/12.7/10.2. Triple-doubles require elite versatility in scoring, rebounding, and playmaking - a rare combination.",
        ground_truth_data=[{"name": "Nikola Jokić", "ppg": 29.6, "rpg": 12.7, "apg": 10.2}],
        category="tier3_rare_achievement",
    ),
    SQLEvaluationTestCase(
        question="Which players have high scoring but low efficiency, and why might teams still rely on them?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.fg_pct, ps.ts_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts > 1500 AND ps.fg_pct < 45 ORDER BY ps.pts DESC",
        ground_truth_answer="High-volume low-efficiency scorers may still be valuable due to clutch performance, defensive attention they draw, or lack of other offensive options.",
        ground_truth_data=None,
        category="tier3_strategic_tradeoff",
    ),
    SQLEvaluationTestCase(
        question="Compare the top defensive players by blocks and steals and explain different defensive styles.",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.stl, ps.blk, (ps.stl + ps.blk) as def_actions FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY (ps.stl + ps.blk) DESC LIMIT 5",
        ground_truth_answer="Top defenders include Dyson Daniels (228 STL, 53 BLK) and Victor Wembanyama (51 STL, 175 BLK). Daniels excels at perimeter defense while Wembanyama is an elite rim protector.",
        ground_truth_data=[
            {"name": "Dyson Daniels", "stl": 228, "blk": 53},
            {"name": "Victor Wembanyama", "stl": 51, "blk": 175},
        ],
        category="tier3_defensive_styles",
    ),
    SQLEvaluationTestCase(
        question="Analyze players with 1500+ points and 400+ assists - what does this dual threat mean strategically?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts >= 1500 AND ps.ast >= 300 ORDER BY ps.pts DESC",
        ground_truth_answer="Dual-threat scorers and playmakers force defenses to make difficult choices, creating advantages for teammates while maintaining personal scoring threat.",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "ast": 486},
            {"name": "Nikola Jokić", "pts": 2072, "ast": 714},
        ],
        category="tier3_dual_threat_strategy",
    ),

    # Tier 4: Advanced synthesis with league-wide trends
    SQLEvaluationTestCase(
        question="What's the relationship between three-point shooting volume and efficiency, and how has this changed the modern NBA?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT AVG(three_pct) as avg_3p, COUNT(*) as player_count FROM player_stats WHERE three_pct IS NOT NULL",
        ground_truth_answer="Modern NBA emphasizes three-point shooting due to analytics showing its efficiency. The 'three-point revolution' has changed offensive strategies and floor spacing.",
        ground_truth_data={"avg_3p": 29.9},
        category="tier4_league_trend_analysis",
    ),
    SQLEvaluationTestCase(
        question="Compare advanced efficiency metrics (PIE, TS%) for MVP candidates and explain what these metrics reveal about player impact.",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pie, ps.ts_pct, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts > 1800 ORDER BY ps.pie DESC LIMIT 5",
        ground_truth_answer="PIE measures overall player impact while TS% captures scoring efficiency. Together they reveal both productivity and effectiveness in generating value.",
        ground_truth_data=None,
        category="tier4_advanced_metrics_interpretation",
    ),
    SQLEvaluationTestCase(
        question="How do young players (high stats) compare to established stars, and what does this suggest about the league's future?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, p.age, ps.pts, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.age IS NOT NULL ORDER BY ps.pts DESC LIMIT 10",
        ground_truth_answer="Young stars with elite stats suggest a generational talent shift, with younger players developing skills faster through modern training and analytics.",
        ground_truth_data=None,
        category="tier4_generational_shift",
    ),
    SQLEvaluationTestCase(
        question="Analyze the correlation between assists and team success - which high-assist players drive winning?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.ast, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ast > 500 ORDER BY ps.ast DESC",
        ground_truth_answer="High-assist players like Trae Young (882 AST) facilitate team offense. Playmaking correlates with winning by creating efficient shot opportunities for teammates.",
        ground_truth_data=[{"name": "Trae Young", "ast": 882}],
        category="tier4_correlation_analysis",
    ),
]

# Verify counts
print(f"SQL Test Cases Loaded: {len(SQL_TEST_CASES)} cases")
print(f"Hybrid Test Cases Loaded: {len(HYBRID_TEST_CASES)} cases")
assert len(SIMPLE_SQL_CASES) == 17, f"Expected 17 simple cases, got {len(SIMPLE_SQL_CASES)}"
assert len(COMPARISON_SQL_CASES) == 14, f"Expected 14 comparison cases, got {len(COMPARISON_SQL_CASES)}"
assert len(AGGREGATION_SQL_CASES) == 17, f"Expected 17 aggregation cases, got {len(AGGREGATION_SQL_CASES)}"
assert len(COMPLEX_SQL_CASES) == 12, f"Expected 12 complex cases, got {len(COMPLEX_SQL_CASES)}"
assert len(CONVERSATIONAL_SQL_CASES) == 8, f"Expected 8 conversational cases, got {len(CONVERSATIONAL_SQL_CASES)}"
assert len(SQL_TEST_CASES) == 68, f"Expected 68 SQL cases, got {len(SQL_TEST_CASES)}"
assert len(HYBRID_TEST_CASES) == 16, f"Expected 16 hybrid cases, got {len(HYBRID_TEST_CASES)}"
