# Evaluation System Guide

**Last Updated**: 2026-02-12
**Version**: 2.0

---

## Overview

The evaluation system tests the Hybrid RAG pipeline through three evaluation runners located in `src/evaluation/runners/`:

- **SQL Evaluation**: 48 test cases for statistical queries
- **Vector Evaluation**: 74 test cases for semantic search (RAGAS metrics)
- **Hybrid Evaluation**: 16 test cases for combined SQL + Vector queries

---

## Directory Structure

```
src/evaluation/
├── models.py                          # Shared evaluation models
├── sql_evaluation.py                  # SQL-specific models/enums
├── runners/                           # Evaluation runners
│   ├── run_sql_evaluation.py         # SQL evaluation (48 tests)
│   ├── run_vector_evaluation.py      # Vector evaluation (74 tests)
│   ├── run_hybrid_evaluation.py      # Hybrid evaluation (16 tests)
│   └── evaluate_ragas.py             # RAGAS metrics calculator
├── analysis/                          # Quality analysis modules
│   ├── sql_quality_analysis.py       # 6 SQL analysis functions
│   ├── vector_quality_analysis.py    # 5 vector analysis functions
│   └── hybrid_quality_analysis.py    # Hybrid analysis functions
├── test_cases/                        # Test case definitions
│   ├── sql_test_cases.py             # SQL_TEST_CASES (48) + HYBRID_TEST_CASES (16)
│   └── vector_test_cases.py          # EVALUATION_TEST_CASES (74)
└── verification/                      # Ground truth verification
    ├── verify_all_sql_ground_truth.py
    └── verify_all_hybrid_ground_truth.py
```

---

## Running Evaluations

### SQL Evaluation

**Script**: `src/evaluation/runners/run_sql_evaluation.py`

**Command**:
```bash
poetry run python -m src.evaluation.runners.run_sql_evaluation
```

**Test Cases**: 48 test cases from `sql_test_cases.py`

**What it tests**:
- SQL query generation from natural language
- Query execution against NBA database (569 players, 48 stat columns)
- Response accuracy vs ground truth
- Classification accuracy (statistical vs contextual)

**Output Files**:
- `evaluation_results/sql_evaluation_YYYYMMDD_HHMMSS.json` - Raw results
- `evaluation_results/sql_evaluation_report_YYYYMMDD_HHMMSS.md` - Analysis report

**Metrics**:
- Execution Success Rate: Query executes without errors
- Classification Accuracy: Correctly identified as SQL query
- Response Quality: Answer matches ground truth
- SQL Correctness: Generated SQL is valid and appropriate

**Current Performance**:
- ✅ Execution: 100% (48/48)
- ✅ Classification: 97.9% (47/48)

---

### Vector Evaluation

**Script**: `src/evaluation/runners/run_vector_evaluation.py`

**Command**:
```bash
poetry run python -m src.evaluation.runners.run_vector_evaluation
```

**Options**:
```bash
# Standard run (all 74 test cases)
poetry run python -m src.evaluation.runners.run_vector_evaluation

# Resume from checkpoint (if interrupted)
poetry run python -m src.evaluation.runners.run_vector_evaluation

# Start fresh (ignore checkpoint)
poetry run python -m src.evaluation.runners.run_vector_evaluation --no-resume

# Vector-only test cases (NOISY + CONVERSATIONAL + contextual COMPLEX)
poetry run python -m src.evaluation.runners.run_vector_evaluation --vector-only
```

**Test Cases**: 74 test cases from `vector_test_cases.py`

**Categories**:
- SIMPLE (15): Direct information retrieval
- COMPLEX (14): Multi-step reasoning
- NOISY (8): Ambiguous queries requiring interpretation
- CONVERSATIONAL (10): Follow-up questions with context

**Features**:
- Auto-checkpointing (saves after each query)
- Conversation ID management for multi-turn queries
- Routing verification (tracks misclassifications)
- Resume capability on interruption

**RAGAS Metrics**:
- **Faithfulness** (0-1): Answer grounded in retrieved context
- **Answer Relevancy** (0-1): Response alignment with query
- **Context Precision** (0-1): Retrieval accuracy
- **Context Recall** (0-1): Context completeness

**Target Scores**:
- Faithfulness: ≥0.82
- Answer Relevancy: ≥0.93
- Context Precision: ≥0.95
- Context Recall: ≥0.84

**Output Files**:
- `evaluation_results/vector_evaluation_YYYYMMDD_HHMMSS.json` - Raw results with RAGAS scores
- `evaluation_results/vector_evaluation_report_YYYYMMDD_HHMMSS.md` - Comprehensive analysis

---

### Hybrid Evaluation

**Script**: `src/evaluation/runners/run_hybrid_evaluation.py`

**Command**:
```bash
poetry run python -m src.evaluation.runners.run_hybrid_evaluation
```

**Test Cases**: 16 test cases from `sql_test_cases.py` (HYBRID_TEST_CASES)

