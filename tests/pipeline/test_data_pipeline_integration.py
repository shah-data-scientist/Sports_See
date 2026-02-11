"""
FILE: test_data_pipeline_integration.py
STATUS: Active
RESPONSIBILITY: Unit tests for DataPipeline stages with mocked dependencies
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.pipeline.models import (
    ChunkData,
    CleanedDocument,
    LoadStageInput,
    RawDocument,
)


class TestDataPipelineLoad:
    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    @patch("src.pipeline.data_pipeline.load_and_parse_files")
    def test_load_stage_returns_documents(self, mock_load, mock_embed, mock_vs):
        mock_load.return_value = [
            {"page_content": "Some NBA content here", "metadata": {"source": "test.pdf"}},
        ]

        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        input_data = LoadStageInput(input_dir="test_inputs")
        result = pipeline.load(input_data)

        assert result.document_count == 1
        assert len(result.documents) == 1
        assert result.documents[0].page_content == "Some NBA content here"

    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    @patch("src.pipeline.data_pipeline.load_and_parse_files")
    def test_load_stage_skips_empty_docs(self, mock_load, mock_embed, mock_vs):
        mock_load.return_value = [
            {"page_content": "", "metadata": {}},
            {"page_content": "   ", "metadata": {}},
            {"page_content": "Valid content here", "metadata": {}},
        ]

        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        input_data = LoadStageInput(input_dir="test_inputs")
        result = pipeline.load(input_data)

        assert result.document_count == 1


class TestDataPipelineClean:
    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    def test_clean_removes_short_documents(self, mock_embed, mock_vs):
        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        docs = [
            RawDocument(page_content="short", metadata={}),
            RawDocument(page_content="This is a long enough document to pass filtering.", metadata={}),
        ]
        result = pipeline.clean(docs)

        assert len(result.documents) == 1
        assert result.removed_count == 1

    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    def test_clean_computes_total_chars(self, mock_embed, mock_vs):
        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        docs = [
            RawDocument(page_content="A" * 100, metadata={}),
            RawDocument(page_content="B" * 200, metadata={}),
        ]
        result = pipeline.clean(docs)

        assert result.total_chars == 300


class TestDataPipelineAnalyzeContent:
    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    def test_player_stats_detection(self, mock_embed, mock_vs):
        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        text = "LeBron James scored 25 PTS with 10 AST and 8 REB in the game."
        result = pipeline._analyze_chunk_content(text)
        assert result == "player_stats"

    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    def test_discussion_detection(self, mock_embed, mock_vs):
        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        text = "The evolution of modern basketball has been truly remarkable in many ways."
        result = pipeline._analyze_chunk_content(text)
        assert result == "discussion"


class TestDataPipelineFilterLowQuality:
    @patch("src.pipeline.data_pipeline.VectorStoreRepository")
    @patch("src.pipeline.data_pipeline.EmbeddingService")
    def test_filters_high_nan_chunks(self, mock_embed, mock_vs):
        from src.pipeline.data_pipeline import DataPipeline

        pipeline = DataPipeline(
            embedding_service=mock_embed.return_value,
            vector_store=mock_vs.return_value,
        )
        chunks = [
            ChunkData(id="good", text="A" * 200, metadata={}),
            ChunkData(id="bad", text="NaN " * 100, metadata={}),
        ]
        filtered = pipeline._filter_low_quality_chunks(chunks)
        assert len(filtered) == 1
        assert filtered[0].id == "good"
