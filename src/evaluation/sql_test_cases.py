"""
FILE: sql_test_cases.py
STATUS: Active
RESPONSIBILITY: Test cases for SQL and Hybrid query evaluation
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

from src.evaluation.sql_evaluation import QueryType, SQLEvaluationTestCase

# SQL-only test cases (statistical queries)
SQL_TEST_CASES = [
    # Simple SQL queries
    SQLEvaluationTestCase(
        question="Who scored the most points this season?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, pts FROM player_stats ORDER BY pts DESC LIMIT 1",
        ground_truth_answer="Luka Dončić scored the most points with 2370 PTS.",
        ground_truth_data={"name": "Luka Dončić", "pts": 2370},
        category="simple_sql",
    ),
    SQLEvaluationTestCase(
        question="What is LeBron James' average points per game?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, pts, gp, ROUND(pts / gp, 1) as ppg FROM player_stats WHERE name LIKE '%LeBron%'",
        ground_truth_answer="LeBron James averages 25.7 points per game (2082 PTS / 81 GP).",
        ground_truth_data={"name": "LeBron James", "ppg": 25.7},
        category="simple_sql",
    ),
    SQLEvaluationTestCase(
        question="How many assists did Chris Paul record?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT name, ast FROM player_stats WHERE name LIKE '%Chris Paul%'",
        ground_truth_answer="Chris Paul recorded 567 assists.",
        ground_truth_data={"name": "Chris Paul", "ast": 567},
        category="simple_sql",
    ),
    # Comparison SQL queries
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
        category="comparison_sql",
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
        category="comparison_sql",
    ),
    # Aggregation SQL queries
    SQLEvaluationTestCase(
        question="What is the average 3-point percentage for all players?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT AVG(fg3_pct) as avg_3p_pct FROM player_stats WHERE fg3_pct IS NOT NULL",
        ground_truth_answer="The average 3-point percentage across all players is 35.8%.",
        ground_truth_data={"avg_3p_pct": 0.358},
        category="aggregation_sql",
    ),
    SQLEvaluationTestCase(
        question="How many players scored over 1000 points?",
        query_type=QueryType.SQL_ONLY,
        expected_sql="SELECT COUNT(*) as player_count FROM player_stats WHERE pts > 1000",
        ground_truth_answer="127 players scored over 1000 points this season.",
        ground_truth_data={"player_count": 127},
        category="aggregation_sql",
    ),
]

# Hybrid test cases (require both SQL + vector search)
HYBRID_TEST_CASES = [
    SQLEvaluationTestCase(
        question="Compare Jokić and Embiid's stats and explain who's better",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT name, pts, reb, ast, fg_pct, per FROM player_stats WHERE name IN ('Nikola Jokić', 'Joel Embiid')",
        ground_truth_answer=(
            "Nikola Jokić: 2018 PTS, 891 REB, 688 AST, 58.3% FG, 27.1 PER. "
            "Joel Embiid: 2159 PTS, 813 REB, 296 AST, 52.9% FG, 28.5 PER. "
            "While Embiid edges Jokić in scoring and PER, Jokić's superior playmaking "
            "(688 vs 296 assists) and passing ability make him the more complete player. "
            "Jokić's efficiency (58.3% FG) and triple-double threat give him the edge for MVP."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2018, "reb": 891, "ast": 688},
            {"name": "Joel Embiid", "pts": 2159, "reb": 813, "ast": 296},
        ],
        category="hybrid_comparison",
    ),
    SQLEvaluationTestCase(
        question="Who has the best 3-point percentage and why are they so effective?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT name, fg3_pct, fg3m, fg3a FROM player_stats ORDER BY fg3_pct DESC LIMIT 1",
        ground_truth_answer=(
            "Seth Curry has the best 3-point percentage at 45.3% (157/347 3PM/3PA). "
            "His effectiveness comes from excellent shot selection, consistent mechanics, "
            "and taking high-percentage looks from catch-and-shoot situations rather than "
            "contested pull-ups."
        ),
        ground_truth_data={"name": "Seth Curry", "fg3_pct": 0.453, "fg3m": 157},
        category="hybrid_analysis",
    ),
    SQLEvaluationTestCase(
        question="What are LeBron James' stats and how does his playstyle work?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT name, pts, reb, ast, gp FROM player_stats WHERE name LIKE '%LeBron%'",
        ground_truth_answer=(
            "LeBron James: 2082 PTS, 534 REB, 587 AST in 81 GP (25.7 PPG, 6.6 RPG, 7.2 APG). "
            "His playstyle combines elite court vision with physical dominance. He acts as a "
            "point-forward, orchestrating the offense while also scoring efficiently in transition "
            "and in the paint. His high basketball IQ allows him to make the right play whether "
            "scoring, passing, or facilitating for teammates."
        ),
        ground_truth_data={"name": "LeBron James", "pts": 2082, "reb": 534, "ast": 587},
        category="hybrid_analysis",
    ),
    SQLEvaluationTestCase(
        question="Show me Giannis' stats and explain why he's a good defender",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT name, pts, reb, blk, stl FROM player_stats WHERE name LIKE '%Giannis%'",
        ground_truth_answer=(
            "Giannis Antetokounmpo: 2017 PTS, 912 REB, 61 BLK, 81 STL. "
            "His defensive prowess stems from his exceptional length (7'3\" wingspan), "
            "quick lateral movement for his size, and versatility to guard 1-5. He can "
            "protect the rim with blocks, disrupt passing lanes with steals, and switch "
            "onto guards and bigs effectively. His high motor and instincts make him a "
            "two-time Defensive Player of the Year."
        ),
        ground_truth_data={"name": "Giannis Antetokounmpo", "pts": 2017, "reb": 912, "blk": 61},
        category="hybrid_analysis",
    ),
]

# Contextual-only test cases (pure vector search, no SQL needed)
CONTEXTUAL_TEST_CASES = [
    SQLEvaluationTestCase(
        question="Why is LeBron considered one of the greatest?",
        query_type=QueryType.CONTEXTUAL_ONLY,
        expected_sql=None,
        ground_truth_answer=(
            "LeBron James is considered one of the greatest due to his longevity, "
            "versatility, and sustained excellence. He's a 4-time MVP, 4-time champion, "
            "and all-time leading scorer. His ability to dominate all facets of the game "
            "(scoring, passing, rebounding, defense) while elevating teammates makes him unique."
        ),
        ground_truth_data=None,
        category="contextual",
    ),
    SQLEvaluationTestCase(
        question="What makes Curry's shooting so special?",
        query_type=QueryType.CONTEXTUAL_ONLY,
        expected_sql=None,
        ground_truth_answer=(
            "Curry revolutionized basketball with his unprecedented range, quick release, "
            "and ability to shoot off the dribble. His gravity creates space for teammates, "
            "and his movement without the ball forces defenses to overextend. He's transformed "
            "the game by proving that elite shooting can be a primary offensive weapon."
        ),
        ground_truth_data=None,
        category="contextual",
    ),
    SQLEvaluationTestCase(
        question="How has the Warriors' dynasty impacted the NBA?",
        query_type=QueryType.CONTEXTUAL_ONLY,
        expected_sql=None,
        ground_truth_answer=(
            "The Warriors dynasty (2015-2022) revolutionized the NBA by prioritizing "
            "3-point shooting, ball movement, and positionless basketball. Their success "
            "with Curry, Thompson, and Green led to league-wide changes in offensive strategy, "
            "with teams emphasizing spacing and perimeter shooting over traditional big-man play."
        ),
        ground_truth_data=None,
        category="contextual",
    ),
]

# Combined test suite
ALL_SQL_TEST_CASES = SQL_TEST_CASES + HYBRID_TEST_CASES + CONTEXTUAL_TEST_CASES
