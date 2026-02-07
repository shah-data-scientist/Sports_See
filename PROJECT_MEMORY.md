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
