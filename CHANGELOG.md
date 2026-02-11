# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **Conversation History System**: Full conversation persistence with session management ([src/models/conversation.py](src/models/conversation.py), [src/repositories/conversation.py](src/repositories/conversation.py), [src/services/conversation.py](src/services/conversation.py))
- **Conversation API**: CRUD endpoints for conversations ([src/api/routes/conversation.py](src/api/routes/conversation.py))
- **Conversation UI**: Sidebar conversation management in Streamlit — new conversation, load, archive ([src/ui/app.py](src/ui/app.py))
- **Conversation-Aware Chat**: Pronoun resolution and follow-up questions using conversation history ([src/services/chat.py](src/services/chat.py))
- **SQL Database Integration**: NBA statistics in SQLite with 569 players, 45+ stat columns ([src/repositories/nba_database.py](src/repositories/nba_database.py), [scripts/load_excel_to_db.py](scripts/load_excel_to_db.py))
- **NBA Pydantic Models**: 48-field PlayerStats validation with Excel formatting fixes ([src/models/nba.py](src/models/nba.py))
- **SQL Query Tool**: Natural language → SQL → results using LangChain + 8 few-shot examples ([src/tools/sql_tool.py](src/tools/sql_tool.py))
- **Query Classifier**: Routes queries to SQL, vector, or hybrid search based on content analysis ([src/services/query_classifier.py](src/services/query_classifier.py))
- **Query Expansion**: NBA-specific query enrichment — 16 stat types, 16 teams, 10 player nicknames, 12 synonyms ([src/services/query_expansion.py](src/services/query_expansion.py))
- **Hybrid Search**: Two-phase fallback — SQL first, vector search if SQL fails or returns "cannot find" ([src/services/chat.py](src/services/chat.py))
- **Category-Aware Prompts**: Phase 9 prompt optimization — different prompts for SIMPLE, COMPLEX, NOISY, CONVERSATIONAL queries ([src/services/chat.py](src/services/chat.py))
- **Evaluation Test Suites**: 3 separate test case files — SQL (48 cases), Vector (47 cases), Hybrid (18 cases) ([src/evaluation/sql_test_cases.py](src/evaluation/sql_test_cases.py), [src/evaluation/vector_test_cases.py](src/evaluation/vector_test_cases.py), [src/evaluation/hybrid_test_cases.py](src/evaluation/hybrid_test_cases.py))
- **3 Master Evaluation Scripts**: SQL, Vector, and Hybrid evaluation with conversation support ([scripts/evaluate_sql.py](scripts/evaluate_sql.py), [scripts/evaluate_vector.py](scripts/evaluate_vector.py), [scripts/evaluate_hybrid.py](scripts/evaluate_hybrid.py))
- **E2E Tests**: End-to-end tests for vector, SQL, hybrid flows, and error handling ([tests/test_e2e.py](tests/test_e2e.py))
- **Conversation Tests**: Model validation, service lifecycle, and chat integration tests ([tests/test_conversation_models.py](tests/test_conversation_models.py), [tests/test_conversation_service.py](tests/test_conversation_service.py), [tests/test_chat_with_conversation.py](tests/test_chat_with_conversation.py))
- **Classification Tests**: Evaluation routing and misclassification detection ([tests/test_classification_evaluation.py](tests/test_classification_evaluation.py))
- **Embedding Tests**: 20 unit tests for Mistral embedding service ([tests/test_embedding.py](tests/test_embedding.py))
- **SQL Conversation Demo Tests**: Conversation-aware SQL query tests ([tests/test_sql_conversation_demo.py](tests/test_sql_conversation_demo.py))
- **RAGAS Evaluation Script**: Automated RAG quality assessment measuring faithfulness, answer relevancy, context precision, and context recall ([src/evaluation/evaluate_ragas.py](src/evaluation/evaluate_ragas.py))
- **Evaluation Models**: Pydantic models for test cases, samples, metric scores, and reports ([src/evaluation/models.py](src/evaluation/models.py))
- **Data Preparation Pipeline**: Validated pipeline with load, clean, chunk, embed, and index stages ([src/pipeline/data_pipeline.py](src/pipeline/data_pipeline.py))
- **Pipeline Stage Models**: Pydantic models for every pipeline stage boundary (I/O validation) ([src/pipeline/models.py](src/pipeline/models.py))
- **Pydantic AI Quality Agent**: Optional LLM-powered chunk quality validation using Pydantic AI Agent ([src/pipeline/quality_agent.py](src/pipeline/quality_agent.py))
- **Logfire Observability**: Pydantic Logfire integration with `@logfire.instrument()` on all pipeline stages ([src/core/observability.py](src/core/observability.py))
- **Feedback System**: Chat history logging with thumbs up/down feedback ([src/models/feedback.py](src/models/feedback.py), [src/repositories/feedback.py](src/repositories/feedback.py), [src/services/feedback.py](src/services/feedback.py))
- **Feedback API**: REST endpoints for submitting/querying feedback ([src/api/routes/feedback.py](src/api/routes/feedback.py))
- **Feedback UI**: Thumbs up/down buttons with comment form in Streamlit ([src/ui/app.py](src/ui/app.py))
- **GLOBAL_POLICY.md Enforcement**: Validation scripts for file headers, locations, orphaned files ([scripts/global_policy/](scripts/global_policy/))
- **Pre-commit hooks**: Automated validation on commits ([.pre-commit-config.yaml](.pre-commit-config.yaml))
- **File documentation headers**: All .py files now have 5-field headers

