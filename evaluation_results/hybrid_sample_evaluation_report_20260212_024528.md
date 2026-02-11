# Hybrid Sample Evaluation Report

**Generated:** 2026-02-12 03:03:09
**Sample Size:** 5 queries (from 50 total)
**Results JSON:** `hybrid_sample_evaluation_20260212_024528.json`

---

## Executive Summary

- **Total Queries:** 5
- **Successful:** 5/5 (100%)
- **Avg Processing Time:** 10680ms

### Routing Distribution

| Routing | Count |
|---------|-------|
| BOTH | 2 |
| SQL | 2 |
| VECTOR | 1 |

## Query-by-Query Results

### 1. [PASS] Who scored the most points this season and what makes them an effective scorer?

- **Category:** tier1_stat_plus_context
- **Routing:** BOTH
- **Sources:** 5
- **Processing Time:** 13329ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.fg_pct, ps.ts_pct, ps.efg_pct
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.pts DESC
LIMIT 1;`
- **Expected Answer:** Shai Gilgeous-Alexander scored 2485 points. His effectiveness comes from his ability to get to the rim and draw fouls.
- **Response:** Shai Gilgeous-Alexander scored 2485 points this season [SQL]. To understand what makes a player an effective scorer, we can look at related metrics. The NBA Statistics Glossary defines "PTS" as points scored per game [Source: regular NBA.xlsx]. Furthermore, True Shooting Percentage (TS%) and Effective Field Goal Percentage (EFG%) provide insights into scoring efficiency. Gilgeous-Alexander has a T...

**Sources Retrieved:**

| # | Source | Score |
|---|--------|-------|
| 1 | regular NBA.xlsx | 77.5% |
| 2 | Reddit 3.pdf | 76.8% |
| 3 | Reddit 3.pdf | 76.5% |
| 4 | Reddit 3.pdf | 76.5% |
| 5 | Reddit 3.pdf | 76.3% |

### 2. [PASS] Compare the Celtics and Lakers stats and how fans view each team's championship 

- **Category:** hybrid_team_comparison
- **Routing:** SQL
- **Sources:** 0
- **Processing Time:** 7421ms
- **Generated SQL:** `SELECT
  p.name,
  ps.pts,
  ps.reb,
  ps.ast,
  p.team_abbr
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE
  p.team_abbr IN ('BOS',`
- **Expected Answer:** Celtics: 9551 PTS, 3723 REB, 2147 AST. Lakers: 8691 PTS, 3321 REB, 2135 AST. The Celtics are statistically dominant while the Lakers rely more on star power.
- **Response:** Here's a comparison of the Celtics and Lakers stats from the provided data, along with a general overview of fan perceptions regarding their championship hopes:

**Team Statistics:**

*   **Boston Celtics (BOS):**
    *   Jayson Tatum: 1930 points, 626 rebounds, 432 assists
    *   Jaylen Brown: 1399 points, 365 rebounds, 284 assists
    *   Derrick White: 1246 points, 342 rebounds, 365 assists
  ...

### 3. [PASS] Which young players under 25 are putting up the best numbers, and what do fans e

- **Category:** hybrid_young_talent
- **Routing:** SQL
- **Sources:** 0
- **Processing Time:** 13177ms
- **Generated SQL:** `SELECT p.name, ps.pts, ps.reb, ps.ast
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
WHERE p.age < 25
ORDER BY ps.pts DESC, ps.reb DESC, p`
- **Expected Answer:** Top young stars under 25: Anthony Edwards (23, 2180 PTS), Cade Cunningham (23, 1827), Jalen Green (23, 1722), Jalen Williams (24, 1490), Alperen Sengun (22, 1452). Fans see this generation as ready to
- **Response:** Based on the data, here are some young players under 25 putting up impressive numbers:

*   **Anthony Edwards:** 2180 points, 450 rebounds, 356 assists
*   **Cade Cunningham:** 1827 points, 427 rebounds, 637 assists
*   **Jalen Green:** 1722 points, 377 rebounds, 279 assists
*   **Jalen Williams:** 1490 points, 366 rebounds, 352 assists
*   **Alperen Sengun:** 1452 points, 783 rebounds, 372 assist...

### 4. [PASS] yo whos got da best stats AND what do ppl think about them on reddit

- **Category:** hybrid_noisy
- **Routing:** VECTOR
- **Sources:** 5
- **Processing Time:** 6409ms
- **Expected Answer:** Shai Gilgeous-Alexander leads with 2485 PTS. Reddit fans praise his complete game and consider him the top player this season.
- **Response:** Based on advanced stats, the two best teams in the playoffs have a chance of playing against each other in the Finals [Source: Reddit 2.pdf]. However, some people consider this potential matchup to be a "snoozefest," and feel that the NBA media is biased and terrible at marketing their product [Source: Reddit 2.pdf]. Many want to see the Thunder lose and SGA "exposed," while others feel Haliburton...

**Sources Retrieved:**

| # | Source | Score |
|---|--------|-------|
| 1 | Reddit 2.pdf | 75.6% |
| 2 | Reddit 2.pdf | 74.9% |
| 3 | Reddit 2.pdf | 74.1% |
| 4 | Reddit 2.pdf | 74.0% |
| 5 | Reddit 2.pdf | 73.9% |

### 5. [PASS] Who leads the league in blocks and what makes them elite defenders according to 

- **Category:** hybrid_defensive
- **Routing:** BOTH
- **Sources:** 5
- **Processing Time:** 13063ms
- **Generated SQL:** `SELECT p.name, ps.blk
FROM players p
JOIN player_stats ps ON p.id = ps.player_id
ORDER BY ps.blk DESC
LIMIT 1;`
- **Expected Answer:** Victor Wembanyama leads with 175 BLK (plus 1118 PTS, 506 REB). Fans consider his shot-blocking a generational skill combining elite length with instinctive timing.
- **Response:** Victor Wembanyama leads the league with 175 blocks [SQL]. While the provided context doesn't directly discuss Wembanyama's defensive prowess, it does highlight the importance of physical defense and avoiding fouls, as seen in the analysis of Randle's defensive style [Source: Reddit 1.pdf]. Randle's ability to defend with his chest rather than his hands to avoid fouls, and his strength in one-on-on...

**Sources Retrieved:**

| # | Source | Score |
|---|--------|-------|
| 1 | Reddit 1.pdf | 76.1% |
| 2 | Reddit 2.pdf | 76.0% |
| 3 | Reddit 2.pdf | 75.6% |
| 4 | Reddit 2.pdf | 75.5% |
| 5 | Reddit 2.pdf | 75.5% |

---

*Report generated from 5-case sample of 50 Hybrid test cases*