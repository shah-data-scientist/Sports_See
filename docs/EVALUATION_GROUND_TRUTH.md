# Ground Truth Establishment Techniques

## Overview

This document describes the methodologies, tools, and scripts used to establish and verify ground truth for the three evaluation datasets in Sports_See.

| Dataset | File | Cases | Ground Truth Method |
|---------|------|-------|---------------------|
| SQL | `test_cases/sql_test_cases.py` | 67 | Direct database queries |
| Hybrid | `test_cases/sql_test_cases.py` | 18 | Database queries + descriptive analysis |
| Vector | `test_cases/vector_test_cases.py` | 79 | LLM-assisted descriptive expectations |

---

## 1. SQL Ground Truth (67 test cases)

### Method: Direct Database Verification

SQL ground truth is established by executing queries directly against the NBA statistics database (`data/sql/nba_stats.db`). This is the most rigorous approach since values can be verified deterministically.

### Process

1. **Write the expected SQL query** (`expected_sql`) that should correctly answer the natural language question
2. **Execute the query** against `data/sql/nba_stats.db` using SQLite3
3. **Record the exact results** in `ground_truth_data` (dict for single-row, list of dicts for multi-row)
4. **Write a human-readable answer** in `ground_truth_answer` that summarizes the data
5. **Run the verification script** to confirm `expected_sql` produces results matching `ground_truth_data`

### Tools Used

| Tool | Purpose |
|------|---------|
| **SQLite3** (Python `sqlite3` module) | Execute queries against `nba_stats.db` |
| **Custom query scripts** | Ad-hoc Python scripts to extract ground truth values in bulk |
| **Verification script** | `verification/verify_all_sql_ground_truth.py` — automated comparison |

### Verification Script

**Location:** `src/evaluation/verification/verify_all_sql_ground_truth.py`

**How it works:**
1. Imports all `SQL_TEST_CASES` from `test_cases/sql_test_cases.py`
2. For each test case, executes `expected_sql` against the live database
3. Compares actual results with `ground_truth_data` using:
   - Row count matching
   - Key-by-key value comparison
   - Float normalization (rounds to 2 decimal places)
   - Sort-independent comparison (sorts by first key)
4. Reports pass/fail for each case with detailed mismatch information

**Run command:**
```bash
poetry run python src/evaluation/verification/verify_all_sql_ground_truth.py
```

**Expected output:** `67/67 passed, 100.0% success rate`

### Ground Truth Data Structure

```python
SQLEvaluationTestCase(
    question="What is the average field goal percentage for the Lakers?",
    query_type=QueryType.SQL_ONLY,
    expected_sql="SELECT ROUND(AVG(ps.fg_pct), 1) as avg_fg_pct FROM players p JOIN player_stats ps ON p.id = ps.player_id WHERE p.team_abbr = 'LAL' AND ps.fg_pct IS NOT NULL",
    ground_truth_answer="The average field goal percentage for the Lakers is 44.6%.",
    ground_truth_data={"avg_fg_pct": 44.6},  # Verified from database
    category="aggregation_sql_team",
)
```

### Key Lessons

- **Ground truth must match actual database schema.** The NBA database has `players` and `player_stats` tables requiring JOIN. Early test cases had incorrect ground truth because they assumed a different schema.
- **Float precision matters.** Use `ROUND()` in SQL and match the same precision in `ground_truth_data`.
- **Sort order can differ.** The verification script sorts both expected and actual by the first key to handle ordering differences.

---

## 2. Hybrid Ground Truth (18 test cases)

### Method: Database Verification + Descriptive Analysis

Hybrid queries combine SQL data with contextual analysis from vector search. The ground truth has two components:

1. **`ground_truth_data`** — Verified from database (same as SQL method)
2. **`ground_truth_answer`** — Combines verified data with expected contextual insights

### Process

1. **SQL component:** Same as SQL method — execute `expected_sql`, verify numeric data
2. **Contextual component:** Written manually based on understanding of the Reddit documents in the vector store and what the LLM should synthesize
3. **Answer verification:** The script checks that `ground_truth_answer` mentions key entities from `ground_truth_data` (e.g., player names)
4. **Some cases have `ground_truth_data=None`** — these are pure analysis questions where only the contextual reasoning matters (e.g., "why is this metric important?")

