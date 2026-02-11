# Architecture Documentation

**Last Updated**: 2026-02-11
**Version**: 2.0 (Hybrid RAG)

---

## System Overview

Sports_See is a **Hybrid RAG** (Retrieval-Augmented Generation) system that combines SQL database queries with semantic vector search to provide accurate, context-aware responses about NBA statistics and analysis.

### Key Innovation: Intelligent Query Routing

The system automatically classifies queries and routes them to the optimal data source:
- **Statistical queries** → SQL Database (exact data)
- **Contextual queries** → Vector Search (semantic understanding)
- **Complex queries** → Hybrid (both sources)

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                            │
│                                                                    │
│  Streamlit UI (src/ui/app.py)          FastAPI (src/api/main.py) │
│  - Chat interface                       - REST endpoints          │
│  - Conversation management              - /api/v1/chat            │
│  - Feedback collection                  - /api/v1/conversation    │
│  - Visualization rendering              - /api/v1/feedback        │
└────────────────────────────┬───────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      SERVICES LAYER                               │
│                                                                    │
│  ChatService (src/services/chat.py)                              │
│  ├─ Query Classification                                          │
│  ├─ Intelligent Routing (SQL/Vector/Hybrid)                      │
│  ├─ Conversation Context Management                               │
│  ├─ Smart Fallback (SQL → Vector on failure)                     │
│  └─ Automatic Visualization Generation                            │
│                                                                    │
│  QueryClassifier (src/services/query_classifier.py)              │
│  ├─ Pattern-based classification                                  │
│  ├─ Statistical keywords detection                                │
│  └─ Contextual keywords detection                                 │
│                                                                    │
│  ConversationService (src/services/conversation.py)              │
│  ├─ Conversation persistence                                      │
│  ├─ Message history                                               │
│  └─ Pronoun resolution context                                    │
│                                                                    │
│  VisualizationService (src/services/visualization_service.py)    │
│  ├─ Top N pattern → Horizontal bar chart                         │
│  ├─ Comparison pattern → Radar chart                             │
│  └─ Plotly chart generation                                       │
└────────────────────────────┬───────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  SQL TOOL    │   │ VECTOR SEARCH│   │ CONVERSATION │
│              │   │              │   │   DATABASE   │
│ SQLTool      │   │ VectorStore  │   │              │
│ ├─ LangChain │   │ ├─ FAISS     │   │ SQLite       │
│ ├─ Few-shot  │   │ ├─ Mistral   │   │ ├─ Sessions  │
│ │  Examples  │   │ │  Embeddings│   │ ├─ Messages  │
│ └─ SQL Gen   │   │ └─ Semantic  │   │ └─ Feedback  │
│              │   │    Search    │   │              │
└──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ NBA Database │   │  Vector DB   │
│              │   │              │
│ SQLite       │   │ FAISS Index  │
│ ├─ players   │   │ ├─ 5 chunks  │
│ │  (569 rows)│   │ │  (Reddit)  │
│ ├─ player_   │   │ └─ Mistral   │
│ │  stats     │   │    1024-dim  │
│ │  (48 cols) │   │    vectors   │
│ └─ teams     │   │              │
└──────────────┘   └──────────────┘
       │                  │
       └────────┬─────────┘
                ▼
        ┌──────────────┐
        │  GEMINI LLM  │
        │              │
        │ gemini-2.0-  │
        │ flash        │
        │              │
        │ + Retry      │
        │   Logic      │
        └──────────────┘
```

---

## Query Flow: Intelligent Routing

### Step 1: Classification

```python
# QueryClassifier analyzes the query
query = "Who are the top 5 scorers?"

classification = classifier.classify(query)
# Result: QueryType.STATISTICAL
```

**Classification Logic**:
- **STATISTICAL**: Contains stat keywords (points, rebounds, top, average) + SQL-compatible
- **CONTEXTUAL**: Contains analysis keywords (why, explain, discuss, impact, style)
- **HYBRID**: Needs both data and context (comparisons with "why")

### Step 2: Routing

```
Query: "Who are the top 5 scorers?"
    │
    ▼
QueryClassifier
    │
    ├─ Match: "top", "scorers" (statistical keywords)
    ├─ No: "why", "explain" (contextual keywords)
    └─ Result: STATISTICAL
    │
    ▼
