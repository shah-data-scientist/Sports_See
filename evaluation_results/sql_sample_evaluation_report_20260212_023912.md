# SQL Sample Evaluation Report

**Generated:** 2026-02-12 02:39:12
**Sample Size:** 5 queries (from 80 total)
**Results JSON:** `sql_sample_evaluation_20260212_023912.json`
**Rate Limit Delay:** 60s between queries

---

## Executive Summary

- **Total Queries:** 5
- **Successful:** 5/5 (100%)
- **Misclassifications:** 0
- **Avg Processing Time:** 13613ms

## Query-by-Query Results

### 1. [PASS] Who scored the most points this season?

- **Category:** simple_sql_top_n
- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 18118ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DESC
LIMIT 1;`
- **Expected Answer:** Shai Gilgeous-Alexander scored the most points with 2485 PTS.
- **Response:** Shai Gilgeous-Alexander scored the most points this season, with 2,485 points.


### 2. [PASS] Compare Jokić and Embiid's stats

- **Category:** comparison_sql_players
- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 8717ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.reb, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.name IN ('Nikola Jokić', 'Joel Embiid');`
- **Expected Answer:** Nikola Jokić: 2072 PTS, 889 REB, 714 AST. Joel Embiid: 452 PTS, 156 REB, 86 AST.
- **Response:** Nikola Jokić has 2072 points, 889 rebounds, and 714 assists, while Joel Embiid has 452 points, 156 rebounds, and 86 assists.


### 3. [PASS] What is the average player age in the NBA?

- **Category:** aggregation_sql_league
- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 13128ms
- **Generated SQL:** `SELECT AVG(age) AS avg_age
FROM players
WHERE age IS NOT NULL;`
- **Expected Answer:** The average player age in the NBA is 26.15 years.
- **Response:** The average player age in the NBA is 26.15 years.


### 4. [PASS] Which players score more points per game than the league average?

- **Category:** complex_sql_subquery
- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 14833ms
- **Generated SQL:** `SELECT p.name, ROUND(CAST(ps.pts AS FLOAT) / ps.gp, 1) AS ppg
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE (CAST(ps.pts AS FLOAT) `
- **Expected Answer:** Top 5 above-avg PPG: Shai Gilgeous-Alexander (32.7), Giannis Antetokounmpo (30.4), Nikola Jokić (29.6), Luka Dončić (28.2), Anthony Edwards (27.6).
- **Response:** Based on the data provided, the following players score more points per game than the league average:

1.  Shai Gilgeous-Alexander (32.7 ppg)
2.  Giannis Antetokounmpo (30.4 ppg)
3.  Nikola Jokić (29.6 ppg)
4.  Luka Dončić (28.2 ppg)
5.  Anthony Edwards (27.6 ppg)
6.  Jayson Tatum (26.8 ppg)
7.  Kev...

### 5. [PASS] whos got da most pts this szn

- **Category:** noisy_sql_typo
- **Expected Routing:** sql_only
- **Actual Routing:** sql_only
- **Processing Time:** 13268ms
- **Generated SQL:** `SELECT p.name, ps.pts
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DESC
LIMIT 1;`
- **Expected Answer:** Shai Gilgeous-Alexander has the most points with 2485.
- **Response:** Shai Gilgeous-Alexander has the most points this season, with 2,485.


---

*Report generated from 5-case sample of 80 SQL test cases*