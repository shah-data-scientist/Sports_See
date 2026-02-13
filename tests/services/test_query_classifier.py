"""
FILE: test_query_classifier.py
STATUS: Active
RESPONSIBILITY: Unit tests for query classification patterns and routing logic
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu
"""

import pytest

from src.services.query_classifier import ClassificationResult, QueryClassifier, QueryType


@pytest.fixture
def classifier():
    return QueryClassifier()


class TestStatisticalClassification:
    def test_top_n_query(self, classifier):
        result = classifier.classify("Who are the top 5 scorers?")
        assert result.query_type == QueryType.STATISTICAL

    def test_average_query(self, classifier):
        result = classifier.classify("What is the average points per game?")
        assert result.query_type == QueryType.STATISTICAL

    def test_how_many_query(self, classifier):
        result = classifier.classify("How many points did LeBron score?")
        assert result.query_type == QueryType.STATISTICAL

    def test_compare_stats(self, classifier):
        result = classifier.classify("Compare stats of Curry and LeBron")
        assert result.query_type == QueryType.STATISTICAL

    def test_stat_abbreviations(self, classifier):
        result = classifier.classify("Show me the pts leaders this season")
        assert result.query_type == QueryType.STATISTICAL


class TestContextualClassification:
    def test_why_question(self, classifier):
        result = classifier.classify("Why is LeBron considered the GOAT?")
        assert result.query_type == QueryType.CONTEXTUAL

    def test_opinion_question(self, classifier):
        result = classifier.classify("What do fans think about the trade?")
        assert result.query_type == QueryType.CONTEXTUAL

    def test_strategy_question(self, classifier):
        result = classifier.classify("Explain the triangle offense strategy")
        assert result.query_type == QueryType.CONTEXTUAL

    def test_history_question(self, classifier):
        result = classifier.classify("How has the history of basketball evolved?")
        assert result.query_type == QueryType.CONTEXTUAL


class TestHybridClassification:
    def test_stats_and_explanation(self, classifier):
        result = classifier.classify(
            "Who has the most points and explain why they are so effective?"
        )
        assert result.query_type == QueryType.HYBRID

    def test_compare_and_explain(self, classifier):
        result = classifier.classify(
            "Compare Jokic and Embiid's stats and explain who's better"
        )
        assert result.query_type == QueryType.HYBRID

    def test_top_with_impact(self, classifier):
        result = classifier.classify(
            "Who are the top scorers and what is their impact on their teams?"
        )
        assert result.query_type == QueryType.HYBRID


class TestDefaultClassification:
    def test_ambiguous_defaults_to_contextual(self, classifier):
        result = classifier.classify("Tell me something interesting about basketball")
        assert result.query_type == QueryType.CONTEXTUAL

    def test_empty_like_query_defaults_to_contextual(self, classifier):
        result = classifier.classify("hello")
        assert result.query_type == QueryType.CONTEXTUAL


class TestGreetingDetection:
    """Tests for QueryClassifier._is_greeting() static method (Phase 15)."""

    def test_simple_greetings(self):
        assert QueryClassifier._is_greeting("hi") is True
        assert QueryClassifier._is_greeting("hello") is True
        assert QueryClassifier._is_greeting("hey") is True
        assert QueryClassifier._is_greeting("thanks") is True
        assert QueryClassifier._is_greeting("goodbye") is True
        assert QueryClassifier._is_greeting("bye") is True

    def test_greeting_with_context(self):
        assert QueryClassifier._is_greeting("hi there") is True
        assert QueryClassifier._is_greeting("hello everyone") is True

    def test_time_greetings(self):
        assert QueryClassifier._is_greeting("good morning") is True
        assert QueryClassifier._is_greeting("good evening") is True
        assert QueryClassifier._is_greeting("good night") is True

    def test_conversational_greetings(self):
        assert QueryClassifier._is_greeting("how are you") is True
        assert QueryClassifier._is_greeting("what's up") is True
        assert QueryClassifier._is_greeting("thank you") is True

    def test_not_greeting_with_question(self):
        assert QueryClassifier._is_greeting("hi, who is the top scorer?") is False
        assert QueryClassifier._is_greeting("hello, show me NBA stats") is False

    def test_not_greeting_basketball_query(self):
        assert QueryClassifier._is_greeting("How many teams are in the NBA?") is False
        assert QueryClassifier._is_greeting("Who scored the most points?") is False

    def test_not_greeting_empty_string(self):
        assert QueryClassifier._is_greeting("") is False

    def test_greeting_case_insensitive(self):
        assert QueryClassifier._is_greeting("HI") is True
        assert QueryClassifier._is_greeting("Hello") is True
        assert QueryClassifier._is_greeting("GOOD MORNING") is True


