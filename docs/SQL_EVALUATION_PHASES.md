# SQL Evaluation Strategy: Two-Phase Approach

**Document Type:** Evaluation Methodology
**Date:** 2026-02-08
**Purpose:** Phased evaluation of SQL and Hybrid queries

---

## Overview

This document describes the **two-phase evaluation strategy** for SQL and Hybrid query handling in the Sports_See NBA RAG system.

**Philosophy:** Separate SQL tool accuracy from integration quality to enable faster, focused optimization.

---

## Evaluation Strategy

```
┌─────────────────────────────────────────────────┐
│  PHASE SQL-1: SQL-Only Queries                  │
│  Goal: Optimize SQL tool accuracy               │
│  Test Cases: 21 (7 Simple, 7 Comparison, 7 Agg)│
│  Target: >85% SQL accuracy                      │
│  Focus: SQL generation, execution, results      │
└─────────────────────────────────────────────────┘
                      ↓
              SQL Tool Optimized
                      ↓
┌─────────────────────────────────────────────────┐
│  PHASE SQL-2: Hybrid Queries                    │
│  Goal: Optimize SQL + Vector integration        │
│  Test Cases: 4 hybrid queries                   │
│  Target: >75% integration quality               │
│  Focus: Component blending, completeness        │
└─────────────────────────────────────────────────┘
                      ↓
          Production Deployment Ready
```

---

## Phase SQL-1: SQL-Only Query Evaluation

### **Objective**

Validate and optimize SQL tool accuracy **before** tackling complex integration challenges.

### **Test Coverage: 21 Cases**

#### **Simple SQL (7 cases)**
- Single-table queries
- Player-specific stats
- Top N queries

**Examples:**
- "Who scored the most points this season?"
- "What is LeBron James' average points per game?"
- "Who are the top 3 rebounders in the league?"

#### **Comparison SQL (7 cases)**
- Multi-player comparisons
- WHERE IN clauses
- Ordered results

**Examples:**
- "Compare Jokić and Embiid's stats"
- "Who has more rebounds, Giannis or Anthony Davis?"
- "Who shoots better from 3, Curry or Lillard?"

#### **Aggregation SQL (7 cases)**
- League-wide statistics
- AVG/COUNT/MAX functions
- Filtering with thresholds

**Examples:**
- "What is the average 3-point percentage for all players?"
- "How many players scored over 1000 points?"
- "What is the highest PER in the league?"

### **Evaluation Metrics**

```python
SQLAccuracyMetrics:
  - sql_syntax_correct (Query executes without errors?)
  - sql_semantic_correct (Query logically correct? ≥60% keyword overlap)
  - results_accurate (Results match ground truth?)
  - execution_success (No execution failures?)

  → Overall Score: Average of 4 binary metrics (0-1)
  → Target: >0.85 (85% accuracy)
```

### **Usage**

```bash
# Run Phase SQL-1 evaluation
poetry run python scripts/evaluate_sql_only.py

# Select test set
Select test set (1-4, default=4): 4  # All 21 cases
```

### **Example Output**

```
==============================================================================
  SQL-ONLY QUERY EVALUATION RESULTS (PHASE SQL-1)
  21 Test Cases | Target: >85% SQL Accuracy
==============================================================================

SIMPLE SQL QUERIES (7 cases)
------------------------------------------------------------------------------
[PASS] Who scored the most points this season?                  | Score: 1.00
[PASS] What is LeBron James' average points per game?           | Score: 1.00
  Category Average: 0.952 | Pass Rate: 100.0%

COMPARISON SQL QUERIES (7 cases)
------------------------------------------------------------------------------
[PASS] Compare Jokić and Embiid's stats                        | Score: 1.00
  Category Average: 0.905 | Pass Rate: 85.7%

AGGREGATION SQL QUERIES (7 cases)
------------------------------------------------------------------------------
[FAIL] How many players scored over 1000 points?               | Score: 0.50
  Category Average: 0.786 | Pass Rate: 71.4%

==============================================================================
OVERALL RESULTS
------------------------------------------------------------------------------
Average SQL Accuracy: 0.881
Pass Rate: 85.7%
TARGET: >85% accuracy

✓ TARGET MET - Ready for Phase SQL-2
==============================================================================
```

### **Optimization Loop**

```
1. Run Phase SQL-1 evaluation
   └─> Identify failing categories

2. Analyze failures
   └─> Read generated SQL queries
   └─> Check error messages
   └─> Identify patterns

3. Fix SQL tool
   └─> Update few-shot examples in src/tools/sql_tool.py
   └─> Improve SQL generation prompt
   └─> Add error handling

4. Re-run evaluation
   └─> Track improvement

5. Repeat until >85% accuracy
   └─> Then proceed to Phase SQL-2
```

