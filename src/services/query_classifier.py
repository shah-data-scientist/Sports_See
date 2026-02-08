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
    # Phase 10: More aggressive - try SQL first, fallback to vector if it fails
    STATISTICAL_PATTERNS = [
        # Superlatives with statistical terms
        r"\b(top|most|highest|lowest|leading|leader)\s+\d+",  # "top 5", "most 10"
        r"\b(who has|which player|which team)\b.*\b(most|highest|top)\b.*\b(points|rebounds|assists|stats)\b",
        # WHO/WHICH queries with superlatives and stat terms
        r"\b(who|which player|which team)\b.*\b(scored|has|recorded|made)\b.*\b(most|highest|top|fewest|lowest|least)\b.*\b(points|rebounds|assists|blocks|steals|three.pointers?)\b",
        r"\b(who|which player)\b.*\b(most|highest|top|fewest|lowest|least)\b.*\b(points|rebounds|assists|blocks|steals|stats)\b",
        # NEW: "best/better" queries with stat terms (aggressive)
        r"\b(who\s+is|who.?s|which player|which team)\b.*\b(best|better)\b.*\b(scorer|rebounder|passer|defender|shooter|player)\b",
        r"\b(best|better)\b.*\b(at|in|for)\b.*\b(scoring|rebounding|assists|defense|shooting)\b",
        r"\b(who has|which player has)\b.*\b(best|highest|top|better)\b.*\b(percentage|pct|efficiency|rating)\b",  # "Who has the best... percentage/efficiency"
        # NEW: "Show/List/Find" queries with stats (aggressive)
        r"\b(show|list|find|get)\b.*\b(assist|rebound|point|steal|block|score|stat).*(leader|top|best)\b",
        r"\b(show|list|find|get)\b.*(the)?\s*(top|best|leading|leader)",
        # NEW: Casual statistical queries
        r"\b(who\s+is|who.?s)\b.*\b(leading|top|number one|#1|the\s+best)\b",
        # Comparative queries with stat terms
        r"\b(who has more|which player has more|who recorded more)\b.*\b(points|rebounds|assists|blocks|steals)\b",
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
        r"\b(with|having)\b.*\d+\+?\s*(points|rebounds|assists|games)",
        # Question words + explicit stats
        r"\bhow many\b.*\b(points|rebounds|assists|games|wins)\b",
        r"\bwhat is\b.*\b(percentage|average|total|rating)\b.*\b(of|for)\b",
        # NEW: Find/filter queries (aggressive)
        r"\b(find|which|who are)\b.*\b(players?|teams?)\b.*\b(with|having|that)\b",
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
    # Phase 12: Enhanced detection - catches "X statistic AND Y explanation" queries
    HYBRID_PATTERNS = [
        # Statistical + Explanation (most common hybrid pattern)
        r"\b(who|which|what).*(most|top|best|highest|leading).*(and|then)\s*(explain|why|what makes|how)\b",
        r"\b(top|most|best|highest|leading).*(and|then)\s*(why|explain|what makes|their|his|her)\b",

        # "What makes X effective/good/great" (stats + qualitative)
        r"\b(what makes|why is|why are).*(effective|good|great|successful|dominant|better)\b",
        r"\b(who|which).*(and|then)\s*what makes\b",

        # Impact/Effect queries (stats + context)
        r"\b(top|most|best|leading).*(impact|effect|influence|contribution)\b",
        r"\b(who|which).*(and|then)\s*(impact|effect|influence)\b",

        # Style/Approach queries with stats
        r"\b(scorer|player|rebounder).*(and|then)\s*(style|approach|playing|game)\b",
        r"\b(compare|comparison).*(style|approach|playing|strategies?)\b",
        r"\b(who|which).*(and|then)\s*(style|playing|approach)\b",

        # "X and explain/analyze Y" patterns
        r"\b(compare|list|show|top).*(and|then)\s*(explain|analyze|discuss|describe)\b",
        r"\b(stats?|statistics?|numbers?).*(and|then)\s*(why|explain|analysis|context)\b",

        # "Better/Best with reasoning" patterns
        r"\b(who is better|which is better|who's better).*(why|explain|because|based on)\b",
        r"\b(best|better).*(and|then)\s*(why|explain|what makes)\b",

        # Performance/Efficiency with analysis
        r"\b(performance|efficiency|effectiveness).*(why|how|explain|what makes)\b",
        r"\b(efficient|effective).*(and|then)\s*(why|explain|what)\b",

        # Two-part questions (CRITICAL for fixing evaluation failures)
        r"(who|which|what).+(\?|and).+(why|how|what makes|explain|style|impact)",
        r"(most|top|best|highest).+(\?|and).+(why|how|explain|what makes|style)",
    ]

    def __init__(self):
        """Initialize query classifier with compiled regex patterns."""
        self.statistical_regex = [re.compile(p, re.IGNORECASE) for p in self.STATISTICAL_PATTERNS]
        self.contextual_regex = [re.compile(p, re.IGNORECASE) for p in self.CONTEXTUAL_PATTERNS]
        self.hybrid_regex = [re.compile(p, re.IGNORECASE) for p in self.HYBRID_PATTERNS]

    def classify(self, query: str) -> QueryType:
        """Classify query type based on patterns.

        Phase 12 improvements:
        - Enhanced hybrid detection (15 patterns vs 4)
        - Promote to HYBRID when both stat and context patterns match strongly
        - Better tie-breaking logic

        Args:
            query: User query string

        Returns:
            QueryType (STATISTICAL, CONTEXTUAL, or HYBRID)
        """
        query_normalized = query.strip().lower()

        # Check hybrid patterns first (most specific)
        hybrid_matches = sum(1 for pattern in self.hybrid_regex if pattern.search(query_normalized))
        if hybrid_matches > 0:
            logger.info(f"Query classified as HYBRID (matched {hybrid_matches} hybrid patterns)")
            return QueryType.HYBRID

        # Check statistical patterns
        stat_matches = sum(1 for pattern in self.statistical_regex if pattern.search(query_normalized))

        # Check contextual patterns
        context_matches = sum(1 for pattern in self.contextual_regex if pattern.search(query_normalized))

        # NEW: If both stat and context patterns match strongly → HYBRID
        # This catches queries like "top scorers and their playing styles"
        if stat_matches >= 2 and context_matches >= 1:
            logger.info(
                f"Query classified as HYBRID (stat: {stat_matches}, context: {context_matches}) "
                "- both components detected"
            )
            return QueryType.HYBRID

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