Route to SQL Path
    │
    ▼
SQLTool.generate_sql()
    ├─ Input: "Who are the top 5 scorers?"
    ├─ Few-shot examples (8 examples)
    ├─ Schema: players + player_stats
    └─ Generated SQL:
        SELECT p.name, ps.pts
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        ORDER BY ps.pts DESC
        LIMIT 5
    │
    ▼
Execute SQL → Results
    │
    ▼
Format Context (numbered list):
    "Found 5 matching records:
     1. name: Shai Gilgeous-Alexander, pts: 2485
     2. name: Luka Doncic, pts: 2370
     ..."
    │
    ▼
Gemini LLM + Context → Response
    │
    ▼
VisualizationService
    ├─ Detect: "top N" pattern
    ├─ Extract: player names + points
    └─ Generate: Horizontal bar chart (Plotly)
    │
    ▼
Return: Answer + Visualization + SQL
```

### Step 3: Smart Fallback

If SQL fails or returns no results:

```
SQL Execution Failed
    │
    ▼
Fallback to Vector Search
    │
    ├─ Generate embedding (Mistral)
    ├─ FAISS similarity search
    ├─ Retrieve relevant chunks
    └─ Send to Gemini LLM
    │
    ▼
Return: Answer (no visualization)
```

---

## Core Components

### 1. Chat Service (`src/services/chat.py`)

**Responsibilities**:
- Query classification
- Intelligent routing (SQL/Vector/Hybrid)
- Conversation context management
- Two-phase fallback system
- Automatic visualization generation
- Rate limit retry logic (exponential backoff)

**Key Methods**:
```python
def process_query_with_conversation(
    query: str,
    conversation_id: str | None = None,
    turn_number: int = 1,
    k: int = 5
) -> ChatResponse:
    """Main entry point for query processing."""

def generate_response(
    query: str,
    query_type: QueryType,
    context: str,
    conversation_history: list[ConversationMessage] | None = None,
    sql_data: dict | None = None
) -> str:
    """Generate response using Gemini with retry logic."""
```

**Retry Logic**:
- Max 3 retries on 429 errors
- Exponential backoff: 2s → 4s → 8s
- Smart error detection (429/RESOURCE_EXHAUSTED only)

### 2. SQL Tool (`src/tools/sql_tool.py`)

**Responsibilities**:
- Natural language → SQL translation
- SQL execution against NBA database
- Result formatting for LLM comprehension
- Retry logic for rate limits

**Implementation**:
- LangChain SQL Agent
- Gemini 2.0 Flash for SQL generation
- 8 few-shot examples (covering JOIN, aggregation, filtering)
- Automatic schema introspection

**Database Schema**:
```sql
-- players table (569 rows)
CREATE TABLE players (
    id INTEGER PRIMARY KEY,
    name TEXT,
    team TEXT,
    position TEXT
);

-- player_stats table (569 rows, 48 columns)
CREATE TABLE player_stats (
    player_id INTEGER,
    gp INTEGER,      -- games played
    pts REAL,        -- points
    reb REAL,        -- rebounds
    ast REAL,        -- assists
    fg_pct REAL,     -- field goal %
    -- ... 42 more stat columns
    FOREIGN KEY (player_id) REFERENCES players(id)
);
```

### 3. Vector Store (`src/repositories/vector_store.py`)

**Responsibilities**:
- FAISS index management
- Mistral embedding generation
- Semantic similarity search
- Document chunk persistence

**Implementation**:
- FAISS `IndexFlatIP` (cosine similarity)
- Mistral `mistral-embed` (1024 dimensions)
- 5 document chunks (Reddit discussions)
- Optimized for small dataset

**Key Methods**:
```python
def search(
    query: str,
    k: int = 5,
    min_score: float = 0.0
) -> list[SearchResult]:
    """Semantic search with score filtering."""
```

### 4. Query Classifier (`src/services/query_classifier.py`)

**Classification Rules**:

```python
STATISTICAL_KEYWORDS = [
    "top", "best", "most", "highest", "lowest",
    "average", "total", "compare", "stats",
    "points", "rebounds", "assists", "games"
]

