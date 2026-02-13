# PROJECT MEMORY - Sports_See (NBA RAG Assistant)

**Project Type:** RAG Chatbot Application
**Primary Language:** Python 3.11+
**Frameworks:** Streamlit (UI), FastAPI (REST API)
**AI Model:** Mistral AI
**Vector DB:** FAISS
**Feedback DB:** SQLite (SQLAlchemy)
**Last Updated:** 2026-01-26
**Status:** Active Development

---

## 📋 Project Requirements

**Last Audit:** 2026-01-26
**Requirements Status:** In Progress

### Initial Requirements

1. **RAG System Implementation**
   - Retrieval-Augmented Generation using FAISS for semantic search
   - Mistral AI for embeddings and response generation
   - Support for multiple document formats (PDF, TXT, DOCX, CSV, JSON, XLSX)

2. **Chat Interface**
   - Streamlit-based web interface
   - Conversation history management
   - Real-time response generation
   - NBA-specific domain expertise

3. **Document Processing**
   - Document indexing pipeline
   - Chunk-based document storage
   - Vector embeddings generation
   - FAISS index management

4. **API Integration**
   - Mistral API for LLM capabilities
   - FastAPI REST API for programmatic access
   - Environment-based configuration (.env)
   - Configurable model selection

5. **Feedback System**
   - Chat history logging to SQLite database
   - Thumbs up/down feedback buttons
   - Comment input for negative feedback
   - Feedback statistics dashboard

### Functional Requirements

- [x] Load and parse multiple document formats
- [x] Generate embeddings for document chunks
- [x] Build and maintain FAISS vector index
- [x] Semantic search with configurable top-k results
- [x] Context-aware response generation
- [x] Streamlit chat interface
- [x] Environment-based configuration
- [x] FastAPI REST API
- [x] Chat history logging
- [x] User feedback collection

### Non-Functional Requirements

- [x] Type hints throughout codebase (Python 3.10+ style)
- [x] Clean Architecture (API → Services → Repositories → Models)
- [x] Comprehensive test coverage using pytest
- [x] Code quality via ruff/black/mypy
- [x] Documentation consistency
- [x] Security: API key protection, input validation, SSRF protection

### Security/Compliance Requirements

- **Security Standard:** OWASP Top 10
- **Compliance:** None (internal tool)
- **Data Handling:** NBA statistics and Reddit posts (public data)
- **API Keys:** Secured via .env file (gitignored)
- **Input Validation:** Pydantic models with constraints
- **SSRF Protection:** URL validation for external requests

### Technical Stack

**Core:**
- Python 3.11+
- Poetry for dependency management
- Streamlit 1.44.1
- FastAPI ^0.115.0
- Uvicorn ^0.34.0
- Pydantic ^2.0.0
- Pydantic-settings ^2.0.0

**AI/ML:**
- Mistral AI 0.4.2
- FAISS-CPU 1.10.0
- LangChain 0.3.23

**Database:**
- SQLAlchemy ^2.0.46 (feedback storage)
- SQLite (interactions.db)

**Document Processing:**
- PyPDF2 3.0.1
- PyMuPDF >=1.22.0
- python-docx 1.1.2
- pandas 2.2.3
- openpyxl 3.1.5
- easyocr
- Pillow ^10.0.0

**Development:**
- pytest ^8.0.0
- pytest-cov ^4.1.0
- pytest-asyncio ^0.24.0
- httpx ^0.28.0
- ruff ^0.8.0
- black ^24.0.0
- mypy ^1.8.0
- interrogate ^1.5.0

### Audit History

- **2026-01-21:** Initial setup - repo structure created, dependencies migrated to Poetry
- **2026-01-26:** Major refactoring - Clean Architecture, FastAPI, security, feedback system

---

## 🏗️ Architecture

### Project Structure

```
Sports_See/
├── src/                           # Source code
│   ├── __init__.py
│   ├── indexer.py                 # Document indexing CLI
│   ├── api/                       # FastAPI REST API
│   │   ├── __init__.py
│   │   ├── main.py                # App factory, middleware, exception handlers
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── chat.py            # Chat endpoints
│   │       ├── feedback.py        # Feedback endpoints
│   │       └── health.py          # Health check endpoint
│   ├── core/                      # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py              # Pydantic Settings
│   │   ├── exceptions.py          # Custom exception hierarchy
│   │   └── security.py            # Input sanitization, SSRF protection
│   ├── models/                    # Pydantic models
│   │   ├── __init__.py
│   │   ├── chat.py                # ChatRequest, ChatResponse, SearchResult
│   │   ├── document.py            # Document, DocumentChunk
│   │   └── feedback.py            # SQLAlchemy + Pydantic feedback models
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── feedback.py            # SQLite feedback repository
│   │   └── vector_store.py        # FAISS index repository
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── chat.py                # RAG pipeline orchestration
│   │   ├── embedding.py           # Mistral embedding service
│   │   └── feedback.py            # Feedback management service
│   ├── ui/                        # Streamlit interface
│   │   ├── __init__.py
│   │   └── app.py                 # Main Streamlit app
│   └── utils/                     # Utility modules
│       ├── __init__.py
│       └── data_loader.py         # Document loading utilities
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_data_loader.py
│   ├── test_feedback.py           # Feedback system tests (19 tests)
│   └── test_vector_store.py
├── docs/                          # Documentation
│   └── API.md
├── inputs/                        # Input documents (gitignored)
├── vector_db/                     # FAISS index and chunks (gitignored)
├── database/                      # SQLite databases (gitignored)
│   └── interactions.db            # Chat history and feedback
├── .env                           # Environment variables (gitignored)
├── .gitignore
├── pyproject.toml                 # Poetry configuration
├── README.md
├── PROJECT_MEMORY.md              # This file
├── DOCUMENTATION_POLICY.md
└── check_docs_consistency.py      # Documentation checker
```

### Key Components

**1. Core Configuration (`src/core/`)**
- `config.py`: Pydantic Settings with validation (chunk_size, overlap, API keys)
- `exceptions.py`: Custom exception hierarchy (AppException, ValidationError, etc.)
- `security.py`: Input sanitization, SSRF protection, URL validation

**2. Models (`src/models/`)**
- `chat.py`: ChatRequest, ChatResponse, SearchResult (Pydantic)
- `document.py`: Document, DocumentChunk
- `feedback.py`: SQLAlchemy ORM + Pydantic models for feedback

**3. Repositories (`src/repositories/`)**
- `vector_store.py`: FAISS index CRUD operations
- `feedback.py`: SQLite feedback repository with session management

**4. Services (`src/services/`)**
- `chat.py`: RAG pipeline (search → context → generate)
- `embedding.py`: Mistral embedding API wrapper
- `feedback.py`: Feedback business logic

**5. API (`src/api/`)**
- `main.py`: FastAPI app factory with CORS, middleware, exception handlers
- `routes/chat.py`: POST /chat, GET /search endpoints
- `routes/feedback.py`: Feedback CRUD endpoints
- `routes/health.py`: Health check endpoint

**6. UI (`src/ui/app.py`)**
- Streamlit interface with ChatService integration
- Feedback buttons (thumbs up/down)
- Comment form for negative feedback
- Feedback statistics in sidebar

**7. Indexer (`src/indexer.py`)**
- CLI tool for document indexing
- Uses EmbeddingService and VectorStoreRepository

---

## 🔄 Development Workflow

### Adding New Features

1. Implement in appropriate layer:
   - `models/` for data structures
   - `repositories/` for data access
   - `services/` for business logic
   - `api/routes/` for endpoints
2. Add tests in `tests/`
3. Update inline docstrings
4. Update relevant docs in `docs/`
5. Run tests: `poetry run pytest`
6. Run linter: `poetry run ruff check .`
7. Format code: `poetry run black .`
8. Update this PROJECT_MEMORY.md if architecture changes
9. Commit with conventional commit message

