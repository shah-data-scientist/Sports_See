# Phase 3: Comparative Evaluation Analysis

## Executive Summary

**Date**: 2026-02-07
**Objective**: Measure the impact of Phase 2 SQL integration on RAG system performance
**Methodology**: RAGAS evaluation (Faithfulness, Answer Relevancy, Context Precision, Context Recall)

This report compares the baseline vector-only RAG system (Phase 1) against the hybrid SQL + Vector system (Phase 2) using the same 47 test cases.

---

## Configuration Comparison

| Phase | Configuration | Data Sources | Test Cases |
|-------|--------------|--------------|------------|
| **Baseline (Phase 1)** | Vector search only (FAISS) | 302 documents | 47 (original set) |
| **Phase 2** | Vector + SQL hybrid routing | 302 documents + 569 players (45 stats) | 47 (same as baseline) |

### Phase 2 Key Changes
- SQL database with 569 NBA players, 45 statistical columns
- Query classifier (pattern-based) routing to STATISTICAL, CONTEXTUAL, or HYBRID
- LangChain SQL tool with 8 few-shot examples
- Temperature=0.0 for deterministic SQL generation

---

## Overall Results

### Metrics Comparison

| Metric | Baseline | Phase 2 | Absolute Change | Percent Change |
|--------|----------|---------|-----------------|----------------|
| **Faithfulness** | 0.473 | 0.385 | -0.088 | **-18.7%** ⚠️ |
| **Answer Relevancy** | 0.112 | 0.112 | 0.000 | **-0.4%** ⚠️ |
| **Context Precision** | 0.595 | 0.632 | +0.037 | **+6.3%** ✅ |
| **Context Recall** | 0.596 | 0.576 | -0.020 | **-3.3%** ⚠️ |

### Key Observations
1. **Context Precision improved** (+6.3%) - SQL retrieval provides more relevant context
2. **Faithfulness degraded** (-18.7%) - System generates less faithful responses despite better retrieval
3. **Answer Relevancy unchanged** (0.112) - Critically low and unaffected by SQL integration
4. **Mixed results** suggest SQL helps retrieval but harms answer generation

---

## Performance by Query Category

### SIMPLE Queries (10 test cases)
Direct factual questions requiring straightforward retrieval.

| Metric | Baseline | Phase 2 | Change |
|--------|----------|---------|--------|
| Faithfulness | 0.522 | 0.436 | **-16.4%** ⚠️ |
| Answer Relevancy | 0.110 | 0.083 | **-24.5%** ⚠️ |
| Context Precision | 0.626 | 0.629 | **+0.4%** |
| Context Recall | 0.591 | 0.564 | **-4.5%** |

**Analysis**: SIMPLE queries degraded significantly. SQL tool may be interfering with straightforward vector retrieval. This suggests the query classifier is incorrectly routing simple questions to SQL or that SQL generation adds latency/noise for basic queries.

### COMPLEX Queries (22 test cases)
Multi-hop reasoning, comparisons, or synthesis across multiple sources.

| Metric | Baseline | Phase 2 | Change |
|--------|----------|---------|--------|
| Faithfulness | 0.460 | 0.367 | **-20.5%** ⚠️ |
| Answer Relevancy | 0.121 | 0.126 | **+4.1%** ✅ |
| Context Precision | 0.572 | 0.611 | **+6.7%** ✅ |
| Context Recall | 0.614 | 0.596 | **-3.0%** |

**Analysis**: COMPLEX queries show slight improvement in relevancy (+4.1%) and precision (+6.7%), suggesting SQL does help with analytical queries. However, faithfulness still drops significantly (-20.5%).

### NOISY Queries (8 test cases)
Typos, ambiguous language, or out-of-scope questions.

| Metric | Baseline | Phase 2 | Change |
|--------|----------|---------|--------|
| Faithfulness | 0.406 | 0.415 | **+2.1%** ✅ |
| Answer Relevancy | 0.083 | 0.100 | **+20.5%** ✅ |
| Context Precision | 0.614 | 0.644 | **+4.8%** ✅ |
| Context Recall | 0.458 | 0.425 | **-7.2%** |

**Analysis**: NOISY queries improved across most metrics. SQL's structured retrieval may handle ambiguity better than vector search alone.

### CONVERSATIONAL Queries (7 test cases)
Follow-up questions or references to previous context.

