# Phase 6 Failure Analysis

**Date**: 2026-02-08
**Issue**: Simple queries dropped to 0.000 answer relevancy (vs 0.247 in Phase 5)
**Root Cause**: Content-based metadata tagging is inverted

## Problem Summary

Phase 6 implemented content-based metadata tagging to improve retrieval precision. However, the regex patterns in `_analyze_chunk_content()` are mis-classifying chunks:

- **Actual player stat rows** (189 chunks) → Tagged as "discussion"
- **Table headers/metadata** (3 chunks) → Tagged as "player_stats"

When Phase 6 applies metadata filters for player queries (e.g., `{'data_type': 'player_stats'}`), it searches among only 3 header chunks instead of 189 actual stat chunks.

## Evidence

### Metadata Distribution
```
discussion    : 189 chunks (74.1%) ← Should be player_stats
game_data     :  46 chunks (18.0%)
player_stats  :   3 chunks ( 1.2%) ← These are headers!
team_stats    :  17 chunks ( 6.7%)
```

### Query Test Results

#### Query 1: "Which player has the best 3-point percentage over the last 5 games?"

**WITHOUT metadata filters** (Phase 5 behavior):
```
1. [discussion] Cam Whitmore   HOU   20  51  30  21  16.2   479  179   403  44.4...
2. [discussion] Alperen Sengun   HOU   22  76  52  24  31.5  1452  570  1140  49.6...
3. [discussion] Garrison Mathews   ATL   28  47  21  26  17.6   353  103   259  39.7...
```
✅ Returns actual player stats

**WITH metadata filters** (Phase 6 behavior):
```
1. [player_stats] 1  2  3  4  5  6  7  8  9  10  11  12  13  14...
2. [player_stats] + / -  Plus-Minus (écart de score lorsque le joueur est...)
3. [player_stats] FTM  Lancers francs réussis (Free Throws Made)...
```
❌ Returns only table headers and column definitions

**Impact**: Filtering excluded Cam Whitmore, Alperen Sengun, Garrison Mathews chunks

---

#### Query 2: "What are LeBron James' average points, rebounds, and assists this season?"

**WITHOUT metadata filters**:
```
1. [discussion] LeBron James  70...
2. [discussion] Austin Reaves  58...
```
✅ First result is LeBron's actual data

**WITH metadata filters**:
```
1. [player_stats] + / -  Plus-Minus (écart de score lorsque le joueur est...)
2. [player_stats] FTM  Lancers francs réussis...
3. [player_stats] 1  2  3  4  5  6  7  8  9  10  11...
```
❌ LeBron chunk completely excluded

**Impact**: Filtering excluded the exact chunk needed to answer the question

---

#### Query 3: "Which team leads the league in rebounds per game?"

**WITHOUT metadata filters**: 5 results
**WITH metadata filters** (`{'data_type': 'team_stats'}`): 5 results
✅ Works because 17 chunks tagged as team_stats (vs only 3 for player_stats)

## Why the Regex Patterns Failed

From `src/pipeline/data_pipeline.py:_analyze_chunk_content()`:

```python
player_stat_patterns = [
    r'\bpts\b', r'\bast\b', r'\breb\b',  # Lowercase abbreviations
    r'\bfg%\b', r'\b3p%\b',              # Specific formats
    r'points per game',                   # Full phrases
]
```

**Problem**: Actual stat tables don't contain these patterns because:
1. Abbreviations appear in UPPERCASE (PTS, not pts)
2. Stats are numeric data, not text descriptions
3. Patterns match column headers/explanations more than actual data rows

**Example actual stat chunk**:
```
Cam Whitmore   HOU   20  51  30  21  16.2   479  179   403  44.4
```
- Contains: Player name, team, numbers
- Missing: "pts", "ast", "reb" text strings
- **Result**: Tagged as "discussion"

**Example header chunk**:
```
PTS  Points per game  AST  Assists per game  REB  Rebounds per game
```
- Contains: "pts", "ast", "reb", "points per game"
- **Result**: Tagged as "player_stats"

## Impact on RAGAS Metrics

### Phase 5 (No metadata filtering)
- Simple queries: **0.247 answer relevancy**
- Searches all 255 chunks, returns relevant stats

### Phase 6 (With metadata filtering)
- Simple queries: **0.000 answer relevancy**
- Searches only 3 header chunks, contexts are irrelevant
- RAGAS evaluator scores responses as completely off-topic

## Proposed Solutions

### Option A: Remove Metadata Filtering (Rollback)
**Pros**:
- Immediate fix, restores Phase 5 performance
- No risk of further mis-classification

**Cons**:
- Loses potential precision gains for complex queries
- Doesn't leverage the metadata infrastructure

**Implementation**:
- Remove metadata filter logic from `ChatService.search()`
- Keep quality filter (47 low-quality chunks removed is still valuable)

---

### Option B: Fix Content-Based Tagging
**Approach**: Improve regex patterns to match actual stat data structure

**New patterns**:
```python
# Match stat rows: player name followed by team code and numbers
player_stat_patterns = [
    r'\b[A-Z]{3}\s+\d{1,2}\s+\d+',  # Team code + age + games (e.g., "HOU 20 51")
    r'\b\d+\.\d+\s+\d+\s+\d+\s+\d+',  # Multiple decimal stats in sequence
    r'\b(PTS|AST|REB|STL|BLK)\b',    # UPPERCASE stat abbreviations
]
```

**Pros**:
- Preserves metadata filtering benefits for future improvements
- Could work for team stats too

**Cons**:
- Requires pipeline rebuild (30-40 minutes)
- Risk of new mis-classification patterns
- May still miss edge cases

---

### Option C: Disable Metadata Filtering, Enable Query Expansion (Phase 7)
**Approach**: Skip metadata filtering, test Phase 7 query expansion as the precision booster

**Pros**:
- Query expansion adds relevant synonyms/abbreviations without filtering
- No risk of excluding relevant chunks
- Phase 7 implementation already complete and tested

**Cons**:
- Haven't validated query expansion effectiveness yet

**Next Step**: Run Phase 7 subset test to measure impact

---

## Recommendation

**Option C** - Disable metadata filtering and proceed to Phase 7 testing:

1. **Immediate**: Disable metadata filtering in `ChatService.search()`
2. **Test**: Run Phase 7 query expansion on 12-sample bad-relevancy subset
3. **Decide**:
   - If query expansion recovers relevancy → Run Phase 7 full evaluation
   - If not → Consider Option B (fix tagging) or Option A (full rollback)

This approach minimizes wasted effort and tests the next improvement before investing in fixing the current one.

## Action Items

- [ ] Disable metadata filtering in `src/services/chat.py`
- [ ] Run Phase 7 subset test (12 problematic queries)
- [ ] Compare metrics: Phase 5 vs Phase 6 (no filter) + Phase 7 (query expansion)
- [ ] Update PROJECT_MEMORY.md with findings