### Running the Application

```bash
# Streamlit UI
poetry run streamlit run src/ui/app.py

# FastAPI Server
poetry run uvicorn src.api.main:app --reload

# Document Indexing
poetry run python src/indexer.py --rebuild
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src tests/

# Run specific test file
poetry run pytest tests/test_feedback.py -v

# Run without coverage (faster)
poetry run pytest --no-cov
```

### Code Quality

```bash
# Linting
poetry run ruff check .

# Formatting
poetry run black .

# Type checking
poetry run mypy src/
```

---

## 📝 Key Decisions

### 1. Clean Architecture
- Separation of concerns: API → Services → Repositories → Models
- Dependency injection pattern
- Each layer has single responsibility

### 2. Poetry over pip
- Better dependency resolution
- Lock file for reproducibility
- Dev/prod dependency separation

### 3. FAISS over alternatives
- Fast similarity search
- CPU-friendly (no GPU required)
- Mature and stable

### 4. Mistral AI
- Good French language support
- Competitive pricing
- Embedding + chat in one API

### 5. SQLite for Feedback
- Lightweight, no server needed
- SQLAlchemy ORM for clean data access
- Separate from vector store

### 6. FastAPI + Streamlit
- FastAPI for programmatic access
- Streamlit for user interface
- Shared services layer

---

## 🚀 Quick Start

### Initial Setup

```bash
# Install Poetry (if not already installed)
# See: https://python-poetry.org/docs/#installation

# Install dependencies
poetry install

# Create .env file with API key
echo "MISTRAL_API_KEY=your_key_here" > .env

# Place documents in inputs/
# Run indexer
poetry run python src/indexer.py

# Launch Streamlit UI
poetry run streamlit run src/ui/app.py

# Or launch FastAPI
poetry run uvicorn src.api.main:app --reload
```

### API Endpoints

- `GET /health` - Health check
- `POST /api/v1/chat` - Chat with RAG
- `GET /api/v1/search` - Semantic search
- `POST /api/v1/feedback` - Submit feedback
- `GET /api/v1/feedback/stats` - Feedback statistics
- `GET /api/v1/feedback/negative` - Negative feedback with comments
- `GET /api/v1/feedback/interactions` - Recent interactions

---

## 🐛 Known Issues

- SQLite file locking on Windows requires proper engine disposal (handled in tests)
- `datetime.utcnow()` deprecation warning in SQLAlchemy (cosmetic)

---

## 📚 Related Documents

- [README.md](README.md) - User-facing documentation
- [DOCUMENTATION_POLICY.md](DOCUMENTATION_POLICY.md) - Documentation guidelines
- [docs/API.md](docs/API.md) - API documentation

---

## 🔮 Future Enhancements

- [x] Add conversation history persistence
- [x] Implement user feedback system
- [ ] Support for more document formats
- [ ] Multilingual support (English + French)
- [ ] Query classification (RAG vs direct answer)
- [ ] Batch indexing improvements
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Feedback analytics dashboard
- [ ] Export feedback data

---

---

## Update: 2026-02-06 — RAGAS Evaluation, Data Pipeline, Logfire Observability

### New Packages

**`src/evaluation/`** — RAGAS-based RAG quality evaluation
- `models.py`: TestCategory (simple/complex/noisy), EvaluationTestCase, EvaluationSample, MetricScores, CategoryResult, EvaluationReport
- `test_cases.py`: 10 categorized NBA business questions
- `evaluate_ragas.py`: Generate samples → run RAGAS evaluate → build report → print comparative table
- Metrics: Faithfulness, ResponseRelevancy, LLMContextPrecisionWithoutReference, LLMContextRecall
- Uses `langchain-mistralai` → `ChatMistralAI` → `LangchainLLMWrapper` for RAGAS evaluator

**`src/pipeline/`** — Validated data preparation pipeline
- `models.py`: Pydantic models for every stage boundary (LoadStageInput/Output, CleanedDocument, ChunkData, QualityCheckResult, EmbedStageOutput, IndexStageOutput, PipelineResult)
- `quality_agent.py`: Pydantic AI Agent for optional LLM-powered chunk quality validation
- `data_pipeline.py`: DataPipeline class — load → clean → chunk → (quality_check) → embed → index

**`src/core/observability.py`** — Logfire integration
- Centralized config with graceful no-op fallback when Logfire is not installed/configured
- `@logfire.instrument()` decorators on ChatService, EmbeddingService, VectorStoreRepository, all pipeline stages

### SDK Migration

- Upgraded `mistralai` from 0.4.2 to >=1.2.5 (v1.12.0 installed)
- `MistralClient` → `Mistral`, `client.chat()` → `client.chat.complete()`, `client.embeddings(input=)` → `client.embeddings.create(inputs=)`, `ChatMessage` → dict, `MistralAPIException` → `SDKError`

### New Dependencies

- ragas >=0.2.0, langchain-mistralai >=0.2.0, datasets >=2.0.0
- pydantic-ai >=0.1.0
- logfire >=1.0.0

### Test Suite

- 145 tests total, all passing (was 95)
- New: test_evaluation (16), test_pipeline (13), test_pipeline_models (19)

### Known Issues

- pyarrow compatibility: ragas imports trigger `pyarrow.PyExtensionType` error; fixed by lazy-importing ragas inside functions
- FAISS + torch AVX2 crash on Windows: fixed by lazy-loading easyocr in data_loader.py

**Maintainer:** Shahu
**Last Updated:** 2026-02-07 (Phase 2: SQL Integration)

---

## Update: 2026-02-07 — Phase 2: Excel Data Integration & SQL Tool

### Overview

Added **structured NBA statistics querying** via SQL database to complement existing vector search (unstructured documents). Users can now ask precise statistical questions ("Who has the most rebounds?") alongside contextual questions ("Why is he effective?").

### New Components

**1. Database Schema (`src/repositories/nba_database.py`)**
- **Teams table**: 30 NBA teams (abbreviation, name)
- **Players table**: 569 players (name, team, age)
- **Player_stats table**: 569 stat records with 45 columns (pts, reb, ast, fg%, advanced metrics, etc.)
- SQLAlchemy ORM models with relationships
- NBADatabase repository with CRUD operations

**2. Pydantic Validation Models (`src/models/nba.py`)**
- `PlayerStats`: 48 fields with validators (percentages, decimals, time-format fixes)
- `Player`, `Team`: Basic entity models
- Handles Excel formatting issues (e.g., "15:00:00" → 3PM)
- Field-level validation with min/max ranges

**3. Ingestion Pipeline (`scripts/load_excel_to_db.py`)**
- Reads `inputs/regular NBA.xlsx` (569 players, 45 columns)
- Validates with Pydantic models
- Inserts into SQLite database
- **Results**: 30 teams, 569 players, 569 stats records (0 errors)
- Usage: `poetry run python scripts/load_excel_to_db.py --drop`

**4. LangChain SQL Tool (`src/tools/sql_tool.py`)**
- **NBAGSQLTool**: Natural language → SQL → results
- **8 Few-Shot Examples**: Common query patterns (top scorers, averages, comparisons)
- **Mistral LLM**: Temperature=0.0 for deterministic SQL generation
- **Methods**: `generate_sql()`, `execute_sql()`, `query()`, `format_results()`
- Schema-aware prompts with column descriptions

### Architecture Changes

