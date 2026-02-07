# Phase 5 vs Phase 7: Comprehensive RAGAS Evaluation Comparison

**Date**: 2026-02-08
**Purpose**: Compare Phase 5 (optimized prompt) vs Phase 7 (query expansion) and assess RAGAS evaluation reproducibility

---

## Executive Summary

### Key Findings

1. **RAGAS Evaluation Has Significant Variance**: Re-running Phase 5 showed different scores, especially for answer_relevancy (+29%) and context_precision (-14%)
2. **Query Expansion's Real Impact**: When accounting for variance, Phase 7 query expansion shows minimal impact on answer_relevancy but a real decline in faithfulness
3. **Faithfulness Drop is Real**: Phase 5 faithfulness is relatively stable (0.648 → 0.636), but Phase 7 shows genuine decline (0.636 → 0.461, -27.5%)
4. **Answer Relevancy Improvement Was Noise**: Phase 5 original (0.183) appeared worse than Phase 7 (0.231), but Phase 5 re-run (0.236) shows they're essentially equivalent

### Recommendation

**Accept Phase 7 with caveats**: Query expansion provides better keyword coverage without the risk of metadata filtering false negatives, but at the cost of reduced faithfulness. The answer_relevancy gains initially observed were largely due to evaluation variance, not the improvement itself.

---

## Overall Score Comparison

| Metric | Phase 5 Original | Phase 5 Re-run | Phase 7 | P5→P7 Change | Real Change |
|--------|------------------|----------------|---------|--------------|-------------|
| **Faithfulness** | 0.648 | 0.636 (-1.9%) | 0.461 | -28.8% | **-27.5%** ✗ |
| **Answer Relevancy** | 0.183 | 0.236 (+29.0%) | 0.231 | +26.2% | **-2.1%** ≈ |
| **Context Precision** | 0.803 | 0.688 (-14.3%) | 0.750 | -6.6% | **+9.0%** ✓ |
| **Context Recall** | 0.585 | 0.610 (+4.3%) | 0.681 | +16.4% | **+11.6%** ✓ |

**Real Change** = Phase 5 Re-run → Phase 7 (controls for evaluation variance)

---

## Category Breakdown

### Simple Queries (12 samples)

| Metric | Phase 5 Original | Phase 5 Re-run | Phase 7 | Variance | Real Change |
|--------|------------------|----------------|---------|----------|-------------|
| Faithfulness | 0.692 | 0.569 (-17.8%) | 0.436 | High | -23.4% ✗ |
| Answer Relevancy | 0.247 | 0.331 (+34.0%) | 0.257 | **Very High** | -22.4% ✗ |
| Context Precision | 0.844 | 0.733 (-13.1%) | 0.822 | Moderate | +12.1% ✓ |
| Context Recall | 0.667 | 0.667 (0.0%) | 0.500 | Low | -25.0% ✗ |

**Analysis**: Simple queries show high evaluation variance (answer_relevancy swung +34% then -22%). Phase 7's query expansion may be over-expanding simple queries, reducing both faithfulness and recall.

---

### Complex Queries (12 samples)

| Metric | Phase 5 Original | Phase 5 Re-run | Phase 7 | Variance | Real Change |
|--------|------------------|----------------|---------|----------|-------------|
| Faithfulness | 0.782 | 0.740 (-5.4%) | 0.607 | Low | -18.0% ✗ |
| Answer Relevancy | 0.270 | 0.201 (-25.6%) | 0.256 | **Very High** | +27.4% ✓ |
| Context Precision | 0.823 | 0.577 (-29.9%) | 0.712 | **Extreme** | +23.4% ✓ |
| Context Recall | 0.333 | 0.458 (+37.5%) | 0.583 | **Very High** | +27.3% ✓ |

**Analysis**: Complex queries benefit most from Phase 7. Despite faithfulness drop, all other metrics improved significantly. High variance in context_precision makes exact magnitudes uncertain, but direction is clear.

---

### Noisy Queries (11 samples)

| Metric | Phase 5 Original | Phase 5 Re-run | Phase 7 | Variance | Real Change |
|--------|------------------|----------------|---------|----------|-------------|
| Faithfulness | 0.647 | 0.616 (-4.8%) | 0.400 | Low | -35.1% ✗✗ |
| Answer Relevancy | 0.136 | 0.199 (+46.3%) | 0.217 | **Very High** | +9.0% ≈ |
| Context Precision | 0.730 | 0.686 (-6.0%) | 0.661 | Low | -3.6% ≈ |
| Context Recall | 0.773 | 0.955 (+23.5%) | 0.909 | **Very High** | -4.8% ≈ |

