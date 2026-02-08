# SQL Hybrid Evaluation Report

**Date:** 2026-02-09
**Test Set:** SQL-only queries (68 test cases)
**Evaluation Script:** `scripts/evaluate_sql_hybrid.py`

---

## Executive Summary

This evaluation assessed the SQL query generation and execution capabilities of the Sports_See RAG chatbot using 68 comprehensive SQL test cases covering simple queries, comparisons, aggregations, complex multi-table queries, and conversational follow-ups.

### Key Results

- **Total Queries Evaluated:** 68 SQL-only queries
- **Average Overall Score:** 0.750 / 1.0
- **Average SQL Accuracy:** 0.864 / 1.0
- **Success Rate (≥ 0.7):** 63.2%
- **Failure Rate (< 0.7):** 36.8%

**Note:** Hybrid queries (SQL + Vector) were not evaluated in this run due to incompatible test case formats. The hybrid test cases in `src/evaluation/hybrid_test_cases.py` use `EvaluationTestCase` format, while the evaluation script expects `SQLEvaluationTestCase` format.

---

## SQL Accuracy Breakdown

### SQL Generation Quality

| Category | Count | Percentage | Description |
|----------|-------|------------|-------------|
| **Perfect (1.0)** | 35 | 51.5% | Correct syntax, semantics, and results |
| **Partial (0.5-1.0)** | 29 | 42.6% | Minor semantic or result accuracy issues |
| **Poor (≤ 0.5)** | 4 | 5.9% | Significant SQL generation problems |

**Key Finding:** The SQL generation component performs well, with 51.5% of queries generating perfect SQL. However, even with correct SQL, the LLM sometimes fails to properly use the results in its final answer.

---

## Quality Distribution

| Score Range | Label | Count | Percentage |
|-------------|-------|-------|------------|
| 0.9 - 1.0 | Excellent | 19 | 27.9% |
| 0.8 - 0.9 | Good | 13 | 19.1% |
| 0.7 - 0.8 | Fair | 11 | 16.2% |
| 0.6 - 0.7 | Poor | 13 | 19.1% |
| < 0.6 | Failing | 12 | 17.6% |

---

## Failure Analysis

### Total Failures: 25 queries (36.8%)

### Failure Reasons

1. **Answer Quality/Correctness (13 cases, 52%)**
   - Response doesn't match ground truth expectations
   - Incorrect interpretation or incomplete answers
   - Example: Query returns correct data but answer is formatted poorly

2. **LLM Cannot Use SQL Results (8 cases, 32%)**
   - SQL executes successfully but LLM responds "I cannot find this information"
   - Prompt engineering issue: LLM doesn't extract data from SQL results
   - Critical issue affecting system reliability

3. **SQL Generation Error (3 cases, 12%)**
   - Query classification fails
   - SQL syntax or semantic errors
   - Wrong table joins or column references

4. **Context/Conversation Tracking (1 case, 4%)**
   - Conversational follow-up queries fail
   - System lacks conversation memory
   - Example: "What about his assists?" after asking about a player

### Failure by Query Pattern

| Pattern | Failures | Notes |
|---------|----------|-------|
| **Aggregation queries** | 6 | COUNT, AVG, SUM operations often fail |
| **Conversational/context-dependent** | 6 | Follow-up queries lose context |
| **Top-N/ranking queries** | 6 | ORDER BY + LIMIT queries work but answers poor |
| **Other** | 5 | Miscellaneous issues |
| **Comparison queries** | 2 | Generally perform well |

---

## Top 5 Failure Cases

### 1. "How many players have more than 500 assists?"
- **Score:** 0.510
- **SQL Accuracy:** 0.75
- **Issue:** LLM responds "I cannot find this information" despite SQL returning correct count
- **Root Cause:** Prompt engineering failure - LLM doesn't extract scalar results

### 2. "Find players averaging double-digits in points, rebounds, and assists"
- **Score:** 0.510
- **SQL Accuracy:** 0.75
- **Issue:** LLM cannot process complex multi-condition results
- **Root Cause:** SQL returns data but LLM prompt fails to format it properly

### 3. "Find the most versatile players with at least 1000 points, 400 rebounds, and 200 assists"
- **Score:** 0.510
- **SQL Accuracy:** 0.75
- **Issue:** Answer provided but doesn't match ground truth format/completeness
- **Root Cause:** Answer quality assessment too strict or response incomplete

### 4. "What percentage of players have a true shooting percentage above 60%?"
- **Score:** 0.510
- **SQL Accuracy:** 0.75
- **Issue:** Percentage calculation result not extracted by LLM
- **Root Cause:** SQL executes correctly but LLM response ignores results

### 5. "What about his assists?"
- **Score:** 0.510
- **SQL Accuracy:** 0.75
- **Issue:** Conversational context lost - "I need more context"
- **Root Cause:** System architecture lacks conversation memory/state

---

## Key Patterns in Failures

### 1. **LLM Result Extraction Failure (Critical)**
- **Frequency:** 32% of failures
- **Impact:** High - SQL works but system appears broken to users
- **Pattern:** Occurs with COUNT, AVG, percentage calculations
- **Recommendation:**
  - Revise prompt template to explicitly instruct LLM to use SQL results
  - Add result formatting instructions
  - Implement fallback to return raw SQL results if LLM fails

