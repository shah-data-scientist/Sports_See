"""
FILE: test_pipeline.py
STATUS: Active
RESPONSIBILITY: Tests for data preparation pipeline logic with mocked services
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.pipeline.data_pipeline import DataPipeline
from src.pipeline.models import (
    ChunkData,
    CleanedDocument,
    LoadStageInput,
    QualityCheckResult,
    RawDocument,
)


@pytest.fixture
def mock_embedding_service():
    service = MagicMock()
    service.embed_batch.return_value = np.random.rand(5, 64).astype(np.float32)
    return service


@pytest.fixture
def mock_vector_store():
    store = MagicMock()
    store.index_size = 5
    store.build_index.return_value = None
    store.save.return_value = None
    return store


@pytest.fixture
def pipeline(mock_embedding_service, mock_vector_store):
    return DataPipeline(
        embedding_service=mock_embedding_service,
        vector_store=mock_vector_store,
        enable_quality_check=False,
    )


class TestDataPipelineLoad:
    def test_load_from_directory(self, pipeline):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("NBA statistics content for testing purposes.")

            result = pipeline.load(LoadStageInput(input_dir=temp_dir))

            assert result.document_count >= 1
            assert len(result.documents) >= 1
            assert result.documents[0].page_content

    def test_load_empty_directory(self, pipeline):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = pipeline.load(LoadStageInput(input_dir=temp_dir))
            assert result.document_count == 0


class TestDataPipelineClean:
    def test_clean_removes_short_docs(self, pipeline):
        docs = [
            RawDocument(page_content="Short"),
            RawDocument(page_content="This is a longer document with enough content."),
        ]
        result = pipeline.clean(docs)
        assert result.removed_count == 1
        assert len(result.documents) == 1

    def test_clean_strips_whitespace(self, pipeline):
        docs = [RawDocument(page_content="  Padded content with spaces  ")]
        result = pipeline.clean(docs)
        assert result.documents[0].page_content == "Padded content with spaces"

    def test_clean_all_valid(self, pipeline):
        docs = [
            RawDocument(page_content="First valid document content."),
            RawDocument(page_content="Second valid document content."),
        ]
        result = pipeline.clean(docs)
        assert result.removed_count == 0
        assert len(result.documents) == 2
        assert result.total_chars > 0


class TestDataPipelineChunk:
    def test_chunk_splits_text(self, pipeline):
        docs = [
            CleanedDocument(
                page_content="A " * 1000,
                char_count=2000,
            ),
        ]
        result = pipeline.chunk(docs, chunk_size=500, chunk_overlap=50)
        assert result.chunk_count > 1
        assert all(isinstance(c, ChunkData) for c in result.chunks)

    def test_chunk_preserves_metadata(self, pipeline):
        docs = [
            CleanedDocument(
                page_content="Content " * 200,
                metadata={"source": "test.pdf"},
                char_count=1600,
            ),
        ]
        result = pipeline.chunk(docs, chunk_size=500, chunk_overlap=50)
        assert result.chunks[0].metadata.get("source") == "test.pdf"
        assert "chunk_id_in_doc" in result.chunks[0].metadata

    def test_chunk_tags_data_type_player_stats(self, pipeline):
        """Test that chunks from player stats files are tagged with data_type='player_stats'."""
        docs = [
            CleanedDocument(
                page_content="LeBron James 28.5 PTS 7.3 REB 8.1 AST 50.2 FG%. " * 50,
                metadata={"source": "player_stats_2023.csv"},
                char_count=2050,
            ),
        ]
        result = pipeline.chunk(docs, chunk_size=500, chunk_overlap=50)
        assert result.chunk_count > 0
        assert result.chunks[0].metadata.get("data_type") == "player_stats"

    def test_chunk_tags_data_type_team_stats(self, pipeline):
        """Test that chunks from team stats files are tagged with data_type='team_stats'."""
        docs = [
            CleanedDocument(
                page_content="Lakers won 112-108 against the Celtics. " * 50,
                metadata={"source": "team_performance.xlsx"},
                char_count=2000,
            ),
        ]
        result = pipeline.chunk(docs, chunk_size=500, chunk_overlap=50)
        assert result.chunk_count > 0
        assert result.chunks[0].metadata.get("data_type") == "team_stats"

    def test_chunk_tags_data_type_game_data(self, pipeline):
        """Test that chunks from schedule/game files are tagged with data_type='game_data'."""
        docs = [
            CleanedDocument(
                page_content="Game scheduled for 7:30 PM at Staples Center. " * 50,
                metadata={"source": "schedule_2023.pdf"},
                char_count=2350,
            ),
        ]
        result = pipeline.chunk(docs, chunk_size=500, chunk_overlap=50)
        assert result.chunk_count > 0
        assert result.chunks[0].metadata.get("data_type") == "game_data"

    def test_chunk_tags_data_type_unknown(self, pipeline):
        """Test that chunks from unrecognized files are tagged with data_type='discussion'."""
        docs = [
            CleanedDocument(
                page_content="Some random content that doesn't match any pattern. " * 50,
                metadata={"source": "random_document.txt"},
                char_count=2650,
            ),
        ]
        result = pipeline.chunk(docs, chunk_size=500, chunk_overlap=50)
        assert result.chunk_count > 0
        assert result.chunks[0].metadata.get("data_type") == "discussion"

    def test_chunk_empty_input(self, pipeline):
        result = pipeline.chunk([])
        assert result.chunk_count == 0


class TestDataPipelineQualityCheck:
    @patch("src.pipeline.quality_agent.check_chunk_quality")
    def test_quality_check_samples_chunks(
        self, mock_check, mock_embedding_service, mock_vector_store
    ):
        pipeline = DataPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
            enable_quality_check=True,
            quality_sample_size=2,
        )

        mock_check.return_value = QualityCheckResult(
            chunk_id="0_0",
            is_coherent=True,
            quality_score=0.9,
        )

        chunks = [ChunkData(id=f"0_{i}", text=f"Chunk text {i}") for i in range(5)]
        results = pipeline.quality_check(chunks)

        assert len(results) == 2
        assert mock_check.call_count == 2


class TestDataPipelineEmbed:
    def test_embed_returns_metadata(self, pipeline, mock_embedding_service):
        mock_embedding_service.embed_batch.return_value = np.random.rand(3, 64).astype(np.float32)
        output, embeddings = pipeline.embed(["text1", "text2", "text3"])

        assert output.embedding_count == 3
        assert output.embedding_dimension == 64
        assert embeddings.shape == (3, 64)


class TestDataPipelineIndex:
    def test_index_builds_and_saves(self, pipeline, mock_vector_store):
        mock_vector_store.index_size = 3

        chunks = [ChunkData(id=f"0_{i}", text=f"Chunk {i}") for i in range(3)]
        embeddings = np.random.rand(3, 64).astype(np.float32)

        result = pipeline.index(chunks, embeddings)

        assert result.index_size == 3
        mock_vector_store.build_index.assert_called_once()
        mock_vector_store.save.assert_called_once()


class TestDataPipelineRun:
    def test_run_end_to_end(self, mock_embedding_service, mock_vector_store):
        mock_embedding_service.embed_batch.return_value = np.random.rand(5, 64).astype(np.float32)
        mock_vector_store.index_size = 5

        pipeline = DataPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("NBA content " * 200)

            result = pipeline.run(input_dir=temp_dir)

            assert result.documents_loaded >= 1
            assert result.chunks_created >= 1
            assert result.embeddings_generated >= 1
            assert result.processing_time_ms > 0

    def test_run_empty_directory(self, mock_embedding_service, mock_vector_store):
        pipeline = DataPipeline(
            embedding_service=mock_embedding_service,
            vector_store=mock_vector_store,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            result = pipeline.run(input_dir=temp_dir)

            assert result.documents_loaded == 0
            assert "No documents found" in result.errors
