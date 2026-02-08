# Vector-Only Evaluation Results - Full Test Suite
**Evaluation Date:** February 9, 2026
**Duration:** 262.9 seconds (4.4 minutes)
**Test Cases:** 47 (All test cases)
**Configuration:** FAISS + Mistral Embeddings (Vector-only, NO SQL/Hybrid)

---

## Executive Summary

This evaluation tests the baseline performance of pure vector search (FAISS + Mistral embeddings) without any SQL database fallback or hybrid capabilities. The system retrieved context using semantic similarity search (k=5) and generated responses using Gemini 2.0 Flash Lite.

### Key Findings
- **Overall Faithfulness:** 55.7% - Moderate accuracy, many hallucinations
- **Answer Relevancy:** 23.7% - **CRITICAL ISSUE** - Very low relevancy scores
- **Context Precision:** 74.1% - Good at finding relevant documents
- **Context Recall:** 69.1% - Decent coverage of ground truth information
- **Failure Rate:** 72.3% (34/47 queries failed with faith<0.5 or rel<0.5)

**Critical Problem:** The extremely low answer relevancy (23.7%) indicates that while the system finds relevant documents, the generated responses are often not properly addressing the user's questions.

---

## Overall Metrics

| Metric | Score | Grade |
|--------|-------|-------|
| Faithfulness | 0.557 | D+ |
| Answer Relevancy | 0.237 | F |
| Context Precision | 0.741 | C+ |
| Context Recall | 0.691 | C |

---

## Category Breakdown

### 1. SIMPLE Queries (12 samples)
Direct factual questions requiring single-hop retrieval.

| Metric | Score | Performance |
|--------|-------|-------------|
| Faithfulness | 0.514 | Poor - Frequent hallucinations |
| Answer Relevancy | 0.268 | Very Low |
| Context Precision | 0.829 | Good - Finds relevant docs |
| Context Recall | 0.750 | Good |

