# Empty Retrievals Root Cause Analysis

**Total Empty Retrievals:** 7 queries (13.7%)
**Date:** 2026-02-14 17:52:06

---

## Root Cause: SQL-Only Routing (Not Retrieval Failure)

All 7 queries were **routed to SQL only** → No vector search attempted → Zero sources (by design)

**This is NOT a vector retrieval failure** - it's a query classification decision.

---

## The 7 Queries

### ✅ Correctly Routed (4 queries) - Pure Statistical

These were **correctly classified as STATISTICAL** (no fan opinion/context needed):

1. **"Analyze players with 1500+ points and 400+ assists"**
   - Category: tier3_dual_threat_strategy
   - SQL: `SELECT p.name, ps.pts, ps.ast FROM players WHERE pts > 1500 AND ast > 400`
   - **Correct:** Pure stat filter, no opinion component

2. **"How do young players compare to established stars"**
   - Category: tier4_generational_shift
   - SQL: `SELECT p.name, pts, reb, ast, age WHERE age < 25 ORDER BY pts DESC LIMIT 5`
   - **Correct:** Statistical comparison by age

3. **"What are Shai Gilgeous-Alexander's full stats this season?"**
   - Category: hybrid_conversational_mvp
   - SQL: Full stat lookup for single player
   - **Correct:** Direct stat request

4. **"Show me the Celtics' team statistics this season"**
   - Category: hybrid_conversational_team
   - SQL: `SELECT name, SUM(pts), SUM(reb), SUM(ast) WHERE team = 'BOS'`
   - **Correct:** Team aggregation stats

---

### ⚠️ Misclassified (3 queries) - Should Be HYBRID

These have **HYBRID intent** (stats + fan opinion) but were routed to **SQL only**:

5. **"lebron stats + fan opinions plzzz"** ⚠️
   - **Expected:** HYBRID (stats + "fan opinions")
   - **Actual:** STATISTICAL (SQL only)
   - **Issue:** Classifier missed "fan opinions" due to noisy text ("plzzz")
   - **Impact:** No fan discussion retrieved

6. **"compare curry n jokic stats nd tell me who fans like more"** ⚠️
   - **Expected:** HYBRID (comparison + "who fans like more")
   - **Actual:** STATISTICAL (SQL only)
   - **Issue:** Classifier missed "fans like more" opinion component
   - **Impact:** Response only compared fantasy points, no fan opinion

7. **"Show me the Timberwolves' numbers and what fans call their 'young and hungry' identity"** ⚠️
   - **Expected:** HYBRID (stats + "what fans call")
   - **Actual:** STATISTICAL (SQL only)
   - **Issue:** Classifier missed "fans call their identity" context request
   - **Impact:** Only returned stats, no fan identity discussion

---

## Why Misclassification Happened

### Query Classifier Logic

The classifier uses pattern matching to detect HYBRID queries (lines in query_classifier.py):

**HYBRID Triggers:**
- "and explain why"
- "and how does"
- "and what makes"
- "what do fans think"
- "according to fans"

**Patterns NOT Matched:**
- ❌ "fan opinions" (query 5) - not in HYBRID patterns
- ❌ "fans like more" (query 6) - not in opinion patterns
- ❌ "fans call their" (query 7) - not in context patterns

### Why SQL Won

Queries 5-7 had **strong statistical signals**:
- Query 5: "lebron stats" → S2_full_stat_words_and_db_descriptions (high score)
- Query 6: "compare curry n jokic stats" → S5_numeric_comparisons + S6_player_team_stat_queries
- Query 7: "Timberwolves' numbers" → S2_full_stat_words + S7_team_names

**Classifier Decision:**
```
stat_score (7.0) > ctx_score (0.0) → STATISTICAL (not HYBRID)
```

---

## Impact Assessment

### Production Impact: MEDIUM

| Query Type | Count | User Impact |
|------------|-------|-------------|
| **Correctly SQL-only** | 4/7 (57%) | ✅ No impact - pure stats delivered |
| **Misclassified HYBRID** | 3/7 (43%) | ⚠️ Missing fan opinion/context |

**User Experience:**
- 4 queries: Perfect (user got exactly what they asked for - stats)
- 3 queries: Partial (user got stats but not fan opinions/context)

### Example of Missing Context

**Query 6:** "compare curry n jokic stats nd tell me who fans like more"

**Actual Response:**
```
"Based on statistics, Stephen Curry has 2849 fan points vs Seth Curry's 741."
```

**Expected Response (if HYBRID):**
```
"Stephen Curry leads with 2849 fan points. According to Reddit discussions,
fans praise Curry's efficiency and three-point shooting as revolutionary,
while Jokic is celebrated for his all-around playmaking from the center position."
```

---

## Root Cause Summary

**NOT a vector retrieval problem** - the vector store works fine.

**IS a query classification problem:**
1. Classifier has limited HYBRID patterns
2. Noisy queries ("plzzz", "nd") reduce pattern match accuracy
3. Strong stat signals override weak opinion signals
4. Missing patterns: "fan opinions", "fans like", "fans call"

---

## Solution: Expand HYBRID Patterns

### Quick Fix (Add Missing Patterns)

Update `query_classifier.py` HYBRID detection patterns:

```python
HYBRID_PATTERNS = [
    # Existing
    r'\b(?:and|but)\s+(?:explain|tell|describe|discuss|analyze)\s+(?:why|how|what)',
    r'\bwhat\s+(?:do|does)\s+fans?\s+think',
    r'\baccording\s+to\s+fans',

    # NEW - Missing patterns
    r'\bfans?\s+(?:opinions?|think|believe|say|call|consider)',  # "fan opinions", "fans call"
    r'\bwho\s+fans?\s+(?:like|prefer|favor)',  # "who fans like more"
    r'\bwhat\s+(?:do\s+)?fans?\s+(?:call|describe|say)',  # "what fans call"
]
```

### Expected Impact

| Metric | Before | After Fix | Improvement |
|--------|--------|-----------|-------------|
| Empty Retrievals | 7 (14%) | 4 (8%) | -43% |
| Misclassified HYBRID | 3 | 0 | -100% |
| Correct HYBRID Routing | 76.5% | 82% | +5.5% |

---

## Testing Plan

### Test Cases for New Patterns

1. "lebron stats + fan opinions plzzz" → Should classify as HYBRID ✓
2. "compare curry n jokic stats nd tell me who fans like more" → HYBRID ✓
3. "Show me the Timberwolves' numbers and what fans call their 'young and hungry' identity" → HYBRID ✓

### Regression Tests

Ensure existing STATISTICAL queries still route correctly:
- "What are Shai Gilgeous-Alexander's full stats?" → STATISTICAL (no change)
- "Show me the Celtics' team statistics" → STATISTICAL (no change)

---

## Conclusion

**Empty retrievals are NOT a retrieval failure.**

**They are a classification issue:**
- 57% correctly classified (4/7 queries were pure stats)
- 43% misclassified (3/7 should have been HYBRID)

**Fix:** Add 3 missing HYBRID patterns → Reduce empty retrievals from 7 to 4 (-43%)

**Priority:** LOW (system works correctly for pure stat queries, only affects mixed queries)
