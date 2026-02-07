"""
FILE: chat.py
STATUS: Active
RESPONSIBILITY: Hybrid RAG pipeline (SQL + Vector Search) orchestration service
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

import logging
import time

from mistralai import Mistral
from mistralai.models import SDKError

from src.core.config import settings
from src.core.exceptions import IndexNotFoundError, LLMError
from src.core.observability import logfire
from src.core.security import sanitize_query, validate_search_params
from src.models.chat import ChatRequest, ChatResponse, SearchResult
from src.repositories.vector_store import VectorStoreRepository
from src.services.embedding import EmbeddingService
from src.services.query_classifier import QueryClassifier, QueryType
from src.tools.sql_tool import NBAGSQLTool

logger = logging.getLogger(__name__)


# System prompt template
# Phase 4 improvements: Explicit relevancy and faithfulness constraints
SYSTEM_PROMPT_TEMPLATE = """Tu es '{app_name} Analyst AI', un assistant expert en analyse sportive NBA.

CONTEXTE:
---
{context}
---

QUESTION DE L'UTILISATEUR:
{question}

INSTRUCTIONS CRITIQUES:
1. Réponds DIRECTEMENT à la question posée - ne dévie pas du sujet
2. Base ta réponse UNIQUEMENT sur les informations du contexte ci-dessus
3. N'ajoute JAMAIS d'informations qui ne sont pas dans le contexte
4. Si le contexte ne contient pas l'information nécessaire, dis clairement "Je ne trouve pas cette information dans le contexte fourni"
5. Sois précis et concis - va droit au but
6. Cite les sources (noms de joueurs, équipes, statistiques) exactement comme indiqué dans le contexte

RÉPONSE:"""


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
            api_key: Mistral API key (default from settings)
            model: Chat model name (default from settings)
            enable_sql: Enable SQL tool for statistical queries (default: True)
        """
        self._api_key = api_key or settings.mistral_api_key
        self._model = model or settings.chat_model
        self._temperature = settings.temperature
        self._enable_sql = enable_sql

        # Dependencies (lazy initialization)
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._client: Mistral | None = None
        self._sql_tool: NBAGSQLTool | None = None
        self._query_classifier: QueryClassifier | None = None

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
            self._embedding_service = EmbeddingService(api_key=self._api_key)
        return self._embedding_service

    @property
    def client(self) -> Mistral:
        """Get Mistral client (lazy initialization)."""
        if self._client is None:
            self._client = Mistral(api_key=self._api_key)
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
                self._sql_tool = NBAGSQLTool(mistral_api_key=self._api_key)
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
        """Search for relevant documents.

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

        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Search
        results = self.vector_store.search(
            query_embedding=query_embedding,
            k=k,
            min_score=min_score,
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
    ) -> str:
        """Generate LLM response with context.

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Generated response text

        Raises:
            LLMError: If LLM call fails
        """
        # Build prompt
        prompt = SYSTEM_PROMPT_TEMPLATE.format(
            app_name=settings.app_name,
            context=context,
            question=query,
        )

        try:
            logger.info("Calling LLM with model %s", self._model)

            response = self.client.chat.complete(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self._temperature,
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content

            logger.warning("LLM returned no choices")
            return "Je n'ai pas pu générer de réponse."

        except SDKError as e:
            logger.error("Mistral API error: %s", e)
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
                        # Format SQL results as context
                        sql_context = self.sql_tool.format_results(sql_result["results"])
                        context_parts.append(f"DONNÉES STATISTIQUES (SQL):\n{sql_context}")
                        logger.info(f"SQL query returned {len(sql_result['results'])} rows")

                except Exception as e:
                    logger.error(f"SQL tool error: {e} - falling back to vector search")
                    sql_failed = True

        # Contextual/Hybrid query → Vector search
        # Also fallback to vector if SQL failed for STATISTICAL queries
        if query_type in (QueryType.CONTEXTUAL, QueryType.HYBRID) or (query_type == QueryType.STATISTICAL and sql_failed):
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
                context_parts.append(f"DOCUMENTS ET DISCUSSIONS:\n{vector_context}")

        # Combine contexts
        if context_parts:
            context = "\n\n=== === ===\n\n".join(context_parts)
        else:
            context = "Aucune information pertinente trouvée."

        # Generate response
        answer = self.generate_response(query=query, context=context)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        return ChatResponse(
            answer=answer,
            sources=search_results if request.include_sources else [],
            query=query,
            processing_time_ms=processing_time_ms,
            model=self._model,
        )