**New Directory Structure**:
```
Sports_See/
├── database/
│   └── nba_stats.db               # SQLite database (569 players)
├── src/
│   ├── models/
│   │   └── nba.py                 # Pydantic NBA models
│   ├── repositories/
│   │   └── nba_database.py        # SQLAlchemy ORM + repository
│   └── tools/
│       └── sql_tool.py            # LangChain SQL agent
└── scripts/
    ├── load_excel_to_db.py        # Excel → SQLite pipeline
    ├── extract_excel_schema.py    # Schema analysis utility
    ├── read_nba_data.py           # Excel reader
    └── test_sql_tool.py           # SQL tool test script
```

### Hybrid Querying (Planned Integration)

**Query Classification**:
- **Statistical** → SQL Tool (e.g., "Who scored the most points?")
- **Contextual** → Vector Search (e.g., "Why is LeBron the GOAT?")
- **Hybrid** → Both sources (e.g., "Compare Jokic and Embiid's stats and explain who's better")

**Implementation Plan**:
1. Add query classifier to `ChatService`
2. Route statistical queries to SQL tool
3. Route contextual queries to vector search
4. Combine results for hybrid queries
5. Update system prompt to handle both sources

### Performance Metrics

- **Database size**: ~250 KB (negligible)
- **Query performance**: 10-20ms (local SQLite)
- **LLM SQL generation**: ~500-1000ms (Mistral API)
- **Cost per query**: ~$0.0001 (SQL generation)

### Known Limitations

1. **Single season data**: No historical trends
2. **No game-by-game data**: Only season aggregates
3. **Static team names**: Hardcoded in script
4. **LLM hallucination risk**: Mitigated with few-shot examples + temperature=0.0

### Testing Status

- ✅ Ingestion pipeline tested (569 players loaded successfully)
- ✅ Pydantic validation working (0 errors)
- ✅ SQL tool created with 8 few-shot examples
- ⚠️ Unit tests pending
- ⚠️ Integration into ChatService pending

### Next Steps

1. Fix FewShotPromptTemplate syntax ✅ (Done)
2. Test SQL tool end-to-end ⚠️
3. Integrate SQL tool into ChatService ⚠️
4. Add query classification logic ⚠️
5. Write unit tests ⚠️
6. Add hybrid query handling ⚠️

### Documentation

- [docs/PHASE2_SQL_INTEGRATION.md](docs/PHASE2_SQL_INTEGRATION.md) - Complete Phase 2 documentation
- Sample queries, architecture diagrams, integration plan

**Maintainer:** Shahu
**Last Updated:** 2026-02-07 (Phase 2: SQL Integration)

---

## Update: 2026-02-07 — Phase 5: Prompt Optimization + Quick Test Methodology

### Overview
Achieved **major improvements** in faithfulness (+37%) and complex query handling by optimizing system prompt. Introduced **quick-test methodology** to rapidly iterate on prompt variations before full evaluation.

### Phase 5 Results (47 samples)
- **Faithfulness**: 0.473 → 0.648 (+37%)
- **Answer Relevancy**: 0.112 → 0.183 (+63%)
- **Context Precision**: 0.595 → 0.803 (+35%)
- **Complex Query Breakthrough**: 0.000 → 0.270 answer relevancy (FIRST SUCCESS across all phases)

### Key Finding
**French vs English**: NO difference (0.3%) — instruction #4 "say if info not in context" was the toxic element causing refusals.

**Maintainer:** Shahu | **Date:** 2026-02-07

---

## Update: 2026-02-08 — Phase 6: Retrieval Quality (Quality Filter + Content Metadata)

### Iteration 1 - Filename-Based (12-sample subset)
- **Quality filter**: Removed 47/302 chunks (15.6%) with excessive NaN values
- **Results**: Faithfulness +30.5%, Answer Relevancy +28.7% (still low at 0.064), Refusals -25%

### Iteration 2 - Content-Based (ABANDONED)
- **Problem**: Filename tagging failed for Reddit PDFs → "unknown"
- **Solution**: Analyze chunk CONTENT with regex patterns (PTS, AST, team names, player names+stats)
- **Classification**: player_stats (2+ stat patterns), team_stats (2+ team patterns), game_data, discussion
- **Fatal Flaw**: Regex patterns matched HEADERS (which contain "pts", "assists" text) instead of actual stat ROWS (which contain numbers)
- **Result**: Only 3/255 chunks tagged as "player_stats" — all were column definitions, not data!
- **Impact**: Simple queries dropped to 0.000 answer relevancy (vs 0.247 in Phase 5)
- **Root Cause**: Inverted classification — metadata filtering excluded the exact chunks needed
- **Status**: ABANDONED — See phase6_failure_analysis.md

**Maintainer:** Shahu | **Date:** 2026-02-08

---

## Update: 2026-02-08 — Phase 7: Query Expansion + RAGAS Reproducibility Analysis

### Overview
Disabled broken metadata filtering from Phase 6 and implemented **NBA-specific query expansion** to improve keyword matching. Conducted **reproducibility study** to distinguish real improvements from RAGAS evaluation variance.

### Phase 7 Implementation

**QueryExpander Module (`src/services/query_expansion.py`)**:
- **16 stat types**: PTS, AST, REB, STL, BLK, 3P%, FG%, FT%, PER, TS%, ORTG, DRTG, TOV, MIN, USG
- **16 teams**: Full names + abbreviations (Lakers/LAL, Celtics/BOS, Warriors/GSW, etc.)
- **10 player nicknames**: LeBron/King James, Curry/Chef Curry, Giannis/Greek Freak, Jokic/Joker, etc.
- **12 query synonyms**: leader/top/best, compare/versus, average/mean, rookie/first-year, etc.
- **Smart expansion strategy**:
  - <8 words: 4 expansions (aggressive)
  - 8-12 words: 3 expansions (moderate)
  - 12-15 words: 2 expansions (light)
  - >15 words: 1 expansion (minimal)
- **Max expansion terms**: 15 (increased from baseline 10)

**ChatService Changes**:
- Metadata filtering **DISABLED** (broken in Phase 6)
- Query expansion **ENABLED** via `QueryExpander.expand_smart(query)`
- Embed expanded query instead of original for better keyword coverage

### Phase 7 Results (47 samples, Gemini 2.0 Flash Lite)

| Metric | Phase 5 Original | Phase 5 Re-run | Phase 7 | Apparent Change | Real Change |
|--------|------------------|----------------|---------|-----------------|-------------|
| **Faithfulness** | 0.648 | 0.636 | 0.461 | -28.8% | **-27.5%** ✗ |
| **Answer Relevancy** | 0.183 | 0.236 | 0.231 | +26.2% | **-2.1%** ≈ |
| **Context Precision** | 0.803 | 0.688 | 0.750 | -6.6% | **+9.0%** ✓ |
| **Context Recall** | 0.585 | 0.610 | 0.681 | +16.4% | **+11.6%** ✓ |

**Real Change** = Phase 5 Re-run → Phase 7 (controls for evaluation variance)

### Key Findings: RAGAS Evaluation Variance

**Reproducibility Study**: Re-ran Phase 5 evaluation with identical configuration to measure variance

**Variance by Metric** (Phase 5 Original vs Re-run):
- **Faithfulness**: ±16.0% average variance (Moderate stability)
- **Answer Relevancy**: ±69.7% average variance (**Very Poor** — unreliable for fine-grained comparisons)
- **Context Precision**: ±13.9% average variance (Moderate stability)
- **Context Recall**: ±22.7% average variance (Poor stability)

**Critical Discovery**: Faithfulness dropped **even for queries with 0 expansion terms** (noisy and conversational categories)

| Category | Typical Expansion | Faithfulness P5→P7 | Conclusion |
|----------|-------------------|---------------------|------------|
| Simple | 20 terms | -23.4% | Expansion may contribute |
| Complex | 2 terms | -18.0% | Minimal expansion, still dropped |
| Noisy | 0 terms | -35.1% | **NO expansion, worst drop!** |
| Conversational | 0 terms | -35.3% | **NO expansion, worst drop!** |

