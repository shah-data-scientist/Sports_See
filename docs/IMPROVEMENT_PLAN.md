# Consolidated Improvement Plan
**Based on 3 Comprehensive Evaluations (131 Queries)**

**Date:** 2026-02-09
**Target:** Improve overall success rate from 38.2% → 75%+

---

## Priority 0: Critical Prompt Engineering Fixes (IMMEDIATE)

### Impact: +40-50% Success Rate
### Effort: Low (2-4 hours)
### Target Completion: Today

---

### **Fix 1: Force LLM to Use Retrieved Data**

#### Problem
- Context precision 74%, but answer relevancy only 24%
- SQL accuracy 86%, but LLM says "cannot find information"
- Vector retrieval 69%, but usage only 6%

#### Solution
Update system prompt to **require explicit data usage**:

**File:** `src/services/chat.py`
**Location:** `SYSTEM_PROMPT_TEMPLATE` constant (around line 30-80)

#### Current Problematic Prompt
```python
SYSTEM_PROMPT_TEMPLATE = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

CRITICAL INSTRUCTIONS:
- Answer ONLY using information from the CONTEXT above
- Be factual, concise, and helpful
- If information is missing, briefly state so

ANSWER:"""
```

#### New Improved Prompt (Version 1: Mandatory Data Usage)
```python
SYSTEM_PROMPT_TEMPLATE = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

CRITICAL INSTRUCTIONS:
1. **EXAMINE the CONTEXT above carefully** - it contains the data needed to answer
2. **EXTRACT specific facts** from the context (numbers, names, statistics)
3. **CITE your sources** - reference where you found each fact
4. **If truly no relevant data exists**, say: "The available data doesn't contain information about [specific aspect]"
5. **NEVER guess or infer** - only state what's explicitly in the context

FORMAT YOUR ANSWER:
- Start with the direct answer
- Include specific data points from the context
- Cite sources in [brackets]
- Be concise but complete

ANSWER:"""
```

#### Testing
```bash
# After implementing, re-run vector-only evaluation
poetry run python scripts/evaluate_vector_only_full.py

# Expected improvement:
# - Answer Relevancy: 23.7% → 55%+
# - Overall Success: 27.7% → 60%+
```

---

### **Fix 2: Add Hybrid Query Synthesis Instructions**

#### Problem
- SQL returns correct stats (86% accuracy)
- Vector retrieves context (69% rate)
- LLM only uses SQL, ignores vector (6% vector usage)

#### Solution
Create **query-type-specific prompts**:

**File:** `src/services/chat.py`
**Add new prompt templates:**

```python
# For SQL-only queries (simple stats)
SQL_ONLY_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

SQL QUERY RESULTS:
---
{sql_results}
---

USER QUESTION:
{question}

INSTRUCTIONS:
1. **READ the SQL results above** - they contain the exact answer
2. **EXTRACT the relevant data** from the results
3. **FORMAT clearly** - present numbers in a readable way
4. If asking for COUNT/AVG/SUM, state the numeric result directly

IMPORTANT: The SQL results ALWAYS contain the answer. Never say "data not available" if results are present.

ANSWER:"""

# For HYBRID queries (stats + context)
HYBRID_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant with two data sources:

{conversation_history}

SQL QUERY RESULTS (Statistical Data):
---
{sql_results}
---

CONTEXTUAL KNOWLEDGE (Analysis & Insights):
---
{context}
---

USER QUESTION:
{question}

INSTRUCTIONS FOR HYBRID ANSWERS:
1. **START with the STATISTICAL answer** from SQL results (WHAT the numbers are)
2. **ADD CONTEXTUAL ANALYSIS** from the contextual knowledge (WHY/HOW it matters)
3. **BLEND both components** - connect stats to analysis with transition words
4. **CITE sources** - [SQL: ...] for stats, [Context: ...] for insights

EXAMPLE FORMAT:
"LeBron James scored 1,708 points this season [SQL]. His scoring comes from a mix of drives to the basket and perimeter shooting, making him a versatile offensive threat [Context: ESPN Analysis]."

YOUR ANSWER (combine stats + context):"""

# For CONTEXTUAL-only queries (qualitative)
CONTEXTUAL_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

INSTRUCTIONS:
1. **ANALYZE the context** provided above
2. **SYNTHESIZE insights** from multiple sources if available
3. **CITE specific sources** when making claims
4. Focus on qualitative analysis (playing style, strategy, impact)

ANSWER:"""
```

