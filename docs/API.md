# API Documentation

## VectorStoreManager

Main class for managing FAISS vector index and semantic search.

### Initialization

```python
from src.utils.vector_store import VectorStoreManager

manager = VectorStoreManager()
```

The constructor automatically loads existing index and chunks if available.

### Methods

#### `build_index(documents: list[dict[str, any]]) -> None`

Builds FAISS index from documents.

**Parameters:**
- `documents`: List of document dictionaries with `page_content` and `metadata` keys

**Example:**
```python
documents = [
    {
        "page_content": "NBA statistics text...",
        "metadata": {"source": "stats.pdf", "filename": "stats.pdf"}
    }
]
manager.build_index(documents)
```

#### `search(query_text: str, k: int = 5, min_score: float | None = None) -> list[dict[str, any]]`

Search for relevant document chunks.

**Parameters:**
- `query_text`: Search query string
- `k`: Number of results to return (default: 5)
- `min_score`: Minimum similarity score 0-1 (optional)

**Returns:**
List of dictionaries containing:
- `text`: Chunk text
- `score`: Similarity score (0-100)
- `metadata`: Document metadata
- `raw_score`: Raw FAISS score

**Example:**
```python
results = manager.search("Who won the championship?", k=3, min_score=0.5)
for result in results:
    print(f"Score: {result['score']:.1f}%")
    print(f"Text: {result['text']}")
    print(f"Source: {result['metadata']['source']}")
```

---

## Data Loader Functions

### `load_and_parse_files(input_dir: str) -> list[dict[str, any]]`

Load and parse files from directory recursively.

**Supported formats:**
- PDF (.pdf)
- Word (.docx)
- Text (.txt)
- CSV (.csv)
- Excel (.xlsx, .xls)

**Parameters:**
- `input_dir`: Path to directory containing documents

**Returns:**
List of document dictionaries with `page_content` and `metadata`

**Example:**
```python
from src.utils.data_loader import load_and_parse_files

documents = load_and_parse_files("inputs/")
print(f"Loaded {len(documents)} documents")
```

### `extract_text_from_pdf(file_path: str) -> str | None`

Extract text from PDF with OCR fallback.

**Parameters:**
- `file_path`: Path to PDF file

**Returns:**
Extracted text or None if failed

### `extract_text_from_docx(file_path: str) -> str | None`

Extract text from Word document.

### `extract_text_from_txt(file_path: str) -> str | None`

Extract text from plain text file.

### `extract_text_from_csv(file_path: str) -> str | None`

Extract text from CSV file.

### `extract_text_from_excel(file_path: str) -> str | dict[str, str] | None`

Extract text from Excel file.

Returns dict with sheet names as keys if multiple sheets, otherwise string.

---

## Configuration

All configuration in [src/utils/config.py](../src/utils/config.py).

### Environment Variables

Set in `.env` file:

```bash
MISTRAL_API_KEY=your_api_key_here
```

### Constants

**Embedding & Models:**
- `EMBEDDING_MODEL`: "mistral-embed"
- `MODEL_NAME`: "mistral-small-latest"

**Chunking:**
- `CHUNK_SIZE`: 1500 characters
- `CHUNK_OVERLAP`: 150 characters
- `EMBEDDING_BATCH_SIZE`: 32

**Search:**
- `SEARCH_K`: 5 (default number of results)

**Paths:**
- `INPUT_DIR`: "inputs"
- `VECTOR_DB_DIR`: "vector_db"
- `FAISS_INDEX_FILE`: "vector_db/faiss_index.idx"
- `DOCUMENT_CHUNKS_FILE`: "vector_db/document_chunks.pkl"

---

## Usage Example

Complete workflow:

```python
from src.utils.data_loader import load_and_parse_files
from src.utils.vector_store import VectorStoreManager

# 1. Load documents
documents = load_and_parse_files("inputs/")
print(f"Loaded {len(documents)} documents")

# 2. Build index
manager = VectorStoreManager()
manager.build_index(documents)
print(f"Indexed {manager.index.ntotal} chunks")

# 3. Search
results = manager.search("Who scored the most points?", k=5)
for i, result in enumerate(results, 1):
    print(f"\n{i}. Score: {result['score']:.1f}%")
    print(f"   Source: {result['metadata']['source']}")
    print(f"   Text: {result['text'][:200]}...")
```

---

## Error Handling

All functions log errors using Python's `logging` module.

**Common exceptions:**
- `FileNotFoundError`: Index or chunks files not found
- `MistralAPIException`: Mistral API errors
- `ValueError`: Invalid parameters

**Example:**
```python
import logging

logging.basicConfig(level=logging.INFO)

manager = VectorStoreManager()
if manager.index is None:
    print("Index not found. Run indexer first.")
```