**Hypothesis**: Faithfulness drop is **NOT primarily caused by query expansion**. Likely due to:
1. RAGAS evaluation variance (±16-28% across categories)
2. Gemini API stochasticity (different API calls score identical responses differently)
3. Sample generation timing differences

### Phase 7 Trade-offs

**Gains** ✓:
- No false negatives from broken metadata filtering
- Better keyword coverage for stat abbreviations (PTS/points/scoring)
- Improved context recall (+11.6% overall, +93% for conversational queries)
- Improved context precision (+9.0%)
- Simpler architecture (no complex content tagging)

**Costs** ✗:
- Reduced faithfulness (-27.5% real drop, 0.636 → 0.461)
- Worst faithfulness drops in noisy (-35%) and conversational (-35%) categories
- Reduced source diversity (expansion prioritizes keyword matches)
- **No real relevancy gain** (+26% was mostly evaluation variance)

### Investigation Scripts

- `scripts/investigate_faithfulness.py`: Analyzes query expansion impact on retrieval
- `scripts/analyze_metadata.py`: Phase 6 failure diagnosis
- `scripts/visualize_comparison.py`: Generates comparison charts
- `phase5_vs_phase7_comparison.md`: Comprehensive analysis report with 3 options
- `phase6_failure_analysis.md`: Root cause documentation

### Visualizations

Generated in `evaluation_results/visualizations/`:
- `overall_metrics_comparison.png`: Bar chart of 4 metrics across 3 evaluations
- `faithfulness_by_category.png`: Category-level faithfulness comparison
- `evaluation_variance.png`: Variance magnitude by metric
- `category_heatmap.png`: All metrics × categories with P5→P7 change heatmap

### Decision: Accept Phase 7

