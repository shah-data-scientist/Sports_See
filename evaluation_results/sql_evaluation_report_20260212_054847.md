# SQL Evaluation Report

**Generated:** 2026-02-12 05:48:47

**Dataset:** 80 SQL test cases

**Results JSON:** `evaluation_results\sql_evaluation_20260212_054847.json`

---

## Executive Summary

- **Total Queries:** 80
- **Successful Executions:** 80 (100.0%)
- **Failed Executions:** 0
- **Classification Accuracy:** 87.5%
- **Misclassifications:** 10
- **Avg Processing Time:** 6839ms

## Failure Analysis

### Execution Failures

✓ No execution failures detected.

### Routing Misclassifications (10)

| Question | Category | Expected | Actual |
|----------|----------|----------|--------|
| Which teams have at least 3 players with more than 1000 poin... | complex_sql_having | sql_only | fallback_to_vector |
| What about his assists? | conversational_followup | sql_only | fallback_to_vector |
| Who is the MVP this season? | conversational_ambiguous | sql_only | fallback_to_vector |
| Only from the Lakers | conversational_progressive_filtering | sql_only | fallback_to_vector |
| Sort them by attempts | conversational_progressive_filtering | sql_only | fallback_to_vector |
| Show me stats for the Warriors | conversational_correction | sql_only | fallback_to_vector |
| Actually, I meant the Celtics | conversational_correction | sql_only | fallback_to_vector |
| How does LeBron James compare? | conversational_multi_entity | sql_only | fallback_to_vector |
| show me currys 3 pt pct | noisy_sql_abbreviation | sql_only | fallback_to_vector |
| whats the avg fg% in da league lol | noisy_sql_slang | sql_only | fallback_to_vector |

### Performance Metrics

- **Average Processing Time:** 6839ms
- **Min Processing Time:** 1316ms
- **Max Processing Time:** 266343ms

## Response Quality Analysis

### Error Taxonomy

- **Total Errors:** 2
- **LLM Declined:** 2
- **Syntax Errors:** 0
- **Empty Responses:** 0

#### LLM Declined Examples

**Q:** Which teams have at least 3 players with more than 1000 points?

**Response:** The available data doesn't contain this information....

**Q:** What about his assists?

**Response:** The available data doesn't contain this information....

### Fallback Patterns

- **SQL Only:** 70 (87.5%)
- **Fallback to Vector:** 10 (12.5%)

#### Fallback by Category

| Category | Total | Fallbacks | Rate |
|----------|-------|-----------|------|
| simple_sql_top_n | 6 | 0 | 0.0% |
| simple_sql_player_stats | 4 | 0 | 0.0% |
| simple_sql_team_roster | 2 | 0 | 0.0% |
| aggregation_sql_league | 7 | 0 | 0.0% |
| comparison_sql_players | 7 | 0 | 0.0% |
| aggregation_sql_count | 4 | 0 | 0.0% |
| aggregation_sql_team | 1 | 0 | 0.0% |
| complex_sql_subquery | 1 | 0 | 0.0% |
| complex_sql_multiple_conditions | 2 | 0 | 0.0% |
| complex_sql_calculated_triple_condition | 1 | 0 | 0.0% |
| complex_sql_calculated_field | 1 | 0 | 0.0% |
| complex_sql_ratio_calculation | 1 | 0 | 0.0% |
| complex_sql_percentage_calculation | 1 | 0 | 0.0% |
| complex_sql_filtering | 1 | 0 | 0.0% |
| complex_sql_filtering_calculation | 1 | 0 | 0.0% |
| complex_sql_versatility | 1 | 0 | 0.0% |
| complex_sql_group_by | 1 | 0 | 0.0% |
| complex_sql_team_comparison | 1 | 0 | 0.0% |
| complex_sql_having | 1 | 1 | 100.0% |
| complex_sql_range | 1 | 0 | 0.0% |
| conversational_initial | 1 | 0 | 0.0% |
| conversational_casual | 3 | 0 | 0.0% |
| conversational_followup | 2 | 1 | 50.0% |
| conversational_comparison | 1 | 0 | 0.0% |
| conversational_filter_followup | 1 | 0 | 0.0% |
| conversational_stat_abbreviation | 1 | 0 | 0.0% |
| conversational_ambiguous | 1 | 1 | 100.0% |
| conversational_progressive_filtering | 3 | 2 | 66.7% |
| conversational_correction | 3 | 2 | 66.7% |
| conversational_implicit_continuation | 3 | 0 | 0.0% |
| conversational_multi_entity | 3 | 1 | 33.3% |
| conversational_team_pronoun | 3 | 0 | 0.0% |
| noisy_sql_typo | 1 | 0 | 0.0% |
| noisy_sql_abbreviation | 2 | 1 | 50.0% |
| noisy_sql_slang | 2 | 1 | 50.0% |
| noisy_sql_informal | 2 | 0 | 0.0% |
| adversarial_sql_injection | 1 | 0 | 0.0% |
| adversarial_raw_sql | 1 | 0 | 0.0% |
| adversarial_path_traversal | 1 | 0 | 0.0% |