#### Implementation Steps

**Step 1:** Update `ChatService.chat()` method to select prompt based on query type:

```python
# File: src/services/chat.py
# In ChatService.chat() method (around line 200-300)

def chat(self, request: ChatRequest) -> ChatResponse:
    """Process chat request with query-type-specific prompts."""

    # ... existing code ...

    # Classify query
    classification = self._classifier.classify(request.query)

    # Choose prompt template based on classification
    if classification.query_type == QueryType.SQL_ONLY:
        prompt_template = SQL_ONLY_PROMPT
    elif classification.query_type == QueryType.HYBRID:
        prompt_template = HYBRID_PROMPT
    elif classification.query_type == QueryType.CONTEXTUAL:
        prompt_template = CONTEXTUAL_PROMPT
    else:
        prompt_template = SYSTEM_PROMPT_TEMPLATE  # fallback

    # Build conversation context if conversation_id provided
    conversation_history = ""
    if request.conversation_id:
        conversation_history = self._build_conversation_context(
            request.conversation_id, request.turn_number
        )

    # For SQL/HYBRID queries, execute SQL first
    sql_results_text = ""
    if classification.query_type in [QueryType.SQL_ONLY, QueryType.HYBRID]:
        sql_result = self._execute_sql_query(request.query)
        if sql_result.results:
            sql_results_text = self._format_sql_results(sql_result.results)

    # For CONTEXTUAL/HYBRID queries, retrieve vector context
    context_text = ""
    if classification.query_type in [QueryType.CONTEXTUAL, QueryType.HYBRID]:
        chunks = self._retrieve_context(request.query, k=request.k)
        context_text = self._format_context(chunks)

    # Generate response with appropriate prompt
    answer = self.generate_response(
        query=request.query,
        context=context_text,
        sql_results=sql_results_text,
        conversation_history=conversation_history,
        prompt_template=prompt_template,
    )

    # ... rest of method ...
```

**Step 2:** Add helper method to format SQL results clearly:

```python
def _format_sql_results(self, results: list[dict]) -> str:
    """Format SQL results for LLM consumption.

    Args:
        results: List of dictionaries from SQL query

    Returns:
        Formatted string for prompt injection
    """
    if not results:
        return "No results found."

    # Single result (e.g., COUNT, AVG)
    if len(results) == 1 and len(results[0]) == 1:
        key, value = list(results[0].items())[0]
        return f"Result: {value}"

    # Multiple results
    formatted_lines = []
    for i, row in enumerate(results[:20], 1):  # Limit to top 20
        row_text = ", ".join(f"{k}: {v}" for k, v in row.items())
        formatted_lines.append(f"{i}. {row_text}")

    if len(results) > 20:
        formatted_lines.append(f"... and {len(results) - 20} more results")

    return f"Found {len(results)} matching records:\n" + "\n".join(formatted_lines)
```

#### Testing
```bash
# After implementing, re-run evaluations
poetry run python scripts/evaluate_sql_hybrid.py
poetry run python scripts/evaluate_hybrid_queries.py

# Expected improvements:
# SQL Hybrid: 63.2% → 80%+ (fix LLM result extraction)
# Hybrid Integration: 40.6% → 75%+ (fix vector usage from 6% → 80%)
```

---

### **Fix 3: Enforce Citation Requirements to Prevent Hallucinations**

#### Problem
- 9/47 vector-only queries hallucinated data
- Example: Claims "LeBron averages 25.6 PPG" with 0.0 faithfulness
- No source attribution makes fabrications undetectable

#### Solution
**Add citation enforcement** to all prompts:

```python
# Add to ALL prompt templates:

CITATION_REQUIREMENT = """
**CITATION RULES:**
- Every factual claim MUST include a source citation
- Format: "LeBron scored 1708 points [SQL: player_stats table]"
- If you cannot cite a source, DO NOT make the claim
- When uncertain, say: "The available data doesn't specify this"
"""

# Example updated SYSTEM_PROMPT_TEMPLATE:
SYSTEM_PROMPT_TEMPLATE = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

CRITICAL INSTRUCTIONS:
1. **EXAMINE the CONTEXT above carefully** - it contains the data needed to answer
2. **EXTRACT specific facts** from the context (numbers, names, statistics)
3. **CITE your sources** - reference where you found each fact using [Source: ...] format
4. **If truly no relevant data exists**, say: "The available data doesn't contain information about [specific aspect]"
5. **NEVER guess or infer** - only state what's explicitly in the context

{citation_requirement}

FORMAT YOUR ANSWER:
- Start with the direct answer
- Include specific data points from the context with citations
- Be concise but complete

ANSWER:"""
```

