"""
FILE: hybrid_test_cases.py
STATUS: Active
RESPONSIBILITY: Hybrid test cases requiring both SQL and Vector search (51 curated cases)
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

from src.evaluation.models.sql_models import QueryType, SQLEvaluationTestCase

# ============================================================================
# HYBRID QUERIES (SQL + Vector Integration)
# Queries requiring both statistical data AND contextual analysis
# 51 cases: 18 original + 33 new (profiles, teams, young talent, historical,
#           contrast, conversational, noisy, defensive, team culture)
# ============================================================================

HYBRID_TEST_CASES = [
    # Tier 1: Simple stat + basic context (4 cases)
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

    # Tier 2: Moderate complexity with multi-stat analysis (4 cases)
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

    # Tier 3: Complex multi-dimensional analysis (4 cases)
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
        ground_truth_answer="Top 5 defenders: Dyson Daniels (228 STL, 53 BLK), Victor Wembanyama (51 STL, 175 BLK), Shai Gilgeous-Alexander (129 STL, 76 BLK), Myles Turner (58 STL, 144 BLK), Jaren Jackson Jr. (89 STL, 111 BLK). Daniels excels at perimeter defense while Wembanyama is an elite rim protector.",
        ground_truth_data=[
            {"name": "Dyson Daniels", "stl": 228, "blk": 53, "def_actions": 281},
            {"name": "Victor Wembanyama", "stl": 51, "blk": 175, "def_actions": 226},
            {"name": "Shai Gilgeous-Alexander", "stl": 129, "blk": 76, "def_actions": 205},
            {"name": "Myles Turner", "stl": 58, "blk": 144, "def_actions": 202},
            {"name": "Jaren Jackson Jr,", "stl": 89, "blk": 111, "def_actions": 200},
        ],
        category="tier3_defensive_styles",
    ),
    SQLEvaluationTestCase(
        question="Analyze players with 1500+ points and 400+ assists - what does this dual threat mean strategically?",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.pts >= 1500 AND ps.ast >= 300 ORDER BY ps.pts DESC LIMIT 5",
        ground_truth_answer="Top dual-threat players: Shai Gilgeous-Alexander (2485 PTS, 486 AST), Anthony Edwards (2180 PTS, 356 AST), Nikola Jokić (2072 PTS, 714 AST), Giannis Antetokounmpo (2037 PTS, 436 AST), Jayson Tatum (1930 PTS, 432 AST). These scorers and playmakers force defenses to make difficult choices, creating advantages for teammates while maintaining personal scoring threat.",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "ast": 486},
            {"name": "Anthony Edwards", "pts": 2180, "ast": 356},
            {"name": "Nikola Jokić", "pts": 2072, "ast": 714},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "ast": 436},
            {"name": "Jayson Tatum", "pts": 1930, "ast": 432},
        ],
        category="tier3_dual_threat_strategy",
    ),

    # Tier 4: Advanced synthesis with league-wide trends (4 cases)
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
        expected_sql="SELECT p.name, ps.ast, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE ps.ast > 500 ORDER BY ps.ast DESC LIMIT 5",
        ground_truth_answer="Top 5 high-assist players: Trae Young (882 AST, PIE 12.9), Nikola Jokić (714 AST, PIE 20.6), James Harden (687 AST, PIE 14.5), Tyrese Haliburton (672 AST, PIE 14.3), Cade Cunningham (637 AST, PIE 15.2). High-assist players facilitate team offense by creating efficient shot opportunities for teammates.",
        ground_truth_data=[
            {"name": "Trae Young", "ast": 882, "pie": 12.9},
            {"name": "Nikola Jokić", "ast": 714, "pie": 20.6},
            {"name": "James Harden", "ast": 687, "pie": 14.5},
            {"name": "Tyrese Haliburton", "ast": 672, "pie": 14.3},
            {"name": "Cade Cunningham", "ast": 637, "pie": 15.2},
        ],
        category="tier4_correlation_analysis",
    ),

    # Tier 2 additions: Team aggregation + correction comparison
    SQLEvaluationTestCase(
        question="What is the average scoring for the Warriors and how is their team culture described by fans?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT ROUND(AVG(ps.pts), 1) as avg_pts, COUNT(*) as player_count "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'GSW'"
        ),
        ground_truth_answer="Warriors average 487.5 points per player across 17 players. Fan discussions describe their culture as built on ball movement and championship pedigree.",
        ground_truth_data={"avg_pts": 487.5, "player_count": 17},
        category="tier2_team_aggregation",
    ),
    SQLEvaluationTestCase(
        question="Actually, compare Giannis to Jokić instead and explain who fans think is better",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast, ps.pie "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name IN ('Giannis Antetokounmpo', 'Nikola Jokić')"
        ),
        ground_truth_answer=(
            "Giannis Antetokounmpo: 2037 PTS, 797 REB, 436 AST (PIE 21.0). "
            "Nikola Jokić: 2072 PTS, 889 REB, 714 AST (PIE 20.6). "
            "Fan opinions are split between Giannis's dominance and Jokić's versatility."
        ),
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "pts": 2037, "reb": 797, "ast": 436, "pie": 21.0},
            {"name": "Nikola Jokić", "pts": 2072, "reb": 889, "ast": 714, "pie": 20.6},
        ],
        category="tier2_correction_comparison",
    ),

    # ======================================================================
    # PLAYER PROFILE HYBRID (4 cases)
    # Full player stats + fan perception / analysis
    # ======================================================================
    SQLEvaluationTestCase(
        question="Who is LeBron?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.team, p.age, ps.gp, ps.pts, ps.reb, ps.ast, ps.stl, ps.blk, "
            "ps.fg_pct, ps.three_pct, ps.ft_pct "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%LeBron%'"
        ),
        ground_truth_answer=(
            "LeBron James (age 40, Los Angeles Lakers): 1708 PTS, 546 REB, 574 AST, "
            "70 STL, 42 BLK in 70 GP (24.4 PPG). FG%: 51.3%, 3P%: 37.6%, FT%: 78.2%. "
            "Reddit fans describe LeBron as the NBA's biggest superstar brand who drives "
            "media narratives. He ranks among the all-time playoff greats (8289 career "
            "playoff PTS, 107 TS). Fans note his dangerous ISO game, elite playmaking, "
            "and shots near the rim make him a hybrid threat. Some debate whether AD was "
            "more impactful during their title run despite LeBron's popularity."
        ),
        ground_truth_data={
            "name": "LeBron James",
            "team": "Los Angeles Lakers",
            "age": 40,
            "gp": 70,
            "pts": 1708,
            "reb": 546,
            "ast": 574,
            "stl": 70,
            "blk": 42,
            "fg_pct": 51.3,
            "three_pct": 37.6,
            "ft_pct": 78.2,
        },
        category="hybrid_player_profile",
    ),
    SQLEvaluationTestCase(
        question="Tell me about Anthony Edwards' season stats and what makes him such an exciting player to watch",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts, ps.reb, ps.ast, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Anthony Edwards%'"
        ),
        ground_truth_answer="Anthony Edwards (age 23, Timberwolves): 2180 PTS, 450 REB, 356 AST in 79 GP (27.6 PPG). His explosiveness and scoring versatility make him one of the league's most exciting players.",
        ground_truth_data={"name": "Anthony Edwards", "age": 23, "pts": 2180, "reb": 450, "ast": 356, "gp": 79, "ppg": 27.6},
        category="hybrid_player_profile",
    ),
    SQLEvaluationTestCase(
        question="What are Victor Wembanyama's stats and why are fans so excited about his potential?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts, ps.reb, ps.blk, ps.gp "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Wembanyama%'"
        ),
        ground_truth_answer="Victor Wembanyama (age 21): 1118 PTS, 506 REB, 175 BLK in 46 GP. His combination of size, shot-blocking, and offensive skill at such a young age has fans calling him a generational talent.",
        ground_truth_data={"name": "Victor Wembanyama", "age": 21, "pts": 1118, "reb": 506, "blk": 175, "gp": 46},
        category="hybrid_player_profile",
    ),
    SQLEvaluationTestCase(
        question="Show me Trae Young's stats — is he underrated or overrated according to fans?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.ast, ps.fg_pct, ps.tov "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Trae Young%'"
        ),
        ground_truth_answer="Trae Young: 1839 PTS, 882 AST, 41.1% FG, 357 TOV. Fan debate centers on whether his elite playmaking outweighs his low efficiency and turnovers.",
        ground_truth_data={"name": "Trae Young", "pts": 1839, "ast": 882, "fg_pct": 41.1, "tov": 357},
        category="hybrid_player_profile",
    ),
    SQLEvaluationTestCase(
        question="What are Cade Cunningham's numbers this season and what do fans think about his development?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts, ps.reb, ps.ast, ps.gp "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Cade Cunningham%'"
        ),
        ground_truth_answer="Cade Cunningham (age 23, Pistons): 1827 PTS, 427 REB, 637 AST in 70 GP. Fans view him as a franchise cornerstone whose all-around game is improving each season.",
        ground_truth_data={"name": "Cade Cunningham", "age": 23, "pts": 1827, "reb": 427, "ast": 637, "gp": 70},
        category="hybrid_player_profile",
    ),

    # ======================================================================
    # TEAM COMPARISON HYBRID (4 cases)
    # Team-level stats + fan perception / analysis
    # ======================================================================
    SQLEvaluationTestCase(
        question="Compare the Celtics and Lakers stats and how fans view each team's championship hopes",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, SUM(ps.reb) as total_reb, SUM(ps.ast) as total_ast "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr IN ('BOS', 'LAL') GROUP BY p.team_abbr ORDER BY total_pts DESC"
        ),
        ground_truth_answer="Celtics: 9551 PTS, 3723 REB, 2147 AST. Lakers: 8691 PTS, 3321 REB, 2135 AST. The Celtics are statistically dominant while the Lakers rely more on star power.",
        ground_truth_data=[
            {"team_abbr": "BOS", "total_pts": 9551, "total_reb": 3723, "total_ast": 2147},
            {"team_abbr": "LAL", "total_pts": 8691, "total_reb": 3321, "total_ast": 2135},
        ],
        category="hybrid_team_comparison",
    ),
    SQLEvaluationTestCase(
        question="How do the Thunder and Nuggets compare statistically, and what do fans say about their playoff chances?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, ROUND(AVG(ps.pts), 1) as avg_pts, SUM(ps.ast) as total_ast "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr IN ('OKC', 'DEN') GROUP BY p.team_abbr ORDER BY total_pts DESC"
        ),
        ground_truth_answer="Nuggets: 9899 PTS (582.3 avg), 2538 AST. Thunder: 9880 PTS (548.9 avg), 2195 AST. Both are elite, with fans debating whether Denver's experience or OKC's youth gives the edge.",
        ground_truth_data=[
            {"team_abbr": "DEN", "total_pts": 9899, "avg_pts": 582.3, "total_ast": 2538},
            {"team_abbr": "OKC", "total_pts": 9880, "avg_pts": 548.9, "total_ast": 2195},
        ],
        category="hybrid_team_comparison",
    ),
    SQLEvaluationTestCase(
        question="Which team plays the best defense by stats, and how do fans describe their defensive identity?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.stl + ps.blk) as def_actions, SUM(ps.stl) as total_stl, SUM(ps.blk) as total_blk "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "GROUP BY p.team_abbr ORDER BY def_actions DESC LIMIT 1"
        ),
        ground_truth_answer="OKC leads with 1298 defensive actions (840 STL, 458 BLK). Fan discussions praise their aggressive perimeter defense and switchability.",
        ground_truth_data={"team_abbr": "OKC", "def_actions": 1298, "total_stl": 840, "total_blk": 458},
        category="hybrid_team_defense",
    ),
    SQLEvaluationTestCase(
        question="Show me the Pacers' team stats — why have fans found them impressive this season?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, ROUND(AVG(ps.pts), 1) as avg_pts, SUM(ps.ast) as total_ast "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'IND' GROUP BY p.team_abbr"
        ),
        ground_truth_answer="Pacers: 9630 total PTS (481.5 avg), 2395 AST. Fans admire their fast-paced, team-oriented offense and balanced scoring.",
        ground_truth_data={"team_abbr": "IND", "total_pts": 9630, "avg_pts": 481.5, "total_ast": 2395},
        category="hybrid_team_profile",
    ),

    # ======================================================================
    # YOUNG TALENT HYBRID (3 cases)
    # Age-filtered stats + fan expectations / generational analysis
    # ======================================================================
    SQLEvaluationTestCase(
        question="Which young players under 25 are putting up the best numbers, and what do fans expect from the next generation?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.age < 25 AND ps.pts > 1000 ORDER BY ps.pts DESC LIMIT 5"
        ),
        ground_truth_answer="Top young stars under 25: Anthony Edwards (23, 2180 PTS), Cade Cunningham (23, 1827), Jalen Green (23, 1722), Jalen Williams (24, 1490), Alperen Sengun (22, 1452). Fans see this generation as ready to take over the league.",
        ground_truth_data=[
            {"name": "Anthony Edwards", "age": 23, "pts": 2180},
            {"name": "Cade Cunningham", "age": 23, "pts": 1827},
            {"name": "Jalen Green", "age": 23, "pts": 1722},
            {"name": "Jalen Williams", "age": 24, "pts": 1490},
            {"name": "Alperen Sengun", "age": 22, "pts": 1452},
        ],
        category="hybrid_young_talent",
    ),
    SQLEvaluationTestCase(
        question="Tell me about the youngest stars under 22 and how fans rate their potential",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.age <= 22 AND ps.pts > 500 ORDER BY ps.pts DESC LIMIT 5"
        ),
        ground_truth_answer="Top under-22 players: Alperen Sengun (22, 1452), Shaedon Sharpe (22, 1332), Paolo Banchero (22, 1191), Stephon Castle (20, 1191), Bennedict Mathurin (22, 1159). Fans are excited about their development trajectories.",
        ground_truth_data=[
            {"name": "Alperen Sengun", "age": 22, "pts": 1452},
            {"name": "Shaedon Sharpe", "age": 22, "pts": 1332},
            {"name": "Paolo Banchero", "age": 22, "pts": 1191},
            {"name": "Stephon Castle", "age": 20, "pts": 1191},
            {"name": "Bennedict Mathurin", "age": 22, "pts": 1159},
        ],
        category="hybrid_young_talent",
    ),
    SQLEvaluationTestCase(
        question="How do veteran players over 35 compare to young talent, and what do fans debate about the NBA's generational shift?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, p.age, ps.pts, ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.age >= 35 ORDER BY ps.pts DESC LIMIT 5"
        ),
        ground_truth_answer="Top veterans (35+): Harden (35, 1801), Curry (37, 1715), DeRozan (35, 1709), LeBron (40, 1708), Durant (36, 1649). Fans debate whether these legends can still compete with the young wave.",
        ground_truth_data=[
            {"name": "James Harden", "age": 35, "pts": 1801, "gp": 79},
            {"name": "Stephen Curry", "age": 37, "pts": 1715, "gp": 70},
            {"name": "DeMar DeRozan", "age": 35, "pts": 1709, "gp": 77},
            {"name": "LeBron James", "age": 40, "pts": 1708, "gp": 70},
            {"name": "Kevin Durant", "age": 36, "pts": 1649, "gp": 62},
        ],
        category="hybrid_generational",
    ),

    # ======================================================================
    # HISTORICAL CROSSOVER HYBRID (3 cases)
    # Current stats vs Reddit historical discussions
    # ======================================================================
    SQLEvaluationTestCase(
        question="How do this season's 2000+ point scorers compare to the playoff efficiency legends that fans debate on Reddit?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.gp, ROUND(ps.pts*1.0/ps.gp, 1) as ppg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts >= 2000 ORDER BY ps.pts DESC"
        ),
        ground_truth_answer="2000+ point scorers: SGA (2485, 32.7 PPG), Edwards (2180, 27.6), Jokić (2072, 29.6), Giannis (2037, 30.4). Reddit discusses playoff efficiency legends like Reggie Miller (115 TS%), providing historical context.",
        ground_truth_data=[
            {"name": "Shai Gilgeous-Alexander", "pts": 2485, "gp": 76, "ppg": 32.7},
            {"name": "Anthony Edwards", "pts": 2180, "gp": 79, "ppg": 27.6},
            {"name": "Nikola Jokić", "pts": 2072, "gp": 70, "ppg": 29.6},
            {"name": "Giannis Antetokounmpo", "pts": 2037, "gp": 67, "ppg": 30.4},
        ],
        category="hybrid_historical",
    ),
    SQLEvaluationTestCase(
        question="Fans debate about Reggie Miller's playoff efficiency — how do current top shooters' true shooting compare?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.ts_pct, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 50 AND ps.pts > 1000 ORDER BY ps.ts_pct DESC LIMIT 5"
        ),
        ground_truth_answer="Top current TS%: Jarrett Allen (72.4%), Christian Braun (66.5%), Jokić (66.3%), Harrison Barnes (65.6%), Domantas Sabonis (65.5%). Reddit discusses Reggie Miller's 115 TS% in playoffs, putting modern efficiency in perspective.",
        ground_truth_data=[
            {"name": "Jarrett Allen", "ts_pct": 72.4},
            {"name": "Christian Braun", "ts_pct": 66.5},
            {"name": "Nikola Jokić", "ts_pct": 66.3},
            {"name": "Harrison Barnes", "ts_pct": 65.6},
            {"name": "Domantas Sabonis", "ts_pct": 65.5},
        ],
        category="hybrid_historical",
    ),
    SQLEvaluationTestCase(
        question="Which current players match the historical playoff dominance that fans discuss on Reddit?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 50 ORDER BY ps.pie DESC LIMIT 5"
        ),
        ground_truth_answer="Current dominant players (Giannis, Jokić, SGA) produce historically elite numbers. Reddit's discussions about playoff efficiency legends provide context for evaluating today's stars.",
        ground_truth_data=None,
        category="hybrid_historical",
    ),

    # ======================================================================
    # NEGATION / CONTRAST HYBRID (3 cases)
    # Stats that contrast with expectations + fan debate
    # ======================================================================
    SQLEvaluationTestCase(
        question="Which high-volume scorers have poor shooting efficiency, and are they still considered valuable by fans?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.fg_pct, ps.ts_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.pts > 1500 AND ps.fg_pct < 45 ORDER BY ps.pts DESC LIMIT 5"
        ),
        ground_truth_answer="High-volume low-efficiency: Edwards (2180 PTS, 44.7% FG), Young (1839, 41.1%), Harden (1801, 41.0%), Green (1722, 42.3%), Curry (1715, 44.8%). Fans debate whether volume scoring with lower efficiency is acceptable given their shot creation.",
        ground_truth_data=[
            {"name": "Anthony Edwards", "pts": 2180, "fg_pct": 44.7},
            {"name": "Trae Young", "pts": 1839, "fg_pct": 41.1},
            {"name": "James Harden", "pts": 1801, "fg_pct": 41.0},
            {"name": "Jalen Green", "pts": 1722, "fg_pct": 42.3},
            {"name": "Stephen Curry", "pts": 1715, "fg_pct": 44.8},
        ],
        category="hybrid_contrast",
    ),
    SQLEvaluationTestCase(
        question="Who leads in assists but also in turnovers — do fans think high usage is worth the mistakes?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.ast, ps.tov FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name LIKE '%Trae Young%'"
        ),
        ground_truth_answer="Trae Young leads in assists (882) but also turnovers (357). Fan discussions debate whether his elite playmaking compensates for turnovers.",
        ground_truth_data={"name": "Trae Young", "ast": 882, "tov": 357},
        category="hybrid_contrast",
    ),
    SQLEvaluationTestCase(
        question="Are there players with modest scoring but exceptional all-around impact, and what does this reveal about value?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.pie FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 50 AND ps.pie > 15 ORDER BY ps.pie DESC LIMIT 5"
        ),
        ground_truth_answer="High PIE players include some beyond just top scorers. PIE captures overall impact — scoring, rebounding, assists, defensive actions — revealing value beyond the box score.",
        ground_truth_data=None,
        category="hybrid_contrast",
    ),

    # ======================================================================
    # CONVERSATIONAL HYBRID (6 cases = 2 threads x 3 turns)
    # Multi-turn hybrid queries testing context maintenance
    # ======================================================================
    # --- Thread: MVP Discussion (3 turns) ---
    SQLEvaluationTestCase(
        question="What are Shai Gilgeous-Alexander's full stats this season?",
        query_type=QueryType.SQL_ONLY,  # Standalone: purely statistical (no contextual signal)
        expected_sql=(
            "SELECT p.name, ps.pts, ps.reb, ps.ast, ps.fg_pct, ps.gp "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Shai%'"
        ),
        ground_truth_answer="Shai Gilgeous-Alexander: 2485 PTS, 380 REB, 486 AST, 51.9% FG in 76 GP.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485, "reb": 380, "ast": 486, "fg_pct": 51.9, "gp": 76},
        category="hybrid_conversational_mvp",
    ),
    SQLEvaluationTestCase(
        question="Why do fans on Reddit consider him an MVP favorite?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pie, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name LIKE '%Shai%'"
        ),
        ground_truth_answer="SGA's combination of elite scoring (2485 PTS), efficiency (51.9% FG), and team success makes him a top MVP candidate. Fan discussions highlight his complete game and leadership.",
        ground_truth_data=None,
        category="hybrid_conversational_mvp",
    ),
    SQLEvaluationTestCase(
        question="How does his efficiency compare to the historical playoff scorers that fans debate about?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.ts_pct, ps.efg_pct, ps.pie "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%Shai%'"
        ),
        ground_truth_answer="SGA: 63.7% TS, 56.9% EFG, 19.9 PIE. Reddit debates about historical playoff efficiency (Reggie Miller 115 TS%, Kawhi 112%) provide context — SGA's efficiency is elite by any era's standards.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "ts_pct": 63.7, "efg_pct": 56.9, "pie": 19.9},
        category="hybrid_conversational_mvp",
    ),

    # --- Thread: Team Deep Dive (3 turns) ---
    SQLEvaluationTestCase(
        question="Show me the Celtics' team statistics this season",
        query_type=QueryType.SQL_ONLY,  # Standalone: purely statistical (no contextual signal)
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, ROUND(AVG(ps.pts), 1) as avg_pts, "
            "SUM(ps.reb) as total_reb, SUM(ps.ast) as total_ast "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'BOS' GROUP BY p.team_abbr"
        ),
        ground_truth_answer="Celtics: 9551 total PTS (561.8 avg), 3723 REB, 2147 AST across 17 players.",
        ground_truth_data={"team_abbr": "BOS", "total_pts": 9551, "avg_pts": 561.8, "total_reb": 3723, "total_ast": 2147},
        category="hybrid_conversational_team",
    ),
    SQLEvaluationTestCase(
        question="What do fans think about their chances of repeating as champions?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'BOS' ORDER BY ps.pts DESC LIMIT 3"
        ),
        ground_truth_answer="Fan discussions weigh the Celtics' depth and balanced scoring. With Tatum, Brown, and White leading, fans debate whether their roster continuity gives them an edge in repeating.",
        ground_truth_data=None,
        category="hybrid_conversational_team",
    ),
    SQLEvaluationTestCase(
        question="Compare their stats to the Nuggets — which team is statistically better?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, ROUND(AVG(ps.pts), 1) as avg_pts "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr IN ('BOS', 'DEN') GROUP BY p.team_abbr ORDER BY total_pts DESC"
        ),
        ground_truth_answer="Nuggets: 9899 PTS (582.3 avg) vs Celtics: 9551 PTS (561.8 avg). Denver edges Boston in scoring, but fans note the Celtics' defensive advantages.",
        ground_truth_data=[
            {"team_abbr": "DEN", "total_pts": 9899, "avg_pts": 582.3},
            {"team_abbr": "BOS", "total_pts": 9551, "avg_pts": 561.8},
        ],
        category="hybrid_conversational_team",
    ),

    # ======================================================================
    # NOISY / INFORMAL HYBRID (3 cases)
    # Typos and slang requiring both SQL data + contextual analysis
    # ======================================================================
    SQLEvaluationTestCase(
        question="yo whos got da best stats AND what do ppl think about them on reddit",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1",
        ground_truth_answer="Shai Gilgeous-Alexander leads with 2485 PTS. Reddit fans praise his complete game and consider him the top player this season.",
        ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},
        category="hybrid_noisy",
    ),
    SQLEvaluationTestCase(
        question="lebron stats + fan opinions plzzz",
        query_type=QueryType.HYBRID,
        expected_sql="SELECT p.name, ps.pts, ps.reb, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%LeBron%'",
        ground_truth_answer="LeBron James: 1708 PTS, 546 REB, 574 AST. At age 40, fans marvel at his longevity and debate his legacy as one of the greatest ever.",
        ground_truth_data={"name": "LeBron James", "pts": 1708, "reb": 546, "ast": 574},
        category="hybrid_noisy",
    ),
    SQLEvaluationTestCase(
        question="compare curry n jokic stats nd tell me who fans like more",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pts, ps.ast FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.name IN ('Stephen Curry', 'Nikola Jokić') ORDER BY ps.pts DESC"
        ),
        ground_truth_answer="Jokić: 2072 PTS, 714 AST. Curry: 1715 PTS, 420 AST. Fan opinions split between Curry's revolutionary shooting and Jokić's all-around dominance.",
        ground_truth_data=[
            {"name": "Nikola Jokić", "pts": 2072, "ast": 714},
            {"name": "Stephen Curry", "pts": 1715, "ast": 420},
        ],
        category="hybrid_noisy",
    ),

    # ======================================================================
    # DEFENSIVE / ADVANCED METRICS HYBRID (3 cases)
    # Defensive stats + PIE + fan discussion about intangibles
    # ======================================================================
    SQLEvaluationTestCase(
        question="Who leads the league in blocks and what makes them elite defenders according to fans?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.blk, ps.pts, ps.reb FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY ps.blk DESC LIMIT 1"
        ),
        ground_truth_answer="Victor Wembanyama leads with 175 BLK (plus 1118 PTS, 506 REB). Fans consider his shot-blocking a generational skill combining elite length with instinctive timing.",
        ground_truth_data={"name": "Victor Wembanyama", "blk": 175, "pts": 1118, "reb": 506},
        category="hybrid_defensive",
    ),
    SQLEvaluationTestCase(
        question="Which players have the highest PIE and what does this metric reveal about their value according to fan discussions?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.pie, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE ps.gp > 50 ORDER BY ps.pie DESC LIMIT 5"
        ),
        ground_truth_answer="Top PIE: Giannis (21.0), Jokić (20.6), SGA (19.9), Davis (17.9), LeBron (16.9). PIE captures total impact — fans increasingly value this over raw scoring.",
        ground_truth_data=[
            {"name": "Giannis Antetokounmpo", "pie": 21.0},
            {"name": "Nikola Jokić", "pie": 20.6},
            {"name": "Shai Gilgeous-Alexander", "pie": 19.9},
            {"name": "Anthony Davis", "pie": 17.9},
            {"name": "LeBron James", "pie": 16.9},
        ],
        category="hybrid_advanced_metrics",
    ),
    SQLEvaluationTestCase(
        question="Compare the top 3 assist leaders and explain what fans think about playmaking in modern basketball",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.ast, ps.gp, ROUND(ps.ast*1.0/ps.gp, 1) as apg "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.ast DESC LIMIT 3"
        ),
        ground_truth_answer="Top 3 assists: Trae Young (882, 11.6 APG), Nikola Jokić (714, 10.2 APG), James Harden (687, 8.7 APG). Fans discuss how playmaking has evolved from traditional PG skills to big-man facilitating.",
        ground_truth_data=[
            {"name": "Trae Young", "ast": 882, "gp": 76, "apg": 11.6},
            {"name": "Nikola Jokić", "ast": 714, "gp": 70, "apg": 10.2},
            {"name": "James Harden", "ast": 687, "gp": 79, "apg": 8.7},
        ],
        category="hybrid_playmaking",
    ),

    # ======================================================================
    # TEAM CULTURE HYBRID (3 cases)
    # Team stats + fan description of team identity
    # ======================================================================
    SQLEvaluationTestCase(
        question="What are the Thunder's stats this season and how do fans describe their team identity?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, ROUND(AVG(ps.pts), 1) as avg_pts, "
            "SUM(ps.reb) as total_reb, SUM(ps.ast) as total_ast "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'OKC' GROUP BY p.team_abbr"
        ),
        ground_truth_answer="Thunder: 9880 PTS (548.9 avg), 3660 REB, 2195 AST across 18 players. Fans describe OKC as young, athletic, and defensively relentless.",
        ground_truth_data={"team_abbr": "OKC", "total_pts": 9880, "avg_pts": 548.9, "total_reb": 3660, "total_ast": 2195},
        category="hybrid_team_culture",
    ),
    SQLEvaluationTestCase(
        question="Show me the Timberwolves' numbers and what fans call their 'young and hungry' identity",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.team_abbr, SUM(ps.pts) as total_pts, ROUND(AVG(ps.pts), 1) as avg_pts, "
            "SUM(ps.reb) as total_reb, SUM(ps.ast) as total_ast "
            "FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "WHERE p.team_abbr = 'MIN' GROUP BY p.team_abbr"
        ),
        ground_truth_answer="Timberwolves: 9523 PTS (476.1 avg), 3656 REB, 2175 AST across 20 players. Led by Anthony Edwards, fans see them as a legitimate contender.",
        ground_truth_data={"team_abbr": "MIN", "total_pts": 9523, "avg_pts": 476.1, "total_reb": 3656, "total_ast": 2175},
        category="hybrid_team_culture",
    ),
    SQLEvaluationTestCase(
        question="Who are the top 3-point shooters by volume and how has the three-point revolution changed the game according to fans?",
        query_type=QueryType.HYBRID,
        expected_sql=(
            "SELECT p.name, ps.three_pa, ps.three_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id "
            "ORDER BY ps.three_pa DESC LIMIT 3"
        ),
        ground_truth_answer="Top by 3PA: Edwards (814, 39.5%), Curry (784, 39.7%), Beasley (763, 41.6%). Fan discussions highlight how three-point shooting has fundamentally changed offensive strategy.",
        ground_truth_data=[
            {"name": "Anthony Edwards", "three_pa": 814, "three_pct": 39.5},
            {"name": "Stephen Curry", "three_pa": 784, "three_pct": 39.7},
            {"name": "Malik Beasley", "three_pa": 763, "three_pct": 41.6},
        ],
        category="hybrid_shooting_evolution",
    ),
]

# ============================================================================
# VERIFICATION & SUMMARY
# ============================================================================

print(f"\n{'='*70}")
print(f"HYBRID TEST CASES - SUMMARY")
print(f"{'='*70}")
print(f"Hybrid Test Cases:       {len(HYBRID_TEST_CASES):2d} (51)")
print(f"{'='*70}")

# Assertion for validation
assert len(HYBRID_TEST_CASES) == 51, f"Expected 51 hybrid cases, got {len(HYBRID_TEST_CASES)}"

print(f"\n[OK] Hybrid test cases validated")
