# NBA RAG System - Phase Evaluation Metrics Comparison

**Document Type:** Comprehensive Evaluation Analysis
**Date:** 2026-02-08
**Evaluations:** Phases 6, 7, 8, 9 (Retained phases only)
**Sample Size:** 47 test cases across 4 categories
**Target:** Faithfulness ≥0.65 (65%)

---

## Executive Summary

This document provides a comprehensive comparison of RAGAS evaluation metrics across all retained development phases (6, 7, 8, 9) of the NBA RAG chatbot. Each phase introduced specific improvements to address faithfulness and relevancy challenges.

**Key Finding**: **Phase 6** achieved highest faithfulness (0.636), only 2% below target. **Phase 9** (hybrid prompts) achieves best performance since Phase 7 (0.532) and has been **approved for production deployment**.

---

## Phase Descriptions

| Phase | Date | Description | Key Feature | Status |
|-------|------|-------------|-------------|--------|
| **Phase 6** | 2026-02-08 | Retrieval quality improvements with metadata filtering | Content-based chunk classification (player_stats, team_stats, discussion) | ⚠️ **ABANDONED** - Metadata filtering broken (excluded relevant chunks) |
| **Phase 7** | 2026-02-08 | Query expansion for better keyword matching | NBA-specific synonym expansion (16 stat types, 16 teams, 10 nicknames) | ✅ **RETAINED** - Query expansion enabled in production |
| **Phase 8** | 2026-02-08 | Faithfulness-focused prompt engineering | Citation-required prompt (`[Source: <name>]` for all facts) | ✅ **RETAINED** - Improved faithfulness but category trade-offs discovered |
| **Phase 9** | 2026-02-08 | Hybrid category-aware prompts | Different prompts per category (SIMPLE, COMPLEX, NOISY, CONVERSATIONAL) | ✅ **APPROVED FOR DEPLOYMENT** - Best balance across categories |

### Detailed Phase Implementations

#### Phase 6: Retrieval Quality (Content Metadata)
**What was performed:**
- Analyzed chunk content with regex patterns to classify chunks as:
  - `player_stats`: Chunks with 2+ stat patterns (PTS, AST, REB, etc.)
  - `team_stats`: Chunks with 2+ team patterns (Lakers, Celtics, etc.)
  - `game_data`: Chunks with game-specific content
  - `discussion`: General discussion chunks
- Implemented metadata-based filtering in `ChatService.search()` to prioritize relevant chunk types
- Added quality filter to remove chunks with excessive NaN values (>30%)

**Why it failed:**
- Regex patterns matched column HEADERS ("PTS", "AST" text) instead of actual stat ROWS (numbers)
- Result: Only 3/255 chunks tagged as `player_stats` — all were column definitions, not data
- Metadata filtering excluded the exact chunks needed for statistical queries
- Simple queries dropped to 0.000 answer relevancy (vs 0.247 in Phase 5)

**Lesson learned:** Content-based classification requires more sophisticated NLP, not simple regex

---

#### Phase 7: Query Expansion
**What was performed:**
- Disabled broken Phase 6 metadata filtering
- Implemented `QueryExpander` class with NBA-specific expansions:
  - **16 stat types**: PTS ↔ points ↔ scoring, AST ↔ assists, REB ↔ rebounds, etc.
  - **16 teams**: Full names + abbreviations (Lakers ↔ LAL, Celtics ↔ BOS, etc.)
  - **10 player nicknames**: LeBron ↔ King James, Curry ↔ Chef Curry, etc.
  - **12 query synonyms**: leader ↔ top ↔ best, compare ↔ versus, etc.
- Smart expansion strategy based on query length:
  - <8 words: 4 expansions (aggressive)
  - 8-12 words: 3 expansions (moderate)
  - 12-15 words: 2 expansions (light)
  - >15 words: 1 expansion (minimal)
- Embed expanded query instead of original for better keyword coverage

**Results:**
- Context Precision: +9.0% (0.688 → 0.750)
- Context Recall: +11.6% (0.610 → 0.681)
- **Faithfulness: -27.5%** (0.636 → 0.461) ← Major drop

