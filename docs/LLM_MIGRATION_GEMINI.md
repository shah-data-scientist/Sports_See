# LLM Migration: Mistral → Gemini

**Date:** 2026-02-08
**Purpose:** Switch to Gemini for LLM to avoid Mistral rate limits
**Status:** ✅ COMPLETED (v2.0 - Using Google GenAI SDK)

---

## Changes Made

### 1. SQL Tool (`src/tools/sql_tool.py`)

**BEFORE (Mistral):**
```python
from langchain_mistralai import ChatMistralAI

self.llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0.0,
    api_key=self._api_key,
)
```

**AFTER (Gemini):**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

self.llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.0,
    google_api_key=self._api_key,
)
```

**Impact:** SQL query generation now uses Gemini (bypasses Mistral 429 rate limits)

---

### 2. Chat Service (`src/services/chat.py`)

**BEFORE (Mistral SDK v1.x):**
```python
from mistralai import Mistral
from mistralai.models import SDKError

self._client = Mistral(api_key=self._api_key)

response = self.client.chat.complete(
    model=self._model,
    messages=[{"role": "user", "content": prompt}],
    temperature=self._temperature,
)
```

**AFTER (Google GenAI SDK):**
```python
from google import genai
from google.genai.errors import ClientError

self._client = genai.Client(api_key=self._api_key)

response = self.client.models.generate_content(
    model="gemini-2.0-flash-lite",
    contents=prompt,
    config={
        "temperature": self._temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    },
)
```

**Impact:** Chat response generation now uses Gemini 2.0 Flash Lite (bypasses Mistral 429 rate limits)

---

### 3. Embeddings (`src/services/embedding.py`)

**NO CHANGE** - Still using **Mistral embeddings** as requested

```python
from mistralai import Mistral

response = self.client.embeddings.create(
    model=self._model,  # mistral-embed
    inputs=batch,
)
```

**Reason:** Embeddings must remain consistent with the FAISS index (built with Mistral embeddings)

---

## Architecture Summary

| Component | LLM Provider | Model | Purpose |
|-----------|--------------|-------|---------|
| **SQL Generation** | ✅ Gemini | gemini-2.0-flash-lite | Text-to-SQL conversion |
| **Chat Response** | ✅ Gemini | gemini-2.0-flash-lite | RAG response generation |
| **RAGAS Evaluator** | ✅ Gemini | gemini-2.0-flash-lite | Quality evaluation |
| **Embeddings** | ✅ Mistral | mistral-embed | Vector search (must match FAISS index) |

---

## Benefits

1. ✅ **Bypasses Mistral rate limits** - Can run evaluations immediately
2. ✅ **Higher free tier limits** - Gemini has more generous rate limits
3. ✅ **Faster SQL generation** - Gemini 1.5 Flash is optimized for speed
4. ✅ **Consistent embeddings** - Still using Mistral embeddings (FAISS compatibility)

---

## Environment Variables Required

Make sure these are set in `.env`:

```env
# Gemini (for LLM - chat & SQL generation)
GOOGLE_API_KEY=your_google_api_key_here

# Mistral (for embeddings only)
MISTRAL_API_KEY=your_mistral_api_key_here
```

---

## Testing Checklist

- [x] SQL tool can generate queries without rate limits (Gemini 2.0 Flash Lite)
- [x] Chat service can generate responses without rate limits (Gemini 2.0 Flash Lite)
- [x] Embeddings still work with Mistral
- [x] FAISS vector search returns correct results
- [x] RAGAS evaluation uses Gemini for LLM evaluator
- [ ] Phase 10 (Hybrid) evaluation completes successfully with new model

---

## Implementation Notes

**Why Google GenAI SDK instead of LangChain?**
- Initial migration attempt used `langchain-google-genai` which had API compatibility issues
- Google GenAI SDK provides direct, stable access to Gemini 2.0 models
- Simpler API surface reduces integration complexity

**LangChain still used for SQL tool:**
- `ChatGoogleGenerativeAI` from `langchain-google-genai` works well for structured SQL generation
- Few-shot prompting framework benefits from LangChain's prompt templating

## Rollback Instructions

If issues arise, revert by:

1. **sql_tool.py:** Change `ChatGoogleGenerativeAI` back to `ChatMistralAI`
2. **chat.py:** Change `genai.Client` back to `mistralai.Mistral`
3. Update API key references from `google_api_key` to `mistral_api_key`
4. Update model names from `gemini-2.0-flash-lite` to `mistral-small-latest`

---

**Maintainer:** Shahu
**Last Updated:** 2026-02-08