### **Success Criteria**

✅ **Overall SQL Accuracy: >85%**
✅ **All 3 categories passing (≥85% each)**
✅ **Low failure rate (<15%)**

---

## Phase SQL-2: Hybrid Query Evaluation

### **Objective**

Validate SQL + Vector integration quality **after** SQL tool is proven accurate.

### **Prerequisites**

- ✅ Phase SQL-1 passed (>85% SQL accuracy)
- ✅ SQL tool generating correct queries
- ✅ Few-shot examples working

### **Test Coverage: 4 Cases**

**All hybrid queries require both SQL stats AND contextual analysis:**

1. **"Compare Jokić and Embiid's stats and explain who's better"**
   - SQL: Fetch both players' stats
   - Vector: Retrieve MVP discussion, playstyle analysis
   - Integration: Blend stats with "who's better" reasoning

2. **"Who has the best 3P% and why are they so effective?"**
   - SQL: Find highest 3P% player
   - Vector: Retrieve shooting mechanics context
   - Integration: Connect stats to effectiveness explanation

3. **"What are LeBron's stats and how does his playstyle work?"**
   - SQL: Fetch LeBron's stats
   - Vector: Retrieve playstyle description
   - Integration: Stats + playstyle explanation

4. **"Show me Giannis' stats and explain why he's a good defender"**
   - SQL: Fetch defensive stats
   - Vector: Retrieve defensive ability context
   - Integration: Stats + defensive analysis

### **Evaluation Metrics**

```python
HybridIntegrationMetrics:
  - sql_component_used (SQL results appear in answer?)
  - vector_component_used (Context phrases in answer?)
  - components_blended (Coherent integration, not concatenation?)
  - answer_complete (Addresses both stats AND analysis?)

  → Integration Score: Average of 4 binary metrics (0-1)
  → Target: >0.75 (75% integration quality)
```

### **Usage**

```bash
# Run Phase SQL-2 evaluation
poetry run python scripts/evaluate_hybrid_queries.py
```

### **Example Output**

```
==============================================================================
  HYBRID QUERY EVALUATION RESULTS (PHASE SQL-2)
  4 Test Cases | Target: >75% Integration Quality
==============================================================================

TEST 1: Compare Jokić and Embiid's stats and explain who's better
------------------------------------------------------------------------------
[PASS] Integration Score: 1.00

Integration Metrics:
  SQL component used:    ✓
  Vector component used: ✓
  Components blended:    ✓
  Answer complete:       ✓

Generated Response:
  Nikola Jokić: 2018 PTS, 891 REB, 688 AST. Joel Embiid: 2159 PTS, 813 REB,
  296 AST. While Embiid edges Jokić in scoring, Jokić's superior playmaking...

TEST 2: Who has the best 3P% and why are they so effective?
------------------------------------------------------------------------------
[FAIL] Integration Score: 0.50

DIAGNOSIS:
  ✗ Vector context not used - Check retrieval quality
  ✗ Poor blending - Improve system prompt integration

==============================================================================
OVERALL RESULTS
------------------------------------------------------------------------------
Average Integration Score: 0.750
Pass Rate: 75.0%
TARGET: >75% integration quality

Component Breakdown:
  SQL usage:         100.0%
  Vector usage:      75.0%  ← Need improvement
  Blending quality:  75.0%  ← Need improvement
  Completeness:      75.0%

✓ TARGET MET - Ready for production deployment
==============================================================================
```

### **Optimization Loop**

```
1. Run Phase SQL-2 evaluation
   └─> Identify integration issues

2. Diagnose failures
   └─> SQL not used? → Check QueryClassifier routing
   └─> Vector not used? → Check retrieval quality
   └─> Poor blending? → Check system prompt
   └─> Incomplete? → Check response generation

3. Fix integration
   └─> Update ChatService routing logic
   └─> Improve system prompt for blending
   └─> Enhance QueryClassifier for HYBRID detection

4. Re-run evaluation
   └─> Track improvement

5. Repeat until >75% integration quality
   └─> Then deploy to production
```

### **Success Criteria**

✅ **Overall Integration Score: >75%**
✅ **SQL usage: 100%** (all queries use SQL)
✅ **Vector usage: >75%** (most queries use context)
✅ **Blending quality: >75%** (coherent integration)

---

## Why Two Phases?

### **Advantages of Phased Approach**

#### **1. Isolation of Variables**