### Response Quality Metrics

- **Avg Response Length:** 158 chars
- **Min/Max Length:** 12 / 1218 chars
- **Responses with Hedging:** 2
- **Complete Responses:** 2
- **Incomplete Responses:** 5

## Query Quality Analysis

### Query Structure

- **Total SQL Queries Generated:** 71
- **Queries with JOIN:** 53 (74.6%)
- **Queries with Aggregation:** 20 (28.2%)
- **Queries with Filter (WHERE):** 46 (64.8%)
- **Queries with ORDER BY:** 31 (43.7%)
- **Queries with LIMIT:** 28 (39.4%)

#### JOIN Correctness

- **Correct JOINs:** 35
- **Missing JOINs:** 8

### Query Complexity

- **Avg JOINs per Query:** 0.75
- **Avg WHERE Conditions:** 0.89
- **Queries with Subqueries:** 1
- **Queries with GROUP BY:** 3
- **Queries with HAVING:** 0

#### Complexity Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| Simple | 16 | 22.5% |
| Moderate | 54 | 76.1% |
| Complex | 1 | 1.4% |
| Very Complex | 0 | 0.0% |

### Column Selection

- **Avg Columns Selected:** 2.10
- **SELECT * Usage:** 0 queries
- **Over-selection Rate:** 0.0%
- **Under-selection Rate:** 0.0%

## Key Findings

✓ **Excellent execution reliability** (100.0% success rate)

⚠ **Moderate classification accuracy** (87.5%) - could be improved

⚠ **Moderate fallback rate** (12.5%)

⚠ **Few LLM errors** (2) detected

❌ **8 queries missing required JOINs**

## Detailed Test Results

### Adversarial Path Traversal (1 tests)

**✓ ../../etc/passwd What is Curry's three point percentage?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2076ms
- **Generated SQL:** `SELECT p.name, ps.three_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name ...`
- **Response:** Stephen Curry's three point percentage is 39.7%.


### Adversarial Raw Sql (1 tests)

**✓ SELECT * FROM players; Who has the most assists?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 6533ms
- **Generated SQL:** `SELECT p.name, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.ast DES...`
- **Response:** Trae Young has the most assists with 882.


### Adversarial Sql Injection (1 tests)

**✓ '; DROP TABLE players; -- Who scored the most points?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2064ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** Shai Gilgeous-Alexander scored the most points with 2,485.


### Aggregation Sql Count (4 tests)

**✓ How many players scored over 1000 points?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1910ms
- **Generated SQL:** `SELECT COUNT(*) FROM player_stats WHERE pts > 1000...`
- **Response:** 84 players scored over 1000 points.


**✓ How many players have a true shooting percentage over 60%?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1846ms
- **Generated SQL:** `SELECT COUNT(*)
FROM player_stats
WHERE ts_pct > 60 AND gp >= 20;...`
- **Response:** 118 players have a true shooting percentage over 60%.


**✓ How many players have more than 500 assists?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1934ms
- **Generated SQL:** `SELECT COUNT(*) FROM player_stats WHERE ast > 500;...`
- **Response:** 10 players have more than 500 assists.


**✓ How many players played more than 50 games?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1733ms
- **Generated SQL:** `SELECT COUNT(DISTINCT player_id)
FROM player_stats
WHERE gp > 50;...`
- **Response:** 282 players played more than 50 games.


### Aggregation Sql League (7 tests)

**✓ What is the average player age in the NBA?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1826ms
- **Generated SQL:** `SELECT AVG(age) AS avg_age
FROM players
WHERE age IS NOT NULL;...`
- **Response:** The average player age in the NBA is 26.15 years.


