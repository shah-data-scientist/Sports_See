# RAGAS Evaluation Baseline Report
**Sports_See RAG Chatbot - NBA Q&A System**

**Date**: 2026-02-07
**Model**: gemini-2.0-flash-lite (generation) + Mistral embeddings (relevancy)
**Evaluator**: Google Gemini 2.0 Flash Lite + Mistral embeddings
**Test Samples**: 47 queries across 4 categories
**Evaluation Framework**: RAGAS (Retrieval-Augmented Generation Assessment)

---

## Executive Summary

This baseline evaluation establishes performance benchmarks for the Sports_See RAG system before optimization. The system shows **moderate retrieval quality** (Context Precision: 0.595, Recall: 0.596) but **low answer relevancy** (0.112), indicating responses are not focused enough on user queries.

**Key Finding**: The system retrieves relevant information well but generates verbose, unfocused responses that don't directly answer questions.

---

## 📊 Baseline Metrics

### Overall Performance

| Metric | Score | Interpretation | Status |
|--------|-------|----------------|---------|
| **Faithfulness** | 0.473 | Moderate - responses somewhat grounded in context | ⚠️ Needs Improvement |
| **Answer Relevancy** | 0.112 | Low - responses not focused on question | ⚠️ Critical Issue |
| **Context Precision** | 0.595 | Good - retrieved chunks are relevant | ✅ Acceptable |
| **Context Recall** | 0.596 | Good - needed info is being retrieved | ✅ Acceptable |

### Performance by Query Category

| Category | Count | Faithfulness | Answer Relevancy | Context Precision | Context Recall | Notes |
|----------|-------|-------------|------------------|-------------------|----------------|-------|
| **Simple** | 12 | 0.444 | 0.246 | **0.780** | 0.667 | Best precision, still low relevancy |
| **Complex** | 12 | 0.547 | **0.000** | 0.529 | 0.375 | Zero relevancy - critical issue |
| **Noisy** | 11 | 0.313 | 0.148 | 0.756 | **0.773** | Best recall, poor faithfulness |
| **Conversational** | 12 | **0.574** | 0.058 | 0.491 | 0.583 | Best faithfulness, very low relevancy |

---

## 🔍 Detailed Analysis

### 1. **Answer Relevancy (0.112) - CRITICAL ISSUE** ❌

**Problem**: The system's responses are not directly answering user questions.

**Evidence**:
- **Complex queries**: 0.000 relevancy - system completely fails to focus on multi-part questions
- **Conversational queries**: 0.058 relevancy - system doesn't maintain conversational context
- **Even simple queries**: Only 0.246 relevancy - direct questions get unfocused answers

**Example Scenario**:
```
User: "Who is the leading scorer in the NBA?"
Expected: "Luka Dončić leads with 28.5 PPG this season."
Current System: [Long paragraph about scoring statistics, multiple players,
                 historical context, without clearly answering the question]
```

**Root Causes**:
1. **Verbose LLM responses**: System includes too much context/background
2. **No answer extraction**: Responses don't highlight the direct answer
3. **Prompt engineering**: System prompt may not emphasize conciseness
4. **Context overload**: Passing too much retrieved text to LLM

### 2. **Faithfulness (0.473) - MODERATE ISSUE** ⚠️

**Problem**: Nearly half of response content is not supported by retrieved documents.

**Evidence**:
- **Noisy queries (0.313)**: System adds speculation when context is unclear
- **Simple queries (0.444)**: Even straightforward questions get embellished answers
- **Best case (Conversational: 0.574)**: Still 43% unfaithful content

**Root Causes**:
1. **LLM hallucination**: Model generates plausible but unsupported facts
2. **Insufficient context grounding**: Prompt doesn't enforce strict source adherence
3. **No citation mechanism**: Responses don't explicitly cite sources
4. **Temperature setting**: May be too high (creative vs. factual)

### 3. **Context Precision (0.595) - ACCEPTABLE** ✅

**Problem**: 40% of retrieved chunks are irrelevant noise.

**Evidence**:
- **Simple queries perform best (0.780)**: Clear queries → relevant retrievals
- **Conversational queries worst (0.491)**: Ambiguous queries → noisy retrievals
- **Complex queries (0.529)**: Multi-part questions confuse vector search

**Partial Success**: System retrieves some relevant information, but includes too much noise.

### 4. **Context Recall (0.596) - ACCEPTABLE** ✅

**Problem**: Missing 40% of needed information.

**Evidence**:
- **Best performance on noisy queries (0.773)**: Casting wide net helps
- **Complex queries worst (0.375)**: Missing 62% of needed context for multi-part questions
- **Simple queries (0.667)**: Still missing 33% of required facts

