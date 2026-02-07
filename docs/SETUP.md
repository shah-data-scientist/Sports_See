# Setup Guide

Complete setup instructions for Sports_See NBA RAG Assistant.

## Prerequisites

- Python 3.11 or higher
- Poetry (package manager)
- Mistral API key ([get one here](https://console.mistral.ai/))

## Installation

### 1. Install Poetry

If you don't have Poetry installed:

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**macOS/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Verify installation:
```bash
poetry --version
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd Sports_See
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev dependencies
poetry install

# Install only production dependencies
poetry install --without dev
```

This creates a virtual environment in `.venv/` and installs all packages.

### 4. Configure Environment

Create `.env` file in project root:

```bash
# Copy example file
cp .env.example .env

# Edit with your API key
# Windows
notepad .env

# macOS/Linux
nano .env
```

Add your Mistral API key:
```
MISTRAL_API_KEY=your_actual_api_key_here
```

### 5. Prepare Documents

Place your source documents in the `inputs/` directory:

```bash
Sports_See/
└── inputs/
    ├── document1.pdf
    ├── stats.xlsx
    └── analysis.txt
```

**Supported formats:**
- PDF (.pdf)
- Word (.docx)
- Text (.txt)
- CSV (.csv)
- Excel (.xlsx, .xls)

### 6. Build Vector Index

Run the indexer to process documents:

```bash
poetry run python src/indexer.py
```

This will:
1. Load all documents from `inputs/`
2. Split into chunks
3. Generate embeddings via Mistral API
4. Create FAISS index
5. Save to `vector_db/`

**Expected output:**
```
INFO - Loading and parsing files from: inputs
INFO - 5 documents loaded and parsed.
INFO - Splitting 5 documents into chunks...
INFO - Generating embeddings for 42 chunks...
INFO - FAISS index created with 42 vectors.
INFO - Index saved successfully.
```

### 7. Launch Application

```bash
poetry run streamlit run src/chat_app.py
```

Open browser to http://localhost:8501

## Verification

Test the installation:

```bash
# Run tests
poetry run pytest

# Check code quality
poetry run ruff check .
poetry run black --check .

# Type checking
poetry run mypy src/
```

## Troubleshooting

### Poetry not found

Add Poetry to PATH:

**Windows:**
```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```

**macOS/Linux:**
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Import errors

Ensure virtual environment is activated:

```bash
poetry shell
```

Or use `poetry run` prefix for all commands.

### API key errors

Verify `.env` file exists and contains valid key:

```bash
# Check file exists
ls .env

# Verify format (don't share actual key!)
cat .env
```

### OCR not working for PDFs

Install EasyOCR dependencies:

```bash
poetry add easyocr
```

May require additional system dependencies on Linux.

### Out of memory during indexing

Reduce batch size in [src/utils/config.py](../src/utils/config.py):

```python
EMBEDDING_BATCH_SIZE = 16  # Reduce from 32
```

### Slow performance

- Use smaller model: `MODEL_NAME = "mistral-small-latest"`
- Reduce search results: `SEARCH_K = 3`
- Increase chunk size: `CHUNK_SIZE = 2000`

## Development Setup

Additional steps for development:

```bash
# Install dev dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run full test suite with coverage
poetry run pytest --cov=src tests/

# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type check
poetry run mypy src/
```

## Docker Setup (Optional)

Coming soon...

## Next Steps

1. Read [DOCUMENTATION_POLICY.md](../DOCUMENTATION_POLICY.md)
2. Review [API.md](API.md) for usage examples
3. Check [PROJECT_MEMORY.md](../PROJECT_MEMORY.md) for architecture
4. See [README.md](../README.md) for quick start

## Support

For issues:
1. Check logs in terminal
2. Review [PROJECT_MEMORY.md](../PROJECT_MEMORY.md) Known Issues
3. Search existing GitHub issues
4. Create new issue with logs and steps to reproduce
