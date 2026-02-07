"""
FILE: query_classifier.py
STATUS: Active
RESPONSIBILITY: Classify queries as statistical, contextual, or hybrid for routing
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

import logging
import re
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query type classification."""

    STATISTICAL = "statistical"  # Use SQL tool
    CONTEXTUAL = "contextual"  # Use vector search
    HYBRID = "hybrid"  # Use both


class QueryClassifier:
    """Classify user queries to route to appropriate data source."""

    # Statistical query patterns (SQL database)
    # Phase 4: More conservative - require stronger statistical signals
    STATISTICAL_PATTERNS = [
        # Superlatives with statistical terms (NOT just "best" which is subjective)
        r"\b(top|most|highest|lowest|leading|leader)\s+\d+",  # "top 5", "most 10"
        r"\b(who has|which player|which team)\b.*\b(most|highest|top)\b.*\b(points|rebounds|assists|stats)\b",
        # Explicit aggregations (strong statistical signal)
        r"\b(average|mean|total|sum|count|how many)\b",
        r"\bavg\b.*\b(points|rebounds|assists|per game)\b",
        # Explicit stat comparisons
        r"\bcompare\b.*\b(stats|statistics|numbers)\b",
        # Explicit stat abbreviations (strong signal)
        r"\b(pts|reb|ast|stl|blk|fg%|3p%|ft%|ts%|per|ws|ortg|drtg)\b",
        # Statistical verbs with numbers
        r"\b(scored|averaging)\b.*\d+",
        r"\b(ranks|ranking|ranked)\b.*\b(by|in)\b.*\b(points|rebounds|assists)\b",
        # Explicit filters with numbers
        r"\b(more than|less than|over|under|above|below)\b\s*\d+\s*(points|rebounds|assists)",
        # Question words + explicit stats
        r"\bhow many\b.*\b(points|rebounds|assists|games|wins)\b",
        r"\bwhat is\b.*\b(percentage|average|total|rating)\b.*\b(of|for)\b",
        # Specific statistical queries
        r"\b(who are|list|show me)\b.*\b(top|players with|scorers|leaders)\b",
    ]

    # Contextual query patterns (vector search)
    CONTEXTUAL_PATTERNS = [
        # Why/how questions (qualitative)
        r"\b(why|how|explain|what makes|what caused)\b(?!.*\b(many|much)\b)",
        # Opinions and discussions
        r"\b(think|believe|opinion|discussion|debate|argue)\b",
        r"\b(reddit|fans|people|community)\b.*\b(think|say|discuss)\b",
        # Strategy and style
        r"\b(strategy|style|approach|technique|tactics)\b",
        r"\b(play|playing|game plan)\b",
        # Historical context
        r"\b(history|evolution|changed|transformation)\b",
        # Qualitative assessments
        r"\b(better|worse|greatest|goat|best ever|all.time)\b(?!.*\bstats\b)",
        # Impact and influence
        r"\b(impact|influence|effect|significance)\b",
        # Analysis and interpretation
        r"\b(analysis|interpret|understand|insight)\b",
    ]

    # Hybrid patterns (both sources needed)
    HYBRID_PATTERNS = [
        # Compare + explain
        r"\bcompare\b.*\b(and|then)\b.*\b(explain|why|better)\b",
        r"\b(stats|statistics)\b.*\b(and|then)\b.*\b(why|explain|understand)\b",
        # Performance with reasoning
        r"\b(performance|efficiency)\b.*\b(why|how|explain)\b",
        # Best/worst with justification
        r"\b(who is better|which is better)\b.*\b(and why|explain|based on)\b",
    ]

    def __init__(self):
        """Initialize query classifier with compiled regex patterns."""
        self.statistical_regex = [re.compile(p, re.IGNORECASE) for p in self.STATISTICAL_PATTERNS]
        self.contextual_regex = [re.compile(p, re.IGNORECASE) for p in self.CONTEXTUAL_PATTERNS]
        self.hybrid_regex = [re.compile(p, re.IGNORECASE) for p in self.HYBRID_PATTERNS]

    def classify(self, query: str) -> QueryType:
        """Classify query type based on patterns.

        Args:
            query: User query string

        Returns:
            QueryType (STATISTICAL, CONTEXTUAL, or HYBRID)
        """
        query = query.strip().lower()

        # Check hybrid patterns first (most specific)
        hybrid_matches = sum(1 for pattern in self.hybrid_regex if pattern.search(query))
        if hybrid_matches > 0:
            logger.info(f"Query classified as HYBRID (matched {hybrid_matches} patterns)")
            return QueryType.HYBRID

        # Check statistical patterns
        stat_matches = sum(1 for pattern in self.statistical_regex if pattern.search(query))

        # Check contextual patterns
        context_matches = sum(1 for pattern in self.contextual_regex if pattern.search(query))

        # Classify based on match counts
        if stat_matches > context_matches:
            logger.info(
                f"Query classified as STATISTICAL "
                f"(stat: {stat_matches}, context: {context_matches})"
            )
            return QueryType.STATISTICAL

        if context_matches > stat_matches:
            logger.info(
                f"Query classified as CONTEXTUAL "
                f"(stat: {stat_matches}, context: {context_matches})"
            )
            return QueryType.CONTEXTUAL

        # Default to contextual if no strong match or tie
        logger.info(
            f"Query classified as CONTEXTUAL (default) "
            f"(stat: {stat_matches}, context: {context_matches})"
        )
        return QueryType.CONTEXTUAL


# Example usage
if __name__ == "__main__":
    classifier = QueryClassifier()

    test_queries = [
        # Statistical
        ("Who are the top 5 scorers?", QueryType.STATISTICAL),
        ("What is LeBron's average points per game?", QueryType.STATISTICAL),
        ("Which team has the most wins?", QueryType.STATISTICAL),
        ("Show me players with over 100 three-pointers", QueryType.STATISTICAL),
        # Contextual
        ("Why is LeBron considered the GOAT?", QueryType.CONTEXTUAL),
        ("What do Reddit fans think about the trade?", QueryType.CONTEXTUAL),
        ("Explain the triangle offense strategy", QueryType.CONTEXTUAL),
        ("How has the playing style evolved?", QueryType.CONTEXTUAL),
        # Hybrid
        ("Compare Jokic and Embiid's stats and explain who's better", QueryType.HYBRID),
        ("Who has better efficiency and why?", QueryType.HYBRID),
    ]

    print("Query Classification Test")
    print("=" * 80)

    correct = 0
    for query, expected in test_queries:
        result = classifier.classify(query)
        match = "OK" if result == expected else "FAIL"
        print(f"{match:4} {result.value:15} | Expected: {expected.value:15} | {query}")
        if result == expected:
            correct += 1

    print("=" * 80)
    print(f"Accuracy: {correct}/{len(test_queries)} ({100*correct/len(test_queries):.1f}%)")