**Implication**: Increasing `top_k` (currently 5 chunks) may improve recall.

---

## 🎯 Improvement Recommendations

### Priority 1: Fix Answer Relevancy (HIGH IMPACT) 🔴

#### **Recommendation 1.1: Improve Prompt Engineering**

**Current Prompt**:
```python
SYSTEM_PROMPT_TEMPLATE = """Tu es '{app_name} Analyst AI', un assistant expert.
Ta mission est de répondre aux questions en te basant sur le contexte fourni.

CONTEXTE:
---
{context}
---

QUESTION:
{question}

INSTRUCTIONS:
- Réponds de manière précise et concise basée sur le contexte
- Si le contexte ne contient pas l'information, dis-le clairement
- Cite les sources pertinentes si possible

RÉPONSE:"""
```

**Improved Prompt**:
```python
SYSTEM_PROMPT_TEMPLATE = """You are an NBA statistics assistant. Answer DIRECTLY and CONCISELY.

CONTEXT:
---
{context}
---

QUESTION: {question}

STRICT INSTRUCTIONS:
1. Answer the EXACT question asked - nothing more
2. Start with the direct answer in 1-2 sentences
3. Only add supporting details if requested
4. If information is missing, say "I don't have that information" - DO NOT speculate
5. Cite source document IDs: [Source: doc_123]

FORMAT:
- Direct Answer: [1-2 sentences]
- Supporting Details: [Optional, only if question asks for details]
- Sources: [List document IDs]

ANSWER:"""
```

**Expected Impact**:
- Answer Relevancy: 0.112 → **0.6+** (5x improvement)
- Faithfulness: 0.473 → **0.7+** (fewer hallucinations)

**Implementation**:
```python
# In src/services/chat.py
SYSTEM_PROMPT_TEMPLATE = """..."""  # Update with new template
```

#### **Recommendation 1.2: Add Answer Post-Processing**

Create an answer extraction step:

```python
def extract_direct_answer(full_response: str, query: str) -> str:
    """Extract the direct answer from verbose LLM response."""
    # Use a smaller, faster model to extract the core answer
    extraction_prompt = f"""
    From this response, extract ONLY the direct answer to: "{query}"

    Full Response: {full_response}

    Direct Answer (max 2 sentences):
    """
    return llm_call(extraction_prompt, model="mistral-tiny", max_tokens=50)
```

**Expected Impact**: Answer Relevancy: 0.112 → **0.5+**

#### **Recommendation 1.3: Reduce Temperature**

```python
# In src/services/chat.py - ChatService.generate_response()
response = self.client.chat.complete(
    model=self._model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,  # Change from 0.7 to 0.1 for factual responses
    max_tokens=150,   # Add token limit to enforce conciseness
)
```

**Expected Impact**:
- Answer Relevancy: +0.1-0.2 improvement
- Faithfulness: +0.1-0.15 improvement

---

### Priority 2: Improve Faithfulness (MEDIUM IMPACT) 🟡

#### **Recommendation 2.1: Add Source Attribution**

Modify the response format to require citations:

```python
def generate_response_with_citations(self, query: str, context: str, sources: list) -> dict:
    """Generate response with mandatory source citations."""
    prompt = f"""...[same as before]...

    MANDATORY: Every factual claim must reference a source using [Source: doc_id]
    """

    response = self._generate(prompt)

    # Validate that response contains citations
    if not self._has_citations(response, sources):
        # Retry with stricter prompt
        response = self._generate_with_strict_citations(prompt)

    return {
        "answer": response,
        "citations": self._extract_citations(response),
        "sources": sources,
    }
```

**Expected Impact**: Faithfulness: 0.473 → **0.65+**

#### **Recommendation 2.2: Implement Fact-Checking Layer**

Add a verification step using a second LLM call:

```python
def verify_faithfulness(answer: str, context: str) -> dict:
    """Verify each claim in the answer against context."""
    verification_prompt = f"""
    Check if each statement in ANSWER is supported by CONTEXT.
    Mark unsupported statements.

    CONTEXT: {context}
    ANSWER: {answer}

    Verification:
    """
    verification = llm_call(verification_prompt)

    if verification["unsupported_claims"]:
        # Remove or flag unsupported claims
        answer = remove_unsupported(answer, verification["unsupported_claims"])

    return {"verified_answer": answer, "confidence": verification["score"]}
```

**Expected Impact**: Faithfulness: 0.473 → **0.70+**

---

### Priority 3: Optimize Retrieval (LOW-MEDIUM IMPACT) 🟢

#### **Recommendation 3.1: Increase Top-K for Better Recall**

