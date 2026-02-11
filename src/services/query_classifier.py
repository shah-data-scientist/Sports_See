"""
FILE: query_classifier.py
STATUS: Active
RESPONSIBILITY: Classify queries as statistical, contextual, or hybrid for routing
LAST MAJOR UPDATE: 2026-02-11
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

    # ── NBA Database stat column headers (strong statistical signals) ─────
    # These are the actual column names/aliases from the NBA database.
    # If a user mentions any of these, the query is almost certainly statistical.

    # Basic stat abbreviations (from player_stats table)
    _STAT_ABBRS = (
        r"pts|reb|ast|stl|blk|tov|pf|gp|fgm|fga|fg%|ftm|fta|ft%"
        r"|3pm|3pa|3p%|efg%|ts%|usg%|oreb|dreb|oreb%|dreb%|reb%"
        r"|fp|dd2|td3|pie|pace|poss"
    )
    # Advanced metric abbreviations
    _ADV_ABBRS = r"offrtg|defrtg|netrtg|ast%|ast/to|to\s*ratio|ast\s*ratio"

    # Full stat words (natural language equivalents of column headers)
    _STAT_WORDS = (
        r"points|rebounds|assists|steals|blocks|turnovers|fouls"
        r"|wins|losses|games\s*played|minutes"
        r"|free\s*throws?|field\s*goals?|three.pointers?"
        r"|double.doubles?|triple.doubles?"
        r"|possessions?|personal\s+fouls?"
    )
    # Data dictionary full names (the words people actually use in questions)
    # Source: data_dictionary table in nba_stats.db (45 entries)
    _DICT_NAMES = (
        r"plus.minus|fantasy\s+points"
        r"|3.point\s+(percentage|shots?\s*(attempted|made))"
        r"|assist.to.turnover\s+ratio|assist\s+percentage|assist\s+ratio"
        r"|defensive\s+rebounds?|defensive\s+rebound\s*%"
        r"|offensive\s+rebounds?|offensive\s+rebound\s*%"
        r"|total\s+rebounds?|total\s+rebound\s*%"
        r"|field\s+goal\s+(percentage|attempted|made)"
        r"|free\s+throw\s+(percentage|attempted|made)"
        r"|effective\s+field\s+goal\s*%?"
        r"|true\s+shooting\s*%?"
        r"|games\s+played|minutes\s+per\s+game"
    )
    # Advanced metric full names
    _ADV_WORDS = (
        r"offensive\s+rating|defensive\s+rating|net\s+rating"
        r"|usage\s+rate|player\s+impact(\s+estimate)?"
        r"|assist\s+ratio|turnover\s+ratio"
        r"|rebound\s+percentage|assist\s+percentage"
    )

    # Statistical query patterns (SQL database)
    STATISTICAL_PATTERNS = [
        # ── A. Database column headers as detection patterns ───────────
        # Stat abbreviations (strong signal: PTS, REB, AST, FG%, TS%, PIE, etc.)
        rf"\b({_STAT_ABBRS})\b",
        rf"\b({_ADV_ABBRS})\b",
        # Full stat words (points, rebounds, assists, steals, blocks, etc.)
        rf"\b({_STAT_WORDS})\b",
        # Data dictionary full names (the words people use: "field goal percentage", etc.)
        rf"({_DICT_NAMES})",
        # Advanced metric full names (offensive rating, true shooting, etc.)
        rf"({_ADV_WORDS})",

        # ── B. Superlatives (bidirectional: most↔fewest, highest↔lowest) ──
        r"\b(top|bottom)\s+\d+",
        r"\b(most|fewest|highest|lowest|best|worst|leading|leader)\s+\d*",
        r"\b(who|which)\b.*\b(most|fewest|highest|lowest|best|worst)\b",

        # ── C. Aggregations & calculations ────────────────────────────
        r"\b(average|mean|total|sum|count|how many|maximum|minimum|median)\b",
        r"\bwhat\s+(is|are)\b.*\b(percentage|average|total|rating|ratio)\b",
        r"\bwhat\s+percentage\b",
        r"\bper\s+game\b",

        # ── D. Comparisons (bidirectional: better↔worse, higher↔lower) ──
        # Threshold comparisons with numbers
        r"\b(better|worse|higher|lower|greater|fewer|more|less)\s+than\s+\d+",
        r"\b(over|under|above|below|exceeds?|at\s+least|at\s+most)\s+\d+",
        # Comparative queries
        r"\bcompare\b.*\b(to|vs|versus|and|with)\b",
        r"\bcompare\b.*\b(stats|statistics|numbers)\b",
        r"\b(who has more|who has fewer|who has less|which player has more|who recorded more)\b",

        # ── E. Explicit filters with numbers ──────────────────────────
        r"\b(more than|less than|fewer than|over|under|above|below)\b\s*\d+",
        r"\b(with|having)\b.*\d+\+?\s*(points|rebounds|assists|games|wins|steals|blocks)",
        r"\d+\+?\s*(points|rebounds|assists|steals|blocks|wins|games|percent)",

        # ── F. Player/team stat queries ───────────────────────────────
        # Best/better with stat terms
        r"\b(who\s+is|who.?s|which)\b.*\b(best|better|worst|worse)\b.*\b(scorer|rebounder|passer|defender|shooter|blocker|player)\b",
        r"\b(best|better|worst|worse)\b.*\b(at|in|for)\b.*\b(scoring|rebounding|assists|defense|shooting|blocking|stealing)\b",
        r"\b(who has|which player has)\b.*\b(best|worst|highest|lowest|top|better)\b.*\b(percentage|pct|efficiency|rating)\b",
        # Show/List/Find/Get stat leaders
        r"\b(show|list|find|get)\b.*\b(assist|rebound|point|steal|block|score|stat).*(leader|top|best|worst)\b",
        r"\b(show|list|find|get)\b.*(the)?\s*(top|bottom|best|worst|leading|leader)",
        # Casual queries
        r"\b(who\s+is|who.?s)\b.*\b(leading|top|number one|#1|the\s+best|the\s+worst)\b",
        r"\b(tell me about|gimme|give me)\b.*\b(stats|statistics|numbers|leaders?|scoring|averages?)\b",
        r"\b(leaders?|leader)\b",

        # ── G. Team roster / player list queries ──────────────────────
        r"\b(list|show|find|get)\b.*\b(all\s+)?\bplayers?\b",
        r"\bplays?\s+(for|on)\b",

        # ── H. Statistical verbs ──────────────────────────────────────
        r"\b(scored|averaging|shooting|recording|ranked|ranking)\b.*\d+",
        r"\b(ranks|ranking|ranked)\b.*\b(by|in)\b",

        # ── I. Possessive & pronoun stat queries ──────────────────────
        r"\bwhat is\b.*'s?\s+\b(\d-point|three.point|free.throw|field.goal|scoring|shooting|rebound|assist|block|steal)",
        r"\b(his|her|their|its)\s+(assists?|rebounds?|points?|steals?|blocks?|stats?|scoring|shooting|games?|wins?|losses?|minutes?|turnovers?|fouls?|rating|efficiency|percentage)\b",

        # ── J. 3-point / shooting references ──────────────────────────
        r"\bfrom\s+3\b|\bfrom\s+three\b|\bfrom\s+downtown\b",
        r"\b(shoots?|shooting)\b.*\b(better|worse|best|worst|from\s+\d|from\s+three)\b",

        # ── K. Filter/find queries ────────────────────────────────────
        r"\b(find|which|who are)\b.*\b(players?|teams?)\b.*\b(with|having|that)\b",
        r"\b(who are|list|show me)\b.*\b(top|bottom|players with|scorers|leaders)\b",
        # Informal
        r"\bhow many\b",

        # ── L. Player role terms in comparisons ──────────────────────────
        # "efficient goal maker", "better scorer", "more efficient shooter"
        r"\b(efficient|effective|productive)\s+(goal\s*maker|scorer|shooter|rebounder|passer|blocker|playmaker|player)\b",
        r"\b(who\s+is|who.?s)\b.*\b(more|most|less|least)\b.*\b(efficient|effective|productive)\b",
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
        # Qualitative assessments (exclude "better than [number]" = statistical threshold)
        r"\b(greatest|goat|best ever|all.time)\b(?!.*\bstats\b)",
        r"\b(better|worse)\b(?!.*\bstats\b)(?!.*\bthan\s+\d)",
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
        # Requires context >= 2 to avoid false positives (e.g., "shoots better from 3"
        # where "better" triggers 1 contextual match but the query is purely statistical)
        if stat_matches >= 2 and context_matches >= 2:
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
