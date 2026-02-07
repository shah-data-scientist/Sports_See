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
