"""
FILE: test_evaluate_ragas.py
STATUS: Active
RESPONSIBILITY: Mock-based tests for RAGAS evaluation builder functions and lazy imports
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestLazyImports:
    """Verify that ragas and langchain are NOT imported at module level."""

    def test_ragas_not_in_sys_modules_on_import(self):
        """Importing evaluate_ragas does not eagerly import ragas."""
        # Remove ragas from sys.modules if it was loaded by another test
        ragas_keys = [k for k in sys.modules if k.startswith("ragas")]
        for k in ragas_keys:
            del sys.modules[k]

        # Re-import the module
        if "src.evaluation.runners.evaluate_ragas" in sys.modules:
            del sys.modules["src.evaluation.runners.evaluate_ragas"]

        import src.evaluation.runners.evaluate_ragas  # noqa: F401

        # ragas should not be imported at module level
        # (it's only imported inside _build_evaluator_llm and run_evaluation)
        assert "ragas" not in sys.modules or "ragas.llms" not in sys.modules


class TestBuildEvaluatorLLM:
    """Tests for _build_evaluator_llm with mocked dependencies."""

    @patch("src.evaluation.runners.evaluate_ragas.settings")
    def test_uses_gemini_when_google_api_key_set(self, mock_settings):
        """When google_api_key is set, uses ChatGoogleGenerativeAI."""
        mock_settings.google_api_key = "test-google-key"

        mock_wrapper = MagicMock()
        mock_chat_google = MagicMock()

        with patch.dict(sys.modules, {
            "ragas": MagicMock(),
            "ragas.llms": MagicMock(LangchainLLMWrapper=mock_wrapper),
            "langchain_google_genai": MagicMock(ChatGoogleGenerativeAI=mock_chat_google),
        }):
            from src.evaluation.runners.evaluate_ragas import _build_evaluator_llm
            result = _build_evaluator_llm()

        mock_chat_google.assert_called_once()
        mock_wrapper.assert_called_once()

    @patch("src.evaluation.runners.evaluate_ragas.settings")
    def test_uses_mistral_when_no_google_key(self, mock_settings):
        """When google_api_key is falsy, falls back to ChatMistralAI."""
        mock_settings.google_api_key = None
        mock_settings.chat_model = "mistral-small-latest"
        mock_settings.mistral_api_key = "test-mistral-key"

        mock_wrapper = MagicMock()
        mock_chat_mistral = MagicMock()

        with patch.dict(sys.modules, {
            "ragas": MagicMock(),
            "ragas.llms": MagicMock(LangchainLLMWrapper=mock_wrapper),
            "langchain_mistralai": MagicMock(ChatMistralAI=mock_chat_mistral),
        }):
            from src.evaluation.runners.evaluate_ragas import _build_evaluator_llm
            result = _build_evaluator_llm()

        mock_chat_mistral.assert_called_once()
        mock_wrapper.assert_called_once()


class TestBuildEvaluatorEmbeddings:
    """Tests for _build_evaluator_embeddings with mocked dependencies."""

    @patch("src.evaluation.runners.evaluate_ragas.settings")
    def test_returns_langchain_wrapper(self, mock_settings):
        """_build_evaluator_embeddings wraps MistralAIEmbeddings."""
        mock_settings.embedding_model = "mistral-embed"
        mock_settings.mistral_api_key = "test-key"

        mock_embeddings_wrapper = MagicMock()
        mock_mistral_embeddings = MagicMock()

        with patch.dict(sys.modules, {
            "ragas": MagicMock(),
            "ragas.embeddings": MagicMock(LangchainEmbeddingsWrapper=mock_embeddings_wrapper),
            "langchain_mistralai": MagicMock(MistralAIEmbeddings=mock_mistral_embeddings),
        }):
            from src.evaluation.runners.evaluate_ragas import _build_evaluator_embeddings
            result = _build_evaluator_embeddings()

        mock_mistral_embeddings.assert_called_once_with(
            model="mistral-embed",
            api_key="test-key",
        )
        mock_embeddings_wrapper.assert_called_once()


class TestBuildGenerationClient:
    """Tests for _build_generation_client."""

    @patch("src.evaluation.runners.evaluate_ragas.settings")
    def test_returns_none_without_google_key(self, mock_settings):
        """Without google_api_key, returns None."""
        mock_settings.google_api_key = None

        from src.evaluation.runners.evaluate_ragas import _build_generation_client
        result = _build_generation_client()
        assert result is None

    @patch("src.evaluation.runners.evaluate_ragas.settings")
    def test_returns_client_with_google_key(self, mock_settings):
        """With google_api_key, returns a genai.Client instance (not None)."""
        mock_settings.google_api_key = "test-key"

        mock_genai = MagicMock()
        # Patch 'google.genai' in sys.modules so 'from google import genai'
        # resolves to our mock. Also patch 'google' to expose genai attr.
        mock_google = MagicMock()
        mock_google.genai = mock_genai

        with patch.dict(sys.modules, {
            "google": mock_google,
            "google.genai": mock_genai,
        }):
            from src.evaluation.runners.evaluate_ragas import _build_generation_client
            result = _build_generation_client()

        assert result is not None
        mock_genai.Client.assert_called_once_with(api_key="test-key")
