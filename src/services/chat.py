"""
FILE: chat.py
STATUS: Active
RESPONSIBILITY: Hybrid RAG pipeline (SQL + Vector Search) orchestration service
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import logging
import time

from google import genai
from google.genai.errors import ClientError

from src.core.config import settings
from src.core.exceptions import IndexNotFoundError, LLMError
from src.core.observability import logfire
from src.core.security import sanitize_query, validate_search_params
from src.models.chat import ChatRequest, ChatResponse, SearchResult
from src.repositories.vector_store import VectorStoreRepository
from src.services.embedding import EmbeddingService
from src.services.query_classifier import QueryClassifier, QueryType
from src.services.query_expansion import QueryExpander
from src.tools.sql_tool import NBAGSQLTool

logger = logging.getLogger(__name__)


# System prompt template
# Phase 4 improvements: Explicit relevancy and faithfulness constraints
# Phase 10 improvements: SQL data priority + English-only context
# IMPORTANT: English language to ensure consistent English responses
SYSTEM_PROMPT_TEMPLATE = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

CRITICAL INSTRUCTIONS:
1. Answer DIRECTLY to the question asked - do not deviate from the topic
2. Base your answer ONLY on information from the context above
3. NEVER add information that is not in the context
4. **STATISTICAL DATA (FROM SQL DATABASE)** contains EXACT FACTS from the official database:
   - This is the PRIMARY source for all statistical queries
   - Use these exact numbers - they are authoritative and verified
   - Each numbered entry or bullet point is a complete database record
5. **DOCUMENTS AND ANALYSIS** contains contextual information:
   - Use this for player stories, analysis, opinions, and qualitative insights
   - This supplements but does NOT replace statistical data
6. When SQL data is present, you MUST use it to answer statistical questions
7. If neither section contains the answer, state: "I cannot find this information in the provided context"
8. Be precise and concise - provide exact numbers and names from the data
9. For lists/rankings, present them clearly (numbered or bulleted)
10. ALWAYS respond in English

RESPONSE:"""


