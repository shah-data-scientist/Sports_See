# Architecture Documentation

## System Overview

Sports_See is a Retrieval-Augmented Generation (RAG) chatbot specialized in NBA statistics and analysis. It combines semantic search with large language models to provide accurate, context-aware responses.

## High-Level Architecture

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │
       ├─── Streamlit UI (src/chat_app.py)
       │
       ▼
┌──────────────────────────────────────┐
│     RAG Pipeline                     │
│                                      │
│  1. Query → Embedding (Mistral)      │
│  2. Search → FAISS Index             │
│  3. Context → Retrieved Chunks       │
│  4. Prompt → LLM (Mistral)           │
│  5. Response → User                  │
└──────────────────────────────────────┘
       │
       ├─── VectorStoreManager
       │    (src/utils/vector_store.py)
       │
       ├─── FAISS Index (vector_db/)
       │
       └─── Mistral API
```

## Component Architecture

### 1. Chat Application Layer

**File:** [src/chat_app.py](../src/chat_app.py)

**Responsibilities:**
- Streamlit UI management
- User input handling
- Session state management
- RAG pipeline orchestration
- Response rendering

**Flow:**
```
User Input
  ↓
Vector Search (k=5 chunks)
  ↓
Context Formatting
  ↓
Prompt Construction
  ↓
Mistral API Call
  ↓
Response Display
```

### 2. Vector Store Layer

**File:** [src/utils/vector_store.py](../src/utils/vector_store.py)

**Class:** `VectorStoreManager`

**Responsibilities:**
- Document chunking (LangChain)
- Embedding generation (Mistral)
- FAISS index creation
- Semantic search
- Persistence (pickle + FAISS files)

**Key Methods:**
- `build_index()`: Create index from documents
- `search()`: Semantic similarity search
- `_split_documents_to_chunks()`: Document chunking
- `_generate_embeddings()`: Batch embedding generation

**Index Type:** FAISS `IndexFlatIP` (cosine similarity via inner product)

### 3. Data Loader Layer

**File:** [src/utils/data_loader.py](../src/utils/data_loader.py)

**Responsibilities:**
- Multi-format document parsing
- OCR for scanned PDFs (EasyOCR)
- Metadata extraction
- Error handling and logging

**Supported Formats:**
| Format | Extractor | OCR Support |
|--------|-----------|-------------|
| PDF    | PyPDF2    | ✓ (EasyOCR) |
| DOCX   | python-docx | ✗         |
| TXT    | Built-in  | ✗           |
| CSV    | pandas    | ✗           |
| XLSX   | pandas    | ✗           |

### 4. Configuration Layer

**File:** [src/utils/config.py](../src/utils/config.py)

**Responsibilities:**
- Environment variable loading
- Constants definition
- Path management
- Model configuration

**Key Settings:**
```python
EMBEDDING_MODEL = "mistral-embed"
MODEL_NAME = "mistral-small-latest"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
SEARCH_K = 5
```

### 5. Indexer Script

**File:** [src/indexer.py](../src/indexer.py)

**Purpose:** CLI tool for batch document processing

**Workflow:**
```
Load Documents (inputs/)
  ↓
Parse & Extract Text
  ↓
Chunk Documents
  ↓
Generate Embeddings (Mistral API)
  ↓
Build FAISS Index
  ↓
Save (vector_db/)
```

## Data Flow

### Indexing Flow

```
inputs/
  ├── document1.pdf
  ├── stats.xlsx
  └── analysis.txt
       │
       ▼
DataLoader.load_and_parse_files()
       │
       ▼
[
  {
    "page_content": "...",
    "metadata": {"source": "...", "filename": "..."}
  }
]
       │
       ▼
VectorStoreManager._split_documents_to_chunks()
       │
       ▼
[
  {
    "id": "0_0",
    "text": "...",
    "metadata": {..., "chunk_id_in_doc": 0}
  }
]
       │
       ▼
VectorStoreManager._generate_embeddings()
       │
       ▼
numpy.ndarray (N x 1024) → Mistral embeddings
       │
       ▼
FAISS.IndexFlatIP.add()
       │
       ▼
vector_db/
  ├── faiss_index.idx
  └── document_chunks.pkl
```

### Search Flow

```
User Query: "Who won the championship?"
       │
       ▼
Mistral Embedding API (query → vector)
       │
       ▼
FAISS.search(query_vector, k=5)
       │
       ▼
[
  {
    "score": 87.3,
    "text": "Lakers won...",
    "metadata": {"source": "stats.pdf"}
  },
  ...
]
       │
       ▼
Context String Formatting
       │
       ▼
Prompt Template:
  """
  Tu es NBA Analyst AI...

  Context: {retrieved_chunks}

  Question: {user_query}
  """
       │
       ▼
Mistral Chat API
       │
       ▼