class TestBiographicalDetection:
    """Tests for QueryClassifier._is_biographical() static method (Phase 16-17)."""

    def test_who_is_player(self):
        assert QueryClassifier._is_biographical("Who is LeBron?") is True
        assert QueryClassifier._is_biographical("Who is Michael Jordan?") is True

    def test_tell_me_about(self):
        assert QueryClassifier._is_biographical("Tell me about Kobe") is True
        assert QueryClassifier._is_biographical("Tell me about the Lakers") is True

    def test_not_biographical_stats(self):
        assert QueryClassifier._is_biographical("What are the top 5 scorers?") is False

    def test_not_biographical_generic(self):
        assert QueryClassifier._is_biographical("Who scored the most?") is False

    def test_not_biographical_greeting(self):
        assert QueryClassifier._is_biographical("hello") is False


class TestClassificationResult:
    """Tests for ClassificationResult dataclass and metadata bundling."""

    def test_result_is_dataclass(self, classifier):
        result = classifier.classify("Who are the top 5 scorers?")
        assert isinstance(result, ClassificationResult)

    def test_result_has_query_type(self, classifier):
        result = classifier.classify("Who are the top 5 scorers?")
        assert isinstance(result.query_type, QueryType)

    def test_biographical_flag_set(self, classifier):
        result = classifier.classify("Who is LeBron?")
        assert result.is_biographical is True
        assert result.query_type == QueryType.HYBRID

    def test_biographical_flag_not_set(self, classifier):
        result = classifier.classify("Who are the top 5 scorers?")
        assert result.is_biographical is False

    def test_greeting_flag_set(self, classifier):
        result = classifier.classify("hello")
        assert result.is_greeting is True

    def test_greeting_flag_not_set(self, classifier):
        result = classifier.classify("Who are the top 5 scorers?")
        assert result.is_greeting is False

    def test_complexity_k_simple(self, classifier):
        result = classifier.classify("How many teams?")
        assert result.complexity_k == 3

    def test_complexity_k_moderate(self, classifier):
        result = classifier.classify("Compare LeBron and Curry stats")
        assert result.complexity_k == 5

    def test_complexity_k_complex(self, classifier):
        result = classifier.classify(
            "Explain the impact of LeBron's playing style on the team's offense and defense strategy"
        )
        assert result.complexity_k >= 7


class TestEstimateQuestionComplexity:
    """Tests for QueryClassifier._estimate_question_complexity() (moved from chat.py)."""

    def test_simple_query_returns_3(self):
        assert QueryClassifier._estimate_question_complexity("How many teams?") == 3

    def test_moderate_query_returns_5(self):
        assert QueryClassifier._estimate_question_complexity("Compare LeBron and Curry stats") == 5

    def test_complex_query_returns_high_k(self):
        result = QueryClassifier._estimate_question_complexity(
            "Explain the impact of LeBron's playing style on the team's offense and defense strategy"
        )
        assert result >= 7

    def test_short_query_returns_low_k(self):
        result = QueryClassifier._estimate_question_complexity("LeBron stats")
        assert result <= 5

    def test_compound_query_returns_higher_k(self):
        simple_k = QueryClassifier._estimate_question_complexity("LeBron stats")
        compound_k = QueryClassifier._estimate_question_complexity("LeBron stats and Curry stats")
        assert compound_k >= simple_k


class TestRegexCompilation:
    def test_patterns_compiled_on_init(self, classifier):
        assert len(classifier.statistical_regex) == len(QueryClassifier.STATISTICAL_PATTERNS)
        assert len(classifier.contextual_regex) == len(QueryClassifier.CONTEXTUAL_PATTERNS)
        assert len(classifier.hybrid_regex) == len(QueryClassifier.HYBRID_PATTERNS)