class ChatService:
    """Service for RAG-powered chat functionality.

    Orchestrates the complete RAG pipeline with proper error handling
    and dependency injection.

    Attributes:
        vector_store: Repository for vector search
        embedding_service: Service for generating embeddings
    """

    def __init__(
        self,
        vector_store: VectorStoreRepository | None = None,
        embedding_service: EmbeddingService | None = None,
        api_key: str | None = None,
        model: str | None = None,
        enable_sql: bool = True,
    ):
        """Initialize chat service.

        Args:
            vector_store: Vector store repository (created if not provided)
            embedding_service: Embedding service (created if not provided)
            api_key: Google API key (default from settings)
            model: Chat model name (default from settings)
            enable_sql: Enable SQL tool for statistical queries (default: True)
        """
        self._api_key = api_key or settings.google_api_key
        self._model = model or "gemini-2.0-flash"  # Upgraded from flash-lite for better comprehension
        self._temperature = settings.temperature
        self._enable_sql = enable_sql

        # Dependencies (lazy initialization)
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._client: genai.Client | None = None
        self._sql_tool: NBAGSQLTool | None = None
        self._query_classifier: QueryClassifier | None = None
        self._query_expander: QueryExpander | None = None

    @property
    def vector_store(self) -> VectorStoreRepository:
        """Get vector store repository (lazy initialization)."""
        if self._vector_store is None:
            self._vector_store = VectorStoreRepository()
            self._vector_store.load()
        return self._vector_store

    @property
    def embedding_service(self) -> EmbeddingService:
        """Get embedding service (lazy initialization)."""
        if self._embedding_service is None:
            # EmbeddingService uses Mistral - don't pass Google API key!
            # Let it use settings.mistral_api_key by default
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    @property
    def client(self) -> genai.Client:
        """Get Gemini client (lazy initialization)."""
        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        return self._client

    @property
    def model(self) -> str:
        """Get chat model name."""
        return self._model

    @property
    def sql_tool(self) -> NBAGSQLTool | None:
        """Get SQL tool (lazy initialization)."""
        if not self._enable_sql:
            return None
        if self._sql_tool is None:
            try:
                self._sql_tool = NBAGSQLTool(google_api_key=self._api_key)
                logger.info("SQL tool initialized successfully")
            except Exception as e:
                logger.warning(f"SQL tool initialization failed: {e}")
                self._sql_tool = None
        return self._sql_tool

    @property
    def query_classifier(self) -> QueryClassifier:
        """Get query classifier (lazy initialization)."""
        if self._query_classifier is None:
            self._query_classifier = QueryClassifier()
        return self._query_classifier

    @property
    def query_expander(self) -> QueryExpander:
        """Get query expander (lazy initialization)."""
        if self._query_expander is None:
            self._query_expander = QueryExpander()
        return self._query_expander

    @property
    def is_ready(self) -> bool:
        """Check if service is ready (index loaded)."""
        return self.vector_store.is_loaded

    def ensure_ready(self) -> None:
        """Ensure service is ready.

        Raises:
            IndexNotFoundError: If index is not loaded
        """
        if not self.is_ready:
            # Try to load
            if not self.vector_store.load():
                raise IndexNotFoundError("Vector index not loaded. Run indexer first.")

    @logfire.instrument("ChatService.search {query=}")
    def search(
        self,
        query: str,
        k: int | None = None,
        min_score: float | None = None,
    ) -> list[SearchResult]:
        """Search for relevant documents with smart metadata filtering.

        Args:
            query: Search query
            k: Number of results (default from settings)
            min_score: Minimum similarity score (0-1)

        Returns:
            List of search results

        Raises:
            ValidationError: If query is invalid
            IndexNotFoundError: If index not loaded
            SearchError: If search fails
        """
        # Validate inputs
        query = sanitize_query(query)
        k = k or settings.search_k
        validate_search_params(k, min_score)

        self.ensure_ready()

        # PHASE 7: Expand query for better keyword matching (replaces metadata filtering)
        expanded_query = self.query_expander.expand_smart(query)
        if expanded_query != query:
            logger.info(f"Expanded query: '{query}' -> '{expanded_query[:100]}...'")

        # PHASE 6 metadata filtering DISABLED - caused false negatives
        # (Only 3 chunks tagged as player_stats, all were headers not actual data)
        # Query expansion provides better precision without excluding relevant chunks

        # Generate query embedding using expanded query
        query_embedding = self.embedding_service.embed_query(expanded_query)

        # Search WITHOUT metadata filters (Phase 7 approach)
        results = self.vector_store.search(
            query_embedding=query_embedding,
            k=k,
            min_score=min_score,
            metadata_filters=None,
        )

        # Convert to response models
        return [
            SearchResult(
                text=chunk.text,
                score=score,
                source=chunk.metadata.get("source", "unknown"),
                metadata={
                    k: v
                    for k, v in chunk.metadata.items()
                    if k != "source" and isinstance(v, str | int | float)
                },
            )
            for chunk, score in results
        ]

    @logfire.instrument("ChatService.generate_response")
    def generate_response(
        self,
        query: str,
        context: str,
        prompt_template: str | None = None,
    ) -> str:
        """Generate LLM response with context.

        Args:
            query: User query
            context: Retrieved context
            prompt_template: Optional custom prompt template (for Phase 8 testing)

        Returns:
            Generated response text

        Raises:
            LLMError: If LLM call fails
        """
        # Build prompt (use custom template if provided, otherwise default)
        template = prompt_template if prompt_template is not None else SYSTEM_PROMPT_TEMPLATE
        prompt = template.format(
            app_name=settings.app_name,
            context=context,
            question=query,
        )

        try:
            logger.info("Calling Gemini LLM with model %s", self._model)

            response = self.client.models.generate_content(
                model=self._model,
                contents=prompt,
                config={
                    "temperature": self._temperature,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
            )

            if response.text:
                return response.text

            logger.warning("Gemini returned no text")
            return "I could not generate a response."

        except ClientError as e:
            logger.error("Gemini API error: %s", e)
            raise LLMError(f"LLM API error: {e}") from e

        except Exception as e:
            logger.error("LLM call failed: %s", e)
            raise LLMError(f"LLM call failed: {e}") from e

    @logfire.instrument("ChatService.chat")
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request through hybrid RAG pipeline (SQL + Vector Search).

        Args:
            request: Chat request with query and parameters

        Returns:
            Chat response with answer and sources

        Raises:
            ValidationError: If request is invalid
            IndexNotFoundError: If index not loaded
            SearchError: If search fails
            LLMError: If LLM call fails
        """
        start_time = time.time()

        # Sanitize query
        query = sanitize_query(request.query)

        # Classify query to determine routing
        query_type = self.query_classifier.classify(query) if self._enable_sql else QueryType.CONTEXTUAL

        # Route to appropriate data source(s)
        context_parts = []
        search_results = []
        sql_failed = False  # Track SQL failure for fallback
        sql_success = False  # Track SQL success

        # Statistical query → SQL tool
        if query_type in (QueryType.STATISTICAL, QueryType.HYBRID):
            if self.sql_tool:
                try:
                    logger.info(f"Routing to SQL tool (query_type: {query_type.value})")
                    sql_result = self.sql_tool.query(query)

                    if sql_result["error"]:
                        logger.warning(f"SQL query failed: {sql_result['error']} - falling back to vector search")
                        sql_failed = True
                    elif not sql_result["results"]:
                        logger.warning("SQL query returned no results - falling back to vector search")
                        sql_failed = True
                    else:
                        # Format SQL results with enhanced structure for better LLM comprehension
                        num_rows = len(sql_result["results"])

                        # Create clear, numbered formatting
                        if num_rows == 1:
                            # Single result - use key-value format
                            row = sql_result["results"][0]
                            formatted_data = []
                            for key, value in row.items():
                                formatted_data.append(f"  • {key}: {value}")
                            sql_context = "\n".join(formatted_data)
                            header = "STATISTICAL DATA (FROM SQL DATABASE):\nFound 1 matching record:\n\n"
                        else:
                            # Multiple results - use numbered list format
                            formatted_rows = []
                            for i, row in enumerate(sql_result["results"][:20], 1):  # Limit to top 20
                                row_parts = [f"{k}: {v}" for k, v in row.items()]
                                formatted_rows.append(f"{i}. {', '.join(row_parts)}")

                            sql_context = "\n".join(formatted_rows)

                            if num_rows > 20:
                                sql_context += f"\n\n(Showing top 20 of {num_rows} total results)"
                                header = f"STATISTICAL DATA (FROM SQL DATABASE):\nFound {num_rows} matching records (showing top 20):\n\n"
                            else:
                                header = f"STATISTICAL DATA (FROM SQL DATABASE):\nFound {num_rows} matching records:\n\n"

                        context_parts.append(header + sql_context)
                        logger.info(f"SQL query returned {num_rows} rows")
                        sql_success = True

                except Exception as e:
                    logger.error(f"SQL tool error: {e} - falling back to vector search")
                    sql_failed = True

        # Contextual/Hybrid query → Vector search
        # Also fallback to vector if SQL failed for STATISTICAL queries
        # OR always add vector search for HYBRID queries
        should_use_vector = (
            query_type == QueryType.CONTEXTUAL or
            query_type == QueryType.HYBRID or
            (query_type == QueryType.STATISTICAL and sql_failed)
        )

        if should_use_vector:
            if sql_failed and query_type == QueryType.STATISTICAL:
                logger.info("SQL fallback activated - using vector search for statistical query")
            else:
                logger.info(f"Routing to vector search (query_type: {query_type.value})")

            search_results = self.search(
                query=query,
                k=request.k,
                min_score=request.min_score,
            )

            # Format vector search context
            if search_results:
                vector_context = "\n\n---\n\n".join(
                    [f"Source: {r.source} (Score: {r.score:.1f}%)\n{r.text}" for r in search_results]
                )
                context_parts.append(f"DOCUMENTS AND ANALYSIS:\n{vector_context}")

        # Combine contexts
        if context_parts:
            context = "\n\n=== === ===\n\n".join(context_parts)
        else:
            context = "No relevant information found."

        # Generate response
        answer = self.generate_response(query=query, context=context)

        # SMART FALLBACK: If SQL succeeded but LLM still says "cannot find", retry with vector search
        if sql_success and not sql_failed and "cannot find" in answer.lower():
            logger.warning("SQL succeeded but LLM couldn't use results - retrying with vector search")

            # Get vector search results
            search_results = self.search(
                query=query,
                k=request.k,
                min_score=request.min_score,
            )

            if search_results:
                # Retry with vector context
                vector_context = "\n\n---\n\n".join(
                    [f"Source: {r.source} (Score: {r.score:.1f}%)\n{r.text}" for r in search_results]
                )
                fallback_context = f"DOCUMENTS AND ANALYSIS:\n{vector_context}"

                # Regenerate response with vector context
                answer = self.generate_response(query=query, context=fallback_context)
                logger.info("Vector search fallback succeeded")

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            answer=answer,
            sources=search_results if request.include_sources else [],
            query=query,
            processing_time_ms=processing_time_ms,
            model=self._model,
        )
