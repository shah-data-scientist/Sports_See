# Hybrid Evaluation Report

**Generated:** 2026-02-12T07:06:28.477174
**Dataset:** 50 hybrid test cases
**Results JSON:** `hybrid_evaluation_20260212_070628.json`

---

## Executive Summary

- **Total Queries:** 50
- **Successful Executions:** 44 (88.0%)
- **Failed Executions:** 6
- **Response Quality:** 100.0% have meaningful responses
- **Source Retrieval:** 86.4% retrieved sources
- **Avg Processing Time:** 11269.0ms

### Routing Summary

- **SQL Only:** 6
- **Vector Only:** 18
- **Both (Hybrid):** 20
- **Unknown:** 0

## RAGAS Metrics (Vector Component Quality)

### Overall Vector Quality Scores

These metrics measure the quality of vector-based retrieval and response generation:

| Metric | Average | Min | Max | Std Dev |
|--------|---------|-----|-----|----------|
| Faithfulness | 0.5958 | 0.0000 | 1.0000 | 0.3907 |
| Answer Relevancy | 0.5215 | 0.0000 | 0.9765 | 0.4091 |
| Context Precision | 0.4337 | 0.0000 | 1.0000 | 0.4494 |
| Context Recall | 0.4401 | 0.0000 | 1.0000 | 0.4291 |

**Evaluated:** 71 vector-based queries

### Vector Scores by Category

| Category | Queries | Faithfulness | Answer Relevancy | Context Precision | Context Recall |
|----------|---------|--------------|------------------|-------------------|----------------|
| complex | 15 | 0.4866 | 0.8344 | 0.6922 | 0.4649 |
| conversational | 12 | 0.6948 | 0.623 | 0.5167 | 0.3135 |
| noisy | 24 | 0.5612 | 0.2202 | 0.2653 | 0.6464 |
| simple | 20 | 0.6599 | 0.5875 | 0.3923 | 0.25 |

## SQL Component Analysis

- **Queries with SQL:** 26
- **SQL Generated:** 26 (100.0%)

### Query Structure

- **Total SQL Queries Generated:** 26
- **Queries with JOIN:** 23 (88.5%)
- **Queries with Aggregation:** 1 (3.8%)
- **Queries with Filter (WHERE):** 19 (73.1%)
- **Queries with ORDER BY:** 10 (38.5%)
- **Queries with LIMIT:** 11 (42.3%)

## Vector Component Analysis

- **Average Sources per Query:** 5.0
- **Total Unique Sources:** 4
- **Retrieval Success Rate:** 100.0%

## Hybrid Combination Quality

- **True Hybrid Queries:** 20 (both SQL + Vector)
- **Both Data Types Present:** 20 (100.0%)
- **Avg Response Length:** 888 chars
- **Response Length Range:** 459 - 2341 chars

## Key Findings

- **Excellent execution reliability** (88.0% success rate)
- **Strong hybrid routing** (20/50 queries use both SQL + Vector)
- **Vector Quality** - Faithfulness: 0.5958, Answer Relevancy: 0.5215
- **SQL Integration** - All 26 queries generated successfully