**What it tests**:
- Intelligent query routing (SQL vs Vector vs Hybrid)
- Combined SQL + Vector search performance
- Fallback behavior (SQL → Vector on failure)
- Context blending (statistical data + semantic context)

**Example Queries**:
- "Who are the top 5 scorers and why are they effective?"
- "Compare Jokić and Embiid - who's better and why?"
- "Which players average over 25 points and what's their playing style?"

**Output Files**:
- `evaluation_results/hybrid_evaluation_YYYYMMDD_HHMMSS.json` - Results
- Generated markdown report with analysis

---

## Test Cases

### SQL Test Cases

**File**: `src/evaluation/test_cases/sql_test_cases.py`

**Exports**:
- `SQL_TEST_CASES`: 48 statistical query test cases
- `HYBRID_TEST_CASES`: 16 hybrid query test cases

**SQL Test Case Structure**:
```python
{
    "query": "Who scored the most points this season?",
    "expected_query_type": "sql_only",
    "ground_truth_sql": "SELECT p.name, ps.pts FROM...",
    "ground_truth_data": [...],  # Expected data from database
    "ground_truth_answer": "Shai Gilgeous-Alexander with 2,485 points."
}
```

**Categories**:
- Simple SQL: Direct queries ("Who scored the most points?")
- Comparison SQL: Player comparisons ("Compare Jokić and Embiid")
- Aggregation SQL: Statistical calculations ("What is the average PPG?")
- Complex SQL: Multi-condition queries
- Conversational SQL: Follow-up questions with pronoun resolution

### Vector Test Cases

**File**: `src/evaluation/test_cases/vector_test_cases.py`

**Export**: `EVALUATION_TEST_CASES` (74 test cases)

**Test Case Structure**:
```python
{
    "query": "Why is Nikola Jokić valuable to his team?",
    "category": "COMPLEX",
    "ground_truth_contexts": ["Relevant document excerpts..."],
    "ground_truth_answer": "Expected answer with reasoning..."
}
```

**Distribution**:
- SIMPLE: 15 cases
- COMPLEX: 14 cases
- NOISY: 8 cases
- CONVERSATIONAL: 10 cases
- STATISTICAL: Filtered out (use SQL evaluation)

---

## Quality Analysis Modules

### SQL Quality Analysis

**Module**: `src/evaluation/analysis/sql_quality_analysis.py`

**Functions**:
1. `analyze_execution_summary()` - Success rates, timing stats
2. `analyze_classification_accuracy()` - Routing decision analysis
3. `analyze_response_quality()` - Answer accuracy vs ground truth
4. `analyze_query_structure()` - SQL structure (JOINs, subqueries)
5. `analyze_query_complexity()` - Complexity distribution
6. `analyze_column_selection()` - Column usage patterns

**Usage**: Automatically called by `run_sql_evaluation.py`

### Vector Quality Analysis

**Module**: `src/evaluation/analysis/vector_quality_analysis.py`

**Functions**:
1. `analyze_ragas_metrics()` - RAGAS scores by category
2. `analyze_source_quality()` - Retrieval statistics
3. `analyze_response_patterns()` - Length, completeness, citations
4. `analyze_retrieval_performance()` - Search effectiveness
5. `analyze_category_performance()` - Per-category breakdown

**Usage**: Automatically called by `run_vector_evaluation.py`

### Hybrid Quality Analysis

**Module**: `src/evaluation/analysis/hybrid_quality_analysis.py`

**Functions**:
- `analyze_hybrid_results()` - Combined SQL + Vector performance
- `generate_markdown_report()` - Comprehensive report generation

**Usage**: Automatically called by `run_hybrid_evaluation.py`

---

## Ground Truth Verification

### SQL Ground Truth Verification

**Script**: `src/evaluation/verification/verify_all_sql_ground_truth.py`

**Purpose**: Verify SQL ground truth data matches actual database

**Command**:
```bash
poetry run python -m src.evaluation.verification.verify_all_sql_ground_truth
```

**Checks**:
1. SQL query executes successfully
2. Returned data matches `ground_truth_data`
3. Data types and format are correct

### Hybrid Ground Truth Verification

**Script**: `src/evaluation/verification/verify_all_hybrid_ground_truth.py`

**Purpose**: Verify hybrid test cases have accurate ground truth

**Command**:
```bash
poetry run python -m src.evaluation.verification.verify_all_hybrid_ground_truth
```

**Checks**:
1. SQL component is valid and executes
2. Ground truth data is accurate
3. Ground truth answer appropriately combines SQL + context

---

## Evaluation Workflow

### Standard Workflow

```
1. Run Evaluation
   ↓
2. Review Output (JSON + Report)
   ↓
3. Identify Low-Scoring Cases
   ↓
4. Verify Ground Truth (if needed)
   ↓
5. Fix Issues (classifier, prompts, or test cases)
   ↓
6. Re-run Evaluation
```

### Best Practices

