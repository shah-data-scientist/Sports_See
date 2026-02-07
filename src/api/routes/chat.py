"""
FILE: chat.py
STATUS: Active
RESPONSIBILITY: Chat API endpoints (chat, search, ask)
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import logging

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_chat_service
from src.models.chat import ChatRequest, ChatResponse, SearchResult
from src.services.chat import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with RAG",
    description="Send a question and get an AI-powered answer based on the knowledge base.",
    responses={
        200: {"description": "Successful response with answer and sources"},
        422: {"description": "Validation error in request"},
        503: {"description": "Vector index not available"},
    },
)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request through the RAG pipeline.

    Args:
        request: Chat request containing the query and parameters

    Returns:
        ChatResponse with AI-generated answer and source documents
    """
    logger.info("Chat request received: %s", request.query[:50])

    service = get_chat_service()
    response = service.chat(request)

    logger.info(
        "Chat response generated in %.2fms with %d sources",
        response.processing_time_ms,
        len(response.sources),
    )

    return response


@router.get(
    "/search",
    response_model=list[SearchResult],
    summary="Search Knowledge Base",
    description="Search for relevant documents without generating an answer.",
)
async def search(
    query: str = Query(
        ...,
        min_length=1,
        max_length=2000,
        description="Search query",
        examples=["NBA championship 2023"],
    ),
    k: int = Query(
        default=5,
        ge=1,
        le=20,
        description="Number of results to return",
    ),
    min_score: float | None = Query(
        default=None,
        ge=0,
        le=1,
        description="Minimum similarity score (0-1)",
    ),
) -> list[SearchResult]:
    """Search the knowledge base for relevant documents.

    Args:
        query: Search query string
        k: Number of results to return
        min_score: Minimum similarity score filter

    Returns:
        List of matching documents with scores
    """
    logger.info("Search request: %s (k=%d)", query[:50], k)

    service = get_chat_service()
    results = service.search(query=query, k=k, min_score=min_score)

    logger.info("Found %d search results", len(results))

    return results


@router.post(
    "/ask",
    response_model=ChatResponse,
    summary="Quick Question",
    description="Simplified endpoint - just send a question as query parameter.",
)
async def ask(
    question: str = Query(
        ...,
        min_length=1,
        max_length=2000,
        description="Your question",
        examples=["Who won the NBA championship in 2023?"],
    ),
) -> ChatResponse:
    """Quick question endpoint.

    Simplified interface for asking questions - just pass the question
    as a query parameter.

    Args:
        question: The question to ask

    Returns:
        ChatResponse with AI-generated answer
    """
    request = ChatRequest(query=question)
    service = get_chat_service()
    return service.chat(request)