### Tools Used

| Tool | Purpose |
|------|---------|
| **SQLite3** | Verify SQL data component |
| **Manual review** | Write contextual analysis expectations |
| **Verification script** | `verification/verify_all_hybrid_ground_truth.py` — SQL + answer verification |

### Verification Script

**Location:** `src/evaluation/verification/verify_all_hybrid_ground_truth.py`

**How it works:**
1. Imports all `HYBRID_TEST_CASES`
2. For each test case:
   a. Executes `expected_sql` against the database
   b. Compares actual data with `ground_truth_data` (same as SQL verification)
   c. Checks that `ground_truth_answer` mentions key names from `ground_truth_data`
3. Reports: PASS (data match), FAIL (data mismatch), WARNING (answer doesn't mention entities)

**Run command:**
```bash
poetry run python src/evaluation/verification/verify_all_hybrid_ground_truth.py
```

**Expected output:** `18/18 passed, 100.0% success rate`

### Ground Truth Data Structure

```python
SQLEvaluationTestCase(
    question="Who scored the most points this season and what makes them an effective scorer?",
    query_type=QueryType.HYBRID,
    expected_sql="SELECT p.name, ps.pts FROM ... ORDER BY ps.pts DESC LIMIT 1",
    ground_truth_answer="Shai Gilgeous-Alexander scored 2485 points. His effectiveness comes from his ability to get to the rim and draw fouls.",
    ground_truth_data={"name": "Shai Gilgeous-Alexander", "pts": 2485},  # Verified from DB
    category="tier1_stat_plus_context",
)
```

---

## 3. Vector Ground Truth (79 test cases)

### Method: LLM-Assisted Descriptive Expectations

Vector ground truth cannot be verified against a database because it deals with unstructured text (Reddit discussions, glossary). Instead, ground truth is established as **descriptive expectations** about what the retrieval system should return.

### Process

1. **Analyze the vector store contents** — The vector store contains chunks from 4 Reddit PDFs and a glossary (regular NBA.xlsx). Actual content was inspected to understand what information is available.
2. **Write descriptive ground truth using Claude** — For each test case, Claude was used to write a detailed paragraph describing:
   - Which source documents should be retrieved (e.g., "Reddit 1.pdf", "Reddit 3.pdf")
   - Expected similarity score ranges (e.g., "75-85%")
   - Key content that should appear in retrieved chunks
   - Expected LLM behavior (e.g., "should decline to answer" for out-of-scope)
   - Boosting expectations (e.g., "Reddit 3 should rank first due to 1300 upvotes")
3. **Pattern-based consistency** — Ground truth follows consistent patterns across categories, modeled on the initial test cases written during project development

### Tools Used

| Tool | Purpose |
|------|---------|
| **Claude (Anthropic)** | Write descriptive ground truth paragraphs inspired by existing patterns |
| **Vector store inspection** | Manual review of actual chunks in FAISS index + pickle files |
| **No automated verification script** | Ground truth is qualitative, not verifiable against a DB |

### Why No Automated Verification?

Unlike SQL/Hybrid, vector ground truth describes **expected retrieval behavior** rather than exact values. Verification happens during the actual evaluation run, where RAGAS metrics (faithfulness, answer relevancy, context precision, context recall) measure how well the system performs against these expectations.

### Ground Truth Structure

Each vector test case has a `ground_truth` string field (not `ground_truth_data`), following this template:

```python
EvaluationTestCase(
    question="What do Reddit users think about teams that have impressed in the playoffs?",
    ground_truth=(
        "Should retrieve Reddit 1.pdf: 'Who are teams in the playoffs that have impressed you?' "
        "by u/MannerSuperb (31 upvotes, 236 comments). Expected teams mentioned: Magic, Pacers, "
        "Timberwolves. Comments discuss exceeding expectations, young talent. "
        "Expected sources: 2-5 chunks from Reddit 1.pdf with 75-85% similarity."
    ),
    category=TestCategory.SIMPLE,
)
```

### Ground Truth Categories

| Category | Count | Ground Truth Focus |
|----------|-------|--------------------|
| SIMPLE | 22 | Single-source retrieval, expected document + similarity range |
| COMPLEX | 20 | Multi-document synthesis, cross-document themes, analytical depth |
| NOISY | 25 | Robustness to typos/slang/gibberish/injection, expected LLM behavior |
| CONVERSATIONAL | 12 | Context maintenance across turns, pronoun resolution, topic switching |

### Descriptive Ground Truth Patterns

**For Reddit opinion queries:**
- Specify which Reddit PDF(s) should be retrieved
- Include post metadata (upvotes, comments) for boosting verification
- Mention expected comment content and key entities
- Provide expected similarity range

**For glossary/terminology queries:**
- Specify that glossary (regular NBA.xlsx) should rank highest
- Note if Reddit content might compete (boosting verification)
- Expected similarity: 85-95% for exact term matches

**For out-of-scope/noisy queries:**
- Describe expected LLM decline behavior
- Note that vector search WILL retrieve irrelevant chunks (expected similarity range)
- Specify that LLM should recognize topic mismatch

**For adversarial/security queries:**
- Describe expected sanitization behavior
- Note that no database/file system operations should occur
- Expected: safe error handling or clarification request

---

## Database Schema Reference

The NBA database (`data/sql/nba_stats.db`) has two tables:

### `players` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Player full name |
| team | TEXT | Full team name |
| team_abbr | TEXT | 3-letter team abbreviation |
| age | INTEGER | Player age |

### `player_stats` table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| player_id | INTEGER | FK to players.id |
| gp | INTEGER | Games played |
| w / l | INTEGER | Wins / Losses |
| pts | INTEGER | Total points |
| reb | INTEGER | Total rebounds |
| ast | INTEGER | Total assists |
| stl | INTEGER | Total steals |
| blk | INTEGER | Total blocks |
| tov | INTEGER | Total turnovers |
| fg_pct | REAL | Field goal percentage |
| three_pct | REAL | 3-point percentage |
| three_pa | INTEGER | 3-point attempts |
| ft_pct | REAL | Free throw percentage |
| efg_pct | REAL | Effective field goal % |
| ts_pct | REAL | True shooting % |
| pie | REAL | Player Impact Estimate |
| ... | ... | (40+ columns total) |

---

## File Organization

```
src/evaluation/
    test_cases/
        sql_test_cases.py          # 67 SQL + 18 Hybrid test cases
        vector_test_cases.py       # 79 Vector test cases
    verification/
        verify_all_sql_ground_truth.py     # SQL: DB verification (67 cases)
        verify_all_hybrid_ground_truth.py  # Hybrid: DB + answer verification (18 cases)
    analysis/
        sql_quality_analysis.py    # SQL report generation
        vector_quality_analysis.py # Vector report generation
        hybrid_quality_analysis.py # Hybrid report generation
    runners/
        run_sql_evaluation.py      # SQL evaluation runner
        run_vector_evaluation.py   # Vector evaluation runner
        run_hybrid_evaluation.py   # Hybrid evaluation runner
```

---

## Running All Verifications

```bash
# SQL ground truth (67 cases)
poetry run python src/evaluation/verification/verify_all_sql_ground_truth.py

# Hybrid ground truth (18 cases)
poetry run python src/evaluation/verification/verify_all_hybrid_ground_truth.py

# Vector: no DB verification — ground truth is qualitative
# Validation happens during evaluation via RAGAS metrics
```

---

## Summary of Techniques

| Aspect | SQL | Hybrid | Vector |
|--------|-----|--------|--------|
| **Ground truth type** | Exact numeric values | Numeric + descriptive | Descriptive only |
| **Verification method** | Automated DB comparison | Automated DB + entity mention check | RAGAS metrics during evaluation |
| **Primary tool** | SQLite3 queries | SQLite3 + manual review | Claude (LLM-assisted) |
| **Verification script** | `verify_all_sql_ground_truth.py` | `verify_all_hybrid_ground_truth.py` | None (qualitative) |
| **Reproducibility** | Deterministic (DB is static) | SQL part deterministic, context descriptive | Descriptive (based on vector store contents) |
| **Update trigger** | Database rebuild | Database rebuild or vector store change | Vector store content change |