Response to User
```

## Technology Stack

### Core
- **Python 3.11+**: Modern type hints, performance
- **Poetry**: Dependency management
- **Streamlit 1.44.1**: Web UI framework

### AI/ML
- **Mistral AI 0.4.2**: Embeddings + chat completion
- **FAISS-CPU 1.10.0**: Vector similarity search
- **LangChain 0.3.23**: Text splitting utilities

### Document Processing
- **PyPDF2**: PDF text extraction
- **PyMuPDF**: PDF rendering for OCR
- **EasyOCR**: OCR for scanned PDFs
- **python-docx**: Word document parsing
- **pandas**: CSV/Excel processing

### Development
- **pytest**: Testing framework
- **ruff**: Linting
- **black**: Code formatting
- **mypy**: Type checking

## Design Decisions

### 1. FAISS over Vector DBs

**Choice:** FAISS (local, in-memory)

**Alternatives considered:** Pinecone, Weaviate, Chroma

**Rationale:**
- No external dependencies or services
- Fast for small-to-medium datasets (<100k vectors)
- Simple deployment (no DB server)
- Low latency (in-memory)
- Cost-effective (no hosting fees)

**Trade-offs:**
- No distributed scaling
- Index rebuilds on updates
- No advanced filtering

### 2. Mistral over OpenAI

**Choice:** Mistral AI

**Alternatives considered:** OpenAI, Claude, Local models

**Rationale:**
- Good multilingual support (French + English)
- Competitive pricing
- Single API for embeddings + chat
- European data privacy

**Trade-offs:**
- Smaller ecosystem than OpenAI
- Fewer model options

### 3. Streamlit over FastAPI + React

**Choice:** Streamlit

**Alternatives considered:** FastAPI + React, Gradio, Flask

**Rationale:**
- Rapid prototyping
- Built-in state management
- No frontend expertise needed
- Easy deployment

**Trade-offs:**
- Limited customization
- Session-based (not RESTful)
- Harder to separate frontend/backend

### 4. Functional over OOP

**Choice:** Functional programming paradigm

**Rationale:**
- Stateless transformations are easier to test
- Functional composition for data pipelines
- Simpler to reason about
- Modern Python best practices

**Exception:** `VectorStoreManager` class for state management (index, chunks)

## Scalability Considerations

### Current Limits
- **Documents:** ~1000 documents (depends on size)
- **Chunks:** ~10,000 chunks in FAISS
- **Memory:** ~2-4 GB RAM
- **Concurrent users:** ~10 (Streamlit limitation)

### Scaling Strategies

**For more documents:**
1. Use FAISS `IndexIVFFlat` (partitioned index)
2. Migrate to Pinecone/Weaviate
3. Implement incremental indexing

**For more users:**
1. Deploy multiple Streamlit instances
2. Migrate to FastAPI + React
3. Use load balancer

**For faster search:**
1. Use GPU-accelerated FAISS
2. Reduce embedding dimensions (PCA)
3. Pre-filter by metadata

## Security Architecture

### API Key Protection
- Stored in `.env` (gitignored)
- Never logged or displayed
- Loaded via `python-dotenv`

### Input Validation
- User queries sanitized before API calls
- File type validation on upload
- Path traversal protection

### Data Privacy
- All processing local (except API calls)
- No user data persisted beyond session
- No external tracking

## Performance Optimization

### Embedding Generation
- Batch processing (32 chunks/batch)
- Async API calls (future enhancement)
- Caching (future enhancement)

### Search
- Normalized vectors for fast cosine similarity
- `IndexFlatIP` optimized for small datasets
- Chunking sized for ~512 tokens (balance context/speed)

### Chunking
- `RecursiveCharacterTextSplitter` for semantic coherence
- 1500 char chunks (~350 tokens)
- 150 char overlap for continuity

## Testing Strategy

### Unit Tests
- Configuration validation
- Data loader format support
- Vector store operations

### Integration Tests
- End-to-end indexing
- Search accuracy
- API integration

### Future: E2E Tests
- Streamlit UI testing
- User flow testing

## Deployment

### Current: Local Development
```bash
poetry run streamlit run src/chat_app.py
```

### Future: Production Options

**Option 1: Streamlit Cloud**
- Easy deployment
- Free tier available
- Limited resources

**Option 2: Docker + Cloud Run**
- More control
- Better scalability
- Requires containerization

**Option 3: On-Premise**
- Full data control
- Custom infrastructure
- Higher maintenance

## Monitoring & Logging

### Current Logging
- Python `logging` module
- Log levels: INFO, WARNING, ERROR
- Console output

### Future Enhancements
- Structured logging (JSON)
- Log aggregation (ELK stack)
- Performance metrics
- Error tracking (Sentry)

## Future Architecture

### Planned Enhancements

1. **Conversation Memory**
   - Store chat history
   - Multi-turn context
   - User preferences

2. **Hybrid Search**
   - Keyword + semantic
   - Metadata filtering
   - Re-ranking

3. **Query Classification**
   - RAG vs direct answer
   - Intent detection
   - Confidence scoring

4. **Multi-Modal**
   - Image analysis (charts, diagrams)
   - Table extraction
   - Video transcription

5. **Feedback Loop**
   - User ratings
   - Active learning
   - Continuous improvement

---

**Maintainer:** Shahu
**Last Updated:** 2026-01-21