CONTEXTUAL_KEYWORDS = [
    "why", "how", "explain", "discuss", "analyze",
    "opinion", "style", "impact", "valuable",
    "effective", "strategy", "culture"
]
```

**Logic**:
1. Check for statistical keywords → STATISTICAL
2. Check for contextual keywords → CONTEXTUAL
3. Has both + comparison → HYBRID
4. Default → CONTEXTUAL (safe fallback)

### 5. Conversation Service (`src/services/conversation.py`)

**Responsibilities**:
- Conversation session management
- Message history persistence
- Context retrieval for follow-up questions

**Database Schema**:
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP,
    last_updated TIMESTAMP,
    is_archived BOOLEAN
);

CREATE TABLE conversation_messages (
    id INTEGER PRIMARY KEY,
    conversation_id TEXT,
    role TEXT,  -- 'user' or 'assistant'
    content TEXT,
    timestamp TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

### 6. Visualization Service (`src/services/visualization_service.py`)

**Patterns**:

**Top N Pattern**:
- Queries: "top 5 scorers", "best rebounders"
- Chart: Horizontal bar chart
- Data extraction: Names + values
- Sorting: Descending by value

**Comparison Pattern**:
- Queries: "compare Jokić and Embiid"
- Chart: Radar chart
- Data extraction: Multiple players × multiple stats
- Normalization: 0-100 scale

**Implementation**:
```python
def create_top_n_visualization(
    data: list[dict],
    stat_name: str
) -> dict:
    """Create horizontal bar chart for top N queries."""

def create_comparison_visualization(
    players: list[str],
    stats: list[dict]
) -> dict:
    """Create radar chart for player comparisons."""
