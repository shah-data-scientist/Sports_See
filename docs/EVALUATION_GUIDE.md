# Evaluation System Guide

**Date**: 2026-02-10
**Status**: ✅ Consolidated to 3 Master Scripts

---

## Overview

The evaluation system has been consolidated from 10+ scattered scripts into **3 master evaluation scripts** that test different search capabilities.

---

## The 3 Master Evaluation Scripts

### 1. **evaluate_sql.py** - SQL Query Evaluation

**Purpose**: Tests SQL query generation and execution ONLY

**What it does**:
- Generates SQL queries from natural language
- Executes queries against NBA database
- Validates query correctness and results

**Configuration**:
```python
ChatService(enable_sql=True)  # SQL enabled
# No vector search used - direct SQL execution
```

**Test Cases Used**:
- `SQL_TEST_CASES` from `sql_test_cases.py`
- Includes: SIMPLE_SQL, COMPARISON_SQL, AGGREGATION_SQL, COMPLEX_SQL, CONVERSATIONAL_SQL
- **Total**: ~90 SQL test cases

**Example Queries**:
```
✓ "Who scored the most points this season?"
✓ "What is LeBron James' average points per game?"
✓ "Compare Jokic and Giannis scoring"
✓ "Show me the top scorer" → "What about his assists?" (conversational)
```

**Key Difference**: **ONLY SQL** - No vector search fallback

---

### 2. **evaluate_vector.py** - Vector Search Evaluation

**Purpose**: Tests FAISS vector search with Mistral embeddings ONLY

**What it does**:
- Performs semantic search on documents/discussions
- Retrieves contextual information
- Generates answers from retrieved context

**Configuration**:
```python
ChatService(enable_sql=False)  # SQL DISABLED
# Only vector search (FAISS + Mistral embeddings)
```

**Test Cases Used**:
- Selected from `EVALUATION_TEST_CASES` in `test_cases.py`
- Categories: NOISY, CONVERSATIONAL, contextual COMPLEX
- **Total**: ~30-40 vector-suitable test cases

**Example Queries**:
```
✓ "Why is Nikola Jokic valuable to his team?"
✓ "What makes LeBron's playing style effective?"
✓ "Discuss the impact of three-point shooting on modern NBA"
✓ "Who is valuable?" → "What about his impact?" (conversational)
```

**Selection Criteria**:
```python
# Includes queries with contextual keywords:
["why", "explain", "analysis", "discuss", "opinion",
 "strategy", "style", "valuable", "effective", "impact"]
```

**Key Difference**: **ONLY Vector Search** - SQL completely disabled

---

### 3. **evaluate_hybrid.py** - Hybrid (SQL + Vector) Evaluation

**Purpose**: Tests intelligent routing between SQL and Vector search

**What it does**:
- Classifies queries as SQL or Vector
- Routes to appropriate search method
- Falls back to vector if SQL fails
- Combines both for complex queries

**Configuration**:
```python
ChatService(enable_sql=True)  # SQL enabled
# With QueryClassifier for intelligent routing
# Vector search as fallback
```

**Test Cases Used**:
- `HYBRID_TEST_CASES` from `hybrid_test_cases.py`
- SIMPLE, COMPLEX, CONVERSATIONAL from `EVALUATION_TEST_CASES`
- **Total**: ~80-100 hybrid test cases

**Example Queries**:
```
✓ "Compare Jokic and Embiid stats and explain why Jokic is more valuable"
   → Uses SQL for stats + Vector for explanation

✓ "Who are the most efficient scorers and why?"
   → Uses SQL for TS% leaders + Vector for "why effective"

✓ "Which teams have best offensive rating and what strategies?"
   → Uses SQL for ratings + Vector for strategies
```

**Routing Logic**:
- **SQL**: Statistical queries (stats, numbers, comparisons)
- **Vector**: Contextual queries (why, how, analysis)
- **Both**: Complex queries requiring stats + context

**Key Difference**: **Smart Routing** - Automatically chooses SQL or Vector or Both

---

## Critical Differences Summary