#### Implementation
Add `citation_requirement=CITATION_REQUIREMENT` to all prompt template `.format()` calls.

#### Testing
```bash
# Verify citations present in responses
poetry run python tests/test_chat_service.py -k citation

# Expected: Hallucinations reduced from 9/47 → 0-2/47
```

---

## Priority 1: QueryClassifier Improvements (HIGH)

### Impact: +15-20% Success Rate
### Effort: Medium (4-6 hours)
### Target Completion: This Week

---

### **Fix 4: Add Hybrid Query Pattern Matching**

#### Problem
- 4/16 hybrid queries misclassified (25% error rate)
- Queries with "and explain", "what makes", "why is", "impact" should be HYBRID
- Current classifier only looks at nouns (player names, stats)

#### Solution
**Enhance QueryClassifier with keyword patterns:**

**File:** `src/services/query_classifier.py`
**Add to `classify()` method:**

```python
class QueryClassifier:
    """Enhanced query classifier with hybrid pattern detection."""

    # Add class-level patterns
    HYBRID_INDICATORS = {
        "explanation": ["why", "what makes", "how does", "explain", "what causes"],
        "impact": ["impact", "effect", "affect", "influence", "contribute"],
        "comparison_qualitative": ["compare.*styles", "difference between.*approaches",
                                   "versus.*playing", "better.*and why"],
        "analysis": ["analyze", "evaluate", "assess", "break down", "in-depth"],
    }

    SQL_STATS_KEYWORDS = {
        "aggregation": ["average", "total", "sum", "count", "how many", "top", "most", "least"],
        "ranking": ["best", "worst", "highest", "lowest", "leader", "leading"],
        "comparison_quantitative": ["more than", "less than", "greater", "compare.*stats"],
        "filtering": ["above", "below", "over", "under", "at least", "minimum", "maximum"],
    }

    def classify(self, query: str) -> QueryClassification:
        """Classify query with improved hybrid detection."""
        query_lower = query.lower()

        # Check for hybrid indicators
        has_hybrid_keyword = any(
            any(re.search(pattern, query_lower) for pattern in patterns)
            for patterns in self.HYBRID_INDICATORS.values()
        )

        # Check for SQL stats keywords
        has_sql_keyword = any(
            any(keyword in query_lower for keyword in keywords)
            for keywords in self.SQL_STATS_KEYWORDS.values()
        )

        # Classification logic
        if has_hybrid_keyword and has_sql_keyword:
            # "Top scorers AND explain their playing styles" → HYBRID
            return QueryClassification(
                query_type=QueryType.HYBRID,
                confidence=0.9,
                reasoning="Contains both statistical request and contextual analysis request"
            )
        elif has_hybrid_keyword and not has_sql_keyword:
            # "Explain LeBron's playing style" → CONTEXTUAL
            return QueryClassification(
                query_type=QueryType.CONTEXTUAL,
                confidence=0.85,
                reasoning="Requests qualitative analysis without specific stats"
            )
        elif has_sql_keyword and not has_hybrid_keyword:
            # "Who has the most points?" → SQL_ONLY
            return QueryClassification(
                query_type=QueryType.SQL_ONLY,
                confidence=0.9,
                reasoning="Requests specific statistical data"
            )
        else:
            # Ambiguous - default to CONTEXTUAL
            return QueryClassification(
                query_type=QueryType.CONTEXTUAL,
                confidence=0.6,
                reasoning="No clear statistical or analytical keywords"
            )
```

#### Test Cases
Add to `tests/test_query_classifier.py`:

```python
def test_hybrid_query_detection():
    """Test that hybrid queries are correctly classified."""
    classifier = QueryClassifier()

    hybrid_queries = [
        "Who are the top rebounders and what impact do they have on their teams?",
        "Most efficient scorers and what makes them efficient?",
        "Compare LeBron and Durant's scoring and explain their styles",
        "Top defenders and analyze their defensive strategies",
    ]

    for query in hybrid_queries:
        result = classifier.classify(query)
        assert result.query_type == QueryType.HYBRID, \
            f"Query '{query}' should be HYBRID, got {result.query_type}"
```

#### Testing
```bash
poetry run pytest tests/test_query_classifier.py -v

# Expected: All 4 previously misclassified queries now correct
```

---

## Priority 2: SQL Result Extraction (MEDIUM)

### Impact: +10% SQL Success Rate
### Effort: Medium (3-4 hours)
### Target Completion: This Week

---

### **Fix 5: Handle Scalar SQL Results**

#### Problem
- COUNT, AVG, SUM queries fail 48% of the time
- SQL executes correctly but LLM can't extract single number result
- Example: `SELECT COUNT(*) FROM...` returns 15, LLM says "unavailable"

#### Solution
**Special handling for scalar results:**

**File:** `src/services/chat.py`
**Update `_format_sql_results()` method:**

```python
def _format_sql_results(self, results: list[dict]) -> str:
    """Format SQL results with special handling for aggregations."""
    if not results:
        return "No results found."

    # SPECIAL CASE 1: Single scalar result (COUNT, AVG, SUM)
    if len(results) == 1 and len(results[0]) == 1:
        key, value = list(results[0].items())[0]

        # Format based on aggregation type
        if "count" in key.lower():
            return f"COUNT Result: {value} (total number of records matching the criteria)"
        elif "avg" in key.lower() or "average" in key.lower():
            return f"AVERAGE Result: {value:.2f}"
        elif "sum" in key.lower() or "total" in key.lower():
            return f"SUM/TOTAL Result: {value}"
        elif "max" in key.lower() or "maximum" in key.lower():
            return f"MAXIMUM Result: {value}"
        elif "min" in key.lower() or "minimum" in key.lower():
            return f"MINIMUM Result: {value}"
        else:
            return f"Result: {value}"

    # SPECIAL CASE 2: Single record (player lookup)
    if len(results) == 1:
        row = results[0]
        row_text = "\n".join(f"  • {k}: {v}" for k, v in row.items())
        return f"Found 1 matching record:\n{row_text}"

    # GENERAL CASE: Multiple records
    formatted_lines = [f"Found {len(results)} matching records:\n"]
    for i, row in enumerate(results[:20], 1):
        row_text = ", ".join(f"{k}: {v}" for k, v in row.items())
        formatted_lines.append(f"{i}. {row_text}")

    if len(results) > 20:
        formatted_lines.append(f"\n... and {len(results) - 20} more results")

    return "\n".join(formatted_lines)
```

#### Updated SQL_ONLY_PROMPT
```python
SQL_ONLY_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

SQL QUERY RESULTS:
---
{sql_results}
---

USER QUESTION:
{question}

INSTRUCTIONS:
1. **READ the SQL results above** - they contain the exact answer
2. **EXTRACT the relevant data** from the results:
   - If you see "COUNT Result: X" → answer with the number X
   - If you see "AVERAGE Result: X" → answer with the average X
   - If you see a list of records → summarize or list them
3. **FORMAT clearly** - present numbers in a readable way

CRITICAL: The SQL results section ALWAYS contains the answer if it exists.
Never say "data not available" or "I cannot find this information" if the SQL results section shows data.

ANSWER:"""
```

#### Testing
```bash
# Test scalar result extraction
poetry run python -c "
from src.services.chat import ChatService
service = ChatService(enable_sql=True)
service.ensure_ready()

# Test COUNT query
response = service.chat(ChatRequest(query='How many players have more than 500 assists?'))
print(response.answer)
# Expected: Should state the number (e.g., '15 players')

# Test AVG query
response = service.chat(ChatRequest(query='What is the average points per game?'))
print(response.answer)
# Expected: Should state the average (e.g., '18.7 points per game')
"
```

---

## Priority 2: Conversation Memory Integration (MEDIUM)

### Impact: +10-15% Conversational Success
### Effort: Low (2-3 hours) - Feature already implemented!
### Target Completion: This Week

---

### **Fix 6: Integrate Conversation Memory into Evaluations**

