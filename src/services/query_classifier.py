"""
FILE: query_classifier.py
STATUS: Active
RESPONSIBILITY: Classify queries as statistical, contextual, or hybrid for routing
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Basketball glossary terms that should route to CONTEXTUAL (vector search)
# These are reference/definitional terms, not data queries
BASKETBALL_GLOSSARY_TERMS = [
    # Abbreviations & Metrics
    "triple-double", "double-double", "triple double", "double double",
    # Formal definitions (not just abbreviations, but actual terms people look up)
    "first option", "second option", "third option",
    "iso", "isolation", "pick and roll", "pick-and-roll", "pnr",
    "zone defense", "man-to-man defense", "man to man",
    "variance", "true shooting", "effective field goal",
    "player impact estimate", "plus-minus",
]


class QueryType(Enum):
    """Query type classification."""

    STATISTICAL = "statistical"  # Use SQL tool
    CONTEXTUAL = "contextual"  # Use vector search
    HYBRID = "hybrid"  # Use both


@dataclass
class ClassificationResult:
    """Rich classification result bundling query_type with metadata.

    Eliminates duplicate analysis calls by computing all query properties
    in a single classify() pass:
    - query_type: routing decision (STATISTICAL, CONTEXTUAL, HYBRID)
    - is_biographical: player/team info query (needs SQL stats + vector context)
    - is_greeting: simple greeting (skip RAG entirely)
    - complexity_k: adaptive retrieval depth (3=simple, 5=moderate, 7-9=complex)
    """

    query_type: QueryType
    is_biographical: bool = False
    is_greeting: bool = False
    complexity_k: int = 5


class QueryClassifier:
    """Classify user queries to route to appropriate data source."""

    # ── NBA Database stat column headers (strong statistical signals) ─────
    # These are the actual column names/aliases from the NBA database.
    # If a user mentions any of these, the query is almost certainly statistical.

    # Basic stat abbreviations (from player_stats table)
    # Note: fg%, 3p%, ts% etc. use non-word-boundary matching (see pattern A below)
    # because % is not a word character and \b won't match between letter and %
    _STAT_ABBRS = (
        r"pts|reb|ast|stl|blk|tov|pf|gp|fgm|fga|ftm|fta"
        r"|3pm|3pa|oreb|dreb"
        r"|fp|dd2|td3|pie|pace|poss"
        r"|ppg|rpg|apg|spg|bpg|mpg"  # Per-game abbreviations
        r"|avg|pct"  # Common informal abbreviations
    )
    # Percentage abbreviations (need special matching without trailing \b)
    _PCT_ABBRS = r"fg%|ft%|3p%|efg%|ts%|usg%|oreb%|dreb%|reb%|ast%"
    # Advanced metric abbreviations
    _ADV_ABBRS = r"offrtg|defrtg|netrtg|ast/to|to\s*ratio|ast\s*ratio"

    # Full stat words (natural language equivalents of column headers)
    _STAT_WORDS = (
        r"points|rebounds|assists|steals|blocks|turnovers|fouls"
        r"|wins|losses|games\s*played|minutes"
        r"|free\s*throws?|field\s*goals?|three.pointers?"
        r"|double.doubles?|triple.doubles?"
        r"|possessions?|personal\s+fouls?"
        r"|stats|statistics|averages?|numbers"
        r"|attempts?|makes?|percentage|pct|efficiency"
        r"|record|season|roster"
        r"|mvp|all.star|all.nba|rookie|veteran|starter|bench"
        r"|scorer|rebounder|passer|shooter|blocker|playmaker"
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
        # Stat abbreviations (strong signal: PTS, REB, AST, PIE, etc.)
        rf"\b({_STAT_ABBRS})\b",
        rf"\b({_ADV_ABBRS})\b",
        # Percentage abbreviations (% is not a word char, so match without trailing \b)
        rf"(?<!\w)({_PCT_ABBRS})",
        # Full stat words (points, rebounds, assists, steals, blocks, stats, mvp, etc.)
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
        # Comparative queries (including bare "compare" without "to/vs")
        r"\bcompare\b",
        r"\b(who has more|who has fewer|who has less|which player has more|who recorded more)\b",

        # ── E. Explicit filters with numbers ──────────────────────────
        r"\b(more than|less than|fewer than|over|under|above|below)\b\s*\d+",
        r"\b(with|having)\b.*\d+\+?\s*(points|rebounds|assists|games|wins|steals|blocks)",
        r"\d+\+?\s*(points|rebounds|assists|steals|blocks|wins|games|percent)",

        # ── F. Player/team stat queries ───────────────────────────────
        # REMOVED: "Who is [player]?" queries - these are biographical (CONTEXTUAL) not statistical
        # These should use vector search for biographical/contextual data, not SQL stats
        # Best/better with stat terms
        r"\b(who\s+is|who.?s|which)\b.*\b(best|better|worst|worse)\b.*\b(scorer|rebounder|passer|defender|shooter|blocker|player)\b",
        r"\b(best|better|worst|worse)\b.*\b(at|in|for)\b.*\b(scoring|rebounding|assists|defense|shooting|blocking|stealing)\b",
        r"\b(who has|which player has)\b.*\b(best|worst|highest|lowest|top|better)\b.*\b(percentage|pct|efficiency|rating)\b",
        # Show/List/Find/Get stat leaders or stats
        r"\b(show|list|find|get)\b.*\b(assist|rebound|point|steal|block|score|stat).*(leader|top|best|worst)\b",
        r"\b(show|list|find|get)\b.*(the)?\s*(top|bottom|best|worst|leading|leader)",
        r"\b(show|list|find|get)\b.*\b(me\s+)?\b(stats|statistics|averages?|numbers)\b",
        # Casual queries
        r"\b(who\s+is|who.?s)\b.*\b(leading|top|number one|#1|the\s+best|the\s+worst|the\s+mvp)\b",
        r"\b(tell me about|gimme|give me)\b.*\b(stats|statistics|numbers|leaders?|scoring|averages?)\b",
        r"\b(leaders?|leader)\b",

        # ── G. Team roster / player list queries ──────────────────────
        r"\b(list|show|find|get)\b.*\b(all\s+)?\bplayers?\b",
        r"\bplays?\s+(for|on)\b",
        # Team name + "stats/players/roster"
        r"\b(lakers?|celtics?|warriors?|nets?|knicks?|bulls?|heat|suns?|nuggets?|bucks?|76ers|sixers|cavaliers?|cavs|hawks?|rockets?|clippers?|mavericks?|mavs|grizzlies|thunder|pelicans?|kings?|pistons?|hornets?|wizards?|pacers?|raptors?|blazers?|spurs?|wolves|timberwolves|magic|jazz)\b",

        # ── H. Statistical verbs ──────────────────────────────────────
        r"\b(scored|averaging|shooting|recording|ranked|ranking)\b.*\d+",
        r"\b(ranks|ranking|ranked)\b.*\b(by|in)\b",
        r"\b(scored|averaging|scoring|recording)\b",  # Without numbers too

        # ── I. Possessive & pronoun stat queries ──────────────────────
        r"\bwhat is\b.*'s?\s+\b(\d-point|three.point|free.throw|field.goal|scoring|shooting|rebound|assist|block|steal)",
        r"\b(his|her|their|its)\s+(assists?|rebounds?|points?|steals?|blocks?|stats?|scoring|shooting|games?|wins?|losses?|minutes?|turnovers?|fouls?|rating|efficiency|percentage)\b",
        # Possessive with player name: "curry's", "lebron's"
        r"\w+'s\s+(stats|points|rebounds|assists|steals|blocks|shooting|scoring|efficiency|averages?|numbers|percentage|pct|record)\b",

        # ── J. 3-point / shooting references ──────────────────────────
        r"\bfrom\s+3\b|\bfrom\s+three\b|\bfrom\s+downtown\b",
        r"\b(shoots?|shooting)\b.*\b(better|worse|best|worst|from\s+\d|from\s+three)\b",
        # Informal: "3 pt", "3pt", "3-pt" (with or without spaces)
        r"\b3\s*-?\s*pt\b",

        # ── K. Filter/find queries ────────────────────────────────────
        r"\b(find|which|who are)\b.*\b(players?|teams?)\b.*\b(with|having|that)\b",
        r"\b(who are|list|show me)\b.*\b(top|bottom|players with|scorers|leaders)\b",
        # Informal
        r"\bhow many\b",

        # ── L. Player role terms in comparisons ──────────────────────────
        # "efficient goal maker", "better scorer", "more efficient shooter"
        r"\b(efficient|effective|productive)\s+(goal\s*maker|scorer|shooter|rebounder|passer|blocker|playmaker|player)\b",
        r"\b(who\s+is|who.?s)\b.*\b(more|most|less|least)\b.*\b(efficient|effective|productive)\b",

        # ── M. Noisy/informal query patterns ─────────────────────────
        # Slang verbs + stat terms: "whats the avg", "gimme", "show me"
        r"\b(whats?|wuts|wat)\b.*\b(avg|average|stats?|pct|record|points?|assists?|rebounds?)\b",
        # "da league", "in da", "da nba" (slang)
        r"\bda\s+(league|nba)\b",
        # ── Fix 5: Slang only triggers stat when near a stat term ──────
        # Previously: bare "bro", "yo", "lol" triggered stat for any query
        # Now: require a stat keyword within the same query
        r"\b(plz|pls|lol|yo|bruh|bro|fam)\b.*\b(stats?|points?|assists?|rebounds?|avg|pct|score|scorer|top\s+\d|record)\b",
        r"\b(stats?|points?|assists?|rebounds?|avg|pct|score|scorer|top\s+\d|record)\b.*\b(plz|pls|lol|yo|bruh|bro|fam)\b",
    ]

    # Contextual query patterns (vector search)
    CONTEXTUAL_PATTERNS = [
        # ── Phase 17: Biographical queries (vector search for player/team context) ───
        # These should retrieve biographical data + statistics from vector search
        # NOT routed to SQL database (SQL has only raw numbers, not narrative context)
        # Exclude when stat terms present (e.g., "Tell me about LeBron's stats")
        r"\b(who is|who\?s|who are|tell me about|gimme the scoop on|info on)\b(?!.*\b(stats?|statistics?|scoring|averages?|numbers?|efficient|efficiency|scorer|mvp)\b).*\b(player|lebron|jordan|kobe|curry|james|durant|lakers|celtics|heat|warriors|teams?|athletes?)\b",
        # "Who is LeBron" (proper names) — exclude common words that IGNORECASE would falsely match
        r"\b(who\s+is)\s+(?!the\b|their\b|a\b|an\b|more\b|most\b|less\b|least\b|your\b|my\b|our\b)([A-Z][a-z]+(\s+[A-Z][a-z]+)*)\b",
        r"\b(about|background|history|biography|bio)\b.*\b(player|athlete|team|star)\b",

        # Why/how questions (qualitative) — exclude "how many", "how much", "how does X compare"
        r"\b(why|explain|what makes|what caused)\b",
        r"\bhow\b(?!.*\b(many|much)\b)(?!.*\bcompare\b)",
        # Opinions and discussions
        r"\b(think|believe|opinion|discussion|debate|argue)\b",
        r"\b(reddit|fans|people|community)\b.*\b(think|say|discuss)\b",
        # ── Fix 3: Broader fan/community/opinion detection ───────────────
        # Fan-related queries (even without explicit "think/say/discuss" verb)
        r"\b(fans?|community|reddit|people)\b.*\b(about|love|hate|view|feel|consider|debate|say)\b",
        r"\b(according\s+to|what\s+do)\b.*\b(fans?|reddit|people|community)\b",
        r"\b(popular|discussed|controversial|trending)\s+(opinions?|topics?|debates?|discussions?)\b",
        # Qualitative opinion verbs
        r"\b(view|feel|consider|regard|perceive|expected?|surprising?|chances?|hopes?)\b",
        # Subjective qualifiers (underrated, overrated, surprising, etc.)
        r"\b(underrated|overrated|surprising|disappointing|impressive|controversial|valuable|worth)\b",
        # "what does this mean/reveal/suggest" — qualitative interpretation
        r"\bwhat\s+(does|do)\s+this\b.*\b(mean|reveal|suggest|tell|show|imply)\b",
        # Strategy and style
        r"\b(strategy|style|approach|technique|tactics)\b",
        # Historical context
        r"\b(history|evolution|changed|transformation)\b",
        # Qualitative assessments (exclude "better than [number]" = statistical threshold)
        r"\b(greatest|goat|best ever|all.time)\b(?!.*\bstats\b)",
        r"\b(better|worse)\b(?!.*\bstats\b)(?!.*\bthan\s+\d)(?!.*\bcompare\b)(?!.*\b(from\s+3|from\s+three|shooting|scorer|scoring|field\s+goal|free\s+throw)\b)",
        # Impact and influence
        r"\b(impact|influence|effect|significance)\b",
        # Analysis and interpretation
        r"\b(analy[sz]e|analysis|interpret|understand|insight|correlation)\b",
        # Quoted/reference requests
        r"\b(quote|direct\s+quote|excerpt|what\s+did\s+\w+\s+say)\b",
    ]

    # Hybrid patterns (both sources needed)
    # Phase 12: Enhanced detection - catches "X statistic AND Y explanation" queries
    HYBRID_PATTERNS = [
        # Statistical + Explanation (most common hybrid pattern)
        # ── Fix 4: Broader connectors: and, then, —, +, -, but, yet, while, comma ──
        r"\b(who|which|what).*(most|top|best|highest|leading).*(and|then|but|yet|while|—|–)\s*(explain|why|what makes|how)\b",
        r"\b(top|most|best|highest|leading).*(and|then|but|yet|—|–)\s*(why|explain|what makes|their|his|her)\b",

        # "What makes X effective/good/great" (stats + qualitative)
        r"\b(what makes|why is|why are).*(effective|good|great|successful|dominant|better)\b",
        r"\b(who|which).*(and|then|—|–)\s*what makes\b",

        # Impact/Effect queries (stats + context)
        r"\b(top|most|best|leading).*(impact|effect|influence|contribution)\b",
        r"\b(who|which).*(and|then|—|–)\s*(impact|effect|influence)\b",

        # Style/Approach queries with stats
        r"\b(scorer|player|rebounder).*(and|then|—|–)\s*(style|approach|playing|game)\b",
        r"\b(compare|comparison).*(style|approach|playing|strategies?)\b",
        r"\b(who|which).*(and|then|—|–)\s*(style|playing|approach)\b",

        # "X and explain/analyze Y" patterns
        r"\b(compare|list|show|top).*(and|then|—|–)\s*(explain|analyze|discuss|describe)\b",
        r"\b(stats?|statistics?|numbers?).*(and|then|—|–|,)\s*(why|explain|analysis|context)\b",

        # "Better/Best with reasoning" patterns
        r"\b(who is better|which is better|who's better).*(why|explain|because|based on)\b",
        r"\b(best|better).*(and|then|—|–)\s*(why|explain|what makes)\b",

        # Performance/Efficiency with analysis
        r"\b(performance|efficiency|effectiveness).*(why|how|explain|what makes)\b",
        r"\b(efficient|effective).*(and|then|—|–)\s*(why|explain|what)\b",

        # Two-part questions (CRITICAL for fixing evaluation failures)
        # Note: em-dash/en-dash already normalized to " - " in classify()
        r"(who|which|what|are\s+there|analyze|find|show).+(\?|and|,|\s+-\s+).+(why|how|what makes|what does this|explain|reveal|suggest|style|impact|drive|winning|success)",
        r"(most|top|best|highest|analyze|compare).+(\?|and|,|\s+-\s+).+(why|how|explain|what makes|what does this|reveal|suggest|style|drive|winning)",

        # ── Fix 4b: Stat term + fan/opinion/community signal in same query ──
        # Detects queries that combine data requests with fan discussion
        r"\b(stats?|statistics?|numbers?|scoring|points?|assists?|rebounds?|efficiency|dominance)\b.*(fans?|reddit|opinions?|discuss|debate|overrated|underrated|viewed?|considered?|according)",
        r"(fans?|reddit|opinions?|discuss|debate|overrated|underrated|viewed?|considered?|according).*\b(stats?|statistics?|numbers?|scoring|points?|assists?|rebounds?|efficiency|dominance)\b",
        # "+", "AND" (caps), "nd" (slang) as hybrid connectors between stat + opinion segments
        r"\b(stats?|numbers?|scoring)\s*(\+|AND)\s*(fan|opinions?|what\s+(do|does)\s+\w+\s+(think|say))\b",

        # NEW: Biographical queries should be HYBRID (stats + context)
        # Examples: "Who is LeBron?", "Tell me about Michael Jordan", "Who is Curry?"
        # Exclude when stat terms present (e.g., "efficient goal maker", "LeBron's stats")
        r"\b(who\s+(is|are)|tell\s+me\s+about|who.?s)\b(?!.*\b(stats?|statistics?|efficient|efficiency|scorer|scoring|averages?|numbers?|pct|percentage|goal\s+maker)\b).*\b(player|lebron|jordan|curry|jokic|embiid|luka|giannis|durant|harden|karim|magic|bird|kobe|wilt|chamberlain)\b",
    ]

    def __init__(self):
        """Initialize query classifier with compiled regex patterns."""
        self.statistical_regex = [re.compile(p, re.IGNORECASE) for p in self.STATISTICAL_PATTERNS]
        self.contextual_regex = [re.compile(p, re.IGNORECASE) for p in self.CONTEXTUAL_PATTERNS]
        self.hybrid_regex = [re.compile(p, re.IGNORECASE) for p in self.HYBRID_PATTERNS]

    @staticmethod
    def _is_definitional(query: str) -> bool:
        """Detect if query is asking for definition or explanation.

        Definitions should route to CONTEXTUAL even if they contain stat keywords.
        Examples: "Define TS%", "What is a triple-double?", "What does efficiency mean?"

        Note: Be careful not to catch explanatory "explain" in hybrid queries like
        "explain why they are so effective" - only catch definitional "explain".
        """
        q = query.strip().lower()

        definitional_patterns = [
            r"\b(define|definition)\b",  # Explicit define/definition
            r"\bwhat\s+(is|does|means?|do)\b\s+[a-z]{0,20}(\s+[a-z]{0,20})?$",  # "What is X?" - only at end
            r"\b(what\s+is\s+a)\b",  # "what is a triple-double"
            r"\b(meaning\s+of|refers\s+to|what.*refers?)",  # Reference questions
            r"\bexplain\b\s+(the\s+)?(definition|meaning|concept|difference)",  # Definitional explain only
        ]

        return any(re.search(p, q) for p in definitional_patterns)

    @staticmethod
    def _has_glossary_term(query: str) -> bool:
        """Check if query references a basketball glossary term.

        Glossary terms are definitional/reference content, should route to CONTEXTUAL.
        Examples: "What is a triple-double?", "Explain pick and roll", "First option meaning"
        """
        q = query.lower()

        # Check for glossary terms
        for term in BASKETBALL_GLOSSARY_TERMS:
            # Use word boundaries to avoid false matches
            if re.search(rf"\b{re.escape(term)}\b", q):
                return True

        return False

    @staticmethod
    def _is_greeting(query: str) -> bool:
        """Detect if query is a simple greeting/non-question.

        Greetings should NOT be processed through RAG search.
        Examples: "hi", "hello", "hey", "thanks", "goodbye"
        These should get simple responses, not database searches.
        """
        q = query.strip().lower()

        # Simple greetings (very short, single word or 2 words)
        greeting_patterns = [
            r"^(hi|hello|hey|howdy|greetings|sup|yo|thanks?|thank you|goodbye|bye|see you|farewell|welcome)$",
            r"^(hi|hello)\s+(there|there!|everyone|all|guys|friends?)$",
            r"^(how\s+(are|r)\s+you|how's\s+it\s+going|what's\s+up|wassup|watsup)$",
            r"^(good\s+(morning|afternoon|evening|night)|good\s+day)$",
        ]

        return any(re.search(p, q) for p in greeting_patterns)

    @staticmethod
    def _is_biographical(query: str) -> bool:
        """Detect if query is asking for player/team biographical information.

        Biographical queries should use HYBRID routing to get both:
        - SQL stats (player statistics)
        - Vector context (biographical narratives, player profiles)
        Then synthesize them together.

        Examples: "Who is LeBron?", "Tell me about Kobe", "Who is Michael Jordan?"
        These should route to HYBRID to synthesize stats + biographical context.
        """
        q = query.strip().lower()

        # Biographical query patterns
        biographical_patterns = [
            # "Who is [player]?" patterns
            r"\b(who is|who\?s|who are|tell me about|gimme the scoop on|info on|about)\b.*\b(player|athlete|star|team|squad|lebron|jordan|kobe|curry|james|durant|lakers|celtics|heat|warriors|mavericks|bulls|cavaliers)\b",
            # Capitalized name patterns (e.g., "Who is LeBron")
            r"\b(who is|who\?s|tell me about)\s+([A-Z][a-z]+(\s+[A-Z][a-z]+)*)\b",
            # "Background/history/biography of [player]" patterns
            r"\b(background|history|biography|bio|career|rise of|story of)\b.*\b(player|athlete|team)\b",
        ]

        return any(re.search(p, q, re.IGNORECASE) for p in biographical_patterns)

    @staticmethod
    def _estimate_question_complexity(query: str) -> int:
        """Estimate question complexity and return adaptive k value.

        Complexity levels:
        - Simple (k=3): Straightforward stats, single player/team lookups
        - Moderate (k=5): Multiple stats, top N queries, contextual analysis
        - Complex (k=7-9): Multi-step analysis, comparative analysis, strategic insights

        Args:
            query: User query string

        Returns:
            Adaptive k value (3, 5, 7, or 9)
        """
        query_lower = query.lower()
        word_count = len(query.split())

        # Calculate complexity score
        complexity_score = 0

        # Length indicators
        if word_count < 5:
            complexity_score += 1  # Very short = likely simple
        elif word_count > 15:
            complexity_score += 2  # Long = likely complex

        # Query type indicators (simple)
        simple_patterns = [
            "how many", "what is", "who is", "who scored", "who has",
            "count", "how much", "what does", "player stats",
        ]
        for pattern in simple_patterns:
            if pattern in query_lower:
                complexity_score += 0  # Simple queries don't add to score

        # Query type indicators (moderate)
        moderate_patterns = [
            "top ", "best ", "compare", "versus", "most", "least",
            "ranking", "average", "leaders", "leaders in",
        ]
        for pattern in moderate_patterns:
            if pattern in query_lower:
                complexity_score += 1

        # Query type indicators (complex)
        complex_patterns = [
            "explain", "analyze", "impact", "effect", "why", "how does",
            "strategy", "style", "strengths", "weakness", "capability",
            "tendency", "pattern", "role", "system", "philosophy",
            "efficient", "effectiveness", "defense", "offense",
        ]
        for pattern in complex_patterns:
            if pattern in query_lower:
                complexity_score += 2

        # Multiple data sources indicators
        if " and " in query_lower:
            complexity_score += 1
        if query_lower.count(",") > 0:
            complexity_score += 1

        # Determine k based on complexity score
        if complexity_score <= 1:
            return 3  # Simple: single player/stat lookup
        elif complexity_score <= 3:
            return 5  # Moderate: comparisons, multiple stats
        elif complexity_score <= 5:
            return 7  # Complex: multi-step analysis
        else:
            return 9  # Very complex: deep analytical queries

    def classify(self, query: str) -> ClassificationResult:
        """Classify query type based on patterns and return rich metadata.

        Returns a ClassificationResult bundling the routing decision with
        pre-computed metadata (is_biographical, is_greeting, complexity_k).
        This eliminates duplicate analysis calls in the chat pipeline.

        Args:
            query: User query string

        Returns:
            ClassificationResult with query_type, is_biographical, is_greeting, complexity_k
        """
        # ── Pre-compute metadata (all depend only on query text) ──────────
        is_greeting = self._is_greeting(query)
        is_biographical = self._is_biographical(query)
        complexity_k = self._estimate_question_complexity(query)

        def _result(qt: QueryType) -> ClassificationResult:
            return ClassificationResult(qt, is_biographical, is_greeting, complexity_k)

        query_normalized = query.strip().lower()

        # ── Normalize dashes: treat em-dash (—), en-dash (–), and hyphen (-) equivalently ──
        # Ensures two-part connector patterns work regardless of dash type
        query_normalized = query_normalized.replace("—", " - ").replace("–", " - ")
        # Collapse any resulting double spaces from replacement
        while "  " in query_normalized:
            query_normalized = query_normalized.replace("  ", " ")

        # ──── PHASE 14: Detect opinion/quality-based queries (subjective assessments) ────
        # These should be CONTEXTUAL even if they contain "who/which" + "most/best"
        # Examples: "most exciting", "best player" (bare), "most fun", "coolest moment"
        opinion_quality_patterns = [
            # ── Fix 6: Expanded opinion adjectives ───────────────────────
            # Opinion adjectives (exciting, fun, interesting, wild, etc.)
            r"\b(most|best|worst|greatest|coolest|most\s+\w+ful)\b.*\b(exciting|fun|interesting|dramatic|impressive|thrilling|boring|memorable|legendary|iconic|entertaining|wild|crazy|insane|clutch)\b",
            r"\b(which|who)\b.*\b(most|best|worst)\b.*\b(exciting|fun|interesting|impressive|thrilling|iconic|memorable|entertaining|wild|surprising|disappointing)\b",
            r"\b(most|best|worst)\s+(exciting|fun|interesting|impressive|thrilling|memorable|entertaining|dramatic|boring|wild|surprising|disappointing|clutch)\b",
            # Bare superlatives without stat qualifiers: "best player", "most exciting team"
            # Rule: (who|which) + (best|most) + (player|team|athlete|star) WITHOUT a stat term nearby
            r"\b(who|which)\b.*\b(best|most)\b.*\b(player|team|athlete|star)\b(?!.*\b(scorer|rebounder|passer|defender|shooter|blocker|handler)\b)",
            # "wild this year", "crazy season" (no stat intent)
            r"\b(wild|crazy|insane|nuts)\s+(this\s+year|this\s+season|right\s+now)\b",
        ]
        if any(re.search(p, query_normalized) for p in opinion_quality_patterns):
            logger.info(f"Query is opinion/quality-based (subjective assessment), routing to CONTEXTUAL")
            return _result(QueryType.CONTEXTUAL)

        # ── PHASE 17: Biographical queries always route to HYBRID ─────────────
        # Biographical queries (e.g., "Who is LeBron?", "Tell me about the Lakers")
        # always need BOTH SQL stats + vector context for a complete answer.
        # SQL provides raw numbers; vector provides narrative, opinions, background.
        if is_biographical:
            logger.info(f"Query is biographical (player/team info), routing to HYBRID")
            return _result(QueryType.HYBRID)

        # CRITICAL: Check definitional queries FIRST (override stat keywords)
        # Examples: "Define TS%", "What is a triple-double?" should be CONTEXTUAL not SQL
        if self._is_definitional(query):
            logger.info(f"Query is definitional, routing to CONTEXTUAL")
            return _result(QueryType.CONTEXTUAL)

        # ── Fix 1: Glossary check only for definitional context ──────────
        # Only route to CONTEXTUAL if the query is definitional (asking what a term means)
        # NOT if asking for data using that term (e.g., "highest true shooting percentage?")
        if self._has_glossary_term(query):
            # Check for statistical intent: numbers, "who has", "top", "highest", "how many"
            stat_intent = re.search(
                r"\b(who\s+has|top|highest|lowest|most|fewest|how\s+many|over|above|below|under"
                r"|find|list|show|get|compare|averaging|players?\s+averaging)\b|\d+",
                query_normalized,
            )
            if not stat_intent:
                logger.info(f"Query references glossary term (definitional), routing to CONTEXTUAL")
                return _result(QueryType.CONTEXTUAL)
            else:
                logger.info(f"Query has glossary term but also stat intent, continuing classification")

        # Check hybrid patterns first (most specific)
        hybrid_matches = sum(1 for pattern in self.hybrid_regex if pattern.search(query_normalized))
        if hybrid_matches > 0:
            logger.info(f"Query classified as HYBRID (matched {hybrid_matches} hybrid patterns)")
            return _result(QueryType.HYBRID)

        # Check statistical patterns
        stat_matches = sum(1 for pattern in self.statistical_regex if pattern.search(query_normalized))

        # Check contextual patterns
        context_matches = sum(1 for pattern in self.contextual_regex if pattern.search(query_normalized))

        # Auto-promote to HYBRID when both stat and context patterns match
        # Threshold: stat >= 2 AND context >= 1
        # HYBRID routing is safe (queries both sources), so over-promoting to
        # HYBRID is less harmful than misrouting to wrong single source
        if stat_matches >= 2 and context_matches >= 1:
            logger.info(
                f"Query classified as HYBRID (stat: {stat_matches}, context: {context_matches}) "
                "- both components detected"
            )
            return _result(QueryType.HYBRID)

        # Classify based on match counts
        if stat_matches > context_matches:
            logger.info(
                f"Query classified as STATISTICAL "
                f"(stat: {stat_matches}, context: {context_matches})"
            )
            return _result(QueryType.STATISTICAL)

        if context_matches > stat_matches:
            logger.info(
                f"Query classified as CONTEXTUAL "
                f"(stat: {stat_matches}, context: {context_matches})"
            )
            return _result(QueryType.CONTEXTUAL)

        # Default to contextual if no strong match or tie
        logger.info(
            f"Query classified as CONTEXTUAL (default) "
            f"(stat: {stat_matches}, context: {context_matches})"
        )
        return _result(QueryType.CONTEXTUAL)


# Example usage
if __name__ == "__main__":
    classifier = QueryClassifier()

    test_queries = [
        # Statistical
        ("Who are the top 5 scorers?", QueryType.STATISTICAL),
        ("What is LeBron's average points per game?", QueryType.STATISTICAL),
        ("Which team has the most wins?", QueryType.STATISTICAL),
        ("Show me players with over 100 three-pointers", QueryType.STATISTICAL),
        # Previously-failed statistical queries (should now classify correctly)
        ("Who is the MVP this season?", QueryType.STATISTICAL),
        ("Show me stats for the Warriors", QueryType.STATISTICAL),
        ("show me currys 3 pt pct", QueryType.STATISTICAL),
        ("whats the avg fg% in da league lol", QueryType.STATISTICAL),
        ("How does LeBron James compare?", QueryType.STATISTICAL),
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
        match = "OK" if result.query_type == expected else "FAIL"
        print(f"{match:4} {result.query_type.value:15} | Expected: {expected.value:15} | {query}")
        if result.query_type == expected:
            correct += 1

    print("=" * 80)
    print(f"Accuracy: {correct}/{len(test_queries)} ({100*correct/len(test_queries):.1f}%)")