```python
# In src/services/chat.py - ChatService.search()
def search(self, query: str, k: int = 10) -> list[SearchResult]:
    # Increase from k=5 to k=10
    results = self.vector_store.search(query_embedding, k=k)

    # Re-rank results by relevance score
    results = self._rerank_by_relevance(results, query)

    # Take top 5 after re-ranking
    return results[:5]
```

**Expected Impact**:
- Context Recall: 0.596 → **0.75+**
- Context Precision: May slightly decrease, mitigated by re-ranking

#### **Recommendation 3.2: Implement Hybrid Search**

Combine vector search with keyword search:

```python
def hybrid_search(self, query: str, k: int = 5) -> list[SearchResult]:
    """Combine semantic (vector) + lexical (keyword) search."""
    # Vector search (semantic similarity)
    vector_results = self.vector_store.search(query_embedding, k=k*2)

    # Keyword search (BM25)
    keyword_results = self.bm25_search(query, k=k*2)

    # Combine with weighted scoring
    combined = self._merge_results(
        vector_results, weight=0.7,
        keyword_results, weight=0.3
    )

    return combined[:k]
```

**Expected Impact**:
- Context Precision: 0.595 → **0.70+**
- Context Recall: 0.596 → **0.70+**

#### **Recommendation 3.3: Query Expansion for Complex Queries**

```python
def expand_complex_query(self, query: str) -> list[str]:
    """Break complex queries into sub-queries."""
    if self._is_complex(query):
        # Use LLM to decompose
        sub_queries = llm_call(f"Break this into simple sub-questions: {query}")
        return sub_queries
    return [query]

def search_complex(self, query: str) -> list[SearchResult]:
    """Search with query expansion for complex questions."""
    sub_queries = self.expand_complex_query(query)

    all_results = []
    for sub_q in sub_queries:
        results = self.search(sub_q, k=3)
        all_results.extend(results)

    # Deduplicate and re-rank
    return self._deduplicate(all_results)[:5]
```

**Expected Impact** (for complex queries):
- Faithfulness: 0.547 → **0.65+**
- Answer Relevancy: 0.000 → **0.3+**
- Context Recall: 0.375 → **0.60+**

---

### Priority 4: Query-Specific Optimizations (MEDIUM IMPACT) 🟡

#### **Recommendation 4.1: Query Classification**

Implement query type detection and route to specialized handlers:

```python
class QueryType(Enum):
    SIMPLE_FACT = "simple"      # "Who is X?"
    COMPARISON = "comparison"    # "Compare X and Y"
    AGGREGATION = "aggregation"  # "What are the top 10...?"
    CONVERSATIONAL = "conversational"  # Follow-up questions

def classify_query(query: str) -> QueryType:
    """Classify query type using simple rules or small LLM."""
    # Implementation...
    pass

def chat(self, request: ChatRequest) -> ChatResponse:
    query_type = classify_query(request.query)

    if query_type == QueryType.COMPARISON:
        return self.handle_comparison(request)
    elif query_type == QueryType.AGGREGATION:
        return self.handle_aggregation(request)
    # ... etc
```

**Expected Impact**:
- Complex queries: Answer Relevancy 0.000 → **0.4+**
- Conversational queries: Answer Relevancy 0.058 → **0.3+**

---

## 📈 Expected Improvements After Implementation

### Projected Metrics (Conservative Estimates)

| Metric | Current | After Priority 1 | After All Priorities | Target |
|--------|---------|------------------|---------------------|---------|
| **Faithfulness** | 0.473 | **0.65** | **0.75** | 0.80 |
| **Answer Relevancy** | 0.112 | **0.60** | **0.70** | 0.75 |
| **Context Precision** | 0.595 | 0.60 | **0.70** | 0.75 |
| **Context Recall** | 0.596 | 0.65 | **0.75** | 0.80 |

### Implementation Roadmap

**Phase 1 (1-2 days)** - Critical Fixes:
- ✅ Update system prompt (Rec 1.1)
- ✅ Reduce temperature + add max_tokens (Rec 1.3)
- ✅ Add source attribution (Rec 2.1)

**Phase 2 (2-3 days)** - Core Improvements:
- ✅ Implement answer extraction (Rec 1.2)
- ✅ Increase top-k + re-ranking (Rec 3.1)
- ✅ Add fact-checking layer (Rec 2.2)

**Phase 3 (3-5 days)** - Advanced Features:
- ✅ Implement hybrid search (Rec 3.2)
- ✅ Query classification (Rec 4.1)
- ✅ Query expansion for complex queries (Rec 3.3)