**Before Running**:
- ✅ Ensure dependencies installed: `poetry install`
- ✅ Verify API keys in `.env` (GEMINI_API_KEY, MISTRAL_API_KEY)
- ✅ Check NBA database exists: `data/sql/nba_stats.db`
- ✅ Check vector index exists: `data/vector/faiss_index.pkl`

**During Evaluation**:
- ⏱️ Expect 9-15 second delays between queries (rate limit protection)
- 🔄 Vector evaluation auto-checkpoints - safe to interrupt
- 📊 SQL evaluation: ~12-15 minutes (48 tests × 15s delay)
- 📊 Vector evaluation: ~20-30 minutes (74 tests × 15s delay)

**After Evaluation**:
- 📄 Review markdown report for insights
- 📊 Check JSON for raw data and detailed metrics
- 🔍 Investigate low-scoring queries
- ✅ Verify ground truth if scores are unexpectedly low

---

## Troubleshooting

### Rate Limit Errors (429)

**Symptom**: "RESOURCE_EXHAUSTED" or "Rate limit exceeded"

**Solution**:
- Gemini free tier: 15 requests per minute
- Evaluation scripts include automatic retry (15s + 30s backoff)
- Wait 5-10 minutes if retries exhausted
- Consider upgrading to paid tier ($0.001/request, 360 RPM)

### Checkpoint Recovery (Vector Evaluation)

**Symptom**: Evaluation interrupted mid-run

**Solution**:
```bash
# Resume from last checkpoint (default behavior)
poetry run python -m src.evaluation.runners.run_vector_evaluation

# Start fresh if checkpoint corrupted
poetry run python -m src.evaluation.runners.run_vector_evaluation --no-resume
```

**Checkpoint Location**: `evaluation_checkpoint.json` in project root

### Import Errors

**Symptom**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```bash
# Always use poetry environment
poetry shell

# Or prefix commands
poetry run python -m src.evaluation.runners.run_sql_evaluation
```

### Low RAGAS Scores

**Potential Causes**:
1. **Ground truth inaccurate** → Run verification scripts
2. **Context not retrieved** → Check vector index quality
3. **LLM not following context** → Review prompts
4. **Query misclassified** → Check classifier patterns

**Investigation Steps**:
```bash
# 1. Verify ground truth
poetry run python -m src.evaluation.verification.verify_all_sql_ground_truth

# 2. Check low-scoring queries in report
cat evaluation_results/vector_evaluation_report_*.md | grep -A 5 "Low-Scoring"

# 3. Test specific query manually via API or UI
```

---

## Output Format

### JSON Output Structure

```json
{
  "metadata": {
    "timestamp": "2026-02-12T00:15:30Z",
    "total_cases": 48,
    "script": "run_sql_evaluation",
    "version": "2.0"
  },
  "results": [
    {
      "query": "Who scored the most points?",
      "expected_type": "sql_only",
      "actual_type": "sql_only",
      "execution_success": true,
      "response": "Shai Gilgeous-Alexander with 2,485 points.",
      "processing_time_ms": 1250,
      "generated_sql": "SELECT p.name, ps.pts FROM players p..."
    }
  ],
  "summary": {
    "execution_success_rate": 1.0,
    "classification_accuracy": 0.979,
    "avg_processing_time_ms": 1150
  }
}
```

### Markdown Report Sections

**SQL Report**:
1. Execution Summary (success rates, timing)
2. Classification Accuracy (routing analysis)
3. Response Quality (accuracy metrics)
4. Query Quality (SQL structure, complexity)
5. Error Analysis (if failures occurred)
6. Recommendations

**Vector Report**:
1. RAGAS Metrics Summary (overall + by category)
2. Performance by Category (SIMPLE, COMPLEX, NOISY, CONVERSATIONAL)
3. Low-Scoring Queries (< target threshold)
4. Source Quality Analysis (retrieval stats)
5. Routing Verification (misclassifications)
6. Recommendations

---

## Metrics Reference

### SQL Metrics

| Metric | Range | Target | Description |
|--------|-------|--------|-------------|
| Execution Success | 0-100% | 100% | Queries execute without errors |
| Classification Accuracy | 0-100% | ≥95% | Correctly routed to SQL |
| Response Quality | 0-100% | ≥90% | Answers match ground truth |
| SQL Correctness | 0-100% | 100% | Valid syntax and logic |

### Vector Metrics (RAGAS)

| Metric | Range | Target | Description |
|--------|-------|--------|-------------|
| Faithfulness | 0-1 | ≥0.82 | Answer grounded in context |
| Answer Relevancy | 0-1 | ≥0.93 | Response aligns with query |
| Context Precision | 0-1 | ≥0.95 | Relevant chunks retrieved |
| Context Recall | 0-1 | ≥0.84 | All relevant info retrieved |

### Hybrid Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Routing Accuracy | Correct SQL/Vector/Hybrid decision | ≥95% |
| Fallback Success | Graceful SQL → Vector fallback | 100% |
| Context Blending Quality | SQL + Vector integration | Qualitative |

---

**Maintainer**: Shahu
**Version**: 2.0
**Last Updated**: 2026-02-12
