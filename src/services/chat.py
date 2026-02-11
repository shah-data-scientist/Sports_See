"""
FILE: chat.py
STATUS: Active
RESPONSIBILITY: Hybrid RAG pipeline (SQL + Vector Search) orchestration service
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import logging
import time
from typing import Callable, TypeVar

from google import genai
from google.genai.errors import ClientError

from src.core.config import settings
from src.core.exceptions import IndexNotFoundError, LLMError
from src.core.observability import logfire
from src.core.security import sanitize_query, validate_search_params
from src.models.chat import ChatRequest, ChatResponse, SearchResult, Visualization
from src.repositories.feedback import FeedbackRepository
from src.repositories.vector_store import VectorStoreRepository
from src.services.embedding import EmbeddingService
from src.services.query_classifier import QueryClassifier, QueryType
from src.services.query_expansion import QueryExpander
from src.services.visualization_service import VisualizationService
from src.tools.sql_tool import NBAGSQLTool

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_exponential_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 2.0,
    max_delay: float = 30.0,
) -> T:
    """Retry a function with exponential backoff on rate limit errors.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (doubles each retry)
        max_delay: Maximum delay in seconds

    Returns:
        Result from successful function call

    Raises:
        LLMError: If all retries exhausted or non-rate-limit error occurs
    """
    delay = initial_delay

    for attempt in range(max_retries + 1):
        try:
            return func()
        except ClientError as e:
            # Check if this is a rate limit error (429)
            error_str = str(e)
            is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str

            if not is_rate_limit:
                # Not a rate limit error, raise immediately
                logger.error("Non-rate-limit Gemini API error: %s", e)
                raise LLMError(f"LLM API error: {e}") from e

            if attempt >= max_retries:
                # Exhausted all retries
                logger.error(
                    "Rate limit error after %d retries: %s",
                    max_retries,
                    e
                )
                raise LLMError(
                    f"Rate limit exceeded after {max_retries} retries. "
                    "Please try again in a few moments."
                ) from e

            # Wait with exponential backoff
            wait_time = min(delay, max_delay)
            logger.warning(
                "Rate limit hit (attempt %d/%d), retrying in %.1fs: %s",
                attempt + 1,
                max_retries + 1,
                wait_time,
                error_str[:100]
            )
            time.sleep(wait_time)
            delay *= 2


# System prompt templates
# Phase 12 improvements: Query-type-specific prompts with mandatory data usage
# - SYSTEM_PROMPT_TEMPLATE: Default/fallback for general queries
# - SQL_ONLY_PROMPT: Force extraction of SQL results (COUNT/AVG/SUM)
# - HYBRID_PROMPT: Mandate blending of SQL stats + vector context
# - CONTEXTUAL_PROMPT: For qualitative analysis with citations

# Default prompt (fallback for general queries)
# Phase 12C: Answer relevancy fix - direct, focused instructions
SYSTEM_PROMPT_TEMPLATE = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

CONTEXT:
---
{context}
---

USER QUESTION:
{question}

INSTRUCTIONS:

**ANSWER THE EXACT QUESTION THE USER ASKED - NOTHING MORE, NOTHING LESS**

1. Read the USER QUESTION carefully - understand what they're asking for
2. Find the answer in the CONTEXT above - extract specific facts, numbers, or names
3. Provide a DIRECT answer to the question
4. Cite sources: [Source: document name] or [SQL] for database results
5. If conversation history exists, use it to resolve pronouns (he, his, them)
6. If no relevant data exists, say: "The available data doesn't contain this information"
7. Respond in English

Keep your answer focused and concise. Don't add extra information not requested.

ANSWER:"""

# SQL-only prompt: Force extraction of statistical data
# Phase 12C: Answer relevancy fix - clear, direct extraction
SQL_ONLY_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

STATISTICAL DATA (FROM SQL DATABASE):
---
{context}
---

USER QUESTION:
{question}

INSTRUCTIONS:

**ANSWER THE EXACT QUESTION USING THE STATISTICAL DATA ABOVE**

1. The STATISTICAL DATA contains the exact answer from the database
2. Extract the relevant data:
   - "COUNT Result: X" → answer with the number X
   - "AVERAGE Result: X" → answer with X
   - "Found N records" → list/summarize those records