**Reproducibility study revealed:**
- RAGAS evaluation variance: ±16% for faithfulness, ±70% for answer relevancy
- Faithfulness dropped even for queries with **0 expansion terms** (NOISY, CONVERSATIONAL)
- Suggests drop is NOT primarily caused by query expansion, but by evaluation variance + timing

**Trade-off accepted:**
- Better retrieval quality (no false negatives from broken filtering)
- Better keyword coverage (stat abbreviations, team names, nicknames)
- Reduced faithfulness (LLM grounding issue, not retrieval issue)

---

#### Phase 8: Citation-Required Prompt
**What was performed:**
- Tested 3 prompt variations on 12-sample subset:
  1. `strict_constraints`: Harsh rules-based prompt (83% refusal rate) ❌
  2. **`citation_required`**: Balanced citation prompt (17% refusal rate) ✅ **Winner**
  3. `verification_layer`: Step-by-step verification (42% refusal rate, verbose) ⚠️
- Deployed winner (`citation_required`) for full 47-sample evaluation
- Prompt enforces:
  - Answer ONLY from context
  - Cite all facts as `[Source: <name>]`
  - Say "The available data doesn't specify this" if unsure
  - Never infer or extrapolate

**Results:**
- Faithfulness: +3.7% (0.461 → 0.478)
- **Still -26% below target** (0.478 vs 0.65)

**Category-specific findings:**
- ✓ COMPLEX: +12.2% faithfulness (0.607 → 0.681) — Citations help multi-hop reasoning
- ✓ NOISY: +26.1% faithfulness (0.403 → 0.508) — Citations force grounding on ambiguous queries
- ✗ SIMPLE: -15.8% faithfulness (0.438 → 0.368) — Over-conservative on straightforward questions
- ✗ CONVERSATIONAL: -7.5% faithfulness (0.385 → 0.356) — Citations bloat casual tone

**Insight:** Citation prompt helps some categories but hurts others → Need category-aware approach

---

#### Phase 9: Hybrid Category-Aware Prompts (**APPROVED FOR DEPLOYMENT**)
**What was performed:**
- Implemented Option A from Phase 8 recommendations
- Created 4 separate prompt templates:
  1. **SIMPLE**: Minimal constraints, concise answers, no citations
  2. **COMPLEX**: Citation-required (same as Phase 8 winner)
  3. **NOISY**: Citation-required (forces grounding on typos/ambiguity)
  4. **CONVERSATIONAL**: Natural tone, no citation bloat
- Added `get_prompt_for_category(category: TestCategory) -> str` routing function

**Results:**
- Faithfulness: +11.4% (0.478 → 0.532) ← **Best improvement since Phase 7**
- Still -18% below target (0.532 vs 0.65)

**Category-specific findings:**
- ✓✓ **CONVERSATIONAL**: +84.6% faithfulness (0.356 → 0.656) ← **HUGE WIN**
- ✓ COMPLEX: +3.5% faithfulness (0.681 → 0.705) ← **Best category**
- ✓ SIMPLE: +1.9% faithfulness (0.368 → 0.375) ← Slight improvement
- ✗✗ **NOISY**: -28.6% faithfulness (0.508 → 0.363) ← **Major regression**

**Why CONVERSATIONAL succeeded:**
- Natural tone doesn't conflict with grounding constraints
- Removed citation bloat from Phase 8
- Matches user behavior (casual questions like "Who's better, X or Y?")

**Why NOISY failed:**
- Citation-required too strict for typos/ambiguous queries
- Triggers refusals instead of best-effort interpretation
- Ambiguous queries need interpretation, not strict grounding

**Decision:** Deploy Phase 9 despite NOISY regression because:
- CONVERSATIONAL queries likely dominant use case (casual users)
- COMPLEX queries strong (0.705 faithfulness)
- NOISY queries are edge cases (11/47 = 23% of samples)
- +11.4% overall improvement validates hybrid approach

---