**Rationale**:
- Context metrics improved meaningfully (+9-11%)
- Avoids catastrophic failures from broken metadata filtering (Phase 6's 0.000 relevancy)
- Faithfulness drop is concerning but may be partially due to evaluation variance
- Query expansion provides valuable keyword normalization (e.g., "PTS" = "points" = "scoring")
- Answer relevancy "improvement" (+26%) was evaluation noise, not real gain

**Recommendation**: Monitor user feedback for hallucination complaints. If faithfulness becomes problematic, implement prompt-based constraints in Phase 8 rather than rolling back query expansion.

**True Value of Phase 7**: **Robustness** (no false negatives) and **context recall** (+11.6%), NOT relevancy scoring.

**Test Suite**: 171 tests, all passing (test_query_expansion updated for expansion limit change)

**Maintainer:** Shahu | **Date:** 2026-02-08

---

## Phase 8: Faithfulness-Constrained Prompts (2026-02-08)

### Objective
Improve faithfulness score (currently 0.461, target >0.65) through prompt engineering, without rolling back Phase 7 query expansion gains.

### Approach
Test three prompt variations that enforce citation and context-only answering:

1. **strict_constraints**: Harsh rules-based prompt with explicit "I don't have that information" fallback
2. **citation_required** (✓ **Winner**): Balanced prompt requiring `[Source: <name>]` citations for all facts
3. **verification_layer**: Step-by-step verification prompt (read→answer→verify)

### Subset Testing Results (12 samples, 3 per category)

**LLM**: Gemini 2.0 Flash Lite (consistent with Phase 5/7 evaluations)
**Search**: Vector-only via `ChatService.search()` (Phase 7 query expansion enabled)
**Note**: SQL hybrid search NOT tested (evaluation uses search() not chat() method)

| Prompt | Refusal Rate | Avg Length | Assessment |
|--------|--------------|------------|------------|
| strict_constraints | 83% (10/12) | 51 chars | ❌ Too conservative |
| **citation_required** | **17% (2/12)** | **234 chars** | ✅ **BEST** |
| verification_layer | 42% (5/12) | 387 chars | ⚠️ Verbose |

**Winner**: `citation_required` prompt
- Low refusal rate (only refuses when data truly missing)
- Clean citation format: `[Source: filename.xlsx (Feuille: Sheet)]`
- Concise but complete (234 chars avg)
- Successfully answered vague queries (e.g., "tall guy from milwaukee" → Giannis Antetokounmpo stats with citations)

### Full Evaluation (47 samples) - IN PROGRESS

**Script**: [scripts/evaluate_phase8.py](scripts/evaluate_phase8.py)
**Checkpoint**: `evaluation_checkpoint_phase8.json`
**Status**: Running (22/47 samples completed as of 2026-02-08 13:30)
**Expected Completion**: ~10-15 minutes total

**Evaluation Configuration**:
- Prompt: `citation_required` (Phase 8 winner)
- LLM: Gemini 2.0 Flash Lite (generation) + Gemini 2.0 Flash Lite (RAGAS evaluation)
- Embeddings: Mistral embeddings (FAISS index + RAGAS)
- Metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall
- Incremental checkpointing enabled (resumes on failure)

### Key Implementation Details

**Citation-Required Prompt Template**:
```
You MUST follow these rules:
- Answer ONLY using information from the CONTEXT below
- When stating a fact or statistic, cite it as: [Source: <source_name>]
- If unsure or information is missing, say: "The available data doesn't specify this."
- Never infer or extrapolate beyond what's explicitly stated
- Keep answers factual and concise
```

**Why Gemini for Evaluation?**
- Consistent with Phase 5 and Phase 7 evaluations
- Production (`app.py`) uses Mistral, but evaluations use Gemini for fair comparison
- Avoids Mistral rate limits (more generous free tier on Gemini)

**Why Vector-Only Search?**
- Evaluation scripts call `search()` not `chat()` to access intermediate artifacts (context, search results) for RAGAS
- `search()` = vector-only (no SQL hybrid routing)
- `chat()` = hybrid routing (SQL for statistical queries, vector for contextual)
- Production uses `chat()` with SQL hybrid search enabled

### GLOBAL_POLICY Enforcement Setup (2026-02-08)

**Status**: ✅ **Already enforced** - scripts and hooks in place

**Existing Infrastructure**:
- ✅ Pre-commit hooks configured ([.pre-commit-config.yaml](.pre-commit-config.yaml))
- ✅ File header validation ([scripts/global_policy/validate_changed_files.py](scripts/global_policy/validate_changed_files.py))
- ✅ File location validation ([scripts/global_policy/validate_file_locations.py](scripts/global_policy/validate_file_locations.py))
- ✅ Orphaned file detection ([scripts/global_policy/check_orphaned_files.py](scripts/global_policy/check_orphaned_files.py))
- ✅ CHANGELOG.md following Keep a Changelog format
- ✅ All .py files have 5-field headers (FILE, STATUS, RESPONSIBILITY, LAST MAJOR UPDATE, MAINTAINER)

**Policy Reference**: `C:\Users\shahu\Documents\coding_agent_policies\GLOBAL_POLICY.md` (v1.15)

### Next Steps (Post-Phase 8 Evaluation)

1. **Analyze Phase 8 RAGAS Results**:
   - Compare faithfulness: Phase 7 (0.461) vs Phase 8 (target >0.65)
   - Check if citation constraints cause answer relevancy drop
   - Evaluate category-level performance

2. **Decision Point**:
   - **If faithfulness ≥0.65**: Deploy Phase 8 prompt to production
   - **If faithfulness <0.65**: Investigate Phase 9 options (stricter prompts, retrieval tuning)
   - **If answer relevancy drops >10%**: Balance faithfulness vs helpfulness trade-off

3. **Production Deployment** (if Phase 8 succeeds):
   - Update `SYSTEM_PROMPT_TEMPLATE` in [src/services/chat.py](src/services/chat.py) to `citation_required` prompt
   - Run full test suite (172 tests)
   - Update CHANGELOG.md with Phase 8 deployment
   - Monitor user feedback for hallucination rates

**Maintainer:** Shahu | **Date:** 2026-02-08

---

## Phase 8: Full RAGAS Evaluation Results (2026-02-08)

### Execution Summary
- **Status**: ✅ **Complete** (47/47 samples evaluated)
- **Prompt**: `citation_required` (winner from 12-sample subset testing)
- **LLM**: Gemini 2.0 Flash Lite
- **Checkpoint**: Incremental evaluation with resume capability
- **Bugs Fixed**:
  1. Missing `category` field in EvaluationSample → Added to constructor
  2. Wrong CategoryResult field names → Changed to `count`, `avg_*` prefix
  3. RAGAS API incompatibility → Migrated to `EvaluationDataset.from_list()`
  4. Column name mismatch → `context_precision` → `llm_context_precision_without_reference`
  5. Unicode encoding error → Changed symbols from ✓✗→ to ASCII +-

### Overall Results (Phase 7 → Phase 8)

| Metric | Phase 7 | Phase 8 | Change | Assessment |
|--------|---------|---------|--------|------------|
| **Faithfulness** | 0.461 | **0.478** | **+3.7%** | ⚠️ Improved but far from target (65%) |
| Answer Relevancy | 0.231 | 0.223 | -3.5% | ✗ Slight drop |
| Context Precision | 0.750 | 0.751 | +0.1% | = Stable |
| Context Recall | 0.681 | 0.670 | -1.6% | ≈ Stable |

### Category-Level Results

**SIMPLE (12 samples)**:
- Faithfulness: 0.438 → 0.368 (-15.8%) ✗ **WORSE** — Citation constraints overly conservative
- Answer Relevancy: 0.247 → 0.316 (+27.9%) ✓ BETTER

**COMPLEX (12 samples)**:
- Faithfulness: 0.607 → 0.681 (+12.2%) ✓ **BETTER** — Citations help multi-hop reasoning
- Answer Relevancy: 0.203 → 0.129 (-36.4%) ✗ **MUCH WORSE** — Verbose citations hurt relevancy

**NOISY (11 samples)**:
- Faithfulness: 0.403 → 0.508 (+26.1%) ✓ **MUCH BETTER** — Citations force grounding
- Answer Relevancy: 0.200 → 0.252 (+26.0%) ✓ BETTER

**CONVERSATIONAL (12 samples)**:
- Faithfulness: 0.385 → 0.356 (-7.5%) ✗ WORSE
- Answer Relevancy: 0.270 → 0.196 (-27.4%) ✗ **MUCH WORSE** — Citations clash with casual tone

### Key Findings

1. **TARGET MISSED**: Faithfulness 0.478 vs target >0.65 (**-26% gap**)
2. **Category-Specific Trade-offs**: Citation prompt helps COMPLEX/NOISY but hurts SIMPLE/CONVERSATIONAL
3. **Answer Relevancy Problem**: Severe drops on COMPLEX (-36%) and CONVERSATIONAL (-27%) categories
4. **Retrieval Quality Strong**: Context precision (75%) and recall (67%) are solid → hallucination is LLM-side, not retrieval-side

### Root Cause Analysis

**Why Citation Prompt Helps Some Categories:**
- COMPLEX: Multi-hop queries benefit from forced grounding to sources
- NOISY: Ambiguous queries forced to stick to documents (reduces hallucination)

**Why Citation Prompt Hurts Others:**
- SIMPLE: Over-conservative — refuses straightforward answers
- CONVERSATIONAL: Citations bloat responses, reducing relevancy scores

**Why Overall Faithfulness Still Low (48%):**
- Citation prompt addresses symptoms (verbose citations) not root cause (weak LLM instruction-following)
- Gemini 2.0 Flash Lite may not be capable enough for strict grounding

### Phase 9 Recommendations

**Option A: Hybrid Prompt Strategy** (RECOMMENDED)
- Category-aware prompt selection:
  - Use `citation_required` for COMPLEX/NOISY
  - Use simpler prompt for SIMPLE/CONVERSATIONAL
- Implement `get_prompt_template(category: TestCategory) -> str`

**Option B: Retrieval Quality Focus**
- Increase retrieved chunks: k=5 → k=10
- Add chunk relevance threshold filtering (only include chunks with similarity >0.7)
- Re-rank chunks by relevance before passing to LLM

**Option C: Model Upgrade**
- Switch from Gemini 2.0 Flash Lite to:
  - Mistral Large (better instruction-following)
  - Gemini 1.5 Pro (more capable reasoning)
- Trade-off: Higher cost, slower responses

**Option D: Accept Current Baseline**
- Phase 7/8 faithfulness (46-48%) may be realistic limit for current architecture
- Focus on improving other dimensions:
  - Context precision/recall (already strong at 75%/67%)
  - User feedback collection for identifying specific hallucination patterns

**Maintainer:** Shahu | **Date:** 2026-02-08 (Phase 8 Completion)


---

## Phase 9: Hybrid Category-Aware Prompts (2026-02-08)

### Objective
Implement **Option A from Phase 8 recommendations**: Category-aware prompt selection to address trade-offs discovered in Phase 8, where citation prompt helped COMPLEX/NOISY queries but hurt SIMPLE/CONVERSATIONAL queries.

### Implementation Strategy

**Hybrid Prompt Approach**:
- **SIMPLE queries**: Simple prompt without citation requirements (concise, direct answers)
- **COMPLEX queries**: Citation-required prompt (forces grounding, helps multi-hop reasoning)
- **NOISY queries**: Citation-required prompt (reduces hallucination on ambiguous queries)
- **CONVERSATIONAL queries**: Conversational prompt (natural tone, no citation bloat)

### Prompt Templates

**SIMPLE Prompt** (Minimal constraints):
```
You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

INSTRUCTIONS:
- Answer directly and concisely
- Use only information from the context above
- If information is missing, say so briefly
```

**COMPLEX/NOISY Prompt** (Citation-required):
```
You MUST follow these rules:
- Answer ONLY using information from the CONTEXT below
- When stating a fact or statistic, cite it as: [Source: <source_name>]
- If unsure or information is missing, say: "The available data doesn't specify this."
- Never infer or extrapolate beyond what's explicitly stated
- Keep answers factual and concise
```

**CONVERSATIONAL Prompt** (Natural tone):
```
INSTRUCTIONS:
- Answer naturally and conversationally
- Base your answer on the context above
- Be concise and helpful
- If information isn't in the context, say so clearly
```

### Full Evaluation Results (47 samples)

**Execution Details**:
- **Script**: `scripts/evaluate_phase9_full.py`
- **LLM**: Gemini 2.0 Flash Lite (consistent with Phases 7-8)
- **Search**: Vector-only with Phase 7 query expansion enabled
- **Status**: ✅ Complete (47/47 samples)

### Overall Results (Phase 8 → Phase 9)

| Metric | Phase 8 | Phase 9 | Change | Assessment |
|--------|---------|---------|--------|------------|
| **Faithfulness** | 0.478 | **0.532** | **+11.4%** | ✓ **BEST since Phase 7** (but still -18% from target) |
| Answer Relevancy | 0.223 | 0.188 | -15.7% | ✗ Dropped further |
| Context Precision | 0.751 | 0.708 | -5.7% | ≈ Slight drop |
| Context Recall | 0.670 | 0.691 | +3.1% | ✓ Stable improvement |

### Category-Level Results

**SIMPLE (12 samples)**:
- Faithfulness: 0.368 → **0.375** (+1.9%) ✓ Slight improvement
- Answer Relevancy: 0.316 → 0.280 (-11.4%) ✗ Drop
- **Assessment**: Simple prompt slightly better than citation-required, but still struggling

**COMPLEX (12 samples)**:
- Faithfulness: 0.681 → **0.705** (+3.5%) ✓ **BEST category**
- Answer Relevancy: 0.129 → 0.137 (+6.2%) ✓ Slight improvement
- **Assessment**: Citation prompt working well for multi-hop reasoning

**NOISY (11 samples)**:
- Faithfulness: 0.508 → **0.363** (**-28.6%**) ✗✗ **MAJOR REGRESSION**
- Answer Relevancy: 0.252 → 0.127 (-49.6%) ✗✗ Severe drop
- **Assessment**: Citation prompt TOO strict for ambiguous/typo queries

**CONVERSATIONAL (12 samples)**:
- Faithfulness: 0.356 → **0.656** (**+84.6%**) ✓✓ **HUGE WIN**
- Answer Relevancy: 0.196 → 0.202 (+3.1%) ≈ Stable
- **Assessment**: Conversational prompt massively improved grounding while maintaining natural tone

### Key Findings

1. **Target Status**: Faithfulness 0.532 vs target >0.65 (**-18% gap** — closer but still not met)
2. **Conversational Breakthrough**: +84.6% faithfulness — category-aware prompts work for specific use cases
3. **NOISY Category Regression**: -28.6% faithfulness — citation prompt too rigid for ambiguous queries
4. **Overall Trend**: +11.4% faithfulness improvement validates hybrid approach, but NOISY handling needs refinement
5. **Answer Relevancy Decline**: Continuing downward trend (0.231 → 0.223 → 0.188) across phases

### Subset Testing Lessons Learned

**Phase 9 Subset (12 samples)**: 0.723 faithfulness (misleadingly high)
**Phase 9 Full (47 samples)**: 0.532 faithfulness (-26.4% vs subset)

**Discovery**: 12-sample subsets show high variance (only 3 samples per category) — **NOT representative of full dataset**. Subset testing abandoned for future phases.

**Phase 10 Attempt**: Refined NOISY prompt to fix regression → subset test showed 0.534 faithfulness (-26.2% vs Phase 9 subset) → **FAILED**. Confirmed subset unreliability and abandoned Phase 10.

### Root Cause Analysis

**Why Conversational Prompt Succeeded (+84.6%)**:
- Natural tone doesn't conflict with grounding constraints
- Removed citation bloat that hurt Phase 8 conversational queries
- Users ask casual questions ("Who's better, X or Y?") — conversational prompt fits use case

**Why NOISY Prompt Failed (-28.6%)**:
- Citation-required prompt forces "context-only" answers for queries with typos/ambiguity
- Ambiguous queries (e.g., "who iz the best player ever???") need interpretation, not strict grounding
- Citation prompt triggers refusals instead of best-effort interpretation

**Why Overall Faithfulness Still Low (53%)**:
- NOISY regression (-28.6%) partially offsets CONVERSATIONAL gains (+84.6%)
- SIMPLE and COMPLEX categories show minimal improvement (+1.9%, +3.5%)
- Phase 6 baseline (0.636) remains closest to target — query expansion trade-off may not be worth faithfulness cost

### Performance Comparison Across Phases

| Phase | Faithfulness | Change | Key Feature |
|-------|--------------|--------|-------------|
| **Phase 6** | **0.636** | Baseline | Metadata filtering (broken) |
| Phase 7 | 0.461 | -27.5% | Query expansion (hurts faithfulness) |
| Phase 8 | 0.478 | +3.7% | Citation-required prompt (all categories) |
| **Phase 9** | **0.532** | **+11.4%** | **Hybrid category-aware prompts** |
| Target | 0.650 | -18% gap | — |

**Best Result**: Phase 6 (0.636) was only 2% below target
**Current Best**: Phase 9 (0.532) is 18% below target but has best faithfulness since Phase 7

### Decision: Deploy Phase 9 to Production

**Rationale**:
1. **Best performance since Phase 7** (+11.4% improvement over Phase 8)
2. **Conversational queries excel** (+84.6% faithfulness) — likely dominant use case for casual users
3. **Complex queries strong** (0.705 faithfulness) — citation prompt working for analytical questions
4. **NOISY regression acceptable** — typo/ambiguous queries are edge cases (11/47 samples = 23%)
5. **Hybrid approach validated** — category-specific prompts show promise despite mixed results

**Trade-offs Accepted**:
- 18% gap from target faithfulness (0.532 vs 0.65)
- Answer relevancy continuing to decline (0.188)
- NOISY category needs future refinement
- Requires category classification logic in production

### Next Steps

**Immediate Deployment** (APPROVED):
1. Implement category classification in `ChatService` to detect query type (SIMPLE/COMPLEX/NOISY/CONVERSATIONAL)
2. Add `get_prompt_for_category(category: TestCategory) -> str` function to src/services/chat.py
3. Update `generate_response()` to use category-aware prompt templates
4. Add Phase 9 prompt constants to chat.py
5. Run full test suite (171 tests)
6. Update CHANGELOG.md with Phase 9 deployment
7. Monitor production metrics and user feedback

**Future Exploration**:
- **Phase 11**: Investigate permissive NOISY prompt (handles ambiguity gracefully without strict citations)
- **Retrieval tuning**: Increase k=5 → k=8 for better context coverage
- **Model upgrade**: Test Mistral Large for better instruction-following (if budget allows)
- **Revert consideration**: If production hallucination complaints spike, consider reverting to Phase 6 baseline (0.636 faithfulness, no query expansion complexity)

### Files Modified

- `scripts/evaluate_phase9_full.py` (Created)
- `scripts/evaluate_phase9_subset.py` (Created)
- `evaluation_results/ragas_phase9.json` (Generated)
- `phase9_hybrid_subset.json` (Generated)
- `scripts/evaluate_phase10_subset.py` (Created, Phase 10 abandoned)
- `phase10_refined_subset.json` (Generated, Phase 10 failed)

**Maintainer:** Shahu | **Date:** 2026-02-08 (Phase 9 Completion — APPROVED FOR DEPLOYMENT)

---

## Update: 2026-02-09 — LLM Migration, Hybrid Search Deployment, Database Improvements

### LLM Migration: Mistral → Gemini 2.0 Flash

**Rationale**: Gemini 2.0 Flash improved LLM comprehension of SQL data by ~25% (50% → 75% test pass rate) with same free tier rate limits (15 RPM).

**Changes**:
- `src/services/chat.py`: Replaced Mistral chat completion with `google.genai.Client` → `models.generate_content()`
- Added `google-genai` dependency to `pyproject.toml`
- Mistral still used for embeddings (FAISS index consistency)

### Hybrid Search System (Production Deployed)

**Architecture**:
- `QueryClassifier` (`src/services/query_classifier.py`): Routes queries to SQL, vector, or hybrid search
- Two-phase fallback: (1) SQL error/no results → vector search, (2) SQL succeeds but LLM says "cannot find" → retry with vector search
- SQL context formatting: numbered list format for better LLM comprehension

**Performance**:
- SQL accuracy: 84.7% for statistical queries
- Overall hybrid accuracy: 75.2%
- Category-aware prompts deployed (Phase 9)

### Database Improvements

- Added `team` (full name) column to `players` table for improved SQL generation
- NBA dictionary vectorized for glossary term lookups

### Evaluation Consolidation

- Consolidated ~15 phase-specific evaluation scripts into 3 master scripts:
  - `scripts/evaluate_sql.py` — SQL test cases (48)
  - `scripts/evaluate_vector.py` — Vector test cases (47)
  - `scripts/evaluate_hybrid.py` — Hybrid test cases (18)
- All 3 scripts support conversation-aware evaluation

**Test Suite**: 307+ tests passing

**Maintainer:** Shahu | **Date:** 2026-02-09

---

## Update: 2026-02-10 — Conversation History, Folder Consolidation, Project Cleanup

### Conversation History Feature (Full Implementation)

**New Components**:
- `src/models/conversation.py`: ConversationDB SQLAlchemy model, Pydantic schemas (Create/Update/Response/WithMessages)
- `src/repositories/conversation.py`: ConversationRepository with CRUD, message retrieval, pagination
- `src/services/conversation.py`: ConversationService — create, list, load, archive, auto-title generation
- `src/api/routes/conversation.py`: 6 REST endpoints (POST/GET/PUT/DELETE conversations)
- `src/services/chat.py`: `_build_conversation_context()` — prepends last 5 turns to LLM prompt for pronoun resolution

**Tests Added**:
- `tests/test_conversation_models.py` (~12 tests)
- `tests/test_conversation_service.py` (~22 tests)
- `tests/test_chat_with_conversation.py` (~10 tests)

### Folder Consolidation

**Before**: 4 separate root-level data directories (`inputs/`, `database/`, `vector_db/`, `data/`)
**After**: Unified under `data/`
- `data/inputs/` — raw source documents (PDFs, Excel)
- `data/sql/` — SQLite databases (nba_stats.db, interactions.db)
- `data/vector/` — FAISS index + document chunks
- `data/reference/` — dictionary/glossary files

**Files Updated**: `src/core/config.py` defaults, `.gitignore`, `data_loader.py`, `filter_vector_store.py`, 15+ scripts, 3 test files

### Vector Store Optimization

Reduced from 159 to 5 chunks (97% reduction) by excluding structured Excel data already queryable via SQL. Added `EXCLUDED_EXCEL_SHEETS` to `data_loader.py`.

### Project Cleanup

- Archived old evaluation_results files (phase-specific JSONs, charts, visualizations)
- Moved analysis .md files from evaluation_results/ to docs/
- Renamed `test_cases.py` → `vector_test_cases.py` for naming consistency
- Converted evaluation .txt reports to .md format
- Consolidated CHANGELOG.md with all missing entries

### CORRECTIONS TO EARLIER SECTIONS

**Architecture (from top of file)**: The project structure has changed significantly:
- `inputs/` → `data/inputs/`
- `vector_db/` → `data/vector/`
- `database/` → `data/sql/`
- `DOCUMENTATION_POLICY.md` — archived to `_archived/2026-02/`
- `check_docs_consistency.py` — archived to `_archived/2026-02/`
- AI Model: Production LLM is now **Gemini 2.0 Flash** (Mistral still used for embeddings)
- New directories: `src/tools/`, `src/evaluation/`, `src/pipeline/`
- New key files: `src/services/query_classifier.py`, `src/services/query_expansion.py`, `src/repositories/nba_database.py`, `src/tools/sql_tool.py`

**Test Suite**: 348 tests (up from 145), all passing except 3 external failures (Gemini 429 rate limits, Windows file locking)

**Maintainer:** Shahu | **Date:** 2026-02-10

## Vector Evaluation Consolidation (2026-02-11)

### Objective
Create production-ready vector evaluation system matching SQL evaluation consolidation structure: consolidated analysis module, API-only processing, checkpointing, comprehensive reporting.

### Implementation

**3 New Files Created**:
- `src/evaluation/run_vector_evaluation.py` (280 lines) — Main entry point with API-only processing + checkpointing
- `src/evaluation/vector_quality_analysis.py` (227 lines) — 5 analysis functions for comprehensive quality metrics
- `src/evaluation/README_VECTOR.md` — Complete documentation (usage, architecture, metrics, troubleshooting)

**Test Coverage**: 43 new tests
- `tests/evaluation/test_vector_quality_analysis.py` (25 tests) — All 5 analysis functions
- `tests/evaluation/test_run_vector_evaluation.py` (18 tests) — Checkpointing, retry logic, report generation
- **Code Coverage**: 97.36% for analysis module, 58.93% for runner

### Key Features

**API-Only Processing**:
- Uses Starlette TestClient (simulated HTTP) instead of direct service calls
- Tests full production API stack (routes → services → repositories)
- No server startup required

**Checkpointing System**:
- Saves checkpoint after EACH query (atomic writes for safety)
- Auto-resumes from checkpoint on restart
- Handles failures, rate limits, interruptions
- Checkpoint format: JSON with timestamp, results, next_index
- Auto-cleanup on successful completion

**RAGAS Integration**:
- Gemini 2.0 Flash Lite LLM (free tier, 15 RPM)
- Mistral embeddings (consistent with FAISS index)
- 4 metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall
- Lazy-import to avoid dependency conflicts

**5 Analysis Functions**:
1. `analyze_ragas_metrics()` — Overall scores, by category, low-scoring queries
2. `analyze_source_quality()` — Retrieval stats, top sources, score distribution
3. `analyze_response_patterns()` — Length, completeness, citations, confidence
4. `analyze_retrieval_performance()` — K-value, thresholds, source types
5. `analyze_category_performance()` — Per-category breakdown, comparative analysis

**2-File Output**:
- `vector_evaluation_YYYYMMDD_HHMMSS.json` — Raw results data
- `vector_evaluation_report_YYYYMMDD_HHMMSS.md` — Comprehensive report with automated insights

**Rate Limiting**:
- 9s delay between queries (Gemini free tier: 15 RPM)
- Retry logic: 15s/30s/60s exponential backoff on 429 errors
- Max 3 retries per query

**Integrated Features from scripts/evaluate_vector.py (2026-02-11)**:
- ✅ `get_vector_test_cases()` — Filters to NOISY, CONVERSATIONAL, and contextual COMPLEX queries
- ✅ `_is_followup_question()` — Detects follow-up questions requiring conversation context
- ✅ **Routing Verification** — Tracks SQL/vector/hybrid classification accuracy
- ✅ **Misclassification Detection** — Identifies and reports misclassified queries
- ✅ **Conversation ID Management** — Creates/manages conversations for CONVERSATIONAL queries
- ✅ **Interaction Storage** — Saves interactions to feedback repository for context
- ✅ **CLI Flag**: `--vector-only` to filter test cases
- ✅ **Enhanced Report**: Routing statistics and misclassifications section
- ✅ **Archived Legacy**: Moved `scripts/evaluate_vector.py` to `_archived/2026-02/scripts/`

**RAGAS Integration in Sample Script**:
- ✅ Fixed `scripts/run_vector_sample_4_cases.py` to include RAGAS metrics
- ✅ Added `calculate_ragas_metrics()` call after API evaluation
- ✅ Merged RAGAS scores into results (per-query metrics)
- ✅ Report now includes RAGAS metrics summary and per-test-case breakdown

### Files Modified/Updated
- `src/evaluation/run_vector_evaluation.py` — Added routing verification, conversation support, test case filtering
- `scripts/run_vector_sample_4_cases.py` — Added RAGAS metrics calculation and display
- `_archived/2026-02/scripts/evaluate_vector.py` — Archived old script after integration
- `CHANGELOG.md` — Updated vector evaluation consolidation entry
- `PROJECT_MEMORY.md` — This entry

### Testing Results
- ✅ 43/43 tests passing
- ✅ 97.36% coverage for analysis module
- ✅ Checkpointing validated (atomic writes, UTF-8 encoding, corruption handling)
- ✅ Report generation validated (all sections, markdown format, handles empty data)
- ✅ Retry logic validated (429 handling, non-retryable errors)
- ✅ Routing verification integrated and functional
- ✅ Conversation management integrated
- ✅ RAGAS metrics working in sample script

### Usage
```bash
# Run full vector evaluation (all test cases)
poetry run python -m src.evaluation.run_vector_evaluation

# Run vector-only test cases (NOISY, CONVERSATIONAL, contextual COMPLEX)
poetry run python -m src.evaluation.run_vector_evaluation --vector-only

# Start fresh (ignore checkpoint)
poetry run python -m src.evaluation.run_vector_evaluation --no-resume

# Run 4-case sample with RAGAS metrics
poetry run python scripts/run_vector_sample_4_cases.py
```

**Maintainer:** Shahu | **Date:** 2026-02-11 (Integration completed)

## README Consolidation & Documentation Cleanup (2026-02-11)

### Objective
Consolidate multiple README files into single comprehensive root README, remove duplicate content, and rationalize structure per GLOBAL_POLICY.md requirements.

### Problem
- **8 README files** scattered across repository (root, tests/, tests/ui/, tests/e2e/, tests/integration/, src/evaluation/)
- **843-line root README** with duplicate content and redundancies
- Multiple overlapping sections (test statistics appeared 3+ times)
- Configuration details duplicated in Quick Start and Development sections
- Verbose code examples and excessive detail in some sections

### Solution

**README Consolidation**:
- Merged 8 README files into single root README.md
- **Before**: 843 lines with duplicates
- **After**: ~500 lines (40% reduction)
- Removed redundancies:
  - Consolidated duplicate test statistics tables
  - Merged overlapping configuration sections
  - Trimmed verbose troubleshooting (90 → 40 lines)
  - Condensed development section (156 → 80 lines)
  - Simplified deployment checklist
- Improved structure:
  - Clearer section hierarchy
  - More concise descriptions
  - Removed "Roadmap" section (belongs in separate file)
  - Streamlined "Recent Updates" to key points only

**Files Deleted After Consolidation**:
- tests/README.md
- tests/ui/README_UI_TESTS.md
- tests/e2e/README.md
- tests/integration/README.md
- src/evaluation/README.md
- src/evaluation/README_VECTOR.md

**Impact**:
- ✅ Single source of truth for all documentation
- ✅ Easier to navigate and maintain
- ✅ No duplicate information
- ✅ Reduced cognitive load for contributors

### Testing Documentation Preserved
All test documentation consolidated into root README:
- 247+ test statistics (unit: 182, integration: 16, e2e: 8, ui: 65+)
- Test organization structure
- Running instructions for all test categories
- UI test categories (31 comprehensive, 26 error handling, 8 visualization)
- Evaluation system documentation (SQL, Vector, Hybrid)

**Maintainer:** Shahu | **Date:** 2026-02-11

## Repository Organization & Global Policy Compliance (2026-02-11)

### Objective
Clean up repository structure and ensure full compliance with GLOBAL_POLICY.md v1.17 standards.

### Actions Taken

**1. Root Directory Cleanup**:
- **Before**: 15+ files (docs, scripts, temp files, requirements.txt)
- **After**: Only README.md, PROJECT_MEMORY.md, CHANGELOG.md
- **Archived to `_archived/2026-02/root_docs/`** (10 documentation files):
  - _API_EVALUATION_UPDATE.md
  - _FAISS_CRASH_ANALYSIS.md
  - _FAISS_FIX_COMPLETE.md
  - _FINAL_EVALUATION_CONFIG.md
  - _ONE_TO_ONE_TEST_MAPPING_COMPLETE.md
  - _SQL_EVALUATION_FIXES.md
  - CLEANUP_INSTRUCTIONS.md
  - EVALUATION_SCRIPTS_INVENTORY.md
  - HYBRID_EVALUATION_REFACTOR_COMPLETE.md
  - VISUALIZATION_INTEGRATION_COMPLETE.md
- **Moved**: streamlit_viz_example.py to scripts/
- **Removed**:
  - requirements.txt (project uses Poetry exclusively)
  - test_results.txt (untracked temporary file)
  - Temporary files with _ prefix (already in .gitignore)

**2. File Headers Added**:
- Added 5-field headers to 2 evaluation verification scripts:
  - src/evaluation/verify_all_hybrid_ground_truth.py
  - src/evaluation/verify_all_sql_ground_truth.py
- **Result**: All 200 active Python files now have proper headers
- **Compliance**: FILE, STATUS, RESPONSIBILITY, LAST MAJOR UPDATE, MAINTAINER

**3. .gitignore Verification**:
- ✅ Temporary scripts (`scripts/_*.py`, `scripts/check_*.py`) properly ignored
- ✅ Test result files properly ignored
- ✅ Archived directories (`_archived/`) properly ignored
- ✅ No changes needed - already compliant

**4. CHANGELOG.md Updated**:
- Added entries for test suite reorganization
- Added entries for README consolidation
- Added entries for root directory cleanup
- Added entries for file header additions
- Added entries for removed/archived files
- **Format**: Follows Keep a Changelog standard with file links

### Global Policy Compliance Status

| Rule | Status | Details |
|------|--------|---------|
| **File Headers** (§242-261) | ✅ | All 200 active .py files have 5-field headers |
| **File Organization** (§366-377) | ✅ | Root clean, docs in docs/, scripts in scripts/ |
| **Dead Code Prevention** (§337-363) | ✅ | Obsolete files archived to `_archived/2026-02/` |
| **.gitignore Management** (§381-475) | ✅ | All patterns properly configured |
| **CHANGELOG Maintenance** (§264-308) | ✅ | All changes documented with file links |
| **PROJECT_MEMORY Append-Only** (§731-776) | ✅ | This entry appended (all history preserved) |

### File Organization Summary

**Before Cleanup**:
```
Sports_See/
├── README.md (843 lines)
├── tests/README.md
├── tests/ui/README_UI_TESTS.md
├── tests/e2e/README.md
├── tests/integration/README.md
├── src/evaluation/README.md
├── src/evaluation/README_VECTOR.md
├── _API_EVALUATION_UPDATE.md
├── _FAISS_CRASH_ANALYSIS.md
├── ... (8 more root docs)
├── requirements.txt
├── streamlit_viz_example.py
└── test_results.txt
```

**After Cleanup**:
```
Sports_See/
├── README.md (500 lines, comprehensive)
├── PROJECT_MEMORY.md
├── CHANGELOG.md
├── src/ (all files with headers)
├── tests/ (reorganized: core/services/integration/e2e/ui/)
├── scripts/ (streamlit_viz_example.py moved here)
├── docs/ (all documentation here)
└── _archived/2026-02/
    ├── README.md (archive documentation)
    └── root_docs/ (10 archived documentation files)
```

### Results

**Compliance**: ✅ **100% compliant with GLOBAL_POLICY.md v1.17**

**Improvements**:
- Cleaner repository structure
- Single source of truth for documentation
- All files properly organized
- No orphaned or misplaced files
- Complete file headers
- Updated CHANGELOG

**Impact**:
- Easier navigation for contributors
- Reduced cognitive load
- Better maintainability
- Clearer project structure
- Professional production-ready organization

**Maintainer:** Shahu | **Date:** 2026-02-11

---

## Entry: Unified Ground Truth Verification Script (2026-02-13)

**Change**: Merged two separate verification scripts into one unified `src/evaluation/verify_ground_truth.py`.

**Before**:
- `src/evaluation/verification/verify_all_sql_ground_truth.py` — SQL-only verification
- `src/evaluation/verification/verify_all_hybrid_ground_truth.py` — Hybrid-only verification

**After**:
- `src/evaluation/verify_ground_truth.py` — Unified verification with CLI args: `all` (default), `sql`, `hybrid`

**Deleted**:
- `src/evaluation/verification/` folder (including `__init__.py`, both old scripts, `__pycache__`)
- `tests/evaluation/verification/` folder (including old test files)

**Updated References**: README.md (4 sections), CHANGELOG.md (1 reference)

**Maintainer:** Shahu | **Date:** 2026-02-13
