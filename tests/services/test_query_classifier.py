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
    """Tests for QueryClassifier._is_greeting() static method (Phase 15).

    STRICT DETECTION: Only PURE standalone greetings return True.
    Any greeting + additional content returns False.
    """

    def test_simple_greetings(self):
        """Single-word pure greetings."""
        assert QueryClassifier._is_greeting("hi") is True
        assert QueryClassifier._is_greeting("hello") is True
        assert QueryClassifier._is_greeting("hey") is True
        assert QueryClassifier._is_greeting("thanks") is True
        assert QueryClassifier._is_greeting("goodbye") is True
        assert QueryClassifier._is_greeting("bye") is True

    def test_greeting_with_simple_address(self):
        """Greeting + simple address (still pure)."""
        assert QueryClassifier._is_greeting("hi there") is True
        assert QueryClassifier._is_greeting("hello everyone") is True
        assert QueryClassifier._is_greeting("hey folks") is True

    def test_time_greetings(self):
        """Time-based greetings."""
        assert QueryClassifier._is_greeting("good morning") is True
        assert QueryClassifier._is_greeting("good evening") is True
        assert QueryClassifier._is_greeting("good night") is True

    def test_conversational_greetings(self):
        """Conversational greetings (allowed to have ?)."""
        assert QueryClassifier._is_greeting("how are you") is True
        assert QueryClassifier._is_greeting("how are you?") is True
        assert QueryClassifier._is_greeting("what's up") is True
        assert QueryClassifier._is_greeting("what's up?") is True
        assert QueryClassifier._is_greeting("thank you") is True

    # ── EXCLUSION TESTS: Greeting + Additional Content = NOT PURE ──────

    def test_not_greeting_with_comma_and_question(self):
        """Greeting + comma + question → NOT pure."""
        assert QueryClassifier._is_greeting("hi, who is the top scorer?") is False
        assert QueryClassifier._is_greeting("hello, show me NBA stats") is False
        assert QueryClassifier._is_greeting("hey, what about LeBron?") is False
        assert QueryClassifier._is_greeting("hi, can you help me?") is False

    def test_not_greeting_with_basketball_keywords(self):
        """Greeting containing basketball/sports terms → NOT pure."""
        assert QueryClassifier._is_greeting("hello LeBron fans") is False
        assert QueryClassifier._is_greeting("hi team") is False  # "team" is sports keyword
        assert QueryClassifier._is_greeting("thanks for the stats") is False

    def test_not_greeting_with_action_requests(self):
        """Greeting + action request → NOT pure."""
        assert QueryClassifier._is_greeting("hello, please show me stats") is False
        assert QueryClassifier._is_greeting("hi, can you help") is False
        assert QueryClassifier._is_greeting("hey, tell me about the Lakers") is False

    def test_not_greeting_with_numbers(self):
        """Greeting + numbers → NOT pure."""
        assert QueryClassifier._is_greeting("hi 5 times") is False
        assert QueryClassifier._is_greeting("top 5 players") is False

    def test_not_greeting_too_long(self):
        """Greeting that's too long (>6 words) → NOT pure."""
        assert QueryClassifier._is_greeting("hi there how are you doing today my friend") is False

    def test_not_greeting_basketball_query(self):
        """Basketball queries (even if they contain greeting-like words) → NOT pure."""
        assert QueryClassifier._is_greeting("How many teams are in the NBA?") is False
        assert QueryClassifier._is_greeting("Who scored the most points?") is False
        assert QueryClassifier._is_greeting("Show me the top 5 scorers") is False

    def test_not_greeting_empty_string(self):
        """Empty string → NOT pure."""
        assert QueryClassifier._is_greeting("") is False

    def test_greeting_case_insensitive(self):
        """Greetings work regardless of case."""
        assert QueryClassifier._is_greeting("HI") is True
        assert QueryClassifier._is_greeting("Hello") is True
        assert QueryClassifier._is_greeting("GOOD MORNING") is True

    def test_greeting_with_exclamation(self):
        """Greetings with exclamation marks (still pure)."""
        assert QueryClassifier._is_greeting("hi!") is True
        assert QueryClassifier._is_greeting("hello!") is True
        assert QueryClassifier._is_greeting("good morning!") is True


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

    # NOTE: is_greeting field removed from ClassificationResult
    # Greeting detection now happens in chat.py BEFORE classify() is called
    # These tests are no longer relevant

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