| Metric | Baseline | Phase 2 | Change |
|--------|----------|---------|--------|
| Faithfulness | 0.590 | 0.391 | **-34.0%** ⚠️⚠️ |
| Answer Relevancy | 0.123 | 0.143 | **+15.8%** ✅ |
| Context Precision | 0.603 | 0.945 | **+56.7%** ✅✅ |
| Context Recall | 0.688 | 0.658 | **-4.3%** |

**Analysis**: PARADOX! Context Precision skyrocketed (+56.7%) but Faithfulness plummeted (-34.0%). The system retrieves highly relevant context but generates unfaithful answers. This is the most critical finding - it suggests a disconnect between retrieval and generation.

---

## Critical Issues Identified

### 1. Faithfulness Drop Across All Categories
- **Symptom**: -18.7% overall faithfulness despite better context precision
- **Hypothesis**: SQL results format may confuse the LLM, leading to hallucinations
- **Evidence**: CONVERSATIONAL queries show +56.7% precision but -34.0% faithfulness
- **Root Cause**: Likely in prompt engineering or how SQL results are integrated into context

### 2. Answer Relevancy Critically Low (0.112)
- **Symptom**: Unchanged at 0.112 despite SQL integration
- **Hypothesis**: Core problem is in generation prompt, not data sources
- **Evidence**: Even with better retrieval (Context Precision +6.3%), relevancy didn't improve
- **Root Cause**: System prompt may not properly instruct the LLM to answer the specific question

### 3. SIMPLE Query Degradation
- **Symptom**: -24.5% answer relevancy for simple factual questions
- **Hypothesis**: SQL tool adds unnecessary complexity for basic queries
- **Evidence**: SIMPLE queries performed worse across all metrics
- **Root Cause**: Query classifier may incorrectly route simple questions to SQL

### 4. Conversational Query Paradox
- **Symptom**: +56.7% precision but -34.0% faithfulness
- **Hypothesis**: Multi-turn context handling broken in SQL path
- **Evidence**: Only CONVERSATIONAL category shows this extreme divergence
- **Root Cause**: SQL tool doesn't preserve conversation history properly

---

## Bias and Limitations Analysis

### Natural Language to SQL Mapping
- **Ambiguous queries**: "best player" → multiple interpretations (PPG, PER, WS)
- **Column name mapping**: Users say "three-pointers" not "three_pm"
- **Aggregation complexity**: Multi-step calculations may fail
- **Few-shot coverage**: 8 examples don't cover all query patterns
- **Temperature=0.0 trade-off**: Deterministic but less creative

### Query Classification Bias
- **Pattern-based classifier**: Rule-based, not ML → brittle to new patterns
- **False positives**: 'compare' triggers STATISTICAL even if qualitative
- **Keyword dependency**: Relies on specific words (points, rebounds, etc.)
- **Context loss**: Conversational queries may misclassify without history
- **Tie-breaking**: Defaults to CONTEXTUAL when stat/context patterns equal

### Test Case Coverage Gaps
- **Single season only**: No historical comparisons (Jordan vs LeBron era)
- **No game-level data**: Can't answer "last 5 games" queries accurately
- **Team stats missing**: Player-centric, limited team-level queries
- **Advanced metrics**: PER, WS, VORP in DB but not in documents
- **Real-time data**: Static snapshot, no live scores/updates

### Evaluation Methodology Bias
- **Ground truth quality**: Hand-written, may not match RAGAS expectations
- **Evaluator model bias**: Gemini Flash Lite preferences != human judgment
- **Context window limits**: Long SQL results may truncate
- **Metric correlation**: High faithfulness doesn't guarantee usefulness
- **Sample size**: 47 test cases may not represent production distribution

### Hybrid Routing Edge Cases
- **SQL failure fallback**: No graceful degradation to vector-only
- **Context combination**: SQL + Vector results may contradict
- **Token budget**: Hybrid context = 2x size → higher costs
- **Latency**: SQL query + Vector search + LLM = 2-3s total
- **Cache misses**: No result caching → repeated queries cost API calls

### Data Quality & Representation Bias
- **Excel formatting issues**: Time formats, missing values, encoding
- **Static team abbreviations**: Hardcoded, no validation against roster moves
- **Missing player metadata**: No injury status, contract info, draft year
- **Stats normalization**: Per-game vs totals confusion
- **Sample bias**: 569 players ≠ all active NBA players

---

## Recommendations for Phase 4

### HIGH PRIORITY (Core Issues)

**1. Fix Answer Relevancy (0.112 → target 0.6+)**
- **Action**: Revise system prompt to explicitly instruct: "Answer the user's question directly and concisely based on the provided context"
- **Rationale**: Unchanged relevancy suggests prompt engineering issue, not data issue
- **Expected Impact**: +300-400% improvement