3. Provide a DIRECT answer to the question
4. Format clearly - present numbers in a readable way
5. If conversation history exists, resolve pronouns (he, his, them)
6. Respond in English

CRITICAL: The STATISTICAL DATA above ALWAYS contains the answer.
Do NOT say "data not available" if data is clearly shown above.
Only if the section says "No results found" should you state data is unavailable.

ANSWER:"""

# Hybrid prompt: Mandate blending of SQL + vector
HYBRID_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant with two data sources:

{conversation_history}

STATISTICAL DATA (FROM SQL DATABASE):
---
{sql_context}
---

CONTEXTUAL KNOWLEDGE (Analysis & Insights):
---
{vector_context}
---

USER QUESTION:
{question}

CRITICAL INSTRUCTIONS FOR HYBRID ANSWERS:

**YOU MUST USE BOTH DATA SOURCES ABOVE - THIS IS MANDATORY**

1. **START with the STATISTICAL answer** from SQL data (WHAT the numbers are)
   - Extract exact numbers, names, and stats from the SQL section above

2. **THEN ADD CONTEXTUAL ANALYSIS** from the contextual knowledge (WHY/HOW it matters)
   - Use the contextual knowledge section to explain styles, strategies, impact, or qualitative insights
   - **DO NOT skip this step** - the contextual knowledge is provided for a reason
   - Look for playing styles, strategic analysis, expert opinions, or qualitative assessments

3. **BLEND both components** seamlessly:
   - Connect stats to analysis with transition words ("because", "which", "making", "due to", "this")
   - Create a cohesive answer that combines WHAT (SQL) with WHY/HOW (context)

4. **CITE sources** for transparency:
   - [SQL] for statistics
   - [Source: document name] for contextual insights

5. **If conversation history is provided**, use it to resolve pronouns (he, his, them, etc.)

6. ALWAYS respond in English

**FAILURE TO USE CONTEXTUAL KNOWLEDGE IS UNACCEPTABLE**
If contextual knowledge is provided above, you MUST incorporate it into your answer.
Do not ignore it or say "data not available" when contextual information clearly exists.

EXAMPLE FORMAT:
"LeBron James scored 1,708 points this season [SQL]. His scoring comes from a mix of drives to the basket and perimeter shooting, making him a versatile offensive threat [Context: ESPN Analysis]. This inside-outside combination keeps defenses guessing and creates opportunities for his teammates [Context: Reddit Discussion]."

YOUR ANSWER (MUST combine both SQL stats + contextual analysis):"""

