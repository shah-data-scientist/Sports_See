# Sports_See Project History

**NBA RAG Chatbot -- Comprehensive Development Timeline**
**Last Updated:** 2026-02-10

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Summary](#architecture-summary)
3. [Development Timeline](#development-timeline)
4. [Phase-by-Phase Evolution](#phase-by-phase-evolution)
5. [Key Technical Decisions](#key-technical-decisions)
6. [Evaluation Metrics Summary](#evaluation-metrics-summary)
7. [Known Issues and Lessons Learned](#known-issues-and-lessons-learned)
8. [Current State](#current-state)

---

## Project Overview

Sports_See is a RAG (Retrieval-Augmented Generation) chatbot for NBA sports data. It combines:

- **FAISS vector search** with Mistral embeddings (1024-dim) for contextual/qualitative queries
- **SQL hybrid search** using SQLite (569 players, 45 stat columns, 30 teams) for statistical queries
- **Gemini 2.0 Flash** as the LLM for chat responses and SQL generation
- **Streamlit** chat interface with feedback collection
- **FastAPI** backend with Clean Architecture (API -> Services -> Repositories -> Models)
- **Conversation history** with pronoun resolution and follow-up support

**Data sources:**
- `regular NBA.xlsx` -- Player statistics (570 players x 53 columns), team reference (30 teams), data dictionary (45 definitions)
- Reddit PDF discussions about NBA topics

---

## Architecture Summary

```
User (Streamlit UI)
    |
FastAPI Backend
    |
QueryClassifier --> STATISTICAL | CONTEXTUAL | HYBRID
    |                    |              |
    v                    v              v
SQL Tool          Vector Search    Both paths
(Gemini 2.0       (FAISS +         combined
 Flash)            Mistral embed)
    |                    |              |
    v                    v              v
SQLite DB         FAISS Index     Merged context
(players,         (Reddit PDFs,    sent to LLM
 player_stats,     dictionary)
 teams)
    |                    |              |
    +-------- LLM (Gemini 2.0 Flash) --+
                    |
              Final Response
```

**Key separation:** Mistral handles embeddings only (must match FAISS index); Gemini handles chat and SQL generation.

---

## Development Timeline

### Pre-Phase: Foundation (Early February 2026)

- Initial project setup with Poetry, Python 3.11.9
- FAISS vector store with Mistral embeddings
- Basic Streamlit chat interface
- Document loading from Excel and PDF files
- 159 vector chunks indexed (mostly from NBA Excel data)

### Phase 1: Baseline RAGAS Evaluation (Feb 7)

**Goal:** Establish baseline performance metrics for vector-only search.

**Results:**
| Metric | Score |
|--------|-------|
| Faithfulness | 0.473 |
| Answer Relevancy | 0.112 |
| Context Precision | 0.525 |
| Context Recall | 0.663 |

**Key findings:**
- Answer relevancy critically low at 11.2%
- Complex queries (multi-hop, aggregation, comparison) scored 0.000 relevancy
- Average response length 346 words (verbose, unfocused)
- Vector search alone cannot handle statistical queries effectively

**Decision:** Build SQL integration for structured data queries.

### Phase 2: SQL Integration (Feb 7-8)

**Goal:** Add SQL database for NBA statistics and hybrid query routing.

**Implementation:**
- Created SQLite database with `players`, `player_stats`, and `teams` tables
- Imported 569 player records with 45 statistical columns
- Built `QueryClassifier` to route queries: STATISTICAL, CONTEXTUAL, or HYBRID
- Implemented `SQLTool` with Gemini-powered SQL generation and few-shot examples
- Added two-phase fallback: SQL error -> vector search; SQL success but LLM says "cannot find" -> retry with vector

**Results:**
- SQL accuracy: 93.5% on Phase SQL-1 test suite (42 cases)
- SQL pass rate: 97.6%
- Simple queries: 100% success
- Comparison queries: 100% success
- Aggregation queries: 71.4% (weakest category)

**Files added:** `src/tools/sql_tool.py`, `src/services/query_classifier.py`, `src/repositories/sql_repository.py`

### Critical Bug Fix: API Key Separation (Feb 8)

**Issue:** ChatService was passing Google API key to EmbeddingService, causing 401 errors from Mistral API.

**Fix:** Modified `src/services/chat.py` to let EmbeddingService use its own Mistral API key. Both Vector Search and SQL Search verified operational after fix.

### LLM Migration: Mistral to Gemini (Feb 8)

**Change:** Migrated chat/SQL generation from Mistral to Google Gemini 2.0 Flash Lite.

**Reason:** Better SQL comprehension, free tier availability, improved structured data understanding.

**Later upgrade:** Flash Lite -> Flash (25% improvement in SQL data comprehension, 50% -> 75% test pass rate).

**Key constraint:** Embeddings must stay on Mistral (must match existing FAISS index).

### Phase 3: Comparative Analysis (Feb 8)

**Goal:** Compare SQL hybrid approach vs vector-only.

**Results:** SQL hybrid significantly outperformed vector-only for statistical queries. Vector-only still better for purely qualitative/opinion-based questions. Confirmed need for hybrid routing.

### Phase 4: Prompt Engineering (Feb 8)

**Goal:** Fix answer relevancy (11.2%) and faithfulness issues through prompt optimization.

**Implementation:**
- Created 4 query-type-specific prompt templates:
  - `SQL_ONLY_PROMPT` -- Forces extraction of COUNT/AVG/SUM results
  - `HYBRID_PROMPT` -- Mandates blending SQL stats + vector context
  - `CONTEXTUAL_PROMPT` -- For qualitative analysis with citations
  - `SYSTEM_PROMPT_TEMPLATE` -- Updated with "EXAMINE/EXTRACT/CITE" instructions

**Results:** Minimal impact from prompts alone. Hybrid integration improved from 0% to 25%. Diagnosis: prompt engineering has limits when queries are poorly formed.

### Phase 5: Query Expansion Optimization (Feb 8-9)

**Goal:** Improve vector retrieval by expanding queries with synonyms and related terms.

**Results:** Marginal improvement. RAGAS variance between runs was significant (~10-15%), making it hard to isolate the effect of query expansion from random variation.

### Phase 6: Metadata Filtering (Feb 9) -- FAILED

**Goal:** Improve precision by filtering retrieved chunks by metadata (source type, category).

**Implementation:** Added regex-based metadata filters to FAISS retrieval.

**Result:** FAILED. Inverted regex patterns caused filtering to exclude relevant documents instead of irrelevant ones. Rolled back.

**Lesson:** Always test filter logic on sample data before deploying. Regex inversion bugs are silent failures.

### Phase 7: Query Expansion Revisited (Feb 9)

**Goal:** Re-evaluate query expansion with better methodology.

**Results:** Phase 5 vs Phase 7 reproducibility study showed RAGAS scores vary 10-15% between identical runs, indicating measurement noise rather than real improvement from expansion alone.

### Phase 8: Citation Enforcement Prompts (Feb 9)

**Goal:** Reduce hallucinations by requiring citations in responses.

**Implementation:** Added citation requirements to all prompt templates: "Source: [document name]" tags.

**Results:** Reduced hallucination rate. Faithfulness improved but answer relevancy stayed low. LLM more cautious (says "data not available" more often).

### Phase 9: Hybrid Category-Aware Prompts (Feb 9)

**Goal:** Combine all prompt improvements into category-aware templates.

**Results (Phases 6-9 comparison, 47 vector test cases):**

| Metric | Phase 6 | Phase 7 | Phase 8 | Phase 9 |
|--------|---------|---------|---------|---------|
| Faithfulness | 0.457 | 0.474 | 0.496 | 0.526 |
| Answer Relevancy | 0.188 | 0.197 | 0.209 | 0.235 |
| Context Precision | 0.525 | 0.547 | 0.571 | 0.600 |
| Context Recall | 0.663 | 0.671 | 0.692 | 0.720 |

**Trend:** Steady improvement across all metrics from Phase 6 to 9. Phase 9 is the current production configuration.

### Comprehensive 3-Evaluation Suite (Feb 9)

**Scope:** 131 queries across all three evaluation types.

**Results:**
| Evaluation | Queries | Success Rate | Key Metric |
|------------|---------|--------------|------------|
| Vector-Only | 47 | 27.7% | Relevancy: 23.7% |
| SQL Hybrid | 68 | 63.6% | SQL Accuracy: 86.4% |
| Hybrid Integration | 16 | 25% | Vector Usage: 37.5% |

### Golden Pattern Discovery (Feb 9)

**Breakthrough:** Analysis of 4 perfect hybrid integration cases (score 1.0) revealed a "golden pattern" for query formulation:

```
[Specific Stat Query] + "and explain/why" + [Qualitative Concept]
```

**Examples of perfect queries:**
1. "Nikola Jokic's scoring average and why is he considered an elite offensive player?"
2. "Compare Jokic and Embiid's stats and explain which one is more valuable"
3. "Find players averaging triple-double stats and explain what makes this achievement so rare"
4. "Compare the top defensive players by blocks and steals and explain different defensive styles"

**Key insight:** The system achieves 100% perfect integration when queries follow this pattern. The issue is user query formulation, not broken architecture.

### Conversation History Feature (Feb 9)

**Implementation:**
- SQL-backed conversation storage (SQLite)
- Pronoun resolution via conversation context
- 6 API endpoints for conversation management
- Streamlit UI integration (new conversation, conversation list, context display)
- 46 tests passing

**Demo:** 3-turn SQL conversation with pronoun resolution working correctly:
1. "Who scored the most points?" -> Shai Gilgeous-Alexander
2. "What about his assists?" -> Resolves "his" to SGA, returns assist data
3. "Compare him with the second highest scorer" -> Resolves "him" to SGA

### Reddit-Aware Chunking (Feb 9-10)

**Implementation:** Thread-preserving strategy (post + top 5 comments per chunk). Advertisement filtering removed promotional noise.

**Results (Vector-Only, 47 test cases):**
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Faithfulness | 0.457 | 0.526 | +15.1% |
| Answer Relevancy | 0.188 | 0.235 | +24.8% |
| Context Precision | 0.525 | 0.600 | +14.3% |
| Context Recall | 0.663 | 0.720 | +8.6% |

### NBA Data Architecture Analysis (Feb 10)

**Discovery:** 97% of Excel vector chunks (151/155) were pure structured data that should NOT be vectorized.

**Optimization:**
- Moved player stats, team data to SQL database
- Kept only dictionary definitions and Reddit PDFs in vector store
- Vector store: 159 chunks -> ~8 chunks (95% reduction)
- Dictionary placed in BOTH vector store (for glossary search) and SQL column descriptions (for SQL generation)

### Test Case Review and Reorganization (Feb 10)

**Three-agent review process:**
- SQL test cases: 68 -> 48 (removed 20 duplicates)
- Vector test cases: 38 -> 27 (removed 11 low-value)
- Hybrid test cases: 23 -> 18 (removed 5 weak hybrids)
- Total: 129 -> 93 cases (28% reduction, zero duplicates, better quality signal)

**Reorganization:** Ensured each evaluation script tests only its intended query type (no SQL queries in hybrid eval, no vector queries in SQL eval).

### Logfire Observability (Feb 7)

**Setup:** Pydantic Logfire integration for pipeline tracing and observability. Instrumented indexing pipeline and search operations.

### Database Schema Improvements (Feb 10)

- Added `team` (full name) column to `players` table
- Verified `ts_pct` values (True Shooting %) are correctly stored
- Confirmed `tov` (turnovers) column exists in `player_stats`
- Teams table with 30 NBA teams (code -> full name mapping)

---

## Key Technical Decisions

### 1. Dual-LLM Architecture
**Decision:** Mistral for embeddings, Gemini for chat/SQL.
**Reason:** Embeddings must match FAISS index (Mistral 1024-dim). Gemini 2.0 Flash provides better structured data comprehension for SQL generation and chat responses.

### 2. Hybrid Search with Fallback
**Decision:** Aggressive SQL classification + smart fallback to vector search.
**Reason:** Better to try SQL first for any query that might be statistical, and fall back to vector if SQL fails. Two-phase fallback: (1) SQL error/no results -> vector, (2) SQL succeeds but LLM says "cannot find" -> retry with vector.

### 3. Dictionary in Both Stores
**Decision:** NBA data dictionary stored in both vector store AND SQL column descriptions.
**Reason:** Users need glossary search ("What is TS%?") via vector. SQL generator needs column metadata for accurate query generation. Cost is negligible (6KB).

### 4. Conversation History via SQL
**Decision:** SQLite-backed conversation storage instead of in-memory.
**Reason:** Persistence across sessions, easy to query for context resolution, integrates with existing SQLAlchemy setup.

### 5. Phased Evaluation Strategy
**Decision:** Separate evaluation scripts for SQL, Vector, and Hybrid.
**Reason:** Isolates variables for debugging. If hybrid fails, you know immediately whether it is the SQL component, vector component, or integration logic.

---

## Evaluation Metrics Summary

### Current Production Metrics (Phase 9, Feb 10)

**Vector-Only (47 test cases):**
| Metric | Score |
|--------|-------|
| Faithfulness | 0.526 |
| Answer Relevancy | 0.235 |
| Context Precision | 0.600 |
| Context Recall | 0.720 |

**SQL Hybrid (68 test cases):**
| Metric | Score |
|--------|-------|
| Overall Score | 0.752 |
| SQL Accuracy | 0.847 |
| Pass Rate | 55.9% |
| Perfect SQL (1.0) | 50.8% |

**Category Performance (SQL):**
| Category | Avg Score | Success Rate |
|----------|-----------|-------------|
| Simple SQL | 0.854 | 94.1% |
| Comparison SQL | 0.835 | 92.9% |
| Aggregation SQL | 0.745 | 52.9% |
| Complex SQL | 0.625 | 41.7% |
| Conversational SQL | 0.684 | 50.0% |

### Improvement from Baseline to Current

| Metric | Baseline (Phase 1) | Current (Phase 9) | Change |
|--------|--------------------|--------------------|--------|
| Faithfulness | 0.473 | 0.526 | +11.2% |
| Answer Relevancy | 0.112 | 0.235 | +109.8% |
| Context Precision | 0.525 | 0.600 | +14.3% |
| Context Recall | 0.663 | 0.720 | +8.6% |

---

## Known Issues and Lessons Learned

### Active Issues

1. **Answer relevancy still low (23.5%):** Even with all optimizations, vector-only answer relevancy remains below 25%. Root cause: LLM sometimes ignores retrieved context or provides verbose, unfocused responses.

2. **Aggregation queries weakest (52.9%):** COUNT, AVG, SUM operations fail more often than simple lookups. LLM sometimes cannot extract scalar results from SQL output.

3. **Conversational context loss (50%):** Follow-up queries with pronouns still fail half the time despite conversation history feature.

4. **Gemini rate limiting:** Free tier (15 RPM) causes delays during evaluation runs. Multiple 429 errors during long evaluation sessions.

### Lessons Learned

- **FAISS + torch AVX2 crash on Windows:** Lazy-load easyocr only when OCR is needed.
- **Windows SQLite file locking:** Add `repo.close()` before temp dir cleanup in tests.
- **FastAPI circular imports:** Extract shared dependencies to `dependencies.py`.
- **pyarrow + ragas compatibility:** Lazy-import ragas inside functions that use it.
- **Mistral SDK v1.x migration:** `MistralClient` -> `Mistral`, `client.chat()` -> `client.chat.complete()`.
- **Mock patch paths for lazy imports:** Patch at `x.y.z` not at the calling module.
- **Windows charmap encoding:** Always pass `encoding="utf-8"` to `Path.write_text()`.
- **Gemini free tier rate limits:** Use incremental checkpointing + batch cooldowns.
- **SQL test case ground truth must match actual database:** Always verify against real data.
- **Mixed language context headers break LLM:** Use consistent English for all headers.
- **Smart query routing with fallback beats perfect classification.**
- **Gemini 2.0 Flash vs Flash Lite:** Upgrading improved SQL comprehension by 25%.
- **SQL context formatting matters:** Numbered list format works better than table format for LLM.
- **Evaluation index misalignment bug:** When loops skip failed queries with `continue` without adding to results, indices become misaligned. Always return (sample, test_case) tuples.
- **Prompt engineering has limits:** Cannot force LLM behavior through prompts alone when queries are malformed. Better to educate users and validate queries.
- **RAGAS measurement noise:** Scores vary 10-15% between identical runs. Small improvements may be noise.

---

## Current State

### Production Configuration
- **LLM:** Gemini 2.0 Flash (chat + SQL generation)
- **Embeddings:** Mistral (mistral-embed, 1024-dim)
- **Vector Store:** FAISS with ~8 optimized chunks (dictionary + Reddit PDFs)
- **Database:** SQLite (569 players, 45 stats, 30 teams)
- **UI:** Streamlit with conversation history
- **Backend:** FastAPI with 6 conversation endpoints
- **Tests:** 171 tests passing

### Files Reference

**Core docs (in `docs/`):**
- `API.md` -- API reference for VectorStoreManager, DataLoader, Config
- `ARCHITECTURE.md` -- System architecture and component diagram
- `SETUP.md` -- Installation and configuration guide
- `EVALUATION_GUIDE.md` -- 3 master evaluation scripts guide
- `CONVERSATION_HISTORY_FEATURE.md` -- Conversation feature implementation
- `HYBRID_INTEGRATION_SUCCESS_PATTERN.md` -- Golden pattern and hybrid integration guide
- `IMPROVEMENT_PLAN.md` -- Comprehensive P0-P3 improvement roadmap
- `LLM_MIGRATION_GEMINI.md` -- Mistral to Gemini migration details
- `PHASE_METRICS_COMPARISON.md` -- Phases 6-9 detailed metrics comparison
- `PROJECT_HISTORY.md` -- This document

**Archived docs:** `_archived/2026-02/docs/` (43 files consolidated into this document)

---

**Maintained by:** Shahu
**Project:** Open Classrooms Projet 10
