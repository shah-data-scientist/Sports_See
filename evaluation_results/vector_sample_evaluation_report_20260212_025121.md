# Vector Sample Evaluation Report

**Generated:** 2026-02-12 03:07:22
**Sample Size:** 5 queries (from 75 total)
**Results JSON:** `vector_sample_evaluation_20260212_025121.json`

---

## Executive Summary

- **Total Queries:** 5
- **Successful:** 5/5 (100%)
- **Avg Processing Time:** 5042ms

## Query-by-Query Results

### 1. [PASS] What do Reddit users think about teams that have impressed in the playoffs?

- **Category:** simple
- **Routing:** vector_only
- **Sources Retrieved:** 5
- **Processing Time:** 6704ms
- **Response:** Reddit users have varying opinions on which teams have impressed them in the playoffs. Some users are impressed by the Indiana Pacers and Minnesota Timberwolves, particularly Anthony Edwards of the Timberwolves, noting the team's strong play and Edwards' massive leap in performance [Source: Reddit 1.pdf]. The Orlando Magic have impressed the original poster due to the play of Paolo Banchero and Fr...

**Sources Retrieved:**

| # | Source | Score | Text Preview |
|---|--------|-------|--------------|
| 1 | Reddit 1.pdf | 84.6% | === REDDIT POST === Title: Who are teams in the playoffs tha... |
| 2 | Reddit 1.pdf | 84.5% | === REDDIT POST === Title: Who are teams in the playoffs tha... |
| 3 | Reddit 1.pdf | 84.3% | === REDDIT POST === Title: Who are teams in the playoffs tha... |
| 4 | Reddit 1.pdf | 83.8% | === REDDIT POST === Title: Who are teams in the playoffs tha... |
| 5 | Reddit 1.pdf | 83.7% | === REDDIT POST === Title: Who are teams in the playoffs tha... |

- **Ground Truth:** Should retrieve Reddit 1.pdf: 'Who are teams in the playoffs that have impressed you?' by u/MannerSuperb (31 upvotes, 236 comments). Expected teams mentioned: Magic (Paolo Banchero, Franz Wagner), Ind...

### 2. [PASS] According to basketball discussions, what makes a player efficient in playoffs?

- **Category:** complex
- **Routing:** vector_only
- **Sources Retrieved:** 5
- **Processing Time:** 4975ms
- **Response:** Reggie Miller's efficiency in the playoffs is attributed to his increased output when games mattered, described as being a "monster in the playoffs." [Source: Reddit 3.pdf] He also had multiple postseasons at a high scoring rate with great efficiency, putting him in a category with players like Durant, LeBron, and Kawhi. [Source: Reddit 3.pdf]


**Sources Retrieved:**

| # | Source | Score | Text Preview |
|---|--------|-------|--------------|
| 1 | Reddit 3.pdf | 83.0% | === REDDIT POST === Title: Reggie Miller is the most efficie... |
| 2 | Reddit 3.pdf | 82.8% | === REDDIT POST === Title: Reggie Miller is the most efficie... |
| 3 | Reddit 3.pdf | 82.7% | === REDDIT POST === Title: Reggie Miller is the most efficie... |
| 4 | Reddit 3.pdf | 82.7% | === REDDIT POST === Title: Reggie Miller is the most efficie... |
| 5 | Reddit 3.pdf | 82.6% | === REDDIT POST === Title: Reggie Miller is the most efficie... |

- **Ground Truth:** Should retrieve Reddit 3.pdf discussion about playoff efficiency. Content includes TS% metric (True Shooting %), comparison table of 20 players' playoff efficiency, discussion of what qualifies as 'ef...

### 3. [PASS] What is the weather forecast for Los Angeles tomorrow?

- **Category:** noisy
- **Routing:** vector_only
- **Sources Retrieved:** 5
- **Processing Time:** 4628ms
- **Response:** The available context doesn't contain this information.


**Sources Retrieved:**

| # | Source | Score | Text Preview |
|---|--------|-------|--------------|
| 1 | regular NBA.xlsx | 65.4% | METRIC: FGM Description: Tirs réussis par match (Field Goals... |
| 2 | regular NBA.xlsx | 64.9% | METRIC: OREB Description: Rebonds offensifs ----------------... |
| 3 | regular NBA.xlsx | 64.5% | METRIC: DREB% Description: Idem en défensif ----------------... |
| 4 | regular NBA.xlsx | 64.4% | METRIC: + / - Description: Plus-Minus (écart de score lorsqu... |
| 5 | Reddit 2.pdf | 64.2% | === REDDIT POST === Title: How is it that the two best teams... |

- **Ground Truth:** Out-of-scope query. Vector search WILL retrieve irrelevant chunks (likely Reddit PDFs with ~65-70% similarity due to semantic overlap with 'Los Angeles'). However, LLM should recognize retrieved conte...

### 4. [PASS] What do fans say about the Lakers?

- **Category:** conversational
- **Routing:** vector_only
- **Sources Retrieved:** 5
- **Processing Time:** 2701ms
- **Response:** Fans are desperate for superstars to be in big games, and ESPN could be talking about bowling and they'd turn it into a discussion on LeBron. [Source: Reddit 2.pdf]
In 2020, the Lakers never had home court advantage the entire playoffs for every game [Source: Reddit 4.pdf]


**Sources Retrieved:**

| # | Source | Score | Text Preview |
|---|--------|-------|--------------|
| 1 | Reddit 2.pdf | 74.6% | === REDDIT POST === Title: How is it that the two best teams... |
| 2 | Reddit 2.pdf | 73.8% | === REDDIT POST === Title: How is it that the two best teams... |
| 3 | Reddit 1.pdf | 73.8% | === REDDIT POST === Title: Who are teams in the playoffs tha... |
| 4 | Reddit 2.pdf | 73.5% | === REDDIT POST === Title: How is it that the two best teams... |
| 5 | Reddit 4.pdf | 73.3% | === REDDIT POST === Title: Which NBA team did not have home ... |

- **Ground Truth:** Should retrieve Reddit discussions mentioning Lakers. Most likely source: Reddit 4.pdf mentions '2020 Lakers' as example of team without home court advantage in Finals. May also appear in Reddit 1 or ...

### 5. [PASS] What are the most popular opinions about the two best playoff teams?

- **Category:** simple
- **Routing:** vector_only
- **Sources Retrieved:** 5
- **Processing Time:** 6204ms
- **Response:** The most popular opinions are that people are mad it's not their team in the playoffs, and some doubt it will even be extremely toxic between the Pacers and Thunder fans. [Source: Reddit 2.pdf]


**Sources Retrieved:**

| # | Source | Score | Text Preview |
|---|--------|-------|--------------|
| 1 | Reddit 2.pdf | 80.1% | === REDDIT POST === Title: How is it that the two best teams... |
| 2 | Reddit 2.pdf | 79.9% | === REDDIT POST === Title: How is it that the two best teams... |
| 3 | Reddit 2.pdf | 79.5% | === REDDIT POST === Title: How is it that the two best teams... |
| 4 | Reddit 2.pdf | 79.4% | === REDDIT POST === Title: How is it that the two best teams... |
| 5 | Reddit 2.pdf | 79.0% | === REDDIT POST === Title: How is it that the two best teams... |

- **Ground Truth:** Should retrieve Reddit 2.pdf: 'How is it that the two best teams in the playoffs based on stats, having a chance of playing against each other in the Finals, is considered to be a snoozefest?' by u/mo...

---

*Report generated from 5-case sample of 75 Vector test cases*