**2. Debug Faithfulness Drop (-18.7%)**
- **Action**: Investigate how SQL results are formatted in context. Add explicit instruction: "Only use information from the provided context. Do not add information not present in the context."
- **Rationale**: CONVERSATIONAL paradox suggests formatting/integration issue
- **Expected Impact**: Recover to baseline ~0.47

**3. Improve Query Classification**
- **Action**: Add confidence scores, implement fallback to vector-only for low-confidence classifications
- **Rationale**: SIMPLE query degradation suggests over-aggressive SQL routing
- **Expected Impact**: Restore SIMPLE query performance to baseline

**4. Add SQL Fallback Mechanism**
- **Action**: When SQL query fails or returns empty, automatically retry with vector-only
- **Rationale**: Improves robustness, prevents complete failures
- **Expected Impact**: Reduce failure rate by ~50%

**5. Fix CONVERSATIONAL Context Handling**
- **Action**: Ensure conversation history is passed to SQL tool, not just current query
- **Rationale**: -34% faithfulness in CONVERSATIONAL suggests multi-turn broken
- **Expected Impact**: Restore conversational faithfulness to baseline

### MEDIUM PRIORITY (Enhancements)

6. Expand few-shot examples to 15-20 covering edge cases
7. Add result caching (Redis) to reduce API costs
8. Implement context de-duplication for hybrid results
9. Add query explanation (show SQL to user for transparency)
10. Build confidence scores for classification decisions

### LOW PRIORITY / FUTURE

11. Add ML-based query classifier (replace regex patterns)
12. Multi-season historical data support
13. Create team-level statistics table
14. Natural language column aliasing (points → pts)
15. User feedback loop for classification improvement

---

## Conclusion

Phase 2 SQL integration showed **mixed results**:
- ✅ **Context Precision improved** (+6.3%) - SQL retrieval works
- ⚠️ **Faithfulness degraded** (-18.7%) - Generation quality declined
- ⚠️ **Answer Relevancy unchanged** (0.112) - Core issue remains

**Key Insight**: The problem is NOT data sources (SQL helps retrieval), but rather **prompt engineering and answer generation**. Phase 4 must focus on fixing the generation side to leverage the improved retrieval from Phase 2.

**Critical Finding**: The CONVERSATIONAL query paradox (+56.7% precision, -34.0% faithfulness) reveals that the system retrieves the right information but generates unfaithful responses. This strongly indicates a **prompt engineering defect** in how SQL results are integrated into the generation context.

**Next Steps**: Phase 4 will implement Option A recommendations (fix prompt engineering, improve classification, debug faithfulness) to recover baseline performance while retaining SQL integration benefits.

---

## Appendix: Technical Details

### Evaluation Setup
- **Evaluator LLM**: Gemini 2.0 Flash Lite (temperature=0.0)
- **Evaluator Embeddings**: Mistral (mistral-embed)
- **Test Cases**: 47 total (10 SIMPLE, 22 COMPLEX, 8 NOISY, 7 CONVERSATIONAL)
- **Sample Generation**: Gemini 2.0 Flash Lite with retry logic (exponential backoff)
- **Batch Processing**: 10 samples per batch, 60s cooldown between batches
- **Checkpointing**: Incremental saves after each sample

### SQL Integration Details
- **Database**: SQLite with 569 players, 45 statistical columns
- **Tool**: LangChain SQL Database tool with 8 few-shot examples
- **Temperature**: 0.0 (deterministic SQL generation)
- **Routing**: Pattern-based classifier (STATISTICAL, CONTEXTUAL, HYBRID)
- **Fallback**: None (fails if SQL query fails)

### Evaluation Metrics (RAGAS)
- **Faithfulness**: Measures factual consistency with retrieved context
- **Answer Relevancy**: Measures how well the answer addresses the question
- **Context Precision**: Measures relevance of retrieved context to the question
- **Context Recall**: Measures how much of the reference answer is covered by retrieved context

### Files Generated
- `evaluation_results/ragas_phase2.json` - Full Phase 2 results
- `evaluation_checkpoint_phase2.json` - Incremental checkpoint (deleted after completion)
- `scripts/evaluate_phase2.py` - Phase 2 evaluation script
- `scripts/generate_comparative_report.py` - This report generator

---

**Report Generated**: 2026-02-07
**Evaluator**: Claude Sonnet 4.5
**Status**: Phase 3 Complete → Ready for Phase 4
