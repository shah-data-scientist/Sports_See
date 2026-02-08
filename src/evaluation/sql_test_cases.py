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

# Phase 10: Hybrid test cases (require both SQL + vector search)
# 20+ test cases across 4 complexity tiers
HYBRID_TEST_CASES = [
    # ========== TIER 1: Simple Hybrid (5-7 cases) ==========
    # Single player analysis with stats + playstyle context
    SQLEvaluationTestCase(
        question="What are LeBron James' stats and how does his playstyle work?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%LeBron%'",
        ground_truth_answer=(
            "LeBron James: 1708 PTS, 546 REB, 574 AST in 70 GP (24.4 PPG, 7.8 RPG, 8.2 APG). "
            "His playstyle combines elite court vision with physical dominance. He acts as a "
            "point-forward, orchestrating the offense while also scoring efficiently in transition "
            "and in the paint. His high basketball IQ allows him to make the right play whether "
            "scoring, passing, or facilitating for teammates."
        ),
        ground_truth_data={"name": "LeBron James", "pts": 1708, "reb": 546, "ast": 574, "gp": 70},
        category="tier1_simple",
    ),
    SQLEvaluationTestCase(
        question="Show me Giannis' stats and explain why he's a good defender",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.blk, ps.stl FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Giannis%'",
        ground_truth_answer=(
            "Giannis Antetokounmpo: 2037 PTS, 797 REB, 80 BLK, 60 STL. "
            "His defensive prowess stems from his exceptional length (7'3\" wingspan), "
            "quick lateral movement for his size, and versatility to guard 1-5. He can "
            "protect the rim with blocks, disrupt passing lanes with steals, and switch "
            "onto guards and bigs effectively. His high motor and instincts make him a "
            "two-time Defensive Player of the Year."
        ),
        ground_truth_data={"name": "Giannis Antetokounmpo", "pts": 2037, "reb": 797, "blk": 80, "stl": 60},
        category="tier1_simple",
    ),
    SQLEvaluationTestCase(
        question="What makes Shai Gilgeous-Alexander effective? Show his stats",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.stl, ps.blk, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Shai%'",
        ground_truth_answer=(
            "Shai Gilgeous-Alexander: 2485 PTS, 380 REB, 486 AST, 129 STL, 76 BLK in 76 GP (32.7 PPG). "
            "He's effective due to his elite scoring ability, combining crafty ball-handling with "
            "exceptional finishing at the rim. His length allows him to be disruptive defensively "
            "(129 STL, 76 BLK), making him a two-way threat. His ability to get to the free throw "
            "line and score efficiently in isolation sets him apart."
        ),
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485, "reb": 380, "ast": 486, "stl": 129, "blk": 76, "gp": 76},
        category="tier1_simple",
    ),
    SQLEvaluationTestCase(
        question="Who has the best 3-point percentage and why are they so effective?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.three_pct, ps.three_pm, ps.three_pa FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.three_pa >= 100 ORDER BY ps.three_pct DESC LIMIT 1",
        ground_truth_answer=(
            "Seth Curry has the best 3-point percentage at 45.6% (0/184 3PM/3PA). "
            "His effectiveness comes from excellent shot selection, consistent mechanics, "
            "and taking high-percentage looks from catch-and-shoot situations rather than "
            "contested pull-ups. He's a pure shooter who understands spacing and moves "
            "without the ball to get open looks."
        ),
        ground_truth_data={"name": "Seth Curry", "three_pct": 45.6, "three_pm": 0, "three_pa": 184},
        category="tier1_simple",
    ),
    SQLEvaluationTestCase(
        question="What are Victor Wembanyama's defensive stats and why is he impactful?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.blk, ps.stl, ps.reb, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Wembanyama%'",
        ground_truth_answer=(
            "Victor Wembanyama: 175 BLK, 51 STL with exceptional rim protection. "
            "His impact comes from his rare combination of 7'4\" height with 8'0\" wingspan, "
            "allowing him to alter and block shots at an elite level (175 BLK). His mobility "
            "and defensive IQ enable him to guard multiple positions and protect the paint "
            "while also contributing to perimeter defense (51 STL)."
        ),
        ground_truth_data={"name": "Victor Wembanyama", "blk": 175, "stl": 51},
        category="tier1_simple",
    ),
    SQLEvaluationTestCase(
        question="Show me Trae Young's playmaking stats and explain his style",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.ast, ps.pts, ps.gp, ROUND(ps.ast * 1.0 / ps.gp, 1) as apg FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Trae%'",
        ground_truth_answer=(
            "Trae Young: 882 AST, 1839 PTS in 76 GP (11.6 APG, 24.2 PPG). "
            "His playmaking style is defined by elite court vision and passing ability, "
            "leading the league in assists (882 AST, 11.6 APG). He combines scoring threat "
            "with exceptional passing, using pick-and-roll to break down defenses and create "
            "for teammates. His deep range forces defenses to extend, opening passing lanes."
        ),
        ground_truth_data={"name": "Trae Young", "ast": 882, "pts": 1839, "gp": 76},
        category="tier1_simple",
    ),

    # ========== TIER 2: Moderate Hybrid (5-7 cases) ==========
    # Player comparisons with stats + contextual analysis
    SQLEvaluationTestCase(
        question="Compare Jokić and Embiid's stats and explain who's better",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Joel Embiid')",
        ground_truth_answer=(
            "Nikola Jokić: 2072 PTS, 889 REB, 714 AST, 57.6% FG. "
            "Joel Embiid: 452 PTS, 156 REB, 86 AST, 44.4% FG. "
            "Jokić is clearly superior this season with much higher volume and efficiency. "
            "His exceptional playmaking (714 vs 86 assists) and passing ability make him "
            "the more complete player. Jokić's efficiency (57.6% FG) and triple-double threat, "
            "combined with elite rebounding (889 REB) and scoring (2072 PTS), give him the edge for MVP."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714, "fg_pct": 57.6},
            {"name": "Joel Embiid", "pts": 452, "reb": 156, "ast": 86, "fg_pct": 44.4},
        ],
        category="tier2_moderate",
    ),
    SQLEvaluationTestCase(
        question="Compare Shai Gilgeous-Alexander and Anthony Edwards as scorers",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts * 1.0 / ps.gp, 1) as ppg, ps.fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Shai Gilgeous-Alexander', 'Anthony Edwards')",
        ground_truth_answer=(
            "Shai Gilgeous-Alexander: 2485 PTS in 76 GP (32.7 PPG). "
            "Anthony Edwards: 2180 PTS in 79 GP (27.6 PPG). "
            "Shai is the superior scorer with a 5.1 PPG advantage. His scoring comes from "
            "elite mid-range game and ability to get to the rim, while Edwards relies more "
            "on athleticism and three-point shooting. Shai's efficiency and consistency in "
            "getting his own shot make him more reliable as a primary scoring option."
        ),
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "gp": 76},
            {"name": "Anthony Edwards", "pts": 2180, "gp": 79},
        ],
        category="tier2_moderate",
    ),
    SQLEvaluationTestCase(
        question="Who is the better rebounder: Jokić or Sabonis? Include their stats",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.reb, ps.gp, ROUND(ps.reb * 1.0 / ps.gp, 1) as rpg FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Nikola Jokić', 'Domantas Sabonis')",
        ground_truth_answer=(
            "Nikola Jokić: 889 REB in 70 GP (12.7 RPG). "
            "Domantas Sabonis: 973 REB in 70 GP (13.9 RPG). "
            "Sabonis is the superior rebounder with a +1.2 RPG advantage. His relentless motor "
            "and positioning make him one of the league's best rebounders. However, Jokić's "
            "rebounding is still elite for a center, and he adds superior playmaking and scoring "
            "to make him the more well-rounded player overall."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "reb": 889, "gp": 70},
            {"name": "Domantas Sabonis", "reb": 973, "gp": 70},
        ],
        category="tier2_moderate",
    ),
    SQLEvaluationTestCase(
        question="Compare Dyson Daniels and Victor Wembanyama as defenders with their stats",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.blk, ps.stl, (ps.blk + ps.stl) as defensive_actions FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Dyson Daniels', 'Victor Wembanyama')",
        ground_truth_answer=(
            "Dyson Daniels: 53 BLK, 228 STL (281 total defensive actions). "
            "Victor Wembanyama: 175 BLK, 51 STL (226 total defensive actions). "
            "Daniels leads in total defensive actions (281 vs 226), driven by exceptional "
            "steal numbers (228 STL) from elite perimeter defense and anticipation. "
            "Wembanyama dominates in rim protection (175 BLK) with his elite length and timing. "
            "They excel in different defensive roles - Daniels as perimeter disruptor, "
            "Wembanyama as paint protector."
        ),
        ground_truth_data=[
            {"name": "Dyson Daniels", "blk": 53, "stl": 228},
            {"name": "Victor Wembanyama", "blk": 175, "stl": 51},
        ],
        category="tier2_moderate",
    ),
    SQLEvaluationTestCase(
        question="Compare Trae Young and Tyrese Haliburton as playmakers",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.ast, ps.gp, ROUND(ps.ast * 1.0 / ps.gp, 1) as apg FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name IN ('Trae Young', 'Tyrese Haliburton')",
        ground_truth_answer=(
            "Trae Young: 882 AST in 76 GP (11.6 APG). "
            "Tyrese Haliburton: 672 AST in 73 GP (9.2 APG). "
            "Trae Young is the superior playmaker with a +2.4 APG advantage. His elite court "
            "vision, pick-and-roll mastery, and ability to create off the dribble make him "
            "one of the league's best passers. Haliburton is still excellent with great "
            "decision-making, but Trae's scoring threat and creativity give him the edge."
        ),
        ground_truth_data=[
            {"name": "Trae Young", "ast": 882, "gp": 76},
            {"name": "Tyrese Haliburton", "ast": 672, "gp": 73},
        ],
        category="tier2_moderate",
    ),
    SQLEvaluationTestCase(
        question="Who are the most efficient scorers among high-volume players?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts >= 1500 ORDER BY ps.fg_pct DESC LIMIT 3",
        ground_truth_answer=(
            "Among high-volume scorers (1500+ PTS), the most efficient are players who combine "
            "scoring volume with shooting efficiency. Look for centers and forwards who score "
            "near the rim with high field goal percentages. Efficiency at high volume is rare "
            "and requires excellent shot selection, finishing ability, and offensive system fit."
        ),
        ground_truth_data=None,
        category="tier2_moderate",
    ),

    # ========== TIER 3: Complex Hybrid (5-7 cases) ==========
    # Multi-player cross-analysis with advanced stats + historical context
    SQLEvaluationTestCase(
        question="Which high-scoring players are also elite defenders?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, (ps.blk + ps.stl) as defensive_actions FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts >= 1800 ORDER BY (ps.blk + ps.stl) DESC LIMIT 5",
        ground_truth_answer=(
            "Among elite scorers (1800+ PTS), two-way excellence is rare. "
            "Shai Gilgeous-Alexander (2485 PTS, 205 defensive actions) and "
            "Giannis Antetokounmpo (2037 PTS, 140 defensive actions) stand out as "
            "legitimate two-way stars who can carry offensive load while providing "
            "elite defense. Their combination of scoring volume and defensive impact "
            "makes them among the league's most valuable players."
        ),
        ground_truth_data=None,
        category="tier3_complex",
    ),
    SQLEvaluationTestCase(
        question="Compare the top 3 scorers and explain their different scoring approaches",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts * 1.0 / ps.gp, 1) as ppg, ps.fg_pct, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 3",
        ground_truth_answer=(
            "Top 3 scorers: "
            "1. Shai Gilgeous-Alexander (2485 PTS, 32.7 PPG) - Elite mid-range and rim finisher "
            "2. Anthony Edwards (2180 PTS, 27.6 PPG) - Athletic scorer with three-point range "
            "3. Nikola Jokić (2072 PTS, 29.6 PPG) - Versatile big with elite efficiency (57.6% FG). "
            "Each represents a different archetype: Shai's crafty scoring, Edwards' explosive athleticism, "
            "and Jokić's high-IQ versatile game show multiple paths to elite scoring."
        ),
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "gp": 76},
            {"name": "Anthony Edwards", "pts": 2180, "gp": 79},
            {"name": "Nikola Jokić", "pts": 2072, "gp": 70},
        ],
        category="tier3_complex",
    ),
    SQLEvaluationTestCase(
        question="Who are the triple-double threats and why are they valuable?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts >= 1500 AND ps.reb >= 500 AND ps.ast >= 500",
        ground_truth_answer=(
            "Triple-double threats who excel in all three categories (1500+ PTS, 500+ REB, 500+ AST): "
            "Nikola Jokić (2072 PTS, 889 REB, 714 AST) and LeBron James (1708 PTS, 546 REB, 574 AST). "
            "Their value comes from complete offensive impact - they can score, create for others, "
            "and control possessions. This versatility makes them impossible to game-plan against "
            "and allows their teams to build flexible offensive systems around them."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714, "gp": 70},
            {"name": "LeBron James", "pts": 1708, "reb": 546, "ast": 574, "gp": 70},
        ],
        category="tier3_complex",
    ),
    SQLEvaluationTestCase(
        question="Which centers dominate rebounding and why is that important?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.reb, ps.gp, ROUND(ps.reb * 1.0 / ps.gp, 1) as rpg FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.reb DESC LIMIT 5",
        ground_truth_answer=(
            "Top rebounders: Ivica Zubac (1008 REB, 12.6 RPG), Domantas Sabonis (973 REB, 13.9 RPG), "
            "Karl-Anthony Towns (922 REB, 12.8 RPG), Nikola Jokić (889 REB, 12.7 RPG), "
            "Jalen Duren (803 REB, 10.3 RPG). Elite rebounding is crucial for controlling possessions, "
            "limiting second-chance points, and starting fast breaks. These centers provide defensive "
            "anchoring and additional possessions, directly correlating with team success."
        ),
        ground_truth_data=[
            {"name": "Ivica Zubac", "reb": 1008, "gp": 80},
            {"name": "Domantas Sabonis", "reb": 973, "gp": 70},
            {"name": "Karl-Anthony Towns", "reb": 922, "gp": 72},
        ],
        category="tier3_complex",
    ),
    SQLEvaluationTestCase(
        question="Compare assist-to-turnover ratios for top playmakers",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.ast, ps.tov, ROUND(ps.ast * 1.0 / ps.tov, 2) as ast_to_ratio FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ast >= 500 ORDER BY (ps.ast * 1.0 / ps.tov) DESC LIMIT 5",
        ground_truth_answer=(
            "Elite playmakers with best assist-to-turnover ratios among high-volume passers (500+ AST) "
            "demonstrate exceptional decision-making and ball security. High AST/TOV ratio indicates "
            "ability to create for others while limiting mistakes. This metric separates good passers "
            "from elite playmakers who can be trusted with the ball in critical situations."
        ),
        ground_truth_data=None,
        category="tier3_complex",
    ),
    SQLEvaluationTestCase(
        question="Which players combine elite shooting with high volume?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.three_pct, ps.three_pa, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.three_pa >= 300 ORDER BY ps.three_pct DESC LIMIT 5",
        ground_truth_answer=(
            "Elite three-point shooters with high volume (300+ 3PA) are game-changers who space the "
            "floor and create gravity for teammates. High percentage on high volume indicates both "
            "shooting skill and ability to get quality looks consistently. These players force "
            "defenses to extend, opening driving lanes and creating 4-on-3 advantages."
        ),
        ground_truth_data=None,
        category="tier3_complex",
    ),

    # ========== TIER 4: Advanced Hybrid (3-5 cases) ==========
    # Nuanced analysis requiring deep contextual understanding + statistical verification
    SQLEvaluationTestCase(
        question="How has positionless basketball changed the NBA, and which players exemplify this?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts >= 1500 AND ps.reb >= 500 AND ps.ast >= 400",
        ground_truth_answer=(
            "Positionless basketball emphasizes versatility over traditional positions. Players like "
            "Nikola Jokić (2072 PTS, 889 REB, 714 AST), LeBron James (1708 PTS, 546 REB, 574 AST), "
            "and Giannis Antetokounmpo (2037 PTS, 797 REB, 436 AST) exemplify this with complete stat lines. "
            "They can handle, pass, score, and rebound, making them matchup nightmares. This evolution "
            "prioritizes skill and basketball IQ over size, transforming offensive and defensive schemes."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714},
            {"name": "LeBron James", "pts": 1708, "reb": 546, "ast": 574},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "reb": 797, "ast": 436},
        ],
        category="tier4_advanced",
    ),
    SQLEvaluationTestCase(
        question="What makes a player MVP-caliber? Compare the top candidates statistically",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.gp, ROUND(ps.pts * 1.0 / ps.gp, 1) as ppg FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 5",
        ground_truth_answer=(
            "MVP candidates combine elite production with team success and narrative. "
            "Shai Gilgeous-Alexander (32.7 PPG) leads in scoring. Nikola Jokić (29.6 PPG, 12.7 RPG, 10.2 APG) "
            "offers unmatched all-around excellence. Giannis (30.4 PPG, 11.9 RPG) provides two-way dominance. "
            "MVP requires not just stats but efficiency, winning, and irreplaceability. Jokić's rare "
            "combination of scoring, playmaking, and rebounding while leading his team makes him the frontrunner."
        ),
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "gp": 76},
            {"name": "Nikola Jokić", "pts": 2072, "gp": 70, "reb": 889, "ast": 714},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "gp": 67, "reb": 797},
        ],
        category="tier4_advanced",
    ),
    SQLEvaluationTestCase(
        question="How do modern centers differ from traditional big men statistically?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast, ps.three_pa FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.reb >= 700 ORDER BY ps.ast DESC LIMIT 5",
        ground_truth_answer=(
            "Modern centers like Nikola Jokić (714 AST, 889 REB) blend traditional rebounding "
            "with elite playmaking. Unlike traditional big men who focused solely on interior "
            "scoring and rebounding, today's centers are asked to pass, handle, and sometimes shoot threes. "
            "This evolution reflects pace-and-space offensive systems that value versatility. "
            "Centers who can facilitate (Jokić, Sabonis) provide unique advantages by creating "
            "from the high post and short roll."
        ),
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714},
        ],
        category="tier4_advanced",
    ),
    SQLEvaluationTestCase(
        question="What role does defensive versatility play in modern NBA success?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.blk, ps.stl, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE (ps.blk + ps.stl) >= 150 ORDER BY (ps.blk + ps.stl) DESC LIMIT 5",
        ground_truth_answer=(
            "Defensive versatility is crucial in modern switching defenses. Players like "
            "Dyson Daniels (228 STL, 53 BLK), Victor Wembanyama (175 BLK, 51 STL), and "
            "Shai Gilgeous-Alexander (129 STL, 76 BLK) excel in multiple defensive categories. "
            "Modern defense requires guarding multiple positions, switching on screens, and "
            "protecting the rim. Players who can both contest shots and create turnovers "
            "provide invaluable flexibility in playoff matchups."
        ),
        ground_truth_data=[
            {"name": "Dyson Daniels", "blk": 53, "stl": 228},
            {"name": "Victor Wembanyama", "blk": 175, "stl": 51},
            {"name": "Shai Gilgeous-Alexander", "blk": 76, "stl": 129},
        ],
        category="tier4_advanced",
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
