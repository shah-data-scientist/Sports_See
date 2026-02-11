"""
FILE: test_hybrid_test_cases.py
STATUS: Active
RESPONSIBILITY: Validates hybrid test case data structure and statistics
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import pytest

from src.evaluation.hybrid_test_cases import HYBRID_TEST_CASES, get_hybrid_test_statistics
from src.evaluation.models import EvaluationTestCase, TestCategory


class TestHybridTestCaseStructure:
    """Validate hybrid test case list integrity."""

    def test_list_not_empty(self):
        """HYBRID_TEST_CASES is not empty."""
        assert len(HYBRID_TEST_CASES) > 0

    def test_all_are_evaluation_test_case(self):
        """Every item is an EvaluationTestCase instance."""
        for tc in HYBRID_TEST_CASES:
            assert isinstance(tc, EvaluationTestCase), f"Not EvaluationTestCase: {tc}"

    def test_all_have_question(self):
        """Every test case has a non-empty question."""
        for tc in HYBRID_TEST_CASES:
            assert tc.question and len(tc.question.strip()) > 0

    def test_all_have_ground_truth(self):
        """Every test case has a non-empty ground_truth."""
        for tc in HYBRID_TEST_CASES:
            assert tc.ground_truth and len(tc.ground_truth.strip()) > 0

    def test_no_duplicate_questions(self):
        """No two hybrid test cases share the same question."""
        questions = [tc.question for tc in HYBRID_TEST_CASES]
        assert len(questions) == len(set(questions)), "Duplicate questions found"


class TestHybridTestCaseCategories:
    """Validate category distribution for hybrid test cases."""

    def test_categories_are_valid(self):
        """All categories are valid TestCategory values."""
        valid_categories = set(TestCategory)
        for tc in HYBRID_TEST_CASES:
            assert tc.category in valid_categories, (
                f"Invalid category {tc.category} for: {tc.question}"
            )

    def test_has_complex_cases(self):
        """Suite includes COMPLEX category cases."""
        complex_cases = [tc for tc in HYBRID_TEST_CASES if tc.category == TestCategory.COMPLEX]
        assert len(complex_cases) > 0

    def test_has_noisy_cases(self):
        """Suite includes NOISY category cases."""
        noisy_cases = [tc for tc in HYBRID_TEST_CASES if tc.category == TestCategory.NOISY]
        assert len(noisy_cases) > 0


class TestGetHybridTestStatistics:
    """Tests for get_hybrid_test_statistics function."""

    def test_returns_dict(self):
        """Function returns a dictionary."""
        stats = get_hybrid_test_statistics()
        assert isinstance(stats, dict)

    def test_has_required_keys(self):
        """Result has total, by_category, and distribution keys."""
        stats = get_hybrid_test_statistics()
        assert "total" in stats
        assert "by_category" in stats
        assert "distribution" in stats

    def test_total_matches_list_length(self):
        """Total count matches HYBRID_TEST_CASES length."""
        stats = get_hybrid_test_statistics()
        assert stats["total"] == len(HYBRID_TEST_CASES)

    def test_distribution_sums_to_100(self):
        """Distribution percentages sum close to 100."""
        stats = get_hybrid_test_statistics()
        total_pct = sum(stats["distribution"].values())
        assert abs(total_pct - 100.0) < 1.0