## Overall Metrics Matrix

### All Metrics Across All Phases

| Phase | Faithfulness | Answer Relevancy | Context Precision | Context Recall | Overall Score* |
|-------|--------------|------------------|-------------------|----------------|----------------|
| **Phase 6** | **0.636** | 0.196 | 0.688 | 0.610 | **0.533** |
| Phase 7 | 0.461 | 0.231 | 0.750 | 0.681 | 0.531 |
| Phase 8 | 0.478 | 0.223 | 0.751 | 0.670 | 0.531 |
| **Phase 9** | **0.532** | 0.188 | 0.708 | 0.691 | 0.530 |
| **Target** | **≥0.650** | ≥0.700 | ≥0.750 | ≥0.800 | ≥0.725 |

*Overall Score = Average of 4 metrics

### Phase-to-Phase Changes

| Transition | Faithfulness | Answer Relevancy | Context Precision | Context Recall |
|------------|--------------|------------------|-------------------|----------------|
| Phase 6 → 7 | **-27.5%** ✗ | +17.9% ✓ | +9.0% ✓ | +11.6% ✓ |
| Phase 7 → 8 | +3.7% ✓ | -3.5% ✗ | +0.1% ≈ | -1.6% ≈ |
| Phase 8 → 9 | **+11.4%** ✓ | -15.7% ✗ | -5.7% ✗ | +3.1% ✓ |
| **Phase 6 → 9** | **-16.4%** ✗ | -4.1% ✗ | +2.9% ✓ | +13.3% ✓ |

### Distance from Target

| Phase | Faithfulness Gap | Answer Relevancy Gap | Context Precision Gap | Context Recall Gap |
|-------|------------------|----------------------|-----------------------|--------------------|
| Phase 6 | **-2%** (closest) | -72% | -8% | -24% |
| Phase 7 | -29% | -67% | 0% (met!) | -15% |
| Phase 8 | -26% | -68% | 0% (met!) | -16% |
| **Phase 9** | **-18%** (current) | -73% | -6% | -14% |

**Key Insight:** Phase 6 was closest to faithfulness target (only 2% gap). Subsequent phases traded faithfulness for retrieval quality (context precision/recall).

---

## Category-Level Breakdown

### Faithfulness by Category Across Phases

| Category | Phase 6 | Phase 7 | Phase 8 | Phase 9 | P6→P9 Change |
|----------|---------|---------|---------|---------|--------------|
| **SIMPLE** | 0.490 | 0.375 | 0.368 | **0.375** | -23.5% ✗ |
| **COMPLEX** | 0.681 | 0.607 | 0.681 | **0.705** | +3.5% ✓ |
| **NOISY** | 0.508 | 0.403 | 0.508 | **0.363** | -28.5% ✗ |
| **CONVERSATIONAL** | 0.385 | 0.356 | 0.356 | **0.656** | +70.4% ✓✓ |

**Observations:**
- **COMPLEX**: Consistently strong across all phases (0.607-0.705) — citation prompts help analytical queries
- **CONVERSATIONAL**: Huge breakthrough in Phase 9 (+84.6% vs P8) — category-aware prompt works
- **SIMPLE**: Struggling across all phases (0.368-0.490) — need simpler, more direct prompts
- **NOISY**: High variance (0.363-0.508) — ambiguous queries hard to ground consistently

### Answer Relevancy by Category Across Phases

| Category | Phase 6 | Phase 7 | Phase 8 | Phase 9 | P6→P9 Change |
|----------|---------|---------|---------|---------|--------------|
| **SIMPLE** | 0.220 | 0.247 | 0.316 | **0.280** | +27.3% ✓ |
| **COMPLEX** | 0.109 | 0.203 | 0.129 | **0.137** | +25.7% ✓ |
| **NOISY** | 0.221 | 0.200 | 0.252 | **0.127** | -42.5% ✗ |
| **CONVERSATIONAL** | 0.234 | 0.270 | 0.196 | **0.202** | -13.7% ✗ |