### Changed
- **LLM Migration**: Switched from Mistral AI to Gemini 2.0 Flash for response generation — 25% improvement in data comprehension ([src/services/chat.py](src/services/chat.py))
- **System Prompt**: English-only context headers replacing mixed French/English — fixes "cannot find information" false negatives ([src/services/chat.py](src/services/chat.py))
- **SQL Context Formatting**: Numbered list format for LLM comprehension — single results use bullet points, limited to top 20 results ([src/services/chat.py](src/services/chat.py))
- **Vector Store Optimization**: Reduced from 159 to 5 chunks (97% reduction) by excluding structured Excel data already in SQL ([src/utils/data_loader.py](src/utils/data_loader.py))
- **Folder Consolidation**: Unified 4 data directories (`inputs/`, `database/`, `vector_db/`, `data/`) under single `data/` parent — `data/inputs/`, `data/sql/`, `data/vector/`, `data/reference/` ([src/core/config.py](src/core/config.py))
- **Mistral AI SDK**: Upgraded from `mistralai==0.4.2` to `mistralai>=1.2.5` (v1.12.0) ([src/services/embedding.py](src/services/embedding.py))
- **Config Settings**: Updated default paths for consolidated data directory ([src/core/config.py](src/core/config.py))
- **Ruff Config**: Migrated to `[tool.ruff.lint]` prefix; added D205, D212, D415 ignores ([pyproject.toml](pyproject.toml))
- **Dependencies**: Added ragas, langchain-mistralai, datasets, pydantic-ai, logfire, google-genai ([pyproject.toml](pyproject.toml))
- **API Dependencies**: Extracted `get_chat_service` to `dependencies.py` to fix circular imports ([src/api/dependencies.py](src/api/dependencies.py))
- **Test Suite**: Expanded from 95 to 348 tests covering all new features
- **.gitignore**: Updated for consolidated data/ directory structure

### Fixed
- **French vs English context headers**: Mixed language headers caused LLM to respond "cannot find information" even when data was present
- **FAISS + torch AVX2 crash**: Lazy-load easyocr only when OCR is needed to avoid process crash on Windows
- **Windows SQLite file locking**: Added `repo.close()` for proper SQLAlchemy engine disposal in tests
- **Evaluation index misalignment**: Fixed bug where skipped queries caused samples[i] to evaluate against test_cases[j] where i!=j
- **Windows charmap encoding**: Added `encoding="utf-8"` to all `Path.write_text()` calls

### Removed
- **DOCUMENTATION_POLICY.md**: Archived to `_archived/2026-02/` (superseded by GLOBAL_POLICY.md)
- **check_docs_consistency.py**: Archived to `_archived/2026-02/` (replaced by enforcement scripts)
- **Redundant evaluation scripts**: Consolidated ~15 phase-specific scripts into 3 master scripts
- **Old data directories**: `inputs/`, `database/`, `vector_db/` replaced by `data/` structure

## [0.1.0] - 2026-01-21

### Added
- **Project Setup**: Initial repository structure with Poetry, src/, tests/, docs/
- **Clean Architecture**: API → Services → Repositories → Models layering
- **RAG Pipeline**: FAISS vector search + Mistral AI response generation ([src/services/chat.py](src/services/chat.py))
- **FastAPI REST API**: Chat and search endpoints ([src/api/](src/api/))
- **Streamlit UI**: Chat interface with source display ([src/ui/app.py](src/ui/app.py))
- **Document Indexer**: Multi-format document processing ([src/indexer.py](src/indexer.py))
- **Pydantic Config**: Validated settings with Pydantic Settings ([src/core/config.py](src/core/config.py))
- **Security Module**: Input sanitization and SSRF protection ([src/core/security.py](src/core/security.py))
- **Custom Exceptions**: Structured error hierarchy ([src/core/exceptions.py](src/core/exceptions.py))
- **Test Suite**: Tests for config, data loader, security, models, vector store