| Aspect | SQL-Only | Vector-Only | Hybrid |
|--------|----------|-------------|--------|
| **ChatService Config** | `enable_sql=True` | `enable_sql=False` | `enable_sql=True` |
| **Search Method** | Direct SQL execution | FAISS vector search | SQL → Vector routing |
| **SQL Queries** | ✅ Yes | ❌ No | ✅ Yes (routed) |
| **Vector Search** | ❌ No | ✅ Yes | ✅ Yes (fallback/hybrid) |
| **Query Classifier** | ❌ Not used | ❌ Not used | ✅ Used for routing |
| **Fallback** | None | None | SQL fails → Vector |
| **Test Cases** | SQL_TEST_CASES (90) | Selected NOISY/CONV (40) | HYBRID + SIMPLE + COMPLEX (100) |
| **Example Query** | "Who scored most?" | "Why is Jokic valuable?" | "Compare stats and explain" |
| **Output** | SQL query + results | Vector sources + answer | Routing decision + results |

---

## Test Case Distribution

### Total Test Cases: ~230 across all scripts

| Test Set | SQL | Vector | Hybrid | Description |
|----------|-----|--------|--------|-------------|
| **SIMPLE** | ❌ | ❌ | ✅ | Direct statistical queries → SQL routing |
| **COMPLEX** | ❌ | ✅ (contextual) | ✅ | Multi-step queries → Both or Vector |
| **NOISY** | ❌ | ✅ | ❌ | Opinion/contextual → Vector only |
| **CONVERSATIONAL** | ✅ (SQL type) | ✅ (Vector type) | ✅ (Both types) | Follow-up questions |
| **SQL_TEST_CASES** | ✅ | ❌ | ❌ | Dedicated SQL queries |
| **HYBRID_TEST_CASES** | ❌ | ❌ | ✅ | Dedicated hybrid queries |

---

## Conversation Support

**ALL 3 scripts support conversation-aware queries!**

### How It Works:
```python
# Detects follow-up questions
if _is_followup_question(test_case.question):
    current_turn_number += 1  # Continue conversation
else:
    start_new_conversation()  # New thread

# Passes conversation context
request = ChatRequest(
    query=test_case.question,
    conversation_id=current_conversation_id,  # ✅ Context maintained
    turn_number=current_turn_number
)
```

### Conversational Test Cases Included:
- **SQL**: 8 conversational SQL cases (e.g., "Show top scorer" → "What about his assists?")
- **Vector**: 12 conversational RAGAS cases (contextual follow-ups)
- **Hybrid**: 9 conversational hybrid cases + all from main set

---

## Running the Evaluations

### 1. SQL-Only Evaluation
```bash
poetry run python scripts/evaluate_sql.py
```

**Output**:
```
==================================================
  SQL-ONLY EVALUATION
  Tests: SQL query generation, execution, accuracy
  Mode: SQL ONLY (no vector search)
  Test Cases: 90 total
==================================================

[1/90] simple_sql_top_n: Who scored the most points...
  [PASS] SQL: Y | Time: 1200ms

[2/90] conversational_followup: What about his assists?
  [PASS] SQL: Y | Time: 1100ms (conversation context)

...

Results saved to: evaluation_results/sql_evaluation_20260210_150000.json
```

### 2. Vector-Only Evaluation
```bash
poetry run python scripts/evaluate_vector.py
```

**Output**:
```
==================================================
  VECTOR-ONLY EVALUATION
  Tests: FAISS vector search + Mistral embeddings
  Mode: VECTOR ONLY (SQL disabled)
  Test Cases: 38 selected from EVALUATION_TEST_CASES
==================================================

[1/38] noisy: Why is three-point shooting important...
  [PASS] Sources: 5 | Context: Y | Time: 1500ms

[2/38] conversational: What about his impact?
  [PASS] Sources: 4 | Context: Y | Time: 1300ms (conversation context)

...

Results saved to: evaluation_results/vector_evaluation_20260210_150100.json
```

### 3. Hybrid Evaluation
```bash
poetry run python scripts/evaluate_hybrid.py
```