class TestWeightedGroupScoring:
    """Tests for weighted regex group scoring mechanism."""

    def test_stat_groups_count(self):
        assert len(QueryClassifier.STAT_GROUPS) == 13

    def test_ctx_groups_count(self):
        assert len(QueryClassifier.CTX_GROUPS) == 10

    def test_stat_group_fires_once(self, classifier):
        """Multiple stat abbreviations in one query fire S1 only once."""
        score, groups = classifier._compute_weighted_score(
            "pts reb ast stl blk", QueryClassifier.STAT_GROUPS
        )
        assert groups.count("S1_db_abbreviations") <= 1

    def test_high_signal_stat_query(self, classifier):
        """Pure stat query scores higher on stat than ctx."""
        stat_score, _ = classifier._compute_weighted_score(
            "top 5 players in pts per game", QueryClassifier.STAT_GROUPS
        )
        ctx_score, _ = classifier._compute_weighted_score(
            "top 5 players in pts per game", QueryClassifier.CTX_GROUPS
        )
        assert stat_score > ctx_score

    def test_high_signal_ctx_query(self, classifier):
        """Pure contextual query scores higher on ctx than stat."""
        stat_score, _ = classifier._compute_weighted_score(
            "why is lebron considered the goat", QueryClassifier.STAT_GROUPS
        )
        ctx_score, _ = classifier._compute_weighted_score(
            "why is lebron considered the goat", QueryClassifier.CTX_GROUPS
        )
        assert ctx_score > stat_score

    def test_hybrid_connector_detected(self, classifier):
        """Connector-based hybrid detection works."""
        result = classifier.classify(
            "Who has the most points and explain why they are effective?"
        )
        assert result.query_type == QueryType.HYBRID

    def test_no_hybrid_for_pure_stat(self, classifier):
        """Pure stat query without context signal is not hybrid."""
        result = classifier.classify("Who are the top 5 scorers?")
        assert result.query_type == QueryType.STATISTICAL

    def test_db_description_strong_signal(self, classifier):
        """Full database column description is a strong stat signal."""
        stat_score, groups = classifier._compute_weighted_score(
            "show me the field goal percentage", QueryClassifier.STAT_GROUPS
        )
        assert stat_score >= 3.0
        assert "S2_full_stat_words_and_db_descriptions" in groups


class TestQueryCategoryClassification:
    """Test query category classification for expansion aggressiveness."""

    def test_noisy_slang(self):
        """Detect noisy queries with slang markers."""
        category = QueryClassifier._classify_category("yo whats da best team lol")
        assert category == "noisy"

    def test_noisy_typos(self):
        """Detect noisy queries with typos."""
        category = QueryClassifier._classify_category("whos got da most pts szn")
        assert category == "noisy"

    def test_noisy_out_of_scope(self):
        """Detect noisy out-of-scope queries."""
        category = QueryClassifier._classify_category("How do I bake a cake?")
        assert category == "noisy"

    def test_noisy_security(self):
        """Detect security attack queries as noisy."""
        category = QueryClassifier._classify_category("'; DROP TABLE players; --")
        assert category == "noisy"

    def test_noisy_excessive_punctuation(self):
        """Detect queries with excessive punctuation."""
        category = QueryClassifier._classify_category("Who won the game???")
        assert category == "noisy"

    def test_conversational_pronouns(self):
        """Detect conversational queries with pronouns."""
        category = QueryClassifier._classify_category("What about his assists?")
        assert category == "conversational"

    def test_conversational_followup(self):
        """Detect follow-up conversational queries."""
        category = QueryClassifier._classify_category("And blocks?")
        assert category == "conversational"

    def test_conversational_correction(self):
        """Detect correction phrases as conversational."""
        category = QueryClassifier._classify_category("Actually, I meant the Celtics")
        assert category == "conversational"

    def test_complex_synthesis(self):
        """Detect complex queries with synthesis terms."""
        category = QueryClassifier._classify_category("Analyze patterns in playoff efficiency discussions")
        assert category == "complex"

    def test_complex_multi_part(self):
        """Detect complex multi-part queries."""
        category = QueryClassifier._classify_category("Compare stats and explain why they're effective")
        assert category == "complex"

    def test_complex_long_query(self):
        """Detect complex long queries (>15 words)."""
        category = QueryClassifier._classify_category(
            "Can you provide a comprehensive analysis of the historical evolution of three-point shooting strategies across different NBA eras"
        )
        assert category == "complex"

    def test_simple_ranking(self):
        """Simple ranking queries should be classified as simple."""
        category = QueryClassifier._classify_category("Who are the top 5 scorers?")
        assert category == "simple"

    def test_simple_definition(self):
        """Simple definition queries should be simple."""
        category = QueryClassifier._classify_category("What is a triple-double?")
        assert category == "simple"

    def test_simple_default(self):
        """Clear, well-formed queries default to simple."""
        category = QueryClassifier._classify_category("Tell me about the Lakers")
        assert category == "simple"

    def test_classification_result_includes_category(self, classifier):
        """ClassificationResult should include query_category field."""
        result = classifier.classify("Who are the top 5 scorers?")
        assert hasattr(result, "query_category")
        assert result.query_category in ["noisy", "conversational", "complex", "simple"]
        assert result.query_category == "simple"  # This specific query should be simple

    def test_classification_result_includes_max_expansions(self, classifier):
        """ClassificationResult should include max_expansions field computed from category + word count."""
        # Test simple query (6 words, category=simple, base=4, adj=0) → 4
        result = classifier.classify("Who are the top 5 scorers?")
        assert hasattr(result, "max_expansions")
        assert 1 <= result.max_expansions <= 5
        assert result.max_expansions == 4  # simple (4) + 0 = 4

        # Test noisy short query (4 words, category=noisy, base=1, adj=+1) → 2
        result_noisy = classifier.classify("yo best team lol")
        assert result_noisy.max_expansions == 2  # noisy (1) + 1 = 2

        # Test conversational short query (4 words, category=conversational, base=5, adj=+1) → 5 (clamped)
        result_conv = classifier.classify("What about his assists?")
        assert result_conv.max_expansions == 5  # conversational (5) + 1 = 6 → clamped to 5

        # Test complex long query (18 words, category=complex, base=2, adj=-1) → 1
        result_complex = classifier.classify(
            "Can you provide a comprehensive analysis of the historical evolution of three-point shooting strategies across different NBA eras"
        )
        assert result_complex.max_expansions == 1  # complex (2) - 1 = 1
