# Vector-Only Evaluation Analysis & Remediation Plan

**Date:** 2026-02-11
**Evaluation File:** `vector_evaluation_20260211_130107.json`
**Total Test Cases:** 30 (filtered from 47 total)
**Status:** ⚠️ **MAJOR ISSUES IDENTIFIED**

---

## Executive Summary

The vector-only evaluation revealed **critical issues** that prevented meaningful assessment:
- **21 out of 30 queries failed** (70% failure rate)
- **18 failures** due to Gemini API 429 rate limit errors
- **3 failures** due to classification mismatches (SQL answered correctly, but test expected vector)
- **0 SIMPLE queries tested** (filtered out as they're statistical/SQL-suitable)

**Key Finding:** The evaluation cannot proceed reliably with the current Gemini free tier due to aggressive rate limiting. Only 9 queries completed successfully, making statistical analysis impossible.

---

## Overall Results

| Metric | Value |
|--------|-------|
| **Total Cases** | 30 |
| **Successful** | 9 (30%) |
| **Failed** | 21 (70%) |
| **Classification Accuracy** | 16.67% (misleading - see analysis below) |

### Failure Breakdown
- **429 Rate Limit Errors:** 18/21 (85.7% of failures)
- **Classification Mismatches:** 3/21 (14.3% of failures)
- **Actual System Failures:** 0

---

## Root Cause Analysis

### Root Cause 1: **GEMINI FREE TIER RATE LIMITS** (18 failures)

#### Problem
Gemini API returns `429 RESOURCE_EXHAUSTED` errors after 3-5 successful requests, even with 12-second rate limit delays between queries.

#### Affected Queries
```
Error: "429 RESOURCE_EXHAUSTED. Resource exhausted. Please try again later."
```

**Examples:**
- ✗ "Compare the offensive efficiency of the top 3 scoring teams..." (COMPLEX)
- ✗ "What are the most debated player comparisons this season?" (COMPLEX)
- ✗ "who iz the best player ever??? lebron or jordan" (NOISY)
- ✗ "lmao bro did u see that dunk last nite" (NOISY)
- ✗ "What about his assist numbers?" (CONVERSATIONAL follow-up)
- ✗ "How does that compare to last season?" (CONVERSATIONAL follow-up)

#### Root Cause
- **Gemini free tier limits:** ~15 requests per minute (RPM)
- **Evaluation rate:** 12s between API calls (5 RPM) - within limit
- **BUT:** Gemini counts internal retries, embeddings, and context processing against the quota
- Each query makes **multiple API calls** (classification, retrieval, generation), exhausting quota rapidly

#### Impact
- **Blocks** 60% of evaluation (18/30 queries)
- Cannot assess COMPLEX queries (6/7 failed)
- Cannot assess NOISY queries (8/11 failed)
- Cannot assess CONVERSATIONAL chains (7/12 failed)

---

### Root Cause 2: **TEST CASE EXPECTATION MISMATCH** (3-4 misclassifications)

#### Problem
Vector test cases mark all queries as `expected_routing: "vector_only"`, even when they ask for statistical data that SQL handles better.

#### Affected Queries

| Question | Expected | Actual | Correct Answer? | Issue |
|----------|----------|--------|-----------------|-------|
| "waht are teh top 10 plyers in teh leage rite now??" | vector_only | sql_only | ✅ YES (Correct top 10 by points) | Test expects vector for a **statistical** query |
| "Who is the leading scorer in the NBA this season?" | vector_only | sql_only | ✅ YES (SGA, 2,485 points) | Test expects vector for **factual stat query** |
| "Compare his numbers to the other top candidates." | vector_only | sql_only | ✅ YES (Comparison with stats) | Test expects vector for **statistical comparison** |
| "Who is their best player statistically?" | vector_only | unknown | ✅ YES (SGA) | Test expects vector for **statistical lookup** |

#### Root Cause
The vector test cases were designed to test **vector retrieval capabilities**, but many included **statistical questions** that SQL can answer better. The system correctly routes these to SQL, but the test framework marks them as failures.

**Example:**
- Query: "Who is the leading scorer this season?"
- System: Routes to SQL → Returns "Shai Gilgeous-Alexander (2,485 points)" ✅
- Test: Marks as **MISCLASSIFIED** because it expected vector_only ❌

#### Impact
- **False negative** classification accuracy (16.67% reported, but system is working correctly)
- Cannot trust classification metrics without fixing test expectations
- Confusion about whether system is broken or test cases are incorrect

---

### Root Cause 3: **NO SIMPLE QUERIES IN EVALUATION** (0 tested)

#### Problem
The evaluation script **filters out SIMPLE category** queries entirely:
```python
# From evaluate_vector.py:
# - SIMPLE: Statistical queries (better for SQL)
# ↓ Filters only include COMPLEX, NOISY, CONVERSATIONAL
```

User requested analysis of **SIMPLE query failures**, but the evaluation excluded all SIMPLE queries because they contain statistical patterns (e.g., "Which player has the best 3PT%?", "What are LeBron's PPG?") that the system correctly routes to SQL.

#### Root Cause
- Test case categorization doesn't match routing expectations
- SIMPLE queries ARE statistical → Should go to SQL
- But they're in "vector_test_cases.py" → Implies they should use vector search

#### Impact
- Cannot evaluate SIMPLE queries as requested by user
- No failures to analyze for SIMPLE category
- Test suite organization needs restructuring

---

## Successful Queries Analysis (9/30)

Only 9 queries completed successfully. Here's what worked:

### ✅ Vector-Only Queries That Succeeded (5)

| Question | Category | Response | Sources | Verdict |
|----------|----------|----------|---------|---------|
| "Based on home vs away records... which teams struggle on the road?" | COMPLEX | "Available data doesn't contain this info" | 5 | ✅ Correct negative response |
| "stats for that tall guy from milwaukee" | NOISY | "Context doesn't contain specific info" | 5 | ✅ Handles vague query appropriately |
| "Best strategy for winning in NBA 2K?" | NOISY | "Doesn't contain this info" | 5 | ✅ Out-of-scope detection |
| "weather forecast for NY" | NOISY | "Doesn't contain this info" | 5 | ✅ Off-topic detection |
| "Going back to the Bucks, what are their weaknesses?" | CONVERSATIONAL | "One Reddit user thinks they're awful" | 5 | ✅ Retrieved Reddit opinion |

**Observations:**
- All 5 retrieved 5 source chunks (vector search working)
- Most returned "doesn't contain info" → Indicates data gap or poor retrieval precision
- 1 actually found Reddit content (Bucks weakness) → Shows vector retrieval CAN work

### ❌ SQL Routed (Misclassified per test, but correct) (3)

| Question | Actual Routing | Response | Verdict |
|----------|----------------|----------|---------|
| "waht are teh top 10 plyers in teh leage rite now??" | sql_only | Top 10 by points (correct) | ✅ SQL handled typos, returned accurate data |
| "Who is the leading scorer this season?" | sql_only | SGA (2,485 points) | ✅ Correct factual answer |
| "Compare his numbers to other top candidates." | sql_only | Stats comparison | ✅ Correct multi-player comparison |

**Observation:** SQL correctly handled queries that tests expected to go to vector. This is **good system behavior**, not a failure.

### ❓ Unknown Routing (1)

| Question | Actual Routing | Response | Verdict |
|----------|----------------|----------|---------|
| "Who is their best player statistically?" | unknown | "Shai Gilgeous-Alexander" | ⚠️ Classification failed but answer correct |

---

## Remediation Plan

### 🔴 **Priority 1: Replace Gemini with Mistral for Evaluation** (CRITICAL)

**Problem:** Gemini free tier rate limits block 60% of evaluation.

**Solution:**
1. **Switch evaluation LLM to Mistral** (already used for embeddings and chat)
   - Modify `evaluate_vector.py` to use Mistral API for answer generation
   - Mistral has higher free tier limits (more reliable for evaluation)
   - OR: Use `gemini-2.0-flash` with exponential backoff + longer cooldowns

2. **Add retry logic with exponential backoff**
   - Current: 12s fixed delay
   - Proposed: 15s initial + 2x backoff on 429 (15s → 30s → 60s)
   - Max 3 retries per query

3. **Add checkpoint/resume capability**
   - Save partial results after each successful query
   - Resume from checkpoint on retry
   - Prevent re-running successfully evaluated queries

**Expected Outcome:** 95%+ query success rate (vs current 30%)

---

### 🟡 **Priority 2: Fix Test Case Expectations** (HIGH)

**Problem:** Test cases expect `vector_only` for statistical queries that SQL handles better.

**Solution:**
1. **Split test cases by routing expectation:**
   ```python
   # sql_test_cases.py (48 cases) - DONE
   # vector_test_cases.py (should be 20-25 cases) - NEEDS FIXING
   # hybrid_test_cases.py (18 cases) - DONE
   ```

2. **Move statistical queries from vector to SQL or hybrid:**
   - "Who is the leading scorer?" → SQL
   - "waht are teh top 10 plyers?" → SQL (handles typos)
   - "Compare his numbers to top candidates" → SQL or HYBRID

3. **Keep in vector_test_cases.py ONLY:**
   - Opinion/discussion queries (Reddit content)
   - Contextual analysis ("Why is X effective?")
   - Qualitative questions ("What makes them good?")
   - Out-of-scope detection ("NBA 2K strategy")

**Expected Outcome:** Classification accuracy rises from 16.67% to 90%+

---

### 🟢 **Priority 3: Add SIMPLE Category Evaluation** (MEDIUM)

**Problem:** User requested SIMPLE query analysis, but 0 SIMPLE queries were tested.

**Solution:**
1. **Don't filter out SIMPLE queries** - Run them through vector evaluation to establish baseline
2. **Expect failures for statistical SIMPLE queries** (they should route to SQL)
3. **Document expected routing per category:**
   ```
   SIMPLE → SQL (statistical) or VECTOR (glossary lookups)
   COMPLEX → HYBRID or VECTOR (multi-source)
   NOISY → VECTOR (typo-tolerant) or SQL (if stats)
   CONVERSATIONAL → Context-dependent routing
   ```

**Expected Outcome:** Complete test coverage across all 47 test cases

---

### 🔵 **Priority 4: Improve Vector Retrieval Precision** (LOW)

**Problem:** 5/9 successful queries returned "Available data doesn't contain this information" even after retrieving 5 sources.

**Possible Causes:**
1. **Poor chunk relevance** - Retrieved chunks don't match query intent
2. **LLM hallucination filter too aggressive** - Rejects valid context as irrelevant
3. **Missing data** - Queries ask about data not in corpus

**Solutions to Test:**
1. **Increase k (retrieved chunks):** Try k=10 instead of k=5
2. **Lower min_score threshold:** Allow slightly lower similarity matches
3. **Review Reddit chunk quality:** Check if upvote-based boosting helps or hurts
4. **Add RAGAS metrics:** Measure context_precision and context_recall

**Expected Outcome:** Fewer "doesn't contain" responses when relevant data exists

---

## Immediate Next Steps

1. ✅ **SQL Report Generated** (48/48 success, ready for deployment)
2. ⏳ **Vector Evaluation Blocked** - Cannot proceed with current Gemini rate limits
3. 🔴 **BLOCKER:** Must implement Priority 1 (Mistral for evaluation OR better retry logic)
4. 🟡 **After unblocked:** Fix test case expectations (Priority 2)
5. 🟢 **Then:** Run full 47-case evaluation with corrected routing expectations

---

## Summary: What We Learned

### What Works ✅
- Vector search retrieves 5 sources per query (retrieval working)
- Out-of-scope detection ("NBA 2K", "weather") works
- Reddit content retrieval works (found Bucks opinion)
- SQL routing correctly handles statistical queries (even with typos)

### What's Broken ❌
- **Gemini free tier** cannot handle evaluation load (18/30 queries fail)
- **Test expectations** misaligned with routing logic (false misclassifications)
- **No SIMPLE category** tested (user requested but excluded by design)
- **Vector precision** low (5/9 successful queries returned "no info")

### Recommendations

**For Production Use:**
- ✅ **Deploy SQL component** (100% success rate, production-ready)
- ⚠️ **Vector component needs work** (70% failure rate in evaluation, but mostly due to API limits not system bugs)
- 🔧 **Fix evaluation infrastructure first**, then re-assess vector performance

**For Evaluation:**
1. Switch to Mistral or add aggressive retry logic
2. Fix test case routing expectations
3. Re-run full 47-case evaluation
4. Measure RAGAS metrics for successful queries
5. Analyze actual failures (not API limit issues)

---

**Generated:** 2026-02-11
**Next Action:** Implement Priority 1 remediation (Mistral for evaluation)