#### Current State
- Conversation history feature **already implemented** (Phases 1-6 complete)
- But **not used in evaluations** (all eval scripts run stateless)
- Would fix 9/47 vector-only failures (19%) and 1/68 SQL failures (1.5%)

#### Solution
**Update evaluation scripts to use conversations:**

**File:** `scripts/evaluate_with_conversation.py` (NEW)

```python
"""
FILE: evaluate_with_conversation.py
STATUS: Active
RESPONSIBILITY: Re-run evaluations with conversation context enabled
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import tempfile
from pathlib import Path
from src.models.chat import ChatRequest
from src.repositories.conversation import ConversationRepository
from src.repositories.feedback import FeedbackRepository
from src.services.chat import ChatService
from src.services.conversation import ConversationService
from src.evaluation.test_cases import EVALUATION_TEST_CASES

def evaluate_with_conversation_context():
    """Re-evaluate conversational queries with conversation memory."""

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "eval.db"

        # Initialize services
        conv_repo = ConversationRepository(db_path=db_path)
        conv_service = ConversationService(repository=conv_repo)
        feedback_repo = FeedbackRepository(db_path=db_path)

        chat_service = ChatService(
            feedback_repository=feedback_repo,
            enable_sql=True,
            conversation_history_limit=5
        )

        # Group conversational test cases by conversation
        # (Test cases with pronouns should reference earlier queries)
        conversational_cases = [
            tc for tc in EVALUATION_TEST_CASES
            if tc.category == "conversational"
        ]

        # Start a conversation
        conversation = conv_service.start_conversation()
        conv_id = conversation.id

        results = []
        turn = 1

        for test_case in conversational_cases:
            request = ChatRequest(
                query=test_case.query,
                conversation_id=conv_id,
                turn_number=turn,
                k=5,
            )

            response = chat_service.chat(request)

            # Log interaction (persists to conversation)
            feedback_repo.save_interaction(
                ChatInteractionCreate(
                    query=test_case.query,
                    response=response.answer,
                    sources=[],
                    processing_time_ms=int(response.processing_time_ms),
                    conversation_id=conv_id,
                    turn_number=turn,
                )
            )

            results.append({
                "turn": turn,
                "query": test_case.query,
                "response": response.answer,
                "expected": test_case.expected_answer,
            })

            turn += 1

        # Cleanup
        conv_repo.close()
        feedback_repo.close()

        return results

if __name__ == "__main__":
    results = evaluate_with_conversation_context()

    # Compare with stateless evaluation
    print("\n=== CONVERSATION-AWARE EVALUATION ===\n")
    for r in results:
        print(f"Turn {r['turn']}: {r['query']}")
        print(f"Response: {r['response'][:100]}...")
        print()
```

#### Testing
```bash
poetry run python scripts/evaluate_with_conversation.py

# Expected: Conversational queries should improve from 25% → 70%+
```

---

## Priority 3: Advanced Enhancements (LOWER)

### Impact: +10-15% Complex Query Success
### Effort: High (8-12 hours each)
### Target Completion: Next Month

---

### **Fix 7: Query Decomposition for Complex Multi-Part Queries**

#### Problem
- Complex queries fail 59% of the time
- Example: "Compare top 5 scorers and analyze their efficiency and playing styles"
- Single prompt can't handle multiple sub-tasks

#### Solution
**Decompose complex queries into sub-queries:**

```python
class QueryDecomposer:
    """Break complex queries into manageable sub-queries."""

    def decompose(self, query: str) -> list[str]:
        """Decompose a complex query into sub-queries."""
        # Example: "Top 5 scorers and their efficiency and styles"
        # → ["Who are the top 5 scorers?",
        #    "What is the efficiency of each?",
        #    "What are their playing styles?"]

        # Implementation: Use LLM to decompose
        pass

    def synthesize(self, sub_results: list[str]) -> str:
        """Synthesize sub-query results into final answer."""
        pass
```

**Implementation:** Too complex for immediate deployment - defer to Phase 2.

---

### **Fix 8: Add Team-Level Aggregations**

#### Problem
- Team-level queries fail 100% in vector-only
- "Which team leads in rebounds?" → No team data in vector store

#### Solution
**Extend SQL database schema:**