**Output**:
```
==================================================
  HYBRID EVALUATION (SQL + VECTOR)
  Tests: Intelligent routing between SQL and Vector
  Mode: HYBRID (SQL enabled with Vector fallback)
  Test Cases: 95 from multiple sources
==================================================

[1/95] simple: Who scored the most points...
  [PASS] Routing: SQL | Sources: 0 | Time: 1100ms

[2/95] complex: Compare Jokic stats and explain why valuable...
  [PASS] Routing: BOTH | Sources: 5 | Time: 2200ms

[3/95] noisy: Discuss modern NBA offensive strategies...
  [PASS] Routing: VECTOR | Sources: 6 | Time: 1800ms

...

Routing Statistics:
  SQL only: 35
  Vector only: 28
  Both (Hybrid): 25
  Unknown: 7

Results saved to: evaluation_results/hybrid_evaluation_20260210_150200.json
```

---

## Understanding the Differences

### Why 3 Separate Scripts?

**1. SQL-Only** isolates SQL performance
   - Pure SQL generation testing
   - No vector "contamination"
   - Measures SQL accuracy independently

**2. Vector-Only** isolates retrieval quality
   - Pure semantic search testing
   - No SQL dependency
   - Measures retrieval and context quality

**3. Hybrid** tests real-world usage
   - Tests routing intelligence
   - Tests fallback mechanisms
   - Measures end-to-end system performance

### Are They Really Different?

**YES!** Here's proof:

```python
# evaluate_sql.py
chat_service = ChatService(enable_sql=True)
# Direct SQL execution, no vector search

# evaluate_vector.py
chat_service = ChatService(enable_sql=False)  # ← KEY DIFFERENCE
# Only vector search, SQL completely disabled

# evaluate_hybrid.py
chat_service = ChatService(enable_sql=True)
# Uses QueryClassifier for intelligent routing ← KEY DIFFERENCE
```

---

## Output Structure

All 3 scripts produce JSON results with:

```json
{
  "timestamp": "2026-02-10T15:00:00",
  "total_cases": 90,
  "successful": 88,
  "failed": 2,
  "category_counts": {
    "simple_sql_top_n": 17,
    "conversational_followup": 8,
    ...
  },
  "routing_stats": {  // Only in hybrid
    "sql": 35,
    "vector": 28,
    "both": 25
  },
  "results": [
    {
      "question": "Who scored the most points?",
      "category": "simple_sql_top_n",
      "response": "Shai Gilgeous-Alexander with 2,485 points",
      "sql_used": true,  // SQL-only
      "sources_count": 5,  // Vector-only
      "routing": "sql",  // Hybrid-only
      "processing_time_ms": 1200,
      "success": true
    }
  ]
}
```

---

## Migration from Old Scripts

### Old Scripts → Archive
All phase scripts will be archived:
- ~~evaluate_phase2.py~~ → Archived
- ~~evaluate_phase4.py~~ → Archived
- ~~evaluate_phase5/6/7/8/9/10.py~~ → Archived
- ~~evaluate_sql_hybrid.py~~ → Replaced by evaluate_hybrid.py
- ~~evaluate_vector_only_full.py~~ → Replaced by evaluate_vector.py
- ~~evaluate_conversation_aware.py~~ → Functionality integrated into all 3

### New Structure
```
scripts/
├── evaluate_sql.py       # Master SQL-only evaluation
├── evaluate_vector.py    # Master Vector-only evaluation
├── evaluate_hybrid.py    # Master Hybrid evaluation
└── _archived/
    └── 2026-02/
        ├── evaluate_phase*.py
        └── ...
```

---

## Summary

✅ **3 Master Scripts** - SQL, Vector, Hybrid
✅ **Clear Distinctions** - Different search methods, different test cases
✅ **Full Coverage** - 230+ test cases across all types
✅ **Conversation Support** - All 3 scripts support multi-turn queries
✅ **Comprehensive Reporting** - JSON outputs with detailed metrics

**The scripts are NOT the same** - each tests a different aspect of the RAG system!