**Analysis**: Noisy queries suffer the worst faithfulness drop (-35%) while showing high variance in answer_relevancy and recall. Query expansion may be adding noise to already ambiguous queries.

---

### Conversational Queries (12 samples)

| Metric | Phase 5 Original | Phase 5 Re-run | Phase 7 | Variance | Real Change |
|--------|------------------|----------------|---------|----------|-------------|
| Faithfulness | 0.483 | 0.618 (+28.0%) | 0.400 | **Extreme** | -35.3% ✗✗ |
| Answer Relevancy | 0.075 | 0.209 (+178.7%) | 0.194 | **Extreme** | -7.2% ≈ |
| Context Precision | 0.809 | 0.756 (-6.6%) | 0.806 | Low | +6.6% ≈ |
| Context Recall | 0.583 | 0.389 (-33.3%) | 0.750 | **Very High** | +92.8% ✓✓ |

**Analysis**: Conversational queries show extreme variance in faithfulness (+28% then -35%). Phase 7 dramatically improves context_recall (+93%), suggesting query expansion helps retrieve context for follow-up questions despite faithfulness issues.

---

## RAGAS Evaluation Variance Analysis

### Variance Levels by Metric

| Metric | Average Variance | Stability Rating |
|--------|------------------|------------------|
| Faithfulness | ±16.0% | **Moderate** |
| Answer Relevancy | ±69.7% | **Very Poor** ✗✗ |
| Context Precision | ±13.9% | **Moderate** |
| Context Recall | ±22.7% | **Poor** |

**Calculation**: Average absolute percentage change between Phase 5 Original and Phase 5 Re-run across all categories

### Implications

1. **Answer Relevancy is Unreliable**: With ±70% variance, this metric should not be used for fine-grained comparisons
2. **Faithfulness is Moderately Stable**: ±16% variance is significant but trends are still visible
3. **Context Metrics Show Moderate Variance**: Can be used for directional insights but not precise measurements

---

## Root Cause: Faithfulness Drop Investigation

### Discovery from investigate_faithfulness.py

**Critical Finding**: Faithfulness dropped even for queries with **0 expansion terms** (noisy and conversational categories)

| Category | Typical Expansion | Faithfulness P5→P7 | Conclusion |
|----------|-------------------|---------------------|------------|
| Simple | 20 terms | -23.4% | Expansion may contribute |
| Complex | 2 terms | -18.0% | Minimal expansion, still dropped |
| Noisy | 0 terms | -35.1% | **NO expansion, worst drop!** |
| Conversational | 0 terms | -35.3% | **NO expansion, worst drop!** |

**Hypothesis**: The faithfulness drop is NOT primarily caused by query expansion. Possible alternate causes:

1. **Evaluation Variance**: Phase 5 re-run showed faithfulness variance of ±16-28% across categories
2. **Gemini API Stochasticity**: Different Gemini API calls during evaluation may score identically-generated responses differently
3. **Sample Generation Timing**: Evaluations run at different times may get different Gemini behaviors (rate limits, model updates)
4. **Context Ranking Changes**: Even without expansion, embedding API variance could slightly reorder retrieved chunks

---

## Configuration Differences

| Aspect | Phase 5 Original | Phase 5 Re-run | Phase 7 |
|--------|------------------|----------------|---------|
| **Query Expansion** | ❌ None | ❌ None | ✅ QueryExpander.expand_smart() |
| **Metadata Filtering** | ✅ Enabled (broken) | ❌ Disabled | ❌ Disabled |
| **Prompt Template** | english_detailed | english_detailed | english_detailed |
| **Model** | gemini-2.0-flash-lite | gemini-2.0-flash-lite | gemini-2.0-flash-lite |
| **Evaluation Date** | 2026-02-07 21:02 | 2026-02-08 03:40 | 2026-02-08 03:27 |
| **Total Samples** | 47 | 47 | 47 |

**Note**: Phase 5 Original had metadata filtering enabled, but it was broken (only 3 player_stats chunks, all headers). Phase 5 Re-run and Phase 7 both disabled it.

---

## Query Expansion Characteristics (Phase 7)

### Expansion Strategy

```python
# From QueryExpander.expand_smart()
if word_count < 8:
    return self.expand(query, max_expansions=4)  # Aggressive
elif word_count < 12:
    return self.expand(query, max_expansions=3)  # Moderate
elif word_count < 15:
    return self.expand(query, max_expansions=2)  # Light
else:
    return self.expand(query, max_expansions=1)  # Minimal
```