**Key Issues:**
- 9/12 queries failed (75% failure rate)
- Model often states "data not available" even when context contains the answer
- Hallucinations in factual responses (e.g., LeBron's PPG stated as 25.6 when actual value differs)

**Example Failures:**
1. **"What are LeBron James' average points per game this season?"**
   - Response: "25.6"
   - Faithfulness: 0.0 (hallucination)
   - Relevancy: 0.997 (response format was good, but data wrong)

2. **"Which player has the best 3-point percentage over the last 5 games?"**
   - Response: "I do not have the data for the last 5 games"
   - Faithfulness: 0.0
   - Relevancy: 0.0

### 2. COMPLEX Queries (12 samples)
Multi-step reasoning, comparisons, and analytical questions.

| Metric | Score | Performance |
|--------|-------|-------------|
| Faithfulness | 0.653 | Fair |
| Answer Relevancy | 0.217 | Very Low |
| Context Precision | 0.595 | Mediocre |
| Context Recall | 0.542 | Mediocre |

**Key Issues:**
- 9/12 queries failed (75% failure rate)
- Struggles with multi-faceted analysis
- Missing data for advanced analytics (salaries, injury reports, trade data)
- One query hit Gemini rate limit (429 error)

**Example Failures:**
1. **"Analyze the correlation between a team's pace of play and their defensive rating"**
   - Response: "Context does not contain necessary information"
   - Faithfulness: 0.0
   - Relevancy: 0.0
   - Issue: Requires structured team-level data

2. **"Evaluate trade deadline moves this season"**
   - Response: "[ERROR: 429 RESOURCE_EXHAUSTED...]"
   - Faithfulness: 0.0
   - Relevancy: 0.0

### 3. NOISY Queries (11 samples)
Queries with typos, slang, out-of-scope questions, or malformed input.

| Metric | Score | Performance |
|--------|-------|-------------|
| Faithfulness | 0.698 | **BEST CATEGORY** |
| Answer Relevancy | 0.264 | Low |
| Context Precision | 0.796 | Good |
| Context Recall | 0.955 | **EXCELLENT** |

**Surprising Result:** NOISY queries performed BEST for faithfulness and context recall!

**Key Insights:**
- 7/11 queries failed (64% failure rate - lowest among all categories)
- Model handles typos and slang reasonably well
- Properly rejects out-of-scope questions (weather, NBA 2K, XSS attacks)
- Context retrieval is very effective even with noisy input

**Example Successes:**
1. **"waht are teh top 10 plyers in teh leage rite now??"** (typos)
   - Response: Listed top 10 by points scored with accurate data
   - Faithfulness: 0.952
   - Relevancy: 0.756

2. **"stats for that tall guy from milwaukee"** (vague reference)
   - Response: Provided Chris Livingston stats (MIL player)
   - Faithfulness: 1.0
   - Relevancy: 0.711

3. **"<script>alert('xss')</script> SELECT * FROM players"** (malicious)
   - Response: "Unable to execute JavaScript code and SQL query"
   - Faithfulness: 0.5
   - Properly handled security threat

### 4. CONVERSATIONAL Queries (12 samples)
Follow-up questions requiring context from previous queries.

| Metric | Score | Performance |
|--------|-------|-------------|
| Faithfulness | 0.375 | **WORST CATEGORY** |
| Answer Relevancy | 0.202 | Very Low |
| Context Precision | 0.749 | Good |
| Context Recall | 0.542 | Mediocre |

**Key Issues:**
- 9/12 queries failed (75% failure rate)
- **No conversation context:** Each query evaluated independently without previous message history
- Follow-up questions fail due to missing references ("his", "they", "that")
- This is expected given the evaluation methodology

**Example Failures:**
1. **"What about his assist numbers?"** (follow-up)
   - Response: "I do not have enough information... I do not have the assists numbers"
   - Faithfulness: 0.0
   - Issue: No reference to who "his" refers to

2. **"Which team does Giannis play for?"**
   - Response: "Context does not contain information about which team Giannis plays for"
   - Faithfulness: 0.0
   - **Issue:** This is a simple factual question that should work!

---

## Top 5 Failure Cases

### 1. "Which player has the best 3-point percentage over the last 5 games?"
- **Category:** SIMPLE
- **Faithfulness:** 0.0 | **Relevancy:** 0.0
- **Response:** "I do not have the data for the last 5 games"
- **Issue:** Temporal data not available in vector store

### 2. "What are LeBron James' average points per game this season?"
- **Category:** SIMPLE
- **Faithfulness:** 0.0 | **Relevancy:** 0.997
- **Response:** "25.6"
- **Issue:** Hallucination - provided incorrect data with high confidence

### 3. "Which player leads the league in steals per game?"
- **Category:** SIMPLE
- **Faithfulness:** 0.0 | **Relevancy:** 0.0
- **Response:** "Data does not contain steals per game for each player"
- **Issue:** Specific stat not in retrieved context

### 4. "Analyze the correlation between a team's pace of play and their defensive rating"
- **Category:** COMPLEX
- **Faithfulness:** 0.0 | **Relevancy:** 0.0
- **Response:** "Context does not contain necessary information"
- **Issue:** Requires team-level aggregated data with multiple metrics

### 5. "Evaluate the trade deadline moves this season"
- **Category:** COMPLEX
- **Faithfulness:** 0.0 | **Relevancy:** 0.0
- **Response:** "[ERROR: 429 RESOURCE_EXHAUSTED...]"
- **Issue:** Gemini API rate limit hit during response generation

---

## Key Patterns in Failures

### 1. Data Availability Issues (Most Common)
**Pattern:** Model correctly identifies missing information
- Player stats over "last 5 games" (temporal filtering)
- Team-level aggregated statistics
- Salary data
- Injury reports
- Trade history
- MVP award winners
- Attendance figures

**Recommendation:** Needs SQL database with structured tables for:
- Player stats with game-level granularity
- Team statistics
- Historical awards/accolades
- Transaction/trade data

### 2. Hallucinations (Critical)
**Pattern:** Model provides incorrect data with high confidence
- LeBron's PPG stated as "25.6" (wrong value)
- Claims Giannis has "791 assists" (most in league)
- Incorrect attributions

**Recommendation:**
- Enforce citation requirements in prompts
- Add confidence scoring
- Implement fact-checking layer

### 3. Conversational Context Loss (Expected)
**Pattern:** Follow-up questions fail due to missing references
- "What about his assist numbers?" → No "his" reference
- "How are they doing in the standings?" → No "they" reference

**This is by design:** Each test case is evaluated independently.

### 4. Response Relevancy Problem (Critical)
**Pattern:** Even when context is good, responses don't properly address questions
- Average relevancy of only 23.7% across all queries
- Context Precision is 74.1% but Answer Relevancy is 23.7%
- **Gap indicates prompt engineering issue or model instruction-following problem**

**Recommendation:**
- Review prompt templates
- Add explicit instruction to directly answer the question
- Consider chain-of-thought reasoning

### 5. Team-Level Queries Fail
**Pattern:** Questions about teams (vs. individual players) consistently fail
- "Which team leads the league in rebounds?"
- "Which team has best win-loss record?"
- "Teams most dependent on single player"

**Recommendation:** SQL database with team-aggregated statistics

---

## Successes

Despite the low overall scores, some queries performed well:

### High-Performing Queries:

1. **"What is Stephen Curry's free throw percentage this season?"**
   - Faithfulness: 1.0 | Relevancy: 0.732
   - Response: "93.3%"
   - Clean, accurate, factual

2. **"How many points per game does Nikola Jokic average?"**
   - Faithfulness: 1.0 | Relevancy: 0.664
   - Response: "20.6"
   - Direct stat retrieval

3. **"Which players have shown the most improvement in shooting percentages?"**
   - Faithfulness: 1.0 | Relevancy: 0.893
   - Retrieved Reddit discussion context and provided specific player examples

4. **"waht are teh top 10 plyers in teh leage rite now??"** (NOISY)
   - Faithfulness: 0.952 | Relevancy: 0.756
   - Handled typos perfectly, provided ranked list

5. **"How do advanced analytics compare between MVP candidates?"**
   - Faithfulness: 0.970 | Relevancy: 0.887
   - Provided detailed PER/WS/VORP comparison with statistical arguments

**Pattern:** Queries succeed when:
- Single player stat lookup (specific value in context)
- Information is explicitly stated in retrieved documents
- Question maps cleanly to document content

---

## Comparison: Vector-Only vs. Expected Hybrid Performance

### Current Vector-Only Baseline:
- Faithfulness: 0.557
- Answer Relevancy: 0.237
- Works for: Simple stat lookups, qualitative discussions
- Fails for: Aggregations, comparisons, temporal queries, team stats

### Expected Improvements with SQL Hybrid:
Based on Phase 10 subset results (hybrid approach), we expect:
- Faithfulness: ~0.75-0.85 (+35-53%)
- Answer Relevancy: ~0.65-0.75 (+174-216%)
- Complex query success rate: ~60-70% (vs. current 25%)

**SQL would enable:**
- Player stat comparisons across the league
- Team-level aggregations
- Temporal filtering ("last 5 games", "this season")
- Structured data queries (rankings, leaders, etc.)

---

## Technical Notes

### Performance:
- Total runtime: 262.9 seconds for 47 queries
- Average: 5.6 seconds per query
- Includes: Query expansion, embedding generation, FAISS search, LLM response, RAGAS evaluation

### Rate Limiting:
- Encountered 1 Mistral embedding API rate limit (429) during evaluation
- Encountered 1 Gemini generation rate limit (429) during response generation
- Auto-retry logic successfully handled most rate limits
- Recommended: Add exponential backoff delays (0.5s between queries)

### Search Configuration:
- k=5 documents retrieved per query
- Query expansion enabled (adds synonyms/related terms)
- FAISS index: 255 vectors total
- Embedding model: mistral-embed

### Response Generation:
- Model: Gemini 2.0 Flash Lite
- Temperature: Not specified (likely default)
- Prompt: Simple template without citations or strict instructions

---

## Recommendations

### Immediate Actions (High Priority):

1. **Fix Answer Relevancy (CRITICAL)**
   - Current: 23.7% → Target: >60%
   - Action: Revise prompt templates to enforce direct question answering
   - Add explicit instruction: "Answer the exact question asked"
   - Consider adding few-shot examples

2. **Enable SQL Hybrid Mode**
   - Implement query classification (vector vs. SQL)
   - Add SQL fallback for aggregations, comparisons, team stats
   - Expected improvement: +35% faithfulness, +200% relevancy

3. **Prevent Hallucinations**
   - Enforce citation requirements in prompts
   - Add confidence thresholds
   - When uncertain, return "Data not available" instead of guessing

### Medium Priority:

4. **Expand Knowledge Base**
   - Add missing data: awards, attendance, salaries, trades
   - Improve temporal coverage (game-by-game logs)
   - Add team-level aggregated statistics

5. **Improve Conversational Handling**
   - Implement conversation state management
   - Add co-reference resolution ("his" → "LeBron James")
   - Maintain context window for follow-ups

6. **Optimize Vector Search**
   - Test different k values (currently k=5)
   - Experiment with re-ranking
   - Consider hybrid retrieval (dense + sparse)

### Low Priority:

7. **Rate Limit Handling**
   - Implement exponential backoff
   - Add request queuing
   - Cache embeddings for repeated queries

8. **Evaluation Methodology**
   - Add human evaluation for answer quality
   - Test with conversation context for conversational queries
   - Benchmark against GPT-4/Claude baselines

---

## Conclusion

The vector-only baseline demonstrates **moderate context retrieval capabilities (74.1% precision, 69.1% recall)** but suffers from **critically low answer relevancy (23.7%)** and **frequent failures (72.3% failure rate)**.

**Primary Issues:**
1. Response generation quality - answers don't properly address questions
2. Missing structured data for aggregations and comparisons
3. Hallucinations when confident responses are expected

**Next Steps:**
1. Revise prompts to dramatically improve answer relevancy (target: 3x improvement)
2. Enable SQL hybrid mode for structured queries
3. Implement citation enforcement to reduce hallucinations

The system shows promise for qualitative questions and discussions (especially handling noisy input surprisingly well), but requires significant improvements in structured data access and response generation quality to be production-ready.

---

**Full results available in:** `evaluation_results/vector_only_full_20260209_023719.json`
