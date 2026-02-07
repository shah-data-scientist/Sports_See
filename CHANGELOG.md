# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **RAGAS Evaluation Script**: Automated RAG quality assessment measuring faithfulness, answer relevancy, context precision, and context recall ([src/evaluation/evaluate_ragas.py](src/evaluation/evaluate_ragas.py))
- **Evaluation Models**: Pydantic models for test cases, samples, metric scores, and reports ([src/evaluation/models.py](src/evaluation/models.py))
- **Categorized Test Cases**: 10 NBA business questions across 3 categories: simple, complex, noisy ([src/evaluation/test_cases.py](src/evaluation/test_cases.py))
- **Comparative Table Output**: Formatted ASCII table showing RAGAS scores by category ([src/evaluation/evaluate_ragas.py](src/evaluation/evaluate_ragas.py))
- **Data Preparation Pipeline**: Validated pipeline with load, clean, chunk, embed, and index stages ([src/pipeline/data_pipeline.py](src/pipeline/data_pipeline.py))
- **Pipeline Stage Models**: Pydantic models for every pipeline stage boundary (I/O validation) ([src/pipeline/models.py](src/pipeline/models.py))
- **Pydantic AI Quality Agent**: Optional LLM-powered chunk quality validation using Pydantic AI Agent ([src/pipeline/quality_agent.py](src/pipeline/quality_agent.py))
- **Logfire Observability**: Pydantic Logfire integration with `@logfire.instrument()` on all pipeline stages, ChatService, EmbeddingService, and VectorStoreRepository ([src/core/observability.py](src/core/observability.py))
- **Logfire Graceful Fallback**: No-op fallback when Logfire is not configured, ensuring the app works without tracing ([src/core/observability.py](src/core/observability.py))
- **Evaluation Tests**: 16 tests for evaluation models, test cases, sample generation, report building, and table output ([tests/test_evaluation.py](tests/test_evaluation.py))
- **Pipeline Tests**: 13 tests for pipeline stages with mocked services ([tests/test_pipeline.py](tests/test_pipeline.py))
- **Pipeline Model Tests**: 19 pure validation tests for pipeline Pydantic models ([tests/test_pipeline_models.py](tests/test_pipeline_models.py))
- **Feedback System**: Chat history logging with thumbs up/down feedback ([src/models/feedback.py](src/models/feedback.py), [src/repositories/feedback.py](src/repositories/feedback.py), [src/services/feedback.py](src/services/feedback.py))
- **Feedback API**: REST endpoints for submitting/querying feedback ([src/api/routes/feedback.py](src/api/routes/feedback.py))
- **Feedback UI**: Thumbs up/down buttons with comment form in Streamlit ([src/ui/app.py](src/ui/app.py))
- **Feedback Statistics**: Dashboard in sidebar showing positive/negative rates ([src/ui/app.py](src/ui/app.py))
- **SQLAlchemy**: Database ORM for feedback persistence in SQLite ([src/models/feedback.py](src/models/feedback.py))
- **Feedback Tests**: 19 unit tests for models, repository, and service ([tests/test_feedback.py](tests/test_feedback.py))
- **GLOBAL_POLICY.md Enforcement**: Validation scripts for file headers, locations, orphaned files ([scripts/global_policy/](scripts/global_policy/))
- **CHANGELOG.md**: Project change tracking per Keep a Changelog standard
- **Pre-commit hooks**: Automated validation on commits ([.pre-commit-config.yaml](.pre-commit-config.yaml))
- **File documentation headers**: All .py files now have 5-field headers (FILE, STATUS, RESPONSIBILITY, LAST MAJOR UPDATE, MAINTAINER)

### Changed
- **Mistral AI SDK**: Upgraded from `mistralai==0.4.2` to `mistralai>=1.2.5` (v1.12.0) — migrated `MistralClient` to `Mistral`, `client.chat()` to `client.chat.complete()`, `client.embeddings()` to `client.embeddings.create()` ([src/services/chat.py](src/services/chat.py), [src/services/embedding.py](src/services/embedding.py))
- **Config Settings**: Added `logfire_token` and `logfire_enabled` settings ([src/core/config.py](src/core/config.py))
- **Ruff Config**: Migrated to `[tool.ruff.lint]` prefix; added D205, D212, D415 ignores for 5-field header compatibility ([pyproject.toml](pyproject.toml))
- **Dependencies**: Added ragas, langchain-mistralai, datasets, pydantic-ai, logfire ([pyproject.toml](pyproject.toml))
- **API Dependencies**: Extracted `get_chat_service` to `dependencies.py` to fix circular imports ([src/api/dependencies.py](src/api/dependencies.py), [src/api/main.py](src/api/main.py))
- **.gitignore**: Added mandatory exclusions per GLOBAL_POLICY.md (db-shm, db-wal, archived dirs, root scripts)

### Removed
- **DOCUMENTATION_POLICY.md**: Archived to `_archived/2026-02/` (superseded by GLOBAL_POLICY.md)
- **check_docs_consistency.py**: Archived to `_archived/2026-02/` (replaced by enforcement scripts)

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
