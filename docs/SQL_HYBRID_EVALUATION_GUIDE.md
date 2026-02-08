# SQL + Hybrid Query Evaluation Framework

**Document Type:** Technical Guide
**Date:** 2026-02-08
**Purpose:** Comprehensive evaluation framework for SQL, Vector, and Hybrid queries

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Framework Architecture](#framework-architecture)
3. [Evaluation Metrics](#evaluation-metrics)
4. [How Hybrid Evaluation Works](#how-hybrid-evaluation-works)
5. [Usage Guide](#usage-guide)
6. [Test Cases](#test-cases)
7. [Interpreting Results](#interpreting-results)
8. [Limitations & Future Work](#limitations--future-work)

---

## Problem Statement

### The Challenge: Evaluating Hybrid Queries

**Traditional RAGAS evaluation** (Phases 6-9) only covers **vector-only retrieval**:
- ✅ Measures: Faithfulness, Answer Relevancy, Context Precision, Context Recall
- ✅ Works for: Pure contextual queries ("Why is LeBron great?")
- ❌ Cannot evaluate: SQL queries, Hybrid queries (SQL + Vector)

**Example Hybrid Query:**
```
User: "Compare Jokić and Embiid's stats and explain who's better"

System needs:
1. SQL Tool → Fetch Jokić stats (PTS, REB, AST)
2. SQL Tool → Fetch Embiid stats
3. Vector Search → Retrieve context about playstyle, MVP race
4. LLM → Blend SQL + Vector into coherent answer

Question: How do we evaluate this?
```

**Evaluation Challenges:**
1. **SQL Accuracy**: Did the SQL query execute correctly? Are results accurate?
2. **Vector Faithfulness**: Is the contextual analysis grounded in retrieved documents?
3. **Integration Quality**: Are SQL stats and vector context properly blended?
4. **Answer Completeness**: Does the answer address both "what" (stats) and "why" (analysis)?

---

## Framework Architecture

### Multi-Tier Evaluation System

```
┌─────────────────────────────────────────────────────────────┐
│  Tier 1: SQL Accuracy Evaluation                            │
│  - SQL syntax correctness (executed without errors?)        │
│  - SQL semantic correctness (logically correct query?)      │
│  - Result accuracy (matches ground truth?)                  │
│  - Execution success (no failures?)                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 2: Vector Retrieval Evaluation (RAGAS)                │
│  - Faithfulness (grounding to retrieved context)            │
│  - Context precision (retrieved chunks relevant?)           │
│  - Context recall (all necessary info retrieved?)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 3: Hybrid Integration Evaluation (NEW!)               │
│  - SQL component used? (stats present in answer)            │
│  - Vector component used? (contextual analysis present)     │
│  - Components blended? (coherent integration, not concat)   │
│  - Answer complete? (addresses both stats + analysis)       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Tier 4: Overall Quality (End-to-End)                       │
│  - Answer relevancy (addresses the question?)               │
│  - Answer correctness (factually accurate?)                 │
│  - Overall score (weighted combination of all tiers)        │
└─────────────────────────────────────────────────────────────┘
```

---

## Evaluation Metrics

### 1. SQL Accuracy Metrics

**Class:** `SQLAccuracyMetrics`

| Metric | Description | How Measured |
|--------|-------------|--------------|
| `sql_syntax_correct` | SQL query is syntactically valid | Query executed without syntax errors |
| `sql_semantic_correct` | SQL query logically answers the question | ≥60% keyword overlap with expected SQL |
| `results_accurate` | SQL results match ground truth | Values match within 5% tolerance |
| `execution_success` | Query executed without errors | No execution exceptions |

**Overall SQL Accuracy Score:** Average of 4 binary metrics (0-1)

---

### 2. Vector Retrieval Metrics (RAGAS)

**Standard RAGAS metrics** (already implemented in Phases 6-9):

| Metric | Description | Range |
|--------|-------------|-------|
| `vector_faithfulness` | Answer grounded in retrieved context | 0-1 |
| `vector_context_precision` | Retrieved chunks are relevant | 0-1 |
| `vector_context_recall` | All necessary info was retrieved | 0-1 |

---

### 3. Hybrid Integration Metrics (NEW!)

**Class:** `HybridIntegrationMetrics`

| Metric | Description | How Measured |
|--------|-------------|--------------|
| `sql_component_used` | SQL results appear in final answer | Stats/numbers from SQL results found in response |
| `vector_component_used` | Vector context appears in final answer | Phrases from retrieved documents found in response |
| `components_blended` | Both components integrated coherently | Response contains transition words ("because", "while", "however") |
| `answer_complete` | Answer addresses both stats and analysis | Has numbers (SQL) + long-form text (context) |

**Integration Score:** Average of 4 binary metrics (0-1)

---

### 4. Overall Hybrid Evaluation Score

**Weighted combination:**

```python
overall_score = (
    sql_accuracy * 0.4 +        # If SQL was used
    vector_score * 0.4 +         # If vector was used
    integration * 0.2 +          # If hybrid query
    answer_quality * remaining   # Always included
)
```

**Weights adjust dynamically:**
- **SQL-only query**: SQL (60%) + Answer quality (40%)
- **Contextual-only query**: Vector (60%) + Answer quality (40%)
- **Hybrid query**: SQL (40%) + Vector (40%) + Integration (20%)

---

## How Hybrid Evaluation Works

### Step-by-Step Process

#### Example: "Compare Jokić and Embiid's stats and explain who's better"

**Step 1: Query Execution**
```python
chat_service = ChatService(enable_sql=True)
response = chat_service.chat(ChatRequest(query=user_query))

# Behind the scenes:
# 1. QueryClassifier detects HYBRID query
# 2. SQL tool fetches Jokić and Embiid stats
# 3. Vector search retrieves context about playstyle, MVP race
# 4. LLM blends both sources into answer
```

**Step 2: Component Extraction**
```python
sample = HybridEvaluationSample(
    user_input="Compare Jokić and Embiid...",
    query_type=QueryType.HYBRID,

    # SQL component
    sql_result=SQLExecutionResult(
        query_generated="SELECT name, pts, reb, ast FROM player_stats WHERE...",
        query_executed=True,
        results=[
            {"name": "Nikola Jokić", "pts": 2018, "reb": 891, "ast": 688},
            {"name": "Joel Embiid", "pts": 2159, "reb": 813, "ast": 296}
        ]
    ),

    # Vector component
    vector_result=VectorRetrievalResult(
        retrieved_contexts=[
            "Jokić's passing ability makes him unique...",
            "Embiid's scoring prowess is elite..."
        ],
        retrieval_scores=[0.85, 0.78]
    ),

    # Final answer
    response="Jokić: 2018 PTS, 891 REB, 688 AST. Embiid: 2159 PTS, 813 REB, 296 AST. While Embiid edges Jokić in scoring, Jokić's superior playmaking (688 vs 296 assists) makes him more complete..."
)
```

**Step 3: SQL Accuracy Evaluation**
```python
sql_accuracy = evaluate_sql_accuracy(test_case, sql_result)

# Check 1: Syntax correct? ✓ (query executed)
# Check 2: Semantically correct? ✓ (query fetches player stats)
# Check 3: Results accurate? ✓ (Jokić: 2018 PTS matches ground truth)
# Check 4: Execution success? ✓ (no errors)

# SQL Accuracy Score: 1.0 (4/4 checks passed)
```

**Step 4: Hybrid Integration Evaluation**
```python
integration = evaluate_hybrid_integration(test_case, sample)

# Check 1: SQL component used? ✓ ("2018 PTS" appears in response)
# Check 2: Vector component used? ✓ ("playmaking" from context appears)
# Check 3: Components blended? ✓ ("While...makes him" = transition words)
# Check 4: Answer complete? ✓ (has stats + analysis)

# Integration Score: 1.0 (4/4 checks passed)
```

**Step 5: Vector Faithfulness Evaluation**
```python
# Would use RAGAS here in full implementation
vector_faithfulness = 0.85  # Example score
vector_context_precision = 0.78
```

**Step 6: Overall Score Calculation**
```python
overall_score = (
    sql_accuracy.overall_score * 0.4 +    # 1.0 * 0.4 = 0.40
    vector_faithfulness * 0.4 +            # 0.85 * 0.4 = 0.34
    integration.integration_score * 0.2    # 1.0 * 0.2 = 0.20
)
# = 0.94 (Excellent hybrid query handling!)
```

---

## Usage Guide

### Running the Evaluation

```bash
# Navigate to project root
cd "c:\Users\shahu\Documents\OneDrive\OPEN CLASSROOMS\PROJET 10\Sports_See"

# Run SQL + Hybrid evaluation
poetry run python scripts/evaluate_sql_hybrid.py
```

### Interactive Menu

```
Available test sets:
  1. SQL-only queries (7 cases)
  2. Hybrid queries (4 cases)
  3. Contextual-only queries (3 cases)
  4. All queries (14 cases)

Select test set (1-4, default=4): 2
```

### Output Example

```
==============================================================================
  SQL + HYBRID QUERY EVALUATION RESULTS
==============================================================================

HYBRID QUERIES (4 samples)
------------------------------------------------------------------------------
[PASS] Compare Jokić and Embiid's stats and explain who's better | Score: 0.94
       SQL: 1.00 | Syntax: Y | Results: Y
       Integration: 1.00 | SQL used: Y | Vector used: Y | Blended: Y

[PASS] Who has the best 3P% and why are they so effective? | Score: 0.87
       SQL: 0.88 | Syntax: Y | Results: Y
       Integration: 0.75 | SQL used: Y | Vector used: Y | Blended: Y

  Average Score: 0.905

==============================================================================
OVERALL: 4 queries | Average Score: 0.905
==============================================================================

Results saved to: evaluation_results/sql_hybrid_evaluation.json
```

---

## Test Cases

### SQL-Only Test Cases (7 cases)

**Simple SQL:**
- "Who scored the most points this season?"
- "What is LeBron James' average points per game?"
- "How many assists did Chris Paul record?"

**Comparison SQL:**
- "Compare Jokić and Embiid's stats"
- "Who has more rebounds, Giannis or Anthony Davis?"

**Aggregation SQL:**
- "What is the average 3-point percentage for all players?"
- "How many players scored over 1000 points?"

---

### Hybrid Test Cases (4 cases)

**Statistical + Contextual Analysis:**
1. "Compare Jokić and Embiid's stats and explain who's better"
   - SQL: Fetch both players' stats
   - Vector: Retrieve MVP discussion, playstyle analysis
   - Integration: Blend stats with contextual "why"

2. "Who has the best 3-point percentage and why are they so effective?"
   - SQL: Find player with highest 3P%
   - Vector: Retrieve shooting mechanics, shot selection context
   - Integration: Connect stats to effectiveness reasoning

3. "What are LeBron James' stats and how does his playstyle work?"
   - SQL: Fetch LeBron's stats
   - Vector: Retrieve playstyle description, court vision analysis
   - Integration: Stats + playstyle explanation

4. "Show me Giannis' stats and explain why he's a good defender"
   - SQL: Fetch Giannis' defensive stats (BLK, STL)
   - Vector: Retrieve defensive ability context (wingspan, versatility)
   - Integration: Stats + defensive analysis

---

### Contextual-Only Test Cases (3 cases)

**Pure Vector Search (No SQL):**
- "Why is LeBron considered one of the greatest?"
- "What makes Curry's shooting so special?"
- "How has the Warriors' dynasty impacted the NBA?"

---

## Interpreting Results

### Score Interpretation

| Score Range | Interpretation | Meaning |
|-------------|----------------|---------|
| **0.90 - 1.00** | Excellent | Both SQL and vector components working perfectly |
| **0.75 - 0.89** | Good | Minor issues in SQL accuracy or integration |
| **0.60 - 0.74** | Fair | Significant issues in one component |
| **0.00 - 0.59** | Poor | Multiple components failing |

### Common Failure Patterns

#### 1. SQL Syntax Errors (Score: 0.25)
```
[FAIL] Who scored the most points? | Score: 0.25
       SQL: 0.25 | Syntax: N | Results: N

Problem: SQL query generation failed
Solution: Improve few-shot examples in SQL tool
```

#### 2. Missing Integration (Score: 0.60)
```
[PASS] Compare Jokić and Embiid stats and explain who's better | Score: 0.60
       SQL: 1.00 | Syntax: Y | Results: Y
       Integration: 0.25 | SQL used: Y | Vector used: N | Blended: N

Problem: Answer only shows stats, no contextual analysis
Solution: Check if QueryClassifier correctly detects HYBRID queries
```

#### 3. Poor Blending (Score: 0.75)
```
[PASS] Who has best 3P% and why effective? | Score: 0.75
       SQL: 1.00 | Syntax: Y | Results: Y
       Integration: 0.50 | SQL used: Y | Vector used: Y | Blended: N

Problem: Answer concatenates stats and context without integration
Solution: Improve system prompt to encourage coherent blending
```

---

## Limitations & Future Work

### Current Limitations

1. **No Direct SQL Access**:
   - Current implementation uses `ChatService.chat()` which hides SQL internals
   - Cannot access generated SQL query or raw results
   - **Workaround**: Instrument `ChatService` to return SQL metadata in response

2. **Simplified Metrics**:
   - SQL semantic correctness uses keyword overlap (60% threshold)
   - Integration detection uses simple heuristics (transition words)
   - **Future**: Use LLM-as-judge for more nuanced evaluation

3. **No RAGAS Integration Yet**:
   - Vector metrics currently use placeholders
   - **Future**: Integrate RAGAS for full vector evaluation in hybrid context

4. **Binary Metrics**:
   - Most metrics are binary (pass/fail)
   - **Future**: Use continuous scores (0-1) for finer granularity

---

### Future Enhancements

#### 1. Instrumented ChatService

**Add SQL metadata to ChatResponse:**
```python
class ChatResponse(BaseModel):
    answer: str
    sources: list[SearchResult]

    # NEW: SQL metadata
    sql_used: bool = False
    sql_query: str | None = None
    sql_results: list[dict] | None = None
    query_type: QueryType | None = None  # STATISTICAL, CONTEXTUAL, HYBRID
```

**Benefits:**
- Direct access to SQL query and results for evaluation
- Can measure SQL query quality directly
- Can compute result accuracy precisely

---

#### 2. LLM-as-Judge Metrics

**Use LLM to evaluate integration quality:**
```python
def evaluate_integration_with_llm(sample: HybridEvaluationSample) -> float:
    """Use LLM to judge hybrid integration quality."""

    prompt = f"""
    Evaluate how well this answer integrates SQL statistics with contextual analysis.

    Question: {sample.user_input}
    Answer: {sample.response}

    SQL Data: {sample.sql_result.results}
    Context: {sample.vector_result.retrieved_contexts}

    Rate integration quality (0-1):
    - 1.0: Perfect blend, seamless integration
    - 0.5: Both present but poorly connected
    - 0.0: Only one component used

    Score:
    """

    # Use Mistral to score
    score = mistral_client.complete(prompt)
    return float(score)
```

---

#### 3. RAGAS Integration for Hybrid Queries

**Extend RAGAS to handle hybrid context:**
```python
def evaluate_hybrid_with_ragas(sample: HybridEvaluationSample):
    """Evaluate hybrid query with RAGAS."""

    # Combine SQL results + vector context
    combined_context = [
        f"SQL Results: {format_sql_results(sample.sql_result.results)}",
        *sample.vector_result.retrieved_contexts
    ]

    # Standard RAGAS evaluation
    dataset = EvaluationDataset.from_list([{
        "user_input": sample.user_input,
        "response": sample.response,
        "retrieved_contexts": combined_context,
        "reference": sample.reference
    }])

    result = evaluate(dataset, metrics=[
        Faithfulness(),
        AnswerRelevancy(),
        ContextPrecision(),
        ContextRecall()
    ])

    return result
```

---

#### 4. Category-Specific Hybrid Evaluation

**Extend to SIMPLE/COMPLEX/NOISY/CONVERSATIONAL:**
```python
hybrid_test_cases_by_category = {
    "SIMPLE_HYBRID": [
        "What are LeBron's stats?",  # SQL + brief context
    ],
    "COMPLEX_HYBRID": [
        "Compare Jokić and Embiid considering advanced metrics and playstyle",
    ],
    "CONVERSATIONAL_HYBRID": [
        "Who's better, Jokić or Embiid? Show me the numbers and explain",
    ]
}
```

---

## Summary

### Key Achievements

✅ **Multi-tier evaluation framework** for SQL, Vector, and Hybrid queries
✅ **14 test cases** covering all query types
✅ **Hybrid integration metrics** to measure SQL + Vector blending
✅ **Automated evaluation script** with interactive menu
✅ **Detailed reporting** with pass/fail indicators

### What This Framework Enables

1. **Measure SQL accuracy** independently of vector retrieval
2. **Evaluate hybrid integration** quality (how well SQL + Vector blend)
3. **Identify failure patterns** (SQL errors, missing components, poor blending)
4. **Track improvements** across iterations (like Phase 6-9 for vector-only)
5. **Validate production** SQL + Hybrid query handling

### Next Steps

1. **Instrument ChatService** to expose SQL metadata
2. **Integrate RAGAS** for full vector evaluation in hybrid context
3. **Add LLM-as-judge** for integration quality scoring
4. **Expand test cases** to cover more query patterns
5. **Run baseline evaluation** to establish SQL + Hybrid performance benchmarks

---

**Maintainer:** Shahu
**Last Updated:** 2026-02-08
**Related Documents:**
- [PHASE_METRICS_COMPARISON.md](PHASE_METRICS_COMPARISON.md) - Vector-only evaluation (Phases 6-9)
- [PROJECT_MEMORY.md](../PROJECT_MEMORY.md) - Full project history