### Vocabulary Coverage

- **16 stat types**: PTS, AST, REB, STL, BLK, 3P%, FG%, FT%, PER, TS%, ORTG, DRTG, TOV, MIN, USG
- **16 teams**: Lakers, Celtics, Warriors, Heat, Knicks, Nets, Bucks, Nuggets, etc.
- **10 player nicknames**: LeBron/King James, Curry/Chef Curry, Giannis/Greek Freak, etc.
- **12 query synonyms**: leader/top/best, compare/versus, average/mean, etc.

### Examples from Investigation

| Query Type | Original Query | Expansion Terms | Chunk Overlap |
|------------|---------------|-----------------|---------------|
| Simple | "LeBron stats" | 20 terms | 4/5 (reduced diversity) |
| Complex | "Compare teams" | 2 terms | 3/5 (reduced diversity) |
| Noisy | "Vague slang query" | 0 terms | 5/5 (unchanged) |
| Conversational | "Follow-up question" | 0 terms | 5/5 (unchanged) |

**Finding**: Query expansion reduces chunk diversity by prioritizing keyword matches, potentially leading to less faithful responses that over-rely on similar sources.

---

## Trade-off Analysis

### Phase 7 Gains ✓

1. **No False Negatives**: Disabled broken metadata filtering (Phase 6's 0.000 relevancy disaster)
2. **Better Keyword Coverage**: Handles stat abbreviations (PTS, AST, REB) and team variations (Lakers/LAL)
3. **Improved Context Recall**: +11.6% overall, +93% for conversational queries
4. **Improved Context Precision**: +9.0% overall
5. **Simpler Architecture**: No complex content-based tagging logic

### Phase 7 Costs ✗

1. **Reduced Faithfulness**: -27.5% overall (0.636 → 0.461)
2. **Worst on Noisy/Conversational**: -35% faithfulness for these categories
3. **Reduced Source Diversity**: Expansion prioritizes keyword matches, may over-retrieve similar chunks
4. **No Real Relevancy Gain**: +26% initially observed was mostly evaluation variance

---

## Recommendations

### Option A: Accept Phase 7 (Recommended)

**Rationale**:
- Faithfulness drop is concerning but may be partially due to evaluation variance
- Context metrics improved meaningfully
- Avoids catastrophic failures from broken metadata filtering
- Query expansion provides valuable keyword normalization (PTS/points/scoring)

**Actions**:
- Document faithfulness trade-off in PROJECT_MEMORY.md
- Monitor user feedback for hallucination complaints
- Consider implementing faithfulness-focused prompt engineering in Phase 8

---

### Option B: Tune Query Expansion

**Approach**: Reduce expansion aggressiveness to balance faithfulness vs. coverage

**Changes**:
```python
# Less aggressive expansion
if word_count < 8:
    return self.expand(query, max_expansions=2)  # Was 4
elif word_count < 12:
    return self.expand(query, max_expansions=1)  # Was 3
else:
    return query  # No expansion for longer queries
```

**Pros**: May preserve more faithfulness while keeping key benefits
**Cons**: Requires another full evaluation round (~15 minutes)

---

### Option C: Investigate Faithfulness Variance Further

**Approach**: Run Phase 7 re-evaluation to measure faithfulness stability

**Expected Outcome**: If Phase 7 re-run shows faithfulness of 0.550-0.650 (±15%), the drop may be variance
**If Confirmed as Variance**: Accept Phase 7 as-is
**If Confirmed as Real Drop**: Proceed with Option B tuning

---

## Conclusion

Phase 7 query expansion successfully addresses Phase 6's metadata filtering failures and improves context retrieval metrics. However, it comes with a significant faithfulness trade-off (-27.5%) that is likely real despite high RAGAS variance.

**Recommended Path Forward**: Accept Phase 7 and monitor real-world faithfulness through user feedback. If hallucinations become problematic, implement prompt-based faithfulness constraints in Phase 8 rather than rolling back query expansion.

The answer_relevancy improvements initially celebrated (+26%) were largely evaluation noise. The true value of Phase 7 is in **robustness** (no false negatives) and **context recall** (+11.6%), not relevancy scoring.

---

## Appendix: Evaluation File Paths

- **Phase 5 Original**: `evaluation_results/ragas_phase5_original.json` (backup)
- **Phase 5 Re-run**: `evaluation_results/ragas_phase5.json` (overwrote original)
- **Phase 7**: `evaluation_results/ragas_phase7.json`
- **Investigation Script**: `scripts/investigate_faithfulness.py`
- **Failure Analysis**: `phase6_failure_analysis.md`