```

---

## Technology Stack

### AI/ML
- **Gemini 2.0 Flash**: Main LLM (response generation + SQL)
- **Mistral AI**: Embeddings only (`mistral-embed`, 1024-dim)
- **FAISS**: Vector similarity search (IndexFlatIP)
- **LangChain**: SQL agent framework

### Backend
- **Python 3.11+**: Modern type hints
- **FastAPI**: REST API framework
- **Poetry**: Dependency management
- **SQLite**: Databases (NBA stats + conversations)
- **Pydantic**: Data validation

### Frontend
- **Streamlit 1.44.1**: Web UI
- **Plotly**: Interactive visualizations

### Document Processing
- **PyPDF2**: PDF text extraction
- **PyMuPDF**: PDF rendering for OCR
- **easyOCR**: OCR for scanned PDFs (lazy-loaded)
- **python-docx**: Word documents
- **pandas**: CSV/Excel

### Testing & Quality
- **pytest**: Testing framework (247+ tests)
- **Playwright**: UI automation (65+ tests)
- **RAGAS**: RAG evaluation metrics
- **ruff**: Linting
- **black**: Code formatting

---

## Design Decisions

### 1. Hybrid RAG: SQL + Vector

**Decision**: Dual-path architecture with intelligent routing

**Rationale**:
- SQL provides **exact data** for statistical queries (no hallucination)
- Vector provides **semantic understanding** for contextual queries
- Hybrid combines **both** for complex analysis

**Trade-offs**:
- More complexity than pure RAG
- Two data sources to maintain
- But: **97.9% classification accuracy**, **100% SQL execution success**

### 2. Gemini for LLM, Mistral for Embeddings

**Decision**: Split LLM and embedding providers

**Rationale**:
- **Gemini**: Better SQL data comprehension (+25% over Mistral)
- **Mistral**: Consistent embeddings (avoid re-indexing)
- **Cost**: Both have free tiers

**Trade-offs**:
- Two API keys to manage
- Different rate limits (Gemini: 15 RPM, Mistral: 60 RPM)

### 3. Smart Fallback Over Perfect Classification

**Decision**: Aggressive SQL classification + fallback to vector on failure

**Rationale**:
- Don't need 100% classification accuracy
- Failed SQL → graceful vector fallback
- LLM "cannot find" → automatic retry with vector

**Results**:
- 97.9% classification accuracy
- 100% coverage (all queries answered)

### 4. Pattern-Based Visualization

**Decision**: Automatic chart generation for recognized patterns

**Rationale**:
- Top N queries → obvious bar chart
- Comparisons → obvious radar chart
- No need for LLM to decide

**Trade-offs**:
- Limited to 2 patterns currently
- Manual pattern expansion needed

### 5. SQLite Over PostgreSQL

**Decision**: SQLite for both NBA data and conversations

**Rationale**:
- Simple deployment (single file)
- No server setup
- Fast for small datasets (<10k rows)
- Built-in Python support

**Trade-offs**:
- No concurrent writes
- No distributed scaling
- But: Perfect for this use case

---

## Scalability & Performance

### Current Limits
- **Documents**: 5 vector chunks (optimized to avoid duplication with SQL)
- **SQL Records**: 569 players (scales to 10k+ easily)
- **Concurrent Users**: ~10 (Streamlit limitation)
- **Memory**: ~2-4 GB

### Performance Optimizations

**Embedding Generation**:
- Batch processing (32 chunks/batch)
- Lazy-load OCR (avoid torch+FAISS crash)

**SQL Queries**:
- Indexed by player_id
- JOINs optimized (players ⋈ player_stats)
- Top N queries with LIMIT

**Vector Search**:
- Small index (5 chunks) = fast search
- Normalized vectors (cosine via dot product)
- Min score filtering

**API Calls**:
- Retry logic with exponential backoff
- 9s delay between queries (rate limit protection)

### Scaling Strategies

**For more data**:
1. SQL database already optimized (indexed, JOINs)
2. Vector store intentionally small (only unique content)
3. Could partition FAISS if needed (IndexIVFFlat)

**For more users**:
1. Migrate to FastAPI (already built, REST endpoints)
2. Deploy multiple instances
3. Add load balancer

**For faster responses**:
1. Cache common queries
2. Pre-generate frequent visualizations
3. Async API calls (currently sync)

---

## Security

### API Key Protection
- Stored in `.env` (gitignored)
- Loaded via `python-dotenv`
- Never logged or displayed

### Input Validation
- Query sanitization (`src/core/security.py`)
- SQL injection prevention (parameterized queries)
- Path traversal blocking
- XSS prevention in UI

### Rate Limiting
- Automatic retry with backoff (avoid hammering APIs)
- 9s delay between evaluation queries
- Per-IP rate limiting (future enhancement)

---

## Testing Architecture

### Test Organization (247+ tests)

```
tests/
├── core/              # 67 tests - Config, security, exceptions
├── models/            # 89 tests - Pydantic validation
├── services/          # 30+ tests - Business logic
├── repositories/      # 10+ tests - Data access
├── integration/       # 16 tests - Component interactions
├── e2e/              # 8 tests - Full workflows
└── ui/               # 65+ tests - Browser automation
```

### Evaluation System

**3 Master Scripts**:
1. `src/evaluation/run_sql_evaluation.py` - 48 SQL test cases
2. `src/evaluation/run_vector_evaluation.py` - 75 vector test cases (RAGAS)
3. `scripts/evaluate_hybrid.py` - 18 hybrid test cases

**Metrics**:
- SQL: 100% execution, 97.9% classification
- Vector: RAGAS (Faithfulness, Relevancy, Precision, Recall)
- Hybrid: Combined metrics

---

## Deployment

### Development
```bash
# UI
poetry run streamlit run src/ui/app.py

# API
poetry run uvicorn src.api.main:app --reload --port 8002
```

### Production Considerations

**Environment**:
- Python 3.11+
- 2GB+ memory
- API keys configured

**Data Persistence**:
- `data/sql/nba_stats.db` - NBA statistics
- `data/sql/interactions.db` - Conversations + feedback
- `data/vector/faiss_index.pkl` - Vector index
- `data/vector/document_store.pkl` - Document chunks

**Monitoring**:
- Logfire observability (optional)
- Health check: `/health` endpoint
- Feedback tracking in database

---

## Future Enhancements

### Short-term
- [ ] Request queuing (serialize API calls)
- [ ] Caching layer (common queries)
- [ ] API mocking for tests (eliminate rate limit dependency)

### Medium-term
- [ ] Upgrade to Gemini paid tier (360 RPM vs 15 RPM)
- [ ] Circuit breaker pattern
- [ ] More visualization patterns (time series, heat maps)

### Long-term
- [ ] Multi-language support (English + French)
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Mobile app

---

**Maintainer**: Shahu
**Version**: 2.0
**Last Updated**: 2026-02-11
