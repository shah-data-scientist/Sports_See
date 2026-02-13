"""
FILE: test_run_classification_check.py
STATUS: Active
RESPONSIBILITY: Unit tests for ClassificationChecker with mocked QueryClassifier
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu
"""

import pytest
from unittest.mock import MagicMock, patch
from src.evaluation.run_classification_check import (
    CLASSIFIER_TO_EVAL,
    EVAL_TO_CLASSIFIER,
    SQL_ACCEPTABLE,
    VECTOR_ACCEPTABLE,
    ClassificationChecker,
)
from src.services.query_classifier import QueryType


class TestMappingConstants:
    """Tests for mapping constants between classifier and evaluation enums."""

    def test_classifier_to_eval_mapping(self):
        """Test CLASSIFIER_TO_EVAL mapping correctness."""
        assert CLASSIFIER_TO_EVAL["statistical"] == "sql_only"
        assert CLASSIFIER_TO_EVAL["contextual"] == "contextual_only"
        assert CLASSIFIER_TO_EVAL["hybrid"] == "hybrid"
        assert len(CLASSIFIER_TO_EVAL) == 3

    def test_eval_to_classifier_mapping(self):
        """Test EVAL_TO_CLASSIFIER reverse mapping correctness."""
        assert EVAL_TO_CLASSIFIER["sql_only"] == "statistical"
        assert EVAL_TO_CLASSIFIER["contextual_only"] == "contextual"
        assert EVAL_TO_CLASSIFIER["hybrid"] == "hybrid"
        assert len(EVAL_TO_CLASSIFIER) == 3

    def test_mapping_bidirectional_consistency(self):
        """Test that CLASSIFIER_TO_EVAL and EVAL_TO_CLASSIFIER are bidirectional inverses."""
        for classifier_val, eval_val in CLASSIFIER_TO_EVAL.items():
            assert EVAL_TO_CLASSIFIER[eval_val] == classifier_val

    def test_acceptable_sets(self):
        """Test SQL_ACCEPTABLE and VECTOR_ACCEPTABLE constant values."""
        assert SQL_ACCEPTABLE == {"statistical"}
        assert VECTOR_ACCEPTABLE == {"contextual"}


class TestClassificationChecker:
    """Tests for ClassificationChecker class."""

    @patch("src.evaluation.run_classification_check.QueryClassifier")
    def test_initialization(self, mock_classifier_class):
        """Test ClassificationChecker instantiation creates QueryClassifier."""
        # Arrange
        mock_instance = MagicMock()
        mock_classifier_class.return_value = mock_instance

        # Act
        checker = ClassificationChecker()

        # Assert
        mock_classifier_class.assert_called_once()
        assert checker.classifier == mock_instance
        assert checker.results["sql"]["total"] == 0
        assert checker.results["sql"]["correct"] == 0
        assert checker.results["sql"]["misclassified"] == []
        assert checker.results["vector"]["total"] == 0
        assert checker.results["hybrid"]["total"] == 0

    @patch("src.evaluation.run_classification_check.QueryClassifier")
    def test_analyze_misclassification_patterns_empty(self, mock_classifier_class):
        """Test analyze_misclassification_patterns with no misclassifications."""
        # Arrange
        mock_instance = MagicMock()
        mock_classifier_class.return_value = mock_instance
        checker = ClassificationChecker()

        # Act
        patterns = checker.analyze_misclassification_patterns()

        # Assert
        assert patterns == {}

    @patch("src.evaluation.run_classification_check.QueryClassifier")
    def test_generate_summary_structure(self, mock_classifier_class):
        """Test generate_summary returns correct structure."""
        # Arrange
        mock_instance = MagicMock()
        mock_classifier_class.return_value = mock_instance
        checker = ClassificationChecker()

        # Manually set some results for testing
        checker.results["sql"]["total"] = 10
        checker.results["sql"]["correct"] = 8
        checker.results["vector"]["total"] = 15
        checker.results["vector"]["correct"] = 12
        checker.results["hybrid"]["total"] = 5
        checker.results["hybrid"]["correct"] = 5

        # Act
        summary = checker.generate_summary()

        # Assert
        assert "timestamp" in summary
        assert "overall" in summary
        assert "per_dataset" in summary
        assert summary["overall"]["total_queries"] == 30
        assert summary["overall"]["correct"] == 25
        assert summary["overall"]["misclassified"] == 5
        assert summary["overall"]["accuracy_percent"] == 83.33
        assert "sql" in summary["per_dataset"]
        assert "vector" in summary["per_dataset"]
        assert "hybrid" in summary["per_dataset"]
