"""
FILE: vector_store.py
STATUS: Active
RESPONSIBILITY: FAISS vector store data access layer for index CRUD operations
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import logging
import pickle
from pathlib import Path
from typing import Protocol

import faiss
import numpy as np

from src.core.config import settings
from src.core.exceptions import IndexNotFoundError, SearchError
from src.core.observability import logfire
from src.models.document import DocumentChunk

logger = logging.getLogger(__name__)


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers (dependency injection)."""

    def embed(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        ...


class VectorStoreRepository:
    """Repository for vector store operations.

    Handles FAISS index and document chunk storage with proper
    separation from business logic.

    Attributes:
        index: FAISS index for similarity search
        chunks: List of document chunks with metadata
    """

    def __init__(
        self,
        index_path: Path | None = None,
        chunks_path: Path | None = None,
    ):
        """Initialize repository.

        Args:
            index_path: Path to FAISS index file (default from settings)
            chunks_path: Path to chunks pickle file (default from settings)
        """
        self._index_path = index_path or settings.faiss_index_path
        self._chunks_path = chunks_path or settings.document_chunks_path
        self._index: faiss.Index | None = None
        self._chunks: list[DocumentChunk] = []
        self._is_loaded = False

    @property
    def is_loaded(self) -> bool:
        """Check if index is loaded."""
        return self._is_loaded and self._index is not None

    @property
    def index_size(self) -> int:
        """Get number of vectors in index."""
        if self._index is None:
            return 0
        return self._index.ntotal

    @property
    def chunks(self) -> list[DocumentChunk]:
        """Get document chunks (read-only copy)."""
        return self._chunks.copy()

    def load(self) -> bool:
        """Load index and chunks from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self._index_path.exists() or not self._chunks_path.exists():
            logger.warning(
                "Index files not found: %s, %s",
                self._index_path,
                self._chunks_path,
            )
            return False

        try:
            logger.info("Loading FAISS index from %s", self._index_path)
            self._index = faiss.read_index(str(self._index_path))

            logger.info("Loading chunks from %s", self._chunks_path)
            with open(self._chunks_path, "rb") as f:
                raw_chunks = pickle.load(f)

            # Convert to DocumentChunk models
            self._chunks = [
                DocumentChunk(
                    id=chunk.get("id", f"chunk_{i}"),
                    text=chunk.get("text", ""),
                    metadata=chunk.get("metadata", {}),
                )
                for i, chunk in enumerate(raw_chunks)
            ]

            self._is_loaded = True
            logger.info(
                "Loaded index with %d vectors and %d chunks",
                self._index.ntotal,
                len(self._chunks),
            )
            return True

        except Exception as e:
            logger.error("Failed to load index: %s", e)
            self._index = None
            self._chunks = []
            self._is_loaded = False
            return False

    def save(self) -> None:
        """Save index and chunks to disk.

        Raises:
            ValueError: If no index to save
        """
        if self._index is None:
            raise ValueError("No index to save")

        # Ensure directory exists
        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        self._chunks_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Saving FAISS index to %s", self._index_path)
        faiss.write_index(self._index, str(self._index_path))

        logger.info("Saving %d chunks to %s", len(self._chunks), self._chunks_path)
        # Convert back to dict format for compatibility
        raw_chunks = [{"id": c.id, "text": c.text, "metadata": c.metadata} for c in self._chunks]
        with open(self._chunks_path, "wb") as f:
            pickle.dump(raw_chunks, f)

        logger.info("Index and chunks saved successfully")

    def build_index(
        self,
        chunks: list[DocumentChunk],
        embeddings: np.ndarray,
    ) -> None:
        """Build FAISS index from chunks and embeddings.

        Args:
            chunks: Document chunks to index
            embeddings: Embeddings array (n_chunks x embedding_dim)

        Raises:
            ValueError: If chunks and embeddings don't match
        """
        if len(chunks) != embeddings.shape[0]:
            raise ValueError(f"Mismatch: {len(chunks)} chunks but {embeddings.shape[0]} embeddings")

        # Normalize for cosine similarity
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        # Create index
        dimension = embeddings.shape[1]
        logger.info("Creating FAISS IndexFlatIP with dimension %d", dimension)
        self._index = faiss.IndexFlatIP(dimension)
        self._index.add(embeddings)

        self._chunks = chunks
        self._is_loaded = True

        logger.info("Built index with %d vectors", self._index.ntotal)

    @logfire.instrument("VectorStoreRepository.search {k=}")
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        min_score: float | None = None,
    ) -> list[tuple[DocumentChunk, float]]:
        """Search for similar documents.

        Args:
            query_embedding: Query embedding vector (1 x dim)
            k: Number of results to return
            min_score: Minimum similarity score (0-1)

        Returns:
            List of (chunk, score) tuples sorted by score descending

        Raises:
            IndexNotFoundError: If index not loaded
            SearchError: If search fails
        """
        if not self.is_loaded:
            raise IndexNotFoundError()

        try:
            # Normalize query
            query_embedding = query_embedding.astype("float32")
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)

            # Search more if filtering by min_score
            search_k = k * 3 if min_score is not None else k
            scores, indices = self._index.search(query_embedding, search_k)

            results: list[tuple[DocumentChunk, float]] = []
            for i, idx in enumerate(indices[0]):
                if idx < 0 or idx >= len(self._chunks):
                    continue

                # Convert score to percentage (0-100)
                score_percent = float(scores[0][i]) * 100

                # Apply minimum score filter
                if min_score is not None and score_percent < (min_score * 100):
                    continue

                results.append((self._chunks[idx], score_percent))

            # Sort by score descending and limit to k
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:k]

        except Exception as e:
            logger.error("Search failed: %s", e)
            raise SearchError(f"Search failed: {e}") from e

    def clear(self) -> None:
        """Clear index and chunks from memory."""
        self._index = None
        self._chunks = []
        self._is_loaded = False
        logger.info("Index cleared from memory")

    def delete_files(self) -> None:
        """Delete index files from disk."""
        if self._index_path.exists():
            self._index_path.unlink()
            logger.info("Deleted %s", self._index_path)

        if self._chunks_path.exists():
            self._chunks_path.unlink()
            logger.info("Deleted %s", self._chunks_path)

        self.clear()
