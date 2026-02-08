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

    def test_save_without_index_raises(self, repository):
        """Test that saving without building index raises error."""
        with pytest.raises(ValueError, match="No index to save"):
            repository.save()

    def test_load_error_handling(self, repository, temp_paths, sample_chunks, sample_embeddings):
        """Test load handles corrupted files gracefully."""
        index_path, chunks_path = temp_paths

        # Build and save valid index
        repository.build_index(sample_chunks, sample_embeddings)
        repository.save()

        # Corrupt chunks file
        with open(chunks_path, "w") as f:
            f.write("corrupted data")

        # Create new repository and try to load
        new_repo = VectorStoreRepository(
            index_path=index_path,
            chunks_path=chunks_path,
        )
        assert not new_repo.load()
        assert not new_repo.is_loaded

    def test_search_with_metadata_filters(self, repository, sample_chunks, sample_embeddings):
        """Test search with metadata filters."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)

        # Filter by source
        results = repository.search(
            query_embedding,
            k=5,
            metadata_filters={"source": "nba.pdf"}
        )

        # Should only return chunks from nba.pdf
        assert len(results) <= 2
        for chunk, _ in results:
            assert chunk.metadata.get("source") == "nba.pdf"

    def test_search_with_metadata_filters_no_matches(self, repository, sample_chunks, sample_embeddings):
        """Test search with metadata filters that match nothing."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)

        # Filter by non-existent source
        results = repository.search(
            query_embedding,
            k=2,
            metadata_filters={"source": "nonexistent.pdf"}
        )

        # Should fall back to unfiltered search
        assert len(results) <= 2

    def test_search_with_1d_query_embedding(self, repository, sample_chunks, sample_embeddings):
        """Test search handles 1D query embedding correctly."""
        repository.build_index(sample_chunks, sample_embeddings)

        # 1D query embedding
        query_embedding = np.random.rand(64).astype(np.float32)

        results = repository.search(query_embedding, k=2)

        assert len(results) == 2

    def test_search_with_2d_query_embedding(self, repository, sample_chunks, sample_embeddings):
        """Test search handles 2D query embedding correctly."""
        repository.build_index(sample_chunks, sample_embeddings)

        # 2D query embedding (1 x 64)
        query_embedding = np.random.rand(1, 64).astype(np.float32)

        results = repository.search(query_embedding, k=2)

        assert len(results) == 2

    def test_search_k_larger_than_index(self, repository, sample_chunks, sample_embeddings):
        """Test search when k is larger than index size."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)

        # Request more results than available
        results = repository.search(query_embedding, k=100)

        # Should return all available (3)
        assert len(results) == 3

    def test_search_results_sorted_by_score(self, repository, sample_chunks, sample_embeddings):
        """Test that search results are sorted by score descending."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)
        results = repository.search(query_embedding, k=3)

        # Check scores are in descending order
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_with_metadata_filter_and_min_score(self, repository, sample_chunks, sample_embeddings):
        """Test search with both metadata filter and min_score."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)

        results = repository.search(
            query_embedding,
            k=5,
            min_score=0.01,  # Low threshold to get some results
            metadata_filters={"source": "nba.pdf"}
        )

        # Should filter by both metadata and score
        assert len(results) <= 2
        for chunk, score in results:
            assert chunk.metadata.get("source") == "nba.pdf"
            assert score >= 1.0  # min_score * 100

    def test_index_size_property_no_index(self, repository):
        """Test index_size property returns 0 when no index."""
        assert repository.index_size == 0

    def test_is_loaded_property_false_initially(self, repository):
        """Test is_loaded property is False initially."""
        assert repository.is_loaded is False

    def test_is_loaded_after_build(self, repository, sample_chunks, sample_embeddings):
        """Test is_loaded property after building index."""
        repository.build_index(sample_chunks, sample_embeddings)
        assert repository.is_loaded is True

    def test_search_score_conversion_to_percentage(self, repository, sample_chunks, sample_embeddings):
        """Test that search scores are converted to percentages (0-100)."""
        repository.build_index(sample_chunks, sample_embeddings)

        query_embedding = np.random.rand(64).astype(np.float32)
        results = repository.search(query_embedding, k=3)

        # All scores should be in percentage range
        for _, score in results:
            assert 0 <= score <= 100

    def test_load_converts_dict_to_document_chunk(self, repository, temp_paths, sample_chunks, sample_embeddings):
        """Test that load properly converts dict format to DocumentChunk models."""
        index_path, chunks_path = temp_paths

        # Build and save
        repository.build_index(sample_chunks, sample_embeddings)
        repository.save()

        # Load in new repository
        new_repo = VectorStoreRepository(
            index_path=index_path,
            chunks_path=chunks_path,
        )
        new_repo.load()

        # Verify chunks are DocumentChunk instances
        for chunk in new_repo.chunks:
            assert isinstance(chunk, DocumentChunk)
            assert hasattr(chunk, 'id')
            assert hasattr(chunk, 'text')
            assert hasattr(chunk, 'metadata')

    def test_delete_files_when_files_dont_exist(self, repository):
        """Test delete_files handles non-existent files gracefully."""
        # Should not raise error even if files don't exist
        repository.delete_files()
        assert not repository.is_loaded