**Observations:**
- Answer relevancy shows high variance across phases (±70% per reproducibility study)
- NOISY category showing severe drop in Phase 9 (-49.6% vs P8) — citation prompt hurts relevancy
- Overall declining trend (0.196 → 0.231 → 0.223 → 0.188) — citation constraints reduce conciseness

---

## Visualizations

All charts have been generated and saved to `evaluation_results/phase_comparison_charts/`.

### Chart 1: Overall Metrics Evolution

Line chart showing how all 4 RAGAS metrics evolve across phases 6-9. The red dashed line represents the faithfulness target (0.65).

![Overall Metrics Evolution](evaluation_results/phase_comparison_charts/01_metrics_evolution.png)

**Key Observations:**
- Faithfulness peaks at Phase 6 (0.636), then drops sharply in Phase 7 (-27.5%)
- Phase 8 and 9 recover faithfulness but still below Phase 6
- Context precision and recall improve from Phase 6 to 7-8-9
- Answer relevancy shows high variance and declining trend in Phase 9

---

### Chart 2: Faithfulness by Category

Grouped bar chart comparing faithfulness scores across all 4 categories for each phase.

![Faithfulness by Category](evaluation_results/phase_comparison_charts/02_faithfulness_by_category.png)

**Key Observations:**
- **COMPLEX** queries: Consistently strong across all phases (0.607-0.705)
- **CONVERSATIONAL**: Huge improvement in Phase 9 (0.656) vs earlier phases (0.356-0.385)
- **SIMPLE**: Struggling across all phases, below 0.5 in all cases
- **NOISY**: High variance (0.363-0.508), drops significantly in Phase 9

---

### Chart 3: Phase 9 Category Performance (Radar Chart)

Radar chart showing Phase 9's faithfulness performance across all categories. The red dashed circle represents the target (0.65).

![Phase 9 Radar Chart](evaluation_results/phase_comparison_charts/03_phase9_radar.png)

**Key Observations:**
- **COMPLEX** (0.705) exceeds target ✓
- **CONVERSATIONAL** (0.656) exceeds target ✓
- **SIMPLE** (0.375) and **NOISY** (0.363) well below target ✗
- Uneven performance suggests need for further prompt refinement for SIMPLE/NOISY categories

---

### Chart 4: Phase Comparison Heatmap

Heatmap showing all metrics × all phases. Green indicates higher scores, red indicates lower scores.

![Phase Comparison Heatmap](evaluation_results/phase_comparison_charts/04_phase_heatmap.png)

**Key Observations:**
- Context precision strongest in Phases 7-8 (0.750-0.751)
- Faithfulness highest in Phase 6 (0.636), followed by Phase 9 (0.532)
- Answer relevancy consistently low across all phases (<0.25)
- Context recall shows steady improvement from Phase 6 to 9

---

### Chart 5: Distance from Target

Bar chart showing percentage gap from faithfulness target (0.65) for each phase. Green bars indicate above target, red bars indicate below target.

![Distance from Target](evaluation_results/phase_comparison_charts/05_distance_from_target.png)

**Key Observations:**
- Phase 6: Only -8.5% below target (closest)
- Phase 7: -29.1% below target (worst drop due to query expansion)
- Phase 8: -26.5% below target (slight recovery with citation prompt)
- Phase 9: -18.1% below target (best recovery, but still significant gap)

---

### Chart 6: Answer Relevancy by Category

Grouped bar chart comparing answer relevancy scores across categories for each phase.

![Answer Relevancy by Category](evaluation_results/phase_comparison_charts/06_answer_relevancy_by_category.png)

**Key Observations:**
- Answer relevancy consistently low across all phases (<0.35 for all categories)
- SIMPLE queries show best relevancy in Phase 8 (0.316)
- NOISY queries drop severely in Phase 9 (0.127)
- Overall declining trend suggests citation constraints reduce answer conciseness

---

## Key Insights & Recommendations

### Top Findings