### 2. **Complex Query Handling**
- **Frequency:** Aggregation queries (24% of failures)
- **Impact:** Medium - answers incomplete or incorrect
- **Pattern:** Multi-condition queries, calculated fields, subqueries
- **Recommendation:**
  - Break down complex queries into simpler components
  - Improve SQL generation for nested conditions
  - Add query decomposition logic

### 3. **Conversational Context Loss**
- **Frequency:** 24% of failures
- **Impact:** High - breaks natural conversation flow
- **Pattern:** Follow-up questions with pronouns ("his", "them", "who")
- **Recommendation:**
  - Implement conversation state management
  - Track previously mentioned entities
  - Add context window to prompts

### 4. **Ground Truth Mismatch**
- **Frequency:** 52% of failures
- **Impact:** Low - may be evaluation issue rather than system issue
- **Pattern:** Correct information but different format/completeness
- **Recommendation:**
  - Review ground truth expectations
  - Use semantic similarity for answer comparison
  - Consider LLM-as-judge evaluation instead of keyword matching

---

## Recommendations

### Immediate Actions (Critical)

1. **Fix LLM Result Extraction**
   - Priority: CRITICAL
   - Revise prompt template to force LLM to use SQL results
   - Add explicit instructions: "Based on the SQL results: [results], answer: ..."
   - Test with COUNT/AVG queries that currently fail

2. **Implement Conversation Memory**
   - Priority: HIGH
   - Add session-based state management
   - Track last mentioned player/team
   - Resolve pronouns before query generation

3. **Improve Query Classification**
   - Priority: MEDIUM
   - Ensure PIE, TS%, advanced metrics trigger SQL queries
   - Add more keyword patterns for statistical queries
   - Log misclassifications for training

### Medium-Term Improvements

4. **Enhanced Error Handling**
   - Add SQL fallback responses (show raw results if LLM fails)
   - Implement retry logic with different prompts
   - Better error messages to users

5. **Ground Truth Review**
   - Review test cases with "answer quality" failures
   - Use semantic similarity instead of keyword matching
   - Consider RAGAS metrics for answer evaluation

6. **Hybrid Query Testing**
   - Convert hybrid test cases to `SQLEvaluationTestCase` format
   - Test SQL + Vector integration scenarios
   - Evaluate component blending quality

---

## System Performance by Query Category

### Simple SQL Queries (17 cases)
- **Average Score:** 0.854
- **Success Rate:** 94.1%
- **Issues:** Minimal - mostly high-performing

### Comparison Queries (14 cases)
- **Average Score:** 0.835
- **Success Rate:** 92.9%
- **Issues:** Very few failures

### Aggregation Queries (17 cases)
- **Average Score:** 0.745
- **Success Rate:** 52.9%
- **Issues:** LLM result extraction, percentage calculations

### Complex Queries (12 cases)
- **Average Score:** 0.625
- **Success Rate:** 41.7%
- **Issues:** Multi-condition queries, calculated fields, subqueries

### Conversational Queries (8 cases)
- **Average Score:** 0.684
- **Success Rate:** 50.0%
- **Issues:** Context loss, pronoun resolution

---

## Conclusion

The SQL query generation component demonstrates strong performance with 51.5% perfect SQL accuracy and 86.4% average accuracy. However, the system's overall effectiveness is significantly hampered by:

1. **Critical Issue:** LLM failing to extract and use SQL results in 32% of failures
2. **Major Issue:** Lack of conversation memory affecting follow-up queries
3. **Moderate Issue:** Complex query handling needs improvement

**Overall Assessment:** The SQL component is robust, but prompt engineering and system architecture improvements are needed to achieve production-ready reliability. Addressing the LLM result extraction issue alone could improve success rate from 63.2% to approximately 75-80%.

**Next Steps:**
1. Fix prompt template for result extraction
2. Implement conversation state management
3. Run full hybrid evaluation after fixing test case format compatibility
4. Consider switching to more structured output format (JSON) for SQL results

---

## Appendix: Test Coverage

### Query Types Tested
- ✅ Simple single-table queries
- ✅ Player stat lookups
- ✅ Top-N rankings
- ✅ Player comparisons
- ✅ League-wide aggregations
- ✅ Complex multi-condition queries
- ✅ Calculated fields (PPG, defensive actions)
- ✅ Conversational follow-ups
- ❌ Hybrid (SQL + Vector) queries - not tested
- ❌ Team-level queries - limited coverage
- ❌ Time-based comparisons - not available in data

### SQL Operations Tested
- ✅ SELECT with WHERE
- ✅ JOIN operations
- ✅ ORDER BY + LIMIT
- ✅ Aggregations (COUNT, AVG, SUM, MAX, MIN)
- ✅ LIKE pattern matching
- ✅ IN clauses
- ✅ Calculated fields (CAST, ROUND)
- ✅ Multiple conditions (AND, OR)
- ⚠️ Subqueries (minimal)
- ❌ GROUP BY (not tested)
- ❌ HAVING clauses (not tested)

---

**Report Generated:** 2026-02-09
**Evaluation Duration:** ~2 minutes (no rate limiting)
**Results File:** `evaluation_results/sql_hybrid_evaluation.json`
