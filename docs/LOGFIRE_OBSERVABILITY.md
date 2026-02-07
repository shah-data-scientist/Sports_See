# Logfire Observability for RAG Pipeline

## Overview

The Sports_See RAG pipeline is fully instrumented with [Logfire](https://logfire.pydantic.dev/) for end-to-end observability. This provides visibility into:
- Query processing latency
- Embedding generation performance
- Vector search operations
- LLM token usage and response times
- Error tracking and debugging

## RAG Pipeline Flow

### 1. Query Processing (`ChatService.chat`)

```
User Query
    ↓
[Logfire Span: ChatService.chat]
    ├── Input validation & sanitization
    ├── Query preprocessing
    └── Pipeline orchestration
```

**Tracked Metrics:**
- Total request latency
- Query length
- Final response metadata

### 2. Embedding Generation (`EmbeddingService.embed_batch`)

```
Query Text
    ↓
[Logfire Span: EmbeddingService.embed_batch]
    ├── Batch preparation (size: 1)
    ├── Mistral API call (POST /v1/embeddings)
    └── Embedding vector (1024 dimensions)
```

**Tracked Metrics:**
- Embedding API latency
- Token count
- Batch size
- Embedding model used

### 3. Vector Similarity Search (`ChatService.search`)

```
Query Embedding [1024]
    ↓
[Logfire Span: ChatService.search]
    ├── FAISS index search (302 vectors)
    ├── Distance calculation (cosine similarity)
    ├── Top-k filtering (k=5)
    └── Source metadata extraction
```

**Tracked Metrics:**
- Search latency
- Number of results
- Similarity scores
- Retrieved chunks

### 4. Context Building

```
Search Results (5 chunks)
    ↓
Context Assembly
    ├── Chunk deduplication
    ├── Source metadata aggregation
    └── Context formatting for LLM
```

**Tracked Metrics:**
- Context length (tokens)
- Number of unique sources
- Deduplication ratio

### 5. LLM Response Generation (`ChatService.generate_response`)

```
Context + Query
    ↓
[Logfire Span: ChatService.generate_response]
    ├── System prompt template
    ├── Mistral API call (POST /v1/chat/completions)
    │   └── Model: mistral-small-latest
    └── Response streaming/completion
```

**Tracked Metrics:**
- LLM API latency
- Input tokens
- Output tokens
- Temperature setting
- Model used

## Logfire Trace Waterfall Example

```
ChatService.chat [2.4s total]
├─ EmbeddingService.embed_batch [350ms]
│  └─ Mistral Embeddings API [320ms]
├─ ChatService.search [180ms]
│  └─ FAISS Index Search [165ms]
└─ ChatService.generate_response [1.8s]
   └─ Mistral Chat API [1.75s]
```

## Setup Instructions

### 1. Create Logfire Account

```bash
# Visit https://logfire.pydantic.dev/
# Sign up and create a project named 'sports-see'
```

### 2. Configure API Token

```bash
# Add to .env file
LOGFIRE_TOKEN=your_logfire_token_here
```

### 3. Enable Logfire in Settings

```python
# In src/core/config.py Settings model
logfire_enabled: bool = True  # Default is False
```

### 4. Run the Demo

```bash
poetry run python demo_logfire.py
```

### 5. View Traces

Navigate to https://logfire.pydantic.dev/sports-see to see:

- **Live Traces**: Real-time span waterfall visualizations
- **Performance Metrics**: P50/P95/P99 latencies for each operation
- **Error Tracking**: Failed requests with full stack traces
- **Token Usage**: LLM token consumption over time
- **Query Patterns**: Most common queries and search terms

## Key Benefits

### 1. Performance Optimization

Identify bottlenecks:
- Slow embedding generation → Consider caching
- Long search times → Optimize FAISS index
- High LLM latency → Try smaller models or reduce context

### 2. Cost Monitoring

Track API usage:
- Embedding API calls and token counts
- LLM token consumption by query type
- Rate limit patterns

### 3. Quality Debugging

Trace issues:
- Why did a query return poor results? → Check search span similarity scores
- Why is response quality low? → Inspect context span to see retrieved chunks
- Why did generation fail? → View LLM span error details

### 4. A/B Testing

Compare configurations:
- Different embedding models
- Various top-k search parameters
- Alternative LLM models
- Temperature settings

## Instrumentation Code

The pipeline is instrumented with decorators:

```python
from src.core.observability import logfire

class ChatService:
    @logfire.instrument("ChatService.chat")
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Main RAG pipeline - traced end-to-end."""
        ...

    @logfire.instrument("ChatService.search {query=}")
    def search(self, query: str, k: int = 5) -> list[SearchResult]:
        """Vector search - tracks query and results."""
        ...

    @logfire.instrument("ChatService.generate_response")
    def generate_response(self, query: str, context: str) -> str:
        """LLM generation - tracks tokens and latency."""
        ...
```

Spans are automatically correlated into hierarchical traces.

## Graceful Degradation

If Logfire is not configured:
- ✓ Pipeline continues to work normally
- ✓ No-op instrumentation (zero overhead)
- ✓ Local logging still available
- ⚠ No distributed tracing

## Production Deployment

For production use:

1. **Enable Logfire**: Set `LOGFIRE_TOKEN` in production environment
2. **Set Service Name**: Configured as `"sports-see"` in [`observability.py`](../src/core/observability.py)
3. **Monitor Traces**: Set up alerts for:
   - P95 latency > 5s
   - Error rate > 1%
   - Token usage spikes
4. **Sampling**: For high-traffic scenarios, configure trace sampling:
   ```python
   logfire.configure(
       service_name="sports-see",
       sampling_ratio=0.1  # Sample 10% of traces
   )
   ```

## Related Documentation

- [Logfire Python SDK](https://docs.pydantic.dev/logfire/python/)
- [Pydantic AI Instrumentation](https://ai.pydantic.dev/observability/)
- [RAGAS Evaluation Report](./RAGAS_BASELINE_REPORT.md)