**Problem with evaluating everything at once:**
```
❌ Hybrid query fails (score: 0.40)
   → Is it SQL generation? Integration? Vector retrieval?
   → Hard to debug!
```

**Solution with phased evaluation:**
```
✅ Phase SQL-1: SQL accuracy 0.90 → SQL tool works!
✅ Phase SQL-2: Hybrid fails (0.40)
   → Must be integration issue, not SQL
   → Easy to fix!
```

#### **2. Faster Iteration**

- **Phase SQL-1**: 21 cases, ~3 minutes, quick SQL tool fixes
- **Phase SQL-2**: 4 cases, ~2 minutes, focused integration fixes

vs.

- **Combined**: 25+ cases, ~10 minutes, complex debugging

#### **3. Clear Success Criteria**

- **Phase SQL-1**: >85% SQL accuracy → Move to Phase SQL-2
- **Phase SQL-2**: >75% integration → Deploy to production

vs.

- **Combined**: Unclear when "good enough"

#### **4. Matches Project Philosophy**

**Vector Query Phases (6-9):**
- Phase 6: Baseline retrieval
- Phase 7: Query expansion
- Phase 8: Citation prompt
- Phase 9: Hybrid category-aware prompts

**SQL Query Phases (SQL-1, SQL-2):**
- Phase SQL-1: Baseline SQL accuracy
- Phase SQL-2: Hybrid integration

---

## Files Structure

```
Sports_See/
├── src/
│   └── evaluation/
│       ├── sql_evaluation.py          # Pydantic models
│       ├── sql_test_cases.py          # 4 hybrid cases
│       └── sql_only_test_cases.py     # 21 SQL-only cases ⭐ NEW
├── scripts/
│   ├── evaluate_sql_only.py           # Phase SQL-1 script ⭐ NEW
│   └── evaluate_hybrid_queries.py     # Phase SQL-2 script ⭐ NEW
├── evaluation_results/
│   ├── sql_only_phase1.json          # Phase SQL-1 results
│   └── hybrid_queries_phase2.json    # Phase SQL-2 results
└── docs/
    ├── SQL_HYBRID_EVALUATION_GUIDE.md # Original guide
    └── SQL_EVALUATION_PHASES.md       # This document ⭐ NEW
```

---

## Comparison: Old vs. New

| Aspect | Old (Combined) | **NEW (Phased)** |
|--------|----------------|------------------|
| **Test Cases** | 14 mixed | **21 SQL + 4 Hybrid (25 total)** |
| **Evaluation** | All at once | **2 sequential phases** |
| **SQL Focus** | Mixed with integration | **Isolated in Phase SQL-1** |
| **Integration Focus** | Mixed with SQL | **Isolated in Phase SQL-2** |
| **Debugging** | Complex | **Simple (variables isolated)** |
| **Iteration Speed** | Slow (10+ min) | **Fast (3-5 min per phase)** |
| **Success Criteria** | Unclear | **Clear (85% → 75%)** |

---

## Timeline

### **Recommended Schedule**

**Week 1: Phase SQL-1**
- Day 1: Run baseline evaluation
- Day 2-3: Fix SQL tool (few-shot examples)
- Day 4: Re-run evaluation, iterate
- Day 5: Achieve >85% accuracy

**Week 2: Phase SQL-2**
- Day 1: Run baseline hybrid evaluation
- Day 2-3: Fix integration (system prompt, routing)
- Day 4: Re-run evaluation, iterate
- Day 5: Achieve >75% integration quality

**Week 3: Production Deployment**
- Deploy optimized SQL + Hybrid pipeline
- Monitor production metrics
- Collect user feedback

---

## Summary

### **Key Achievements**

✅ **21 SQL-only test cases** (3x original coverage)
✅ **4 hybrid test cases** (focused integration)
✅ **Two-phase evaluation strategy** (SQL → Integration)
✅ **Clear success criteria** (85% → 75%)
✅ **Automated scripts** with detailed reporting
✅ **Phased optimization loops** for faster iteration

### **Next Steps**

1. **Run Phase SQL-1** → Optimize SQL tool
2. **Run Phase SQL-2** → Optimize integration
3. **Deploy to production** → Monitor metrics

---

**Maintainer:** Shahu
**Last Updated:** 2026-02-08
**Related Documents:**
- [SQL_HYBRID_EVALUATION_GUIDE.md](SQL_HYBRID_EVALUATION_GUIDE.md) - Original comprehensive guide
- [PHASE_METRICS_COMPARISON.md](PHASE_METRICS_COMPARISON.md) - Vector query phases 6-9
