"""
FILE: test_vector_store.py
STATUS: Active
RESPONSIBILITY: Tests for FAISS vector store repository
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.core.exceptions import IndexNotFoundError, SearchError
from src.models.document import DocumentChunk
from src.repositories.vector_store import VectorStoreRepository


class TestVectorStoreRepository:
    """Tests for VectorStoreRepository."""

    @pytest.fixture
    def temp_paths(self, tmp_path):
        """Create temporary paths for testing."""
        index_path = tmp_path / "test_index.idx"
        chunks_path = tmp_path / "test_chunks.pkl"
        return index_path, chunks_path

    @pytest.fixture
    def repository(self, temp_paths):
        """Create a repository with temp paths."""
        index_path, chunks_path = temp_paths
        return VectorStoreRepository(
            index_path=index_path,
            chunks_path=chunks_path,
        )

    @pytest.fixture
    def sample_chunks(self):
        """Create sample document chunks."""
        return [
            DocumentChunk(
                id="doc0_0",
                text="The Lakers won the championship.",
                metadata={"source": "nba.pdf", "page": 1},
            ),
            DocumentChunk(
                id="doc0_1",
                text="Michael Jordan played for the Bulls.",
                metadata={"source": "nba.pdf", "page": 2},
            ),
            DocumentChunk(
                id="doc1_0",
                text="LeBron James is considered one of the greatest.",
                metadata={"source": "players.pdf", "page": 1},
            ),
        ]

    @pytest.fixture
    def sample_embeddings(self):
        """Create sample embeddings."""
        return np.random.rand(3, 64).astype(np.float32)

    def test_initial_state(self, repository):
        """Test repository initial state."""
        assert not repository.is_loaded
        assert repository.index_size == 0
        assert repository.chunks == []

    def test_build_index(self, repository, sample_chunks, sample_embeddings):
        """Test building index from chunks and embeddings."""
        repository.build_index(sample_chunks, sample_embeddings)

        assert repository.is_loaded
        assert repository.index_size == 3
        assert len(repository.chunks) == 3

    def test_build_index_mismatch_raises(self, repository, sample_chunks):
        """Test that mismatched chunks and embeddings raises error."""
        wrong_embeddings = np.random.rand(5, 64).astype(np.float32)

        with pytest.raises(ValueError, match="Mismatch"):
            repository.build_index(sample_chunks, wrong_embeddings)

    def test_save_and_load(self, repository, sample_chunks, sample_embeddings, temp_paths):
        """Test saving and loading index."""
        index_path, chunks_path = temp_paths

        # Build and save
        repository.build_index(sample_chunks, sample_embeddings)
        repository.save()

        # Verify files exist
        assert index_path.exists()
        assert chunks_path.exists()

        # Create new repository and load
        new_repo = VectorStoreRepository(
            index_path=index_path,
            chunks_path=chunks_path,
        )
        assert new_repo.load()
        assert new_repo.is_loaded
        assert new_repo.index_size == 3

    def test_load_nonexistent_files(self, repository):
        """Test loading when files don't exist."""
        assert not repository.load()
        assert not repository.is_loaded

    def test_search(self, repository, sample_chunks, sample_embeddings):
        """Test searching the index."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)
        results = repository.search(query_embedding, k=2)

        assert len(results) == 2
        assert all(isinstance(chunk, DocumentChunk) for chunk, _ in results)
        assert all(isinstance(score, float) for _, score in results)

    def test_search_not_loaded_raises(self, repository):
        """Test that search on unloaded index raises error."""
        query_embedding = np.random.rand(64).astype(np.float32)

        with pytest.raises(IndexNotFoundError):
            repository.search(query_embedding)

    def test_search_with_min_score(self, repository, sample_chunks, sample_embeddings):
        """Test search with minimum score filter."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)
        # High min_score should return fewer results
        results = repository.search(query_embedding, k=10, min_score=0.99)

        # Results should be filtered
        assert len(results) <= 3

    def test_clear(self, repository, sample_chunks, sample_embeddings):
        """Test clearing the index."""
        repository.build_index(sample_chunks, sample_embeddings)
        assert repository.is_loaded

        repository.clear()

        assert not repository.is_loaded
        assert repository.index_size == 0

    def test_delete_files(self, repository, sample_chunks, sample_embeddings, temp_paths):
        """Test deleting index files."""
        index_path, chunks_path = temp_paths

        repository.build_index(sample_chunks, sample_embeddings)
        repository.save()

        assert index_path.exists()
        assert chunks_path.exists()

        repository.delete_files()

        assert not index_path.exists()
        assert not chunks_path.exists()
        assert not repository.is_loaded

    def test_chunks_returns_copy(self, repository, sample_chunks, sample_embeddings):
        """Test that chunks property returns a copy."""
        repository.build_index(sample_chunks, sample_embeddings)

        chunks1 = repository.chunks
        chunks2 = repository.chunks

        assert chunks1 is not chunks2
        assert chunks1 == chunks2