```sql
CREATE TABLE team_stats (
    team_id INTEGER PRIMARY KEY,
    team_name TEXT,
    wins INTEGER,
    losses INTEGER,
    pts_per_game REAL,
    reb_per_game REAL,
    ast_per_game REAL,
    -- ... other team stats
);
```

**Implementation:** Requires data ingestion from NBA API - defer to Phase 3.

---

## Implementation Timeline

### Week 1 (This Week)
- **Day 1 (Today):**
  - ✅ P0 Fix 1: Update SYSTEM_PROMPT_TEMPLATE
  - ✅ P0 Fix 2: Add query-type-specific prompts (SQL_ONLY, HYBRID, CONTEXTUAL)
  - ✅ P0 Fix 3: Enforce citation requirements
  - **Test:** Re-run vector-only evaluation (expect 27% → 55%+)

- **Day 2:**
  - ✅ P1 Fix 4: Enhance QueryClassifier with hybrid patterns
  - ✅ P2 Fix 5: Handle scalar SQL results
  - **Test:** Re-run SQL hybrid evaluation (expect 63% → 80%+)

- **Day 3:**
  - ✅ P1 Fix 4 (cont.): Add comprehensive test cases for QueryClassifier
  - ✅ P2 Fix 6: Create evaluate_with_conversation.py script
  - **Test:** Re-run hybrid integration evaluation (expect 0% → 75%+)

- **Day 4-5:**
  - Full regression testing across all 3 evaluation sets
  - Fix any regressions discovered
  - Document improvements

### Week 2 (Next Week)
- Integrate conversation memory into all evaluation scripts
- Add confidence scoring to QueryClassifier
- Begin query decomposition research

### Month 2 (February)
- Implement query decomposition for complex queries
- Add team-level SQL aggregations
- Full system re-evaluation with all fixes

---

## Success Metrics

### Immediate Targets (Week 1)
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Vector-Only Success | 27.7% | 55%+ | ⏳ In Progress |
| SQL Hybrid Success | 63.2% | 80%+ | ⏳ In Progress |
| Hybrid Integration | 40.6% | 75%+ | ⏳ In Progress |
| Answer Relevancy | 23.7% | 55%+ | ⏳ In Progress |
| Vector Usage (Hybrid) | 6.3% | 80%+ | ⏳ In Progress |
| Hallucination Rate | 19% | <5% | ⏳ In Progress |

### Long-Term Targets (Month 2)
| Metric | Target |
|--------|--------|
| Overall Success Rate | 75%+ |
| Faithfulness | 80%+ |
| Answer Relevancy | 70%+ |
| Context Precision | 75%+ (maintain) |
| SQL Accuracy | 90%+ |
| Hybrid Integration | 85%+ |

---

## Validation Plan

### After Each Fix
1. **Unit Tests:** Verify specific fix works in isolation
2. **Integration Tests:** Ensure no regressions in related components
3. **Evaluation Re-run:** Measure impact on full test suite

### Before Deployment
1. **Full Evaluation Suite:** All 131 queries pass targets
2. **Regression Testing:** No degradation in previously passing queries
3. **Manual QA:** Test 10 random queries manually
4. **User Acceptance:** Stakeholder review of improvements

---

## Rollback Plan

If any fix causes regressions:
1. **Git revert** to previous working commit
2. **Isolate the problematic fix** in a feature branch
3. **Debug in isolation** before re-integration

---

## Files to Modify

| Priority | File | Changes |
|----------|------|---------|
| **P0** | `src/services/chat.py` | Add new prompts, update `chat()` method |
| **P0** | `src/services/chat.py` | Add `_format_sql_results()` method |
| **P1** | `src/services/query_classifier.py` | Add hybrid pattern matching |
| **P1** | `tests/test_query_classifier.py` | Add hybrid classification tests |
| **P2** | `scripts/evaluate_with_conversation.py` | New script for conversational eval |

---

## Monitoring Post-Deployment

After deploying fixes:
1. **Weekly Evaluations:** Re-run all 3 evaluation sets weekly
2. **User Feedback:** Monitor thumbs up/down rates in production
3. **Error Logging:** Track "data not available" responses
4. **Latency Monitoring:** Ensure prompt changes don't increase response time

---

**Prepared by:** Claude Sonnet 4.5
**Next Review:** 2026-02-16 (1 week)
**Status:** Implementation in progress