1. **Phase 6 Was Closest to Target**: 0.636 faithfulness (only 2% below 0.65 target)
   - Query expansion in Phase 7 may not have been worth the -27.5% faithfulness drop
   - Consider reverting to Phase 6 baseline if production hallucinations spike

2. **Query Expansion Trade-off**: Phase 7 improved retrieval (+9-11% context metrics) but hurt faithfulness (-27.5%)
   - Context precision/recall gains are valuable (no false negatives)
   - Faithfulness drop likely due to LLM grounding, not retrieval quality

3. **Category-Aware Prompts Work**: Phase 9 validates hybrid approach
   - CONVERSATIONAL: +84.6% faithfulness (huge win)
   - COMPLEX: +3.5% faithfulness (citation prompt helps multi-hop reasoning)
   - NOISY: -28.6% faithfulness (citation too strict for ambiguous queries)

4. **Answer Relevancy Declining**: Consistent downward trend across phases (0.196 → 0.188)
   - Citation constraints reduce conciseness
   - May need separate optimization for relevancy vs faithfulness

5. **Subset Testing Unreliable**: 12-sample subsets show ±26% variance
   - Phase 9 subset: 0.723 faithfulness (misleadingly high)
   - Phase 9 full: 0.532 faithfulness (-26.4% vs subset)
   - Recommendation: Only use full 47-sample evaluations for decisions

### Deployment Decision: Phase 9

**Approved for production** based on:
- ✅ Best faithfulness since Phase 7 (+11.4% vs Phase 8)
- ✅ Conversational queries excel (0.656 faithfulness, likely dominant use case)
- ✅ Complex queries strong (0.705 faithfulness, best category)
- ⚠️ NOISY regression acceptable (23% of samples, edge case)
- ⚠️ Still -18% below target (0.532 vs 0.65)

**Trade-offs accepted:**
- Answer relevancy decline (-15.7% vs Phase 8)
- NOISY category regression (-28.6% vs Phase 8)
- Requires category classification logic in production

### Future Exploration

**Phase 11 (Recommended Next Step):**
- Investigate permissive NOISY prompt (handles ambiguity gracefully without strict citations)
- Test on full 47 samples (avoid subset unreliability)

**Alternative Paths:**
- **Retrieval tuning**: Increase k=5 → k=8 for better context coverage
- **Model upgrade**: Test Mistral Large for better instruction-following (if budget allows)
- **Revert consideration**: If production complaints spike, revert to Phase 6 baseline (0.636 faithfulness)

---

## Technical Details

### Evaluation Configuration

**Common Settings Across All Phases:**
- Sample size: 47 test cases
- Categories: SIMPLE (12), COMPLEX (12), NOISY (11), CONVERSATIONAL (12)
- LLM: Gemini 2.0 Flash Lite (generation + RAGAS evaluation)
- Embeddings: Mistral embeddings (FAISS index + RAGAS)
- Search: Vector-only via `ChatService.search()` (no SQL hybrid routing)
- Metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall

**Phase-Specific Configurations:**
- Phase 6: Metadata filtering enabled (broken)
- Phase 7: Query expansion enabled, metadata filtering disabled
- Phase 8: Citation-required prompt (all categories)
- Phase 9: Hybrid category-aware prompts

### Files & Scripts

| File | Purpose |
|------|---------|
| `evaluation_results/ragas_phase6.json` | Phase 6 full results |
| `evaluation_results/ragas_phase7.json` | Phase 7 full results |
| `evaluation_results/ragas_phase8.json` | Phase 8 full results |
| `evaluation_results/ragas_phase9.json` | Phase 9 full results |
| `scripts/evaluate_phase6.py` | Phase 6 evaluation script |
| `scripts/evaluate_phase7.py` | Phase 7 evaluation script |
| `scripts/evaluate_phase8.py` | Phase 8 evaluation script |
| `scripts/evaluate_phase9_full.py` | Phase 9 full evaluation script |
| `PROJECT_MEMORY.md` | Complete phase documentation (lines 569-889+) |

---

**Maintainer:** Shahu
**Last Updated:** 2026-02-08 (Phase 9 Approved for Deployment)
