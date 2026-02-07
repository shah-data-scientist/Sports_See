"""
FILE: test_models.py
STATUS: Active
RESPONSIBILITY: Tests for Pydantic model validation
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import pytest
from pydantic import ValidationError

from src.models.chat import ChatMessage, ChatRequest, ChatResponse, SearchResult
from src.models.document import Document, DocumentChunk, DocumentMetadata, IndexingRequest


class TestChatMessage:
    """Tests for ChatMessage model."""

    def test_valid_user_message(self):
        """Test creating a valid user message."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.timestamp is not None

    def test_valid_assistant_message(self):
        """Test creating a valid assistant message."""
        msg = ChatMessage(role="assistant", content="Hi there!")
        assert msg.role == "assistant"

    def test_invalid_role_raises(self):
        """Test that invalid role raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatMessage(role="system", content="test")

    def test_empty_content_raises(self):
        """Test that empty content raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatMessage(role="user", content="")

    def test_content_stripped(self):
        """Test that content is stripped."""
        msg = ChatMessage(role="user", content="  test  ")
        assert msg.content == "test"


class TestChatRequest:
    """Tests for ChatRequest model."""

    def test_valid_request(self):
        """Test creating a valid request."""
        req = ChatRequest(query="Who won?")
        assert req.query == "Who won?"
        assert req.k == 5  # default
        assert req.include_sources is True  # default

    def test_custom_params(self):
        """Test request with custom parameters."""
        req = ChatRequest(query="Test", k=10, min_score=0.5, include_sources=False)
        assert req.k == 10
        assert req.min_score == 0.5
        assert req.include_sources is False

    def test_empty_query_raises(self):
        """Test that empty query raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest(query="")

    def test_k_out_of_range_raises(self):
        """Test that k outside valid range raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest(query="test", k=0)

        with pytest.raises(ValidationError):
            ChatRequest(query="test", k=100)

    def test_min_score_out_of_range_raises(self):
        """Test that min_score outside 0-1 raises ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest(query="test", min_score=1.5)


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_valid_result(self):
        """Test creating a valid search result."""
        result = SearchResult(
            text="Document content",
            score=85.5,
            source="doc.pdf",
        )
        assert result.text == "Document content"
        assert result.score == 85.5
        assert result.source == "doc.pdf"

    def test_score_bounds(self):
        """Test that score must be 0-100."""
        with pytest.raises(ValidationError):
            SearchResult(text="test", score=150, source="doc")

        with pytest.raises(ValidationError):
            SearchResult(text="test", score=-10, source="doc")

    def test_metadata_optional(self):
        """Test that metadata is optional."""
        result = SearchResult(text="test", score=50, source="doc")
        assert result.metadata == {}


class TestChatResponse:
    """Tests for ChatResponse model."""

    def test_valid_response(self):
        """Test creating a valid response."""
        resp = ChatResponse(
            answer="The answer is 42",
            query="What is the answer?",
            processing_time_ms=150.5,
            model="mistral-small",
        )
        assert resp.answer == "The answer is 42"
        assert resp.processing_time_ms == 150.5

    def test_sources_default_empty(self):
        """Test that sources default to empty list."""
        resp = ChatResponse(
            answer="test",
            query="test",
            processing_time_ms=100,
            model="test",
        )
        assert resp.sources == []


class TestDocumentChunk:
    """Tests for DocumentChunk model."""

    def test_valid_chunk(self):
        """Test creating a valid chunk."""
        chunk = DocumentChunk(
            id="doc1_0",
            text="This is chunk content",
            metadata={"source": "doc.pdf", "page": 1},
        )
        assert chunk.id == "doc1_0"
        assert chunk.source == "doc.pdf"
        assert chunk.chunk_index == 0

    def test_empty_text_raises(self):
        """Test that empty text raises ValidationError."""
        with pytest.raises(ValidationError):
            DocumentChunk(id="1", text="", metadata={})


class TestIndexingRequest:
    """Tests for IndexingRequest model."""

    def test_valid_request(self):
        """Test creating a valid indexing request."""
        req = IndexingRequest(input_dir="inputs", rebuild=True)
        assert req.input_dir == "inputs"
        assert req.rebuild is True

    def test_path_traversal_blocked(self):
        """Test that path traversal is blocked."""
        with pytest.raises(ValidationError):
            IndexingRequest(input_dir="../secret")

    def test_invalid_url_raises(self):
        """Test that invalid URL raises ValidationError."""
        with pytest.raises(ValidationError):
            IndexingRequest(data_url="ftp://example.com")

    def test_valid_url_accepted(self):
        """Test that valid URL is accepted."""
        req = IndexingRequest(data_url="https://example.com/data.zip")
        assert req.data_url == "https://example.com/data.zip"
