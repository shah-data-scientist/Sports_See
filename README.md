# Sports_See - NBA RAG Assistant

An intelligent NBA statistics assistant powered by Mistral AI and FAISS vector search. Get accurate, context-aware answers about NBA teams, players, and statistics using Retrieval-Augmented Generation (RAG).

## Features

- 🔍 **Semantic Search**: FAISS-powered vector similarity search
- 🤖 **AI-Powered Responses**: Mistral AI for embeddings and chat completion
- 📄 **Multi-Format Support**: PDF, Word, TXT, CSV, Excel with OCR for scanned documents
- 💬 **Interactive Chat**: Streamlit-based conversational interface
- ⚙️ **Customizable**: Configurable models, chunk sizes, and search parameters

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/) (dependency manager)
- Mistral API key from [console.mistral.ai](https://console.mistral.ai/)

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd Sports_See

# 2. Install Poetry (if not already installed)
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# 3. Install dependencies
poetry install

# 4. Configure environment
# Create .env file and add your Mistral API key:
# MISTRAL_API_KEY=your_api_key_here
```

### Usage

```bash
# 1. Place your documents in inputs/ directory
mkdir -p inputs
# Add your PDF, DOCX, TXT, CSV, or XLSX files

# 2. Build vector index
poetry run python src/indexer.py

# 3. Launch chat application
poetry run streamlit run src/chat_app.py
```

Open browser to [http://localhost:8501](http://localhost:8501)

## Project Structure

```
Sports_See/
├── src/                      # Source code
│   ├── chat_app.py          # Streamlit chat interface
│   ├── indexer.py           # Document indexing script
│   └── utils/               # Utility modules
│       ├── config.py        # Configuration
│       ├── data_loader.py   # Document parsing
│       └── vector_store.py  # FAISS vector store
├── tests/                   # Test suite
├── docs/                    # Documentation
│   ├── API.md              # API reference
│   ├── SETUP.md            # Detailed setup guide
│   └── ARCHITECTURE.md     # System architecture
├── inputs/                  # Source documents (place files here)
├── vector_db/              # FAISS index & chunks (auto-generated)
├── notebooks/              # Jupyter notebooks
├── pyproject.toml          # Poetry configuration
├── PROJECT_MEMORY.md       # Project overview & requirements
└── README.md               # This file
```

## Supported Document Formats

| Format | Extension | OCR Support |
|--------|-----------|-------------|
| PDF    | .pdf      | ✓ (EasyOCR) |
| Word   | .docx     | ✗           |
| Text   | .txt      | ✗           |
| CSV    | .csv      | ✗           |
| Excel  | .xlsx, .xls | ✗         |

## Configuration

Edit [src/utils/config.py](src/utils/config.py) or set environment variables:

```python
# AI Models
EMBEDDING_MODEL = "mistral-embed"
MODEL_NAME = "mistral-small-latest"  # or mistral-large-latest

# Chunking
CHUNK_SIZE = 1500        # characters
CHUNK_OVERLAP = 150      # characters

# Search
SEARCH_K = 5             # number of results
```

Environment variables (in `.env`):

```bash
MISTRAL_API_KEY=your_api_key_here
MODEL_NAME=mistral-large-latest  # optional override
SEARCH_K=10                      # optional override
```

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
poetry install

# Run tests
poetry run pytest

# Code quality checks
poetry run ruff check .
poetry run black .
poetry run mypy src/

# Documentation consistency
poetry run python check_docs_consistency.py
```

### Running Tests

```bash
# All tests with coverage
poetry run pytest --cov=src tests/

# Specific test file
poetry run pytest tests/test_vector_store.py

# With verbose output
poetry run pytest -v
```

### Code Style

This project follows:
- **Functional programming** paradigm (prefer functions over classes)
- **Python 3.10+ type hints** (`list[str]` not `List[str]`)
- **Google-style docstrings**
- **Black** formatting (100 char line length)
- **Ruff** linting
- **pytest** for testing

## How It Works

### RAG Pipeline

```
User Query
    ↓
Embedding Generation (Mistral API)
    ↓
Vector Search (FAISS)
    ↓
Context Retrieval (Top-K chunks)
    ↓
Prompt Construction
    ↓
LLM Response (Mistral API)
    ↓
Display to User
```

### Indexing Pipeline

```
Documents (inputs/)
    ↓
Text Extraction (PyPDF2, python-docx, pandas)
    ↓
Chunking (LangChain RecursiveCharacterTextSplitter)
    ↓
Embedding Generation (Mistral API)
    ↓
FAISS Index Creation
    ↓
Persistence (vector_db/)
```

## Documentation

- [API Reference](docs/API.md) - Detailed API documentation
- [Setup Guide](docs/SETUP.md) - Comprehensive setup instructions
- [Architecture](docs/ARCHITECTURE.md) - System design and decisions
- [Project Memory](PROJECT_MEMORY.md) - Project overview and requirements
- [Documentation Policy](DOCUMENTATION_POLICY.md) - Documentation standards

## Troubleshooting

### Import Errors

```bash
# Ensure using Poetry environment
poetry shell

# Or prefix commands with poetry run
poetry run python src/indexer.py
```

### API Key Not Found

Check `.env` file exists and contains valid key:

```bash
# Verify file exists (Windows)
dir .env

# Check format
type .env
```

### OCR Not Working

Install OCR dependencies:

```bash
poetry add easyocr
```

### Out of Memory

Reduce batch size in `src/utils/config.py`:

```python
EMBEDDING_BATCH_SIZE = 16  # reduce from 32
```

## Contributing

1. Read [DOCUMENTATION_POLICY.md](DOCUMENTATION_POLICY.md)
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

## Technology Stack

**Core:**
- Python 3.11+
- Poetry (dependency management)
- Streamlit 1.44.1 (web UI)

**AI/ML:**
- Mistral AI 0.4.2 (embeddings + chat)
- FAISS-CPU 1.10.0 (vector search)
- LangChain 0.3.23 (text splitting)

**Document Processing:**
- PyPDF2, PyMuPDF (PDF)
- EasyOCR (OCR)
- python-docx (Word)
- pandas (CSV/Excel)

**Development:**
- pytest (testing)
- ruff (linting)
- black (formatting)
- mypy (type checking)

## License

[Your License Here]

## Contact

**Maintainer:** Shahu

For issues and questions, please use the GitHub issue tracker.

---

**Powered by Mistral AI & FAISS | Data-driven NBA Insights**