**✓ What is the average 3-point percentage for all players?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2103ms
- **Generated SQL:** `SELECT AVG(three_pct) AS avg_3p_pct
FROM player_stats
WHERE three_pct IS NOT NULL;...`
- **Response:** The average 3-point percentage for all players is 29.90.


**✓ What is the average field goal percentage in the league?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2189ms
- **Generated SQL:** `SELECT AVG(fg_pct) AS avg_fg_pct
FROM player_stats
WHERE fg_pct IS NOT NULL;...`
- **Response:** The average field goal percentage in the league is 44.61.


**✓ What is the average PIE in the league?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1803ms
- **Generated SQL:** `SELECT AVG(pie) AS avg_pie
FROM player_stats
WHERE pie IS NOT NULL;...`
- **Response:** The average PIE in the league is 8.87.


**✓ What is the average rebounds per game league-wide?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1999ms
- **Generated SQL:** `SELECT ROUND(AVG(CAST(reb AS REAL) / gp), 1) AS avg_rpg
FROM player_stats
WHERE gp > 0;...`
- **Response:** The average rebounds per game league-wide is 3.60.


**✓ What is the highest PIE in the league?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1892ms
- **Generated SQL:** `SELECT MAX(pie) FROM player_stats...`
- **Response:** The highest PIE in the league is 40.


**✓ What is the maximum number of blocks recorded by any player?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1879ms
- **Generated SQL:** `SELECT MAX(blk) AS max_blocks
FROM player_stats;...`
- **Response:** The maximum number of blocks recorded by any player is 175.


### Aggregation Sql Team (1 tests)

**✓ What is the average field goal percentage for the Lakers?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 9235ms
- **Generated SQL:** `SELECT AVG(ps.fg_pct)
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.team_abbr =...`
- **Response:** The average field goal percentage for the Lakers is 44.64.


### Comparison Sql Players (7 tests)

**✓ Compare Jokić and Embiid's stats**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2279ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.reb, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHE...`
- **Response:** Nikola Jokić has 2072 points, 889 rebounds, and 714 assists, while Joel Embiid has 452 points, 156 rebounds, and 86 assists.


**✓ Who shoots better from 3, Curry or Lillard?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2241ms
- **Generated SQL:** `SELECT p.name, ps.three_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name ...`
- **Response:** Stephen Curry shoots better from 3, with a 39.7% accuracy compared to Damian Lillard's 37.6%.


**✓ Who is more efficient goal maker, Jokić or Embiid?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2510ms
- **Generated SQL:** `SELECT p.name, ps.efg_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name IN...`
- **Response:** Based on the data, Nikola Jokić has an effective field goal percentage (eFG%) of 62.7. To determine who is more efficient, we would need Embiid's eFG%. Since that data is not provided, we can only say...

**✓ Compare Jayson Tatum and Kevin Durant scoring efficiency**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2550ms
- **Generated SQL:** `SELECT p.name, ps.efg_pct, ps.ts_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHER...`
- **Response:** Kevin Durant is more efficient than Jayson Tatum. Durant has an effective field goal percentage (eFG%) of 59.8% and a true shooting percentage (TS%) of 64.2%, while Tatum has an eFG% of 53.7% and a TS...

**✓ Who has more assists, James Harden or Chris Paul?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2252ms
- **Generated SQL:** `SELECT p.name, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name IN ('J...`
- **Response:** James Harden has more assists (687) than Chris Paul (607).


**✓ Compare the top 2 steals leaders**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2081ms
- **Generated SQL:** `SELECT p.name, ps.stl
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.stl DES...`
- **Response:** Dyson Daniels has 228 steals, while Shai Gilgeous-Alexander has 129 steals.


**✓ Compare blocks between the top 2 leaders**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2230ms
- **Generated SQL:** `SELECT p.name, ps.blk
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.blk DES...`
- **Response:** Victor Wembanyama has 175 blocks, while Brook Lopez has 152 blocks.


### Complex Sql Calculated Field (1 tests)

**✓ Find the top 5 players by total defensive actions (steals + blocks)**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2298ms
- **Generated SQL:** `SELECT p.name, ps.stl + ps.blk AS total_defensive_actions
FROM players p
JOIN player_stats ps ON p.i...`
- **Response:** The top 5 players by total defensive actions are:

1. Dyson Daniels: 281
2. Victor Wembanyama: 226
3. Shai Gilgeous-Alexander: 205
4. Myles Turner: 202
5. Jaren Jackson Jr: 200