**Phase 4 (Ongoing)** - Monitoring:
- ✅ Re-run RAGAS evaluation after each phase
- ✅ Track metrics with Logfire observability
- ✅ A/B test improvements with real users

---

## 🔬 Testing Methodology

### Evaluation Setup

**Test Cases**: 47 queries across 4 categories:
1. **Simple** (12 queries): Direct factual questions
   - Example: "Who is the leading scorer in the NBA?"

2. **Complex** (12 queries): Multi-part or analytical questions
   - Example: "Compare the offensive efficiency of the top 3 scoring teams"

3. **Noisy** (11 queries): Typos, poor grammar, vague references
   - Example: "stats for that tall guy from milwaukee"

4. **Conversational** (12 queries): Follow-up questions with context
   - Example: "Who is their best player statistically?" (after asking about Lakers)

### RAGAS Metrics Explained

1. **Faithfulness** (0-1):
   - Measures if LLM response is grounded in retrieved context
   - Calculated by checking if each claim in response is supported by context
   - High score = fewer hallucinations

2. **Answer Relevancy** (0-1):
   - Measures if response directly addresses the user's question
   - Calculated using embedding similarity between question and answer
   - Low score = verbose/unfocused responses

3. **Context Precision** (0-1):
   - Measures if retrieved chunks are relevant to the question
   - Calculated by checking if context chunks help answer the question
   - High score = less noise in retrieval

4. **Context Recall** (0-1):
   - Measures if all needed information was retrieved
   - Calculated by checking if answer can be formed from retrieved context
   - Low score = missing important information

### Evaluation Tool Configuration

- **Generation Model**: Google Gemini 2.0 Flash Lite
- **Evaluator LLM**: Google Gemini 2.0 Flash Lite
- **Embeddings**: Mistral AI (mistral-embed, 1024 dimensions)
- **Vector Store**: FAISS (302 document chunks)
- **Retrieval**: Top-5 similarity search (cosine distance)
- **Generation**: Temperature 0.7, no max tokens

---

## 📁 Baseline Data

### Saved Artifacts

1. **Metrics Report**: `evaluation_results/ragas_baseline.json`
   - Complete JSON export of all metrics
   - Timestamp: 2026-02-07
   - Category breakdowns included

2. **Test Cases**: `src/evaluation/test_cases.py`
   - All 47 evaluation queries
   - Categorized by difficulty
   - Ground truth where available

3. **Evaluation Script**: `src/evaluation/evaluate_ragas.py`
   - Reproducible evaluation pipeline
   - Incremental checkpointing enabled
   - Run with: `poetry run python -m src.evaluation.evaluate_ragas`

---

## 🎓 Lessons Learned

### Technical Challenges

1. **Gemini API Rate Limits**:
   - Free tier very aggressive (429 errors)
   - Solution: Switched to `gemini-2.0-flash-lite` + checkpointing

2. **Embedding Model Compatibility**:
   - Gemini `text-embedding-004` not available on v1beta API
   - Solution: Use Mistral embeddings consistently (FAISS + RAGAS)

3. **OpenMP Runtime Conflicts** (Windows):
   - Multiple OpenMP libraries caused crashes
   - Solution: Set `KMP_DUPLICATE_LIB_OK=TRUE` environment variable

### Evaluation Insights

1. **Answer Relevancy Most Critical**:
   - Lowest score (0.112) with biggest user impact
   - Users want direct answers, not essays

2. **Retrieval Is Decent**:
   - Precision/Recall at ~0.6 is acceptable baseline
   - Focus optimization efforts on generation quality

3. **Complex Queries Need Special Handling**:
   - Zero answer relevancy indicates complete failure mode
   - Cannot be fixed with prompt engineering alone

---

## 🔗 Related Documentation

- **Logfire Observability**: [`docs/LOGFIRE_OBSERVABILITY.md`](./LOGFIRE_OBSERVABILITY.md)
- **Test Cases**: [`src/evaluation/test_cases.py`](../src/evaluation/test_cases.py)
- **Evaluation Script**: [`src/evaluation/evaluate_ragas.py`](../src/evaluation/evaluate_ragas.py)
- **Project Memory**: [`MEMORY.md`](../../../.claude/projects/c--Users-shahu-Documents-OneDrive-OPEN-CLASSROOMS-PROJET-10-Sports-See/memory/MEMORY.md)

---

## 📞 Next Steps

1. **Review this report** with stakeholders
2. **Prioritize improvements** based on business impact
3. **Implement Phase 1 fixes** (1-2 days)
4. **Re-evaluate** with same 47 queries
5. **Compare** new metrics vs. baseline
6. **Iterate** through remaining phases

**Contact**: Shahu (Maintainer)
**Last Updated**: 2026-02-07
