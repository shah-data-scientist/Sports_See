"""
FILE: test_query_classifier.py
STATUS: Active
RESPONSIBILITY: Unit tests for query classification patterns and routing logic
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import pytest

from src.services.query_classifier import QueryClassifier, QueryType


@pytest.fixture
def classifier():
    return QueryClassifier()


class TestStatisticalClassification:
    def test_top_n_query(self, classifier):
        result = classifier.classify("Who are the top 5 scorers?")
        assert result == QueryType.STATISTICAL

    def test_average_query(self, classifier):
        result = classifier.classify("What is the average points per game?")
        assert result == QueryType.STATISTICAL

    def test_how_many_query(self, classifier):
        result = classifier.classify("How many points did LeBron score?")
        assert result == QueryType.STATISTICAL

    def test_compare_stats(self, classifier):
        result = classifier.classify("Compare stats of Curry and LeBron")
        assert result == QueryType.STATISTICAL

    def test_stat_abbreviations(self, classifier):
        result = classifier.classify("Show me the pts leaders this season")
        assert result == QueryType.STATISTICAL


class TestContextualClassification:
    def test_why_question(self, classifier):
        result = classifier.classify("Why is LeBron considered the GOAT?")
        assert result == QueryType.CONTEXTUAL

    def test_opinion_question(self, classifier):
        result = classifier.classify("What do fans think about the trade?")
        assert result == QueryType.CONTEXTUAL

    def test_strategy_question(self, classifier):
        result = classifier.classify("Explain the triangle offense strategy")
        assert result == QueryType.CONTEXTUAL

    def test_history_question(self, classifier):
        result = classifier.classify("How has the history of basketball evolved?")
        assert result == QueryType.CONTEXTUAL


class TestHybridClassification:
    def test_stats_and_explanation(self, classifier):
        result = classifier.classify(
            "Who has the most points and explain why they are so effective?"
        )
        assert result == QueryType.HYBRID

    def test_compare_and_explain(self, classifier):
        result = classifier.classify(
            "Compare Jokic and Embiid's stats and explain who's better"
        )
        assert result == QueryType.HYBRID

    def test_top_with_impact(self, classifier):
        result = classifier.classify(
            "Who are the top scorers and what is their impact on their teams?"
        )
        assert result == QueryType.HYBRID


class TestDefaultClassification:
    def test_ambiguous_defaults_to_contextual(self, classifier):
        result = classifier.classify("Tell me something interesting about basketball")
        assert result == QueryType.CONTEXTUAL

    def test_empty_like_query_defaults_to_contextual(self, classifier):
        result = classifier.classify("hello")
        assert result == QueryType.CONTEXTUAL


class TestRegexCompilation:
    def test_patterns_compiled_on_init(self, classifier):
        assert len(classifier.statistical_regex) == len(QueryClassifier.STATISTICAL_PATTERNS)
        assert len(classifier.contextual_regex) == len(QueryClassifier.CONTEXTUAL_PATTERNS)
        assert len(classifier.hybrid_regex) == len(QueryClassifier.HYBRID_PATTERNS)