# Contextual prompt: For qualitative analysis
# Phase 12C: Answer relevancy fix - focused qualitative analysis
CONTEXTUAL_PROMPT = """You are '{app_name} Analyst AI', an expert NBA sports analysis assistant.

{conversation_history}

CONTEXTUAL KNOWLEDGE:
---
{context}
---

USER QUESTION:
{question}

INSTRUCTIONS:

**ANSWER THE EXACT QUESTION USING THE CONTEXTUAL KNOWLEDGE ABOVE**

1. Read the question - understand what qualitative insight they want
2. Find the answer in the CONTEXTUAL KNOWLEDGE - look for playing styles, strategies, expert opinions, analysis
3. Provide a DIRECT answer to the question
4. Cite sources for credibility: [Source: document name]
5. Focus on qualitative analysis (WHY/HOW, not statistics)
6. If conversation history exists, resolve pronouns (he, his, them)
7. If context lacks the information, say: "The available context doesn't contain this information"
8. Respond in English

Keep your answer focused on what was asked. Don't add unrelated analysis.

ANSWER:"""


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
        feedback_repository: FeedbackRepository | None = None,
        api_key: str | None = None,
        model: str | None = None,
        enable_sql: bool = True,
        enable_vector_fallback: bool = True,
        conversation_history_limit: int = 5,
    ):
        """Initialize chat service.

        Args:
            vector_store: Vector store repository (created if not provided)
            embedding_service: Embedding service (created if not provided)
            feedback_repository: Feedback repository for conversation history (created if not provided)
            api_key: Google API key (default from settings)
            model: Chat model name (default from settings)
            enable_sql: Enable SQL tool for statistical queries (default: True)
            enable_vector_fallback: Enable fallback to vector search when SQL fails (default: True)
            conversation_history_limit: Number of previous turns to include in context (default: 5)
        """
        self._api_key = api_key or settings.google_api_key
        self._model = model or "gemini-2.0-flash"  # Upgraded from flash-lite for better comprehension
        self._temperature = settings.temperature
        self._enable_sql = enable_sql
        self._enable_vector_fallback = enable_vector_fallback
        self._conversation_history_limit = conversation_history_limit

        # Dependencies (lazy initialization)
        self._vector_store = vector_store
        self._embedding_service = embedding_service
        self._feedback_repository = feedback_repository
        self._client: genai.Client | None = None
        self._sql_tool: NBAGSQLTool | None = None
        self._query_classifier: QueryClassifier | None = None
        self._query_expander: QueryExpander | None = None
        self._visualization_service: VisualizationService | None = None

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
    def visualization_service(self) -> VisualizationService:
        """Get visualization service (lazy initialization)."""
        if self._visualization_service is None:
            self._visualization_service = VisualizationService()
        return self._visualization_service

    @property
    def feedback_repository(self) -> FeedbackRepository:
        """Get feedback repository (lazy initialization)."""
        if self._feedback_repository is None:
            self._feedback_repository = FeedbackRepository()
        return self._feedback_repository

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

    def _build_conversation_context(self, conversation_id: str, current_turn: int) -> str:
        """Build conversation history context for the prompt.

        Args:
            conversation_id: Conversation ID
            current_turn: Current turn number

        Returns:
            Formatted conversation history string, or empty string if no history
        """
        # Get previous messages (excluding current turn)
        messages = self.feedback_repository.get_messages_by_conversation(conversation_id)

        # Filter to only previous turns (not including current)
        previous_messages = [msg for msg in messages if msg.turn_number and msg.turn_number < current_turn]

        # Limit to last N turns
        if len(previous_messages) > self._conversation_history_limit:
            previous_messages = previous_messages[-self._conversation_history_limit :]

        # No history to show
        if not previous_messages:
            return ""

        # Format history
        history_lines = ["CONVERSATION HISTORY:"]
        for msg in previous_messages:
            history_lines.append(f"User: {msg.query}")
            history_lines.append(f"Assistant: {msg.response}")

        history_lines.append("---\n")
        return "\n".join(history_lines)

    def _format_sql_results(self, sql_results: list[dict]) -> str:
        """Format SQL results with special handling for scalar values (COUNT, AVG, SUM).

        Args:
            sql_results: List of result dictionaries from SQL query

        Returns:
            Formatted string for LLM prompt
        """
        if not sql_results:
            return "No results found."

        num_rows = len(sql_results)

        # SPECIAL CASE 1: Single scalar result (COUNT, AVG, SUM, MAX, MIN)
        if num_rows == 1 and len(sql_results[0]) == 1:
            key, value = list(sql_results[0].items())[0]
            key_lower = key.lower()

            # Format based on aggregation type
            if "count" in key_lower:
                return f"COUNT Result: {value} (total number of records matching the criteria)"
            elif "avg" in key_lower or "average" in key_lower:
                return f"AVERAGE Result: {value:.2f}"
            elif "sum" in key_lower or "total" in key_lower:
                return f"SUM/TOTAL Result: {value}"
            elif "max" in key_lower or "maximum" in key_lower:
                return f"MAXIMUM Result: {value}"
            elif "min" in key_lower or "minimum" in key_lower:
                return f"MINIMUM Result: {value}"
            else:
                return f"Result: {value}"

        # SPECIAL CASE 2: Single record (player/team lookup)
        if num_rows == 1:
            row = sql_results[0]
            row_text = "\n".join(f"  • {k}: {v}" for k, v in row.items())
            return f"Found 1 matching record:\n\n{row_text}"

        # GENERAL CASE: Multiple records (top N, rankings, comparisons)
        formatted_rows = []
        for i, row in enumerate(sql_results[:20], 1):
            row_parts = [f"{k}: {v}" for k, v in row.items()]
            formatted_rows.append(f"{i}. {', '.join(row_parts)}")

        result = "\n".join(formatted_rows)

        if num_rows > 20:
            result += f"\n\n(Showing top 20 of {num_rows} total results)"
            return f"Found {num_rows} matching records (showing top 20):\n\n{result}"
        else:
            return f"Found {num_rows} matching records:\n\n{result}"

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
        conversation_history: str = "",
        prompt_template: str | None = None,
    ) -> str:
        """Generate LLM response with context.

        Args:
            query: User query
            context: Retrieved context
            conversation_history: Conversation history context (optional)
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
            conversation_history=conversation_history,
            context=context,
            question=query,
        )

        try:
            logger.info("Calling Gemini LLM with model %s", self._model)

            # Wrap API call with retry logic for rate limit handling
            def _call_llm():
                return self.client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config={
                        "temperature": self._temperature,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    },
                )

            response = retry_with_exponential_backoff(_call_llm)

            if response.text:
                return response.text

            logger.warning("Gemini returned no text")
            return "I could not generate a response."

        except Exception as e:
            logger.error("LLM call failed: %s", e)
            raise LLMError(f"LLM call failed: {e}") from e

    @logfire.instrument("ChatService.generate_response_hybrid")
    def generate_response_hybrid(
        self,
        query: str,
        sql_context: str,
        vector_context: str,
        conversation_history: str = "",
    ) -> str:
        """Generate LLM response for hybrid queries (SQL + Vector).

        Args:
            query: User query
            sql_context: SQL query results context
            vector_context: Vector search context
            conversation_history: Conversation history context (optional)

        Returns:
            Generated response text

        Raises:
            LLMError: If LLM call fails
        """
        # Build prompt with separate SQL and vector contexts
        prompt = HYBRID_PROMPT.format(
            app_name=settings.app_name,
            conversation_history=conversation_history,
            sql_context=sql_context,
            vector_context=vector_context,
            question=query,
        )

        try:
            logger.info("Calling Gemini LLM with model %s (hybrid query)", self._model)

            # Wrap API call with retry logic for rate limit handling
            def _call_llm():
                return self.client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config={
                        "temperature": self._temperature,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    },
                )

            response = retry_with_exponential_backoff(_call_llm)

            if response.text:
                return response.text

            logger.warning("Gemini returned no text")
            return "I could not generate a response."

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

        # Build conversation context if conversation_id provided
        conversation_history = ""
        if request.conversation_id:
            conversation_history = self._build_conversation_context(
                request.conversation_id,
                request.turn_number
            )
            if conversation_history:
                logger.info(f"Including conversation history ({request.turn_number - 1} previous turns)")

        # Classify query to determine routing
        query_type = self.query_classifier.classify(query) if self._enable_sql else QueryType.CONTEXTUAL

        # Route to appropriate data source(s)
        search_results = []
        sql_failed = False  # Track SQL failure for fallback
        sql_success = False  # Track SQL success
        sql_context = ""
        vector_context = ""
        generated_sql = None  # Track generated SQL for Phase 2 analysis
        sql_result_data = None  # Track SQL results for visualization

        # Statistical query → SQL tool
        if query_type in (QueryType.STATISTICAL, QueryType.HYBRID):
            if self.sql_tool:
                try:
                    logger.info(f"Routing to SQL tool (query_type: {query_type.value})")
                    sql_result = self.sql_tool.query(query)

                    # Capture generated SQL for evaluation/analysis
                    if sql_result["sql"]:
                        generated_sql = sql_result["sql"]
                        logger.debug(f"Generated SQL: {generated_sql}")

                    if sql_result["error"]:
                        logger.warning(f"SQL query failed: {sql_result['error']} - falling back to vector search")
                        sql_failed = True
                    elif not sql_result["results"]:
                        logger.warning("SQL query returned no results - falling back to vector search")
                        sql_failed = True
                    else:
                        # Use new _format_sql_results() method with scalar handling
                        sql_context = self._format_sql_results(sql_result["results"])
                        logger.info(f"SQL query returned {len(sql_result['results'])} rows")
                        sql_success = True
                        # Store SQL results for visualization
                        sql_result_data = sql_result["results"]

                except Exception as e:
                    logger.error(f"SQL tool error: {e} - falling back to vector search")
                    sql_failed = True

        # Contextual/Hybrid query → Vector search
        # Also fallback to vector if SQL failed for STATISTICAL queries (when fallback enabled)
        # OR always add vector search for HYBRID queries
        should_use_vector = (
            query_type == QueryType.CONTEXTUAL or
            query_type == QueryType.HYBRID or
            (query_type == QueryType.STATISTICAL and sql_failed and self._enable_vector_fallback)
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

        # Select prompt template and format context based on query type
        if query_type == QueryType.STATISTICAL and sql_success:
            # SQL-only: Use SQL_ONLY_PROMPT
            prompt_template = SQL_ONLY_PROMPT
            context = sql_context
        elif query_type == QueryType.HYBRID and sql_success and vector_context:
            # Hybrid: Use HYBRID_PROMPT with separate SQL and vector sections
            prompt_template = HYBRID_PROMPT
            # HYBRID_PROMPT expects separate sql_context and vector_context parameters
            # We'll handle this in generate_response call
            context = None  # Signal to use sql_context + vector_context
        elif query_type == QueryType.CONTEXTUAL and vector_context:
            # Contextual: Use CONTEXTUAL_PROMPT
            prompt_template = CONTEXTUAL_PROMPT
            context = vector_context
        else:
            # Fallback: Use default SYSTEM_PROMPT_TEMPLATE
            prompt_template = SYSTEM_PROMPT_TEMPLATE
            # Combine contexts for fallback
            context_parts = []
            if sql_context:
                context_parts.append(f"STATISTICAL DATA (FROM SQL DATABASE):\n{sql_context}")
            if vector_context:
                context_parts.append(f"DOCUMENTS AND ANALYSIS:\n{vector_context}")
            context = "\n\n=== === ===\n\n".join(context_parts) if context_parts else "No relevant information found."

        # Generate response with appropriate prompt
        if context is None:
            # HYBRID case: pass sql_context and vector_context separately
            answer = self.generate_response_hybrid(
                query=query,
                sql_context=sql_context,
                vector_context=vector_context,
                conversation_history=conversation_history,
            )
        else:
            # All other cases: use standard generate_response
            answer = self.generate_response(
                query=query,
                context=context,
                conversation_history=conversation_history,
                prompt_template=prompt_template,
            )

        # SMART FALLBACK: If SQL succeeded but LLM still says "cannot find", retry with vector search
        if sql_success and not sql_failed and "cannot find" in answer.lower():
            logger.warning("SQL succeeded but LLM couldn't use results - retrying with vector search")

            # Get vector search results (if not already retrieved)
            if not search_results:
                search_results = self.search(
                    query=query,
                    k=request.k,
                    min_score=request.min_score,
                )

            if search_results:
                # Retry with vector context using CONTEXTUAL_PROMPT
                fallback_vector_context = "\n\n---\n\n".join(
                    [f"Source: {r.source} (Score: {r.score:.1f}%)\n{r.text}" for r in search_results]
                )

                # Regenerate response with vector context
                answer = self.generate_response(
                    query=query,
                    context=fallback_vector_context,
                    conversation_history=conversation_history,
                    prompt_template=CONTEXTUAL_PROMPT,
                )
                logger.info("Vector search fallback succeeded")

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Generate visualization for statistical queries with SQL results
        visualization = None
        if query_type in (QueryType.STATISTICAL, QueryType.HYBRID):
            if sql_success and sql_result_data:
                try:
                    logger.info("Generating visualization for SQL results")
                    viz_data = self.visualization_service.generate_visualization(
                        query=query,
                        sql_result=sql_result_data
                    )
                    visualization = Visualization(
                        pattern=viz_data["pattern"],
                        viz_type=viz_data["viz_type"],
                        plot_json=viz_data["plot_json"],
                        plot_html=viz_data["plot_html"],
                    )
                    logger.info(f"Visualization generated: {viz_data['viz_type']} ({viz_data['pattern']})")
                except Exception as e:
                    # Don't fail the whole request if visualization fails
                    logger.warning(f"Visualization generation failed: {e}")
            else:
                # Log why visualization was skipped
                if not sql_success:
                    logger.info(
                        "Visualization skipped: SQL query failed, used vector fallback. "
                        "Visualizations require structured data from SQL results."
                    )
                elif not sql_result_data:
                    logger.info("Visualization skipped: SQL query returned no results")

        return ChatResponse(
            answer=answer,
            sources=search_results if request.include_sources else [],
            query=query,
            processing_time_ms=processing_time_ms,
            model=self._model,
            conversation_id=request.conversation_id,
            turn_number=request.turn_number,
            generated_sql=generated_sql,
            visualization=visualization,
        )
