"""
FILE: test_evaluation.py
STATUS: Active
RESPONSIBILITY: Tests for RAGAS evaluation module with mocked API calls
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.evaluation.models import (
    CategoryResult,
    EvaluationReport,
    EvaluationSample,
    EvaluationTestCase,
    MetricScores,
    TestCategory,
)
from src.evaluation.test_cases import EVALUATION_TEST_CASES


class TestEvaluationModels:
    def test_test_category_enum(self):
        assert TestCategory.SIMPLE.value == "simple"
        assert TestCategory.COMPLEX.value == "complex"
        assert TestCategory.NOISY.value == "noisy"
        assert TestCategory.CONVERSATIONAL.value == "conversational"

    def test_evaluation_test_case_valid(self):
        tc = EvaluationTestCase(
            question="Who won the championship?",
            ground_truth="The Denver Nuggets won in 2023.",
            category=TestCategory.SIMPLE,
        )
        assert tc.category == TestCategory.SIMPLE

    def test_evaluation_test_case_empty_question_raises(self):
        with pytest.raises(ValueError):
            EvaluationTestCase(
                question="",
                ground_truth="Answer",
                category=TestCategory.SIMPLE,
            )

    def test_evaluation_sample_valid(self):
        sample = EvaluationSample(
            user_input="Who won?",
            response="The Nuggets won.",
            retrieved_contexts=["Context 1", "Context 2"],
            reference="The Nuggets won in 2023.",
            category=TestCategory.SIMPLE,
        )
        assert len(sample.retrieved_contexts) == 2

    def test_metric_scores_defaults(self):
        scores = MetricScores()
        assert scores.faithfulness is None
        assert scores.answer_relevancy is None

    def test_metric_scores_with_values(self):
        scores = MetricScores(
            faithfulness=0.85,
            answer_relevancy=0.90,
            context_precision=0.75,
            context_recall=0.80,
        )
        assert scores.faithfulness == 0.85

    def test_category_result(self):
        cr = CategoryResult(
            category=TestCategory.SIMPLE,
            count=4,
            avg_faithfulness=0.9,
        )
        assert cr.count == 4

    def test_evaluation_report(self):
        report = EvaluationReport(
            overall_scores=MetricScores(faithfulness=0.85),
            category_results=[
                CategoryResult(category=TestCategory.SIMPLE, count=4),
            ],
            sample_count=4,
            model_used="mistral-small-latest",
        )
        assert report.sample_count == 4


class TestTestCases:
    def test_test_cases_not_empty(self):
        assert len(EVALUATION_TEST_CASES) > 0

    def test_all_categories_represented(self):
        categories = {tc.category for tc in EVALUATION_TEST_CASES}
        assert TestCategory.SIMPLE in categories
        assert TestCategory.COMPLEX in categories
        assert TestCategory.NOISY in categories
        assert TestCategory.CONVERSATIONAL in categories

    def test_total_cases_at_least_40(self):
        assert len(EVALUATION_TEST_CASES) >= 40

    def test_simple_cases_exist(self):
        simple = [tc for tc in EVALUATION_TEST_CASES if tc.category == TestCategory.SIMPLE]
        assert len(simple) >= 10

    def test_complex_cases_exist(self):
        complex_cases = [tc for tc in EVALUATION_TEST_CASES if tc.category == TestCategory.COMPLEX]
        assert len(complex_cases) >= 10

    def test_noisy_cases_exist(self):
        noisy = [tc for tc in EVALUATION_TEST_CASES if tc.category == TestCategory.NOISY]
        assert len(noisy) >= 8

    def test_conversational_cases_exist(self):
        conv = [tc for tc in EVALUATION_TEST_CASES if tc.category == TestCategory.CONVERSATIONAL]
        assert len(conv) >= 10

    def test_statistics_function(self):
        from src.evaluation.test_cases import get_test_case_statistics

        stats = get_test_case_statistics()
        assert stats["total"] == len(EVALUATION_TEST_CASES)
        assert "by_category" in stats
        assert "distribution" in stats
        assert sum(stats["by_category"].values()) == stats["total"]


class TestGenerateSamples:
    @patch("src.evaluation.evaluate_ragas._load_checkpoint")
    @patch("src.evaluation.evaluate_ragas._save_checkpoint")
    def test_generate_samples(self, mock_save_checkpoint, mock_load_checkpoint):
        from src.evaluation.evaluate_ragas import generate_samples

        # Mock checkpoint to return empty list (no cached samples)
        mock_load_checkpoint.return_value = []

        mock_service = MagicMock()
        mock_search_result = MagicMock()
        mock_search_result.text = "Some NBA context text"
        mock_search_result.source = "nba.pdf"
        mock_search_result.score = 85.0
        mock_service.search.return_value = [mock_search_result]
        mock_service.generate_response.return_value = "Generated answer"

        samples = generate_samples(mock_service)

        assert len(samples) == len(EVALUATION_TEST_CASES)
        assert all(isinstance(s, EvaluationSample) for s in samples)
        assert mock_service.search.call_count == len(EVALUATION_TEST_CASES)
        assert mock_service.generate_response.call_count == len(EVALUATION_TEST_CASES)


class TestBuildReport:
    def test_build_report(self):
        from src.evaluation.evaluate_ragas import _build_report

        mock_result = MagicMock()
        mock_result.to_pandas.return_value = pd.DataFrame(
            {
                "faithfulness": [0.9, 0.8, 0.7, 0.85],
                "answer_relevancy": [0.85, 0.75, 0.65, 0.80],
                "llm_context_precision_without_reference": [0.8, 0.7, 0.6, 0.75],
                "context_recall": [0.95, 0.85, 0.75, 0.90],
            }
        )

        samples = [
            EvaluationSample(
                user_input="Q1",
                response="A1",
                retrieved_contexts=["C1"],
                reference="R1",
                category=TestCategory.SIMPLE,
            ),
            EvaluationSample(
                user_input="Q2",
                response="A2",
                retrieved_contexts=["C2"],
                reference="R2",
                category=TestCategory.COMPLEX,
            ),
            EvaluationSample(
                user_input="Q3",
                response="A3",
                retrieved_contexts=["C3"],
                reference="R3",
                category=TestCategory.NOISY,
            ),
            EvaluationSample(
                user_input="Q4",
                response="A4",
                retrieved_contexts=["C4"],
                reference="R4",
                category=TestCategory.CONVERSATIONAL,
            ),
        ]

        report = _build_report(mock_result, samples)

        assert isinstance(report, EvaluationReport)
        assert report.sample_count == 4
        assert report.overall_scores.faithfulness is not None
        assert len(report.category_results) == 4


class TestPrintComparisonTable:
    def test_print_table_runs(self, capsys):
        from src.evaluation.evaluate_ragas import print_comparison_table

        report = EvaluationReport(
            overall_scores=MetricScores(
                faithfulness=0.85,
                answer_relevancy=0.90,
                context_precision=0.75,
                context_recall=0.80,
            ),
            category_results=[
                CategoryResult(
                    category=TestCategory.SIMPLE,
                    count=4,
                    avg_faithfulness=0.9,
                    avg_answer_relevancy=0.92,
                    avg_context_precision=0.8,
                    avg_context_recall=0.85,
                ),
                CategoryResult(
                    category=TestCategory.COMPLEX,
                    count=3,
                    avg_faithfulness=0.75,
                ),
            ],
            sample_count=7,
            model_used="mistral-small-latest",
        )

        print_comparison_table(report)

        captured = capsys.readouterr()
        assert "RAGAS EVALUATION REPORT" in captured.out
        assert "simple" in captured.out
        assert "complex" in captured.out
        assert "0.850" in captured.out