### Complex Sql Calculated Triple Condition (1 tests)

**✓ Find players averaging double-digits in points, rebounds, and assists**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2715ms
- **Generated SQL:** `SELECT p.name, ROUND(CAST(ps.pts AS FLOAT) / ps.gp, 1) AS ppg, ROUND(CAST(ps.reb AS FLOAT) / ps.gp, ...`
- **Response:** Nikola Jokić is averaging double-digits in points (29.6), rebounds (12.7), and assists (10.2).


### Complex Sql Filtering (1 tests)

**✓ Who are the most efficient scorers among players with 50+ games played?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2428ms
- **Generated SQL:** `SELECT p.name, ps.efg_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.gp >= ...`
- **Response:** The most efficient scorers among players with 50+ games played, based on effective field goal percentage (eFG%), are: Jaxson Hayes (72.2%), Jarrett Allen (70.6%), Dwight Powell (70.5%), Adem Bona (70....

### Complex Sql Filtering Calculation (1 tests)

**✓ Who are the top 3 players in points per game among those who played at least 70 games?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2302ms
- **Generated SQL:** `SELECT p.name, ROUND(CAST(ps.pts AS FLOAT) / ps.gp, 1) AS ppg
FROM players p
JOIN player_stats ps ON...`
- **Response:** Shai Gilgeous-Alexander (32.7 ppg), Nikola Jokić (29.6 ppg), and Anthony Edwards (27.6 ppg) are the top 3 players in points per game.


### Complex Sql Group By (1 tests)

**✓ Which team has the highest average points per player?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2195ms
- **Generated SQL:** `SELECT p.team_abbr, AVG(ps.pts) AS avg_pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_i...`
- **Response:** The Denver Nuggets (DEN) have an average of 582.29 points per player.


### Complex Sql Having (1 tests)

**✗ Which teams have at least 3 players with more than 1000 points?**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 3098ms
- **Response:** The available data doesn't contain this information.


### Complex Sql Multiple Conditions (2 tests)

**✓ Find players with both high scoring (1500+ points) and high assists (300+ assists)**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 3816ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.pt...`
- **Response:** The following players have scored 1500+ points and have 300+ assists:

*   Shai Gilgeous-Alexander: 2485 points, 486 assists
*   Anthony Edwards: 2180 points, 356 assists
*   Nikola Jokić: 2072 points...

**✓ Which players have better than 50% field goal percentage AND 35%+ from three?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 4951ms
- **Generated SQL:** `SELECT p.name, ps.fg_pct, ps.three_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WH...`
- **Response:** The following players have a field goal percentage better than 50% and a three-point percentage of 35% or higher:

*   Shai Gilgeous-Alexander, fg_pct: 51.9, three_pct: 37.5
*   Nikola Jokić, fg_pct: ...

### Complex Sql Percentage Calculation (1 tests)

**✓ What percentage of players have a true shooting percentage above 60%?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2518ms
- **Generated SQL:** `SELECT CAST(SUM(CASE WHEN ts_pct > 60 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*)
FROM player_stats...`
- **Response:** Based on the data, 25.88% of players have a true shooting percentage above 60%.


### Complex Sql Range (1 tests)

**✓ Find players between 25 and 30 years old with more than 1500 points**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 3924ms
- **Generated SQL:** `SELECT p.name, ps.pts, p.age
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.age ...`
- **Response:** The players between 25 and 30 years old with more than 1500 points are:

*   Shai Gilgeous-Alexander, 2485 points, age 26
*   Nikola Jokić, 2072 points, age 30
*   Giannis Antetokounmpo, 2037 points, ...

### Complex Sql Ratio Calculation (1 tests)

**✓ Which players have the best assist-to-turnover ratio among those with 300+ assists?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2632ms
- **Generated SQL:** `SELECT p.name, ps.ast_to
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.ast >= ...`
- **Response:** Based on the provided data, the players with the best assist-to-turnover ratio are:

1. Tyrese Haliburton: 5.61
2. Tyus Jones: 4.71
3. Chris Paul: 4.69
4. Mike Conley: 4.25
5. Fred VanVleet: 3.83


### Complex Sql Subquery (1 tests)

**✓ Which players score more points per game than the league average?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 29807ms
- **Generated SQL:** `SELECT p.name, ROUND(CAST(ps.pts AS FLOAT) / ps.gp, 1) AS ppg
FROM players p
JOIN player_stats ps ON...`
- **Response:** Based on the data provided, the following players score more points per game than the league average:

1.  Shai Gilgeous-Alexander (32.7 ppg)
2.  Giannis Antetokounmpo (30.4 ppg)
3.  Nikola Jokić (29....

### Complex Sql Team Comparison (1 tests)

**✓ Compare the average points per player between the Celtics and Lakers**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2062ms
- **Generated SQL:** `SELECT team_abbr, ROUND(AVG(CAST(pts AS REAL) / gp), 1) AS avg_ppg
FROM player_stats
WHERE team_abbr...`
- **Response:** The Celtics average 9.2 points per player, while the Lakers average 7.7 points per player.


### Complex Sql Versatility (1 tests)

**✓ Find the most versatile players with at least 1000 points, 400 rebounds, and 200 assists**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 4867ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.reb, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHE...`
- **Response:** Based on the provided data, here are the players with at least 1000 points, 400 rebounds, and 200 assists:

*   Anthony Edwards: 2180 points, 450 rebounds, 356 assists
*   Nikola Jokić: 2072 points, 8...

### Conversational Ambiguous (1 tests)

**✗ Who is the MVP this season?**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 2313ms
- **Response:** The available context doesn't contain this information


### Conversational Casual (3 tests)

**✓ Who's the best rebounder?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2190ms
- **Generated SQL:** `SELECT p.name, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.reb DES...`
- **Response:** Ivica Zubac is the best rebounder with 1,008 rebounds.


**✓ Tell me about LeBron's stats**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2362ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.reb, ps.ast, ps.stl, ps.blk
FROM players p
JOIN player_stats ps ON p.id = ...`
- **Response:** LeBron James has 1,708 points, 546 rebounds, 574 assists, 70 steals, and 42 blocks.


**✓ gimme the assist leaders plz**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2423ms
- **Generated SQL:** `SELECT p.name, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.ast DES...`
- **Response:** The assist leaders are: Trae Young (882), Nikola Jokić (714), James Harden (687), Tyrese Haliburton (672), and Cade Cunningham (637).


### Conversational Comparison (1 tests)

**✓ Compare him to Curry**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 266343ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.reb, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHE...`
- **Response:** Comparing Stephen Curry to Seth Curry: Stephen Curry has 1715 points, 308 rebounds, and 420 assists, while Seth Curry has 442 points, 116 rebounds, and 61 assists.


### Conversational Correction (3 tests)

**✗ Show me stats for the Warriors**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 1451ms
- **Response:** The Warriors will cease to be important once Steph retires [Source: Reddit 2.pdf]


**✗ Actually, I meant the Celtics**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 10930ms
- **Response:** The Celtics are considered one of the best teams in the playoffs based on stats [Source: Reddit 2.pdf]. In previous years, the Celtics would likely absorb an injury year from Tatum and then run it bac...

**✓ Who is their top scorer?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2296ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** Shai Gilgeous-Alexander is their top scorer with 2,485 points.


### Conversational Filter Followup (1 tests)

**✓ Which of them plays for the Hawks?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2112ms
- **Generated SQL:** `SELECT p.name
FROM players p
WHERE p.team_abbr = 'ATL';...`
- **Response:** Trae Young, Onyeka Okongwu, Jalen Johnson, Clint Capela, Vít Krejčí, Garrison Mathews, Kobe Bufkin, and Daeqwon Plowden play for the Hawks.


### Conversational Followup (2 tests)

**✗ What about his assists?**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 2603ms
- **Generated SQL:** `SELECT p.name, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name LIKE '...`
- **Response:** The available data doesn't contain this information.


**✓ How many games did he play?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2840ms
- **Generated SQL:** `SELECT ps.gp FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.name LIKE '%';...`
- **Response:** The player played in a variety of games, ranging from 62 to 82 games played. Here is a sample of the number of games played: 76, 79, 70, 67, 72, 75, 77, 76, 70, 79, 72, 74, 82, 70, 77, 70, 71, 65, 62,...

### Conversational Implicit Continuation (3 tests)

**✓ Who leads in steals?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 3288ms
- **Generated SQL:** `SELECT p.name, ps.stl
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.stl DES...`
- **Response:** Dyson Daniels leads in steals with 228.


**✓ And blocks?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2767ms
- **Generated SQL:** `SELECT p.name, ps.blk
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.blk DES...`
- **Response:** 175 blocks.


**✓ What about turnovers?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 3162ms
- **Generated SQL:** `SELECT p.name, ps.tov
FROM players p
JOIN player_stats ps ON p.id = ps.player_id;...`
- **Response:** Here are the turnover (tov) numbers for the players listed:

1. Shai Gilgeous-Alexander, tov: 182
2. Anthony Edwards, tov: 253
3. Nikola Jokić, tov: 231
4. Giannis Antetokounmpo, tov: 208
5. Jayson Ta...

### Conversational Initial (1 tests)

**✓ Show me the top scorer**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 4802ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** Shai Gilgeous-Alexander is the top scorer with 2,485 points.


### Conversational Multi Entity (3 tests)

**✓ Tell me about Jayson Tatum's scoring**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 3014ms
- **Generated SQL:** `SELECT p.name, ps.pts, ROUND(CAST(ps.pts AS FLOAT) / ps.gp, 1) AS ppg, ps.fgm, ps.fga, ps.fg_pct, ps...`
- **Response:** Jayson Tatum scored 1930 points, averaging 26.8 points per game (ppg). He made 662 field goals out of 1462 attempts, resulting in a field goal percentage of 45.2%. He made 0 three-pointers out of 727 ...

**✗ How does LeBron James compare?**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 2564ms
- **Response:** LeBron James is mentioned in the context of a discussion about why the media focuses on superstars rather than team play. One comment suggests that the media is "desperate for superstars to be in big ...

**✓ Between the two, who has more rebounds?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2215ms
- **Generated SQL:** `SELECT p.name, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name IN ('N...`
- **Response:** Nikola Jokić has 889 rebounds. Since you only provided data for Nikola Jokić, I cannot compare him to anyone else to determine who has more rebounds.


### Conversational Progressive Filtering (3 tests)

**✓ Show me players with good three-point shooting**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2742ms
- **Generated SQL:** `SELECT p.name, ps.three_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.thre...`
- **Response:** Here are players with good three-point shooting percentages, according to the data:

*   Patrick Baldwin Jr: 56.5%
*   Drew Eubanks: 50%
*   Taj Gibson: 50%
*   Markelle Fultz: 50%
*   Alex Ducas: 47....

**✗ Only from the Lakers**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 1388ms
- **Response:** The 2020 Lakers never had home court advantage throughout the entire playoffs [Source: Reddit 4.pdf].


**✗ Sort them by attempts**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 1499ms
- **Response:** The available context doesn't contain this information.


### Conversational Stat Abbreviation (1 tests)

**✓ Show me the pts leaders this season**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2669ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** The points leaders this season are:

1. Shai Gilgeous-Alexander: 2485 points
2. Anthony Edwards: 2180 points
3. Nikola Jokić: 2072 points
4. Giannis Antetokounmpo: 2037 points
5. Jayson Tatum: 1930 po...

### Conversational Team Pronoun (3 tests)

**✓ Which team has the highest total points?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 10383ms
- **Generated SQL:** `SELECT p.team_abbr, SUM(ps.pts) AS total_points
FROM players p
JOIN player_stats ps ON p.id = ps.pla...`
- **Response:** DET has the highest total points with 10,292.


**✓ Who are their top scorers?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2365ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** Shai Gilgeous-Alexander (2485 points) is the top scorer, followed by Anthony Edwards (2180 points), Nikola Jokić (2072 points), Giannis Antetokounmpo (2037 points), and Jayson Tatum (1930 points).


**✓ What is the average age of their players?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1904ms
- **Generated SQL:** `SELECT AVG(age)
FROM players;...`
- **Response:** The average age of their players is 26.15 years old.


### Noisy Sql Abbreviation (2 tests)

**✗ show me currys 3 pt pct**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 1618ms
- **Response:** The available context doesn't contain this information.


**✓ compare lebron n harden assists**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 6517ms
- **Generated SQL:** `SELECT p.name, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name IN ('L...`
- **Response:** James Harden has 687 assists and LeBron James has 574 assists.


### Noisy Sql Informal (2 tests)

**✓ jokic rebounds total plzz**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 15852ms
- **Generated SQL:** `SELECT p.name, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name LIKE '...`
- **Response:** 889 rebounds

**✓ top 3 reb guys??**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2552ms
- **Generated SQL:** `SELECT p.name, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.reb DES...`
- **Response:** Ivica Zubac (1008), Domantas Sabonis (973), and Karl-Anthony Towns (922) are the top 3 in rebounds.


### Noisy Sql Slang (2 tests)

**✓ how many playas got more than 1k points??**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 3151ms
- **Generated SQL:** `SELECT COUNT(id) FROM player_stats WHERE pts > 1000...`
- **Response:** 84 players got more than 1,000 points.


**✗ whats the avg fg% in da league lol**

- **Expected Routing:** sql_only
- **Actual Routing:** fallback_to_vector
- **Processing Time:** 1316ms
- **Response:** The available context doesn't contain this information.


### Noisy Sql Typo (1 tests)

**✓ whos got da most pts this szn**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2696ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** Shai Gilgeous-Alexander has the most points this season, with 2,485.


### Simple Sql Player Stats (4 tests)

**✓ What is LeBron James' average points per game?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2145ms
- **Generated SQL:** `SELECT p.name, ROUND(CAST(ps.pts AS FLOAT) / ps.gp, 1) AS ppg
FROM players p
JOIN player_stats ps ON...`
- **Response:** LeBron James' average points per game is 24.4.


**✓ What is Stephen Curry's 3-point percentage?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 6203ms
- **Generated SQL:** `SELECT p.name, ps.three_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name ...`
- **Response:** Stephen Curry's 3-point percentage is 39.7%.


**✓ What is Nikola Jokić's total rebounds?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2155ms
- **Generated SQL:** `SELECT p.name, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name LIKE '...`
- **Response:** Nikola Jokić's total rebounds are 889.


**✓ How many assists did Chris Paul record?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 1970ms
- **Generated SQL:** `SELECT p.name, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name LIKE '...`
- **Response:** Chris Paul recorded 607 assists.


### Simple Sql Team Roster (2 tests)

**✓ How many players on the Lakers roster?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 5046ms
- **Generated SQL:** `SELECT COUNT(*)
FROM players
WHERE team_abbr = 'LAL';...`
- **Response:** There are 20 players on the Lakers roster.


**✓ List all players on the Golden State Warriors.**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2361ms
- **Generated SQL:** `SELECT p.name
FROM players p
WHERE p.team_abbr = 'GSW';...`
- **Response:** The players on the Golden State Warriors are: Stephen Curry, Brandin Podziemski, Moses Moody, Jonathan Kuminga, Draymond Green, Trayce Jackson-Davis, Gary Payton II, Kevon Looney, Quinten Post, and Gu...

### Simple Sql Top N (6 tests)

**✓ Who scored the most points this season?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 4426ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DES...`
- **Response:** Shai Gilgeous-Alexander scored the most points this season, with 2,485 points.


**✓ Who are the top 3 rebounders in the league?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2252ms
- **Generated SQL:** `SELECT p.name, ps.reb
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.reb DES...`
- **Response:** The top 3 rebounders in the league are: 1. Ivica Zubac with 1,008 rebounds, 2. Domantas Sabonis with 973 rebounds, and 3. Karl-Anthony Towns with 922 rebounds.


**✓ Who are the top 5 players in steals?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 6625ms
- **Generated SQL:** `SELECT p.name, ps.stl
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.stl DES...`
- **Response:** The top 5 players in steals are:

1. Dyson Daniels, stl: 228
2. Shai Gilgeous-Alexander, stl: 129
3. Nikola Jokić, stl: 126
4. Kris Dunn, stl: 126
5. Cason Wallace, stl: 122


**✓ Who has the best free throw percentage?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 6029ms
- **Generated SQL:** `SELECT p.name, ps.ft_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.ft_pct ...`
- **Response:** Sam Hauser has the best free throw percentage at 100%.


**✓ Who has the highest true shooting percentage?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2817ms
- **Generated SQL:** `SELECT p.name, ps.ts_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE ps.ts_pct ...`
- **Response:** Kai Jones has the highest true shooting percentage.


**✓ Which player has the most wins this season?**

- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 2019ms
- **Generated SQL:** `SELECT p.name, ps.w
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.w DESC
LI...`
- **Response:** Jarrett Allen has the most wins this season with 64.


---

## Report Sections

1. Executive Summary - Overall metrics and success rates
2. Failure Analysis - Execution failures, misclassifications, performance
3. Response Quality Analysis - Error patterns, fallback behavior, response metrics
4. Query Quality Analysis - SQL structure, complexity, column selection
5. Key Findings - Actionable insights and recommendations
6. Detailed Test Results - Complete test-by-test breakdown

