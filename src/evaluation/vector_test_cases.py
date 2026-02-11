"""
FILE: vector_test_cases.py
STATUS: Active
RESPONSIBILITY: Pure vector test cases for Reddit discussions, glossary, and contextual queries
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

NOTES:
- Contains 50+ test cases for PURE VECTOR retrieval (no SQL needed)
- Based on actual Reddit content from 4 PDFs in vector store
- Includes boosting logic tests (upvotes, NBA official, post engagement)
- Follows evaluation best practices: variety, edge cases, adversarial inputs
- Ground truth established from actual vector DB contents
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

# ==============================================================================
# REDDIT DISCUSSION QUERIES (Based on actual 4 Reddit posts in vector store)
# ==============================================================================
# Reddit 1: "Who are teams in the playoffs that have impressed you?" (31 upvotes)
# Reddit 2: "How is it that the two best teams in the playoffs..." (457 upvotes)
# Reddit 3: "Reggie Miller is the most efficient first option..." (1300 upvotes, 11515 max comment upvotes)
# Reddit 4: "Which NBA team did not have home court advantage..." (272 upvotes)
# ==============================================================================

EVALUATION_TEST_CASES: list[EvaluationTestCase] = [
    # ==========================================================================
    # REDDIT OPINION & DISCUSSION QUERIES (15 cases)
    # ==========================================================================
    EvaluationTestCase(
        question="What do Reddit users think about teams that have impressed in the playoffs?",
        ground_truth=(
            "Reddit post discusses which playoff teams have impressed fans. "
            "Comments should contain user opinions about surprising or impressive playoff performances."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="According to fan discussions, which teams exceeded expectations in the playoffs?",
        ground_truth=(
            "Related to Reddit post about impressive playoff teams. "
            "Retrieves user opinions and discussions about underdog or surprise playoff performers."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What are the most popular opinions about the two best playoff teams?",
        ground_truth=(
            "Reddit post asks 'How is it that the two best teams in the playoffs...' "
            "Comments discuss why top teams perform well or unexpected aspects of their success."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do fans debate about Reggie Miller's efficiency?",
        ground_truth=(
            "Reddit post titled 'Reggie Miller is the most efficient first option in NBA playoffs' "
            "with 1300 upvotes. Comments debate his playoff efficiency and historical comparisons."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Is Reggie Miller considered an efficient playoff scorer according to Reddit?",
        ground_truth=(
            "High-engagement Reddit post (1300 upvotes, 11515 comment upvotes) discusses "
            "Reggie Miller as the most efficient first option in NBA playoff history. "
            "Should retrieve this discussion with high relevance due to boosting."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which NBA teams didn't have home court advantage in finals according to discussions?",
        ground_truth=(
            "Reddit post asks 'Which NBA team did not have home court advantage until the NBA Finals?' "
            "Comments discuss historical instances of teams reaching finals without home court."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do fans think about home court advantage in the playoffs?",
        ground_truth=(
            "Related to Reddit discussion about teams without home court advantage. "
            "Comments may discuss importance of home court or historical examples."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What are the most upvoted opinions about playoff performance?",
        ground_truth=(
            "Should retrieve comments with high upvote counts across Reddit posts. "
            "Boosting logic should prioritize highly-upvoted comments about playoff performance."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="According to basketball discussions, what makes a player efficient in playoffs?",
        ground_truth=(
            "Reddit discussions mention efficiency in context of Reggie Miller and playoff scoring. "
            "Should retrieve contextual discussion about efficiency metrics and playoff performance."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What are the common themes in NBA Reddit discussions about playoffs?",
        ground_truth=(
            "Across 4 Reddit posts, common themes include: impressive teams, top teams' performance, "
            "efficiency of scorers, and home court advantage. Should synthesize across multiple posts."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Do fans debate about historical playoff performances?",
        ground_truth=(
            "Reddit posts contain debates about Reggie Miller's efficiency and historical home court scenarios. "
            "Should retrieve opinionated discussions about past playoff performances."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What are controversial takes about playoff basketball?",
        ground_truth=(
            "Reddit discussions may contain contrarian or debated opinions. "
            "Should retrieve comments that challenge conventional wisdom or spark debate."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What insights do basketball fans share about playoff strategies?",
        ground_truth=(
            "Comments across Reddit posts may discuss playoff strategies, adjustments, "
            "or what makes teams successful in postseason play."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Which playoff topics generate the most discussion on Reddit?",
        ground_truth=(
            "Post about Reggie Miller has 1300 upvotes (highest engagement), "
            "followed by 'two best teams' (457), home court (272), and impressive teams (31). "
            "Boosting should prioritize high-engagement topics."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What do NBA fans consider surprising about playoff results?",
        ground_truth=(
            "Reddit post 'Who are teams that have impressed you' and 'two best teams' "
            "discuss surprising or unexpected playoff outcomes."
        ),
        category=TestCategory.SIMPLE,
    ),

    # ==========================================================================
    # BOOSTING LOGIC TESTS (10 cases)
    # Test metadata-based re-ranking: upvotes, NBA official, post engagement
    # ==========================================================================
    EvaluationTestCase(
        question="Tell me about the most discussed playoff efficiency topic.",
        ground_truth=(
            "Reddit post about Reggie Miller's efficiency has highest engagement (1300 post upvotes, "
            "11515 max comment upvotes). Boosting should rank this post's content highest."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What's the most popular Reddit discussion about playoffs?",
        ground_truth=(
            "Post engagement boost (0-1%) should prioritize Reggie Miller post (1300 upvotes) "
            "over others (457, 272, 31 upvotes). Tests post-level boosting."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Show me highly upvoted comments about basketball.",
        ground_truth=(
            "Comment upvote boost (0-2% relative within post) should prioritize comments "
            "with high upvotes within each post. Tests comment-level boosting."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What are the most credible sources in basketball discussions?",
        ground_truth=(
            "If NBA official accounts are detected (Lakers account in data), "
            "their comments should get 2% boost. Tests is_nba_official boosting."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do authoritative voices say about playoff basketball?",
        ground_truth=(
            "Should prioritize NBA official accounts or highly-upvoted comments "
            "as more authoritative. Tests combined boosting logic."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Compare opinions on efficiency from high-engagement vs low-engagement posts.",
        ground_truth=(
            "Reggie Miller post (1300 upvotes) vs impressive teams post (31 upvotes). "
            "Higher engagement post should rank higher due to post boost."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What are the consensus views on playoff performance?",
        ground_truth=(
            "Highly-upvoted comments represent consensus. "
            "Boosting should surface popular opinions over niche takes."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Find the most engaged discussion about NBA history.",
        ground_truth=(
            "Reggie Miller post (historical playoff efficiency) has highest engagement. "
            "Tests post-level boosting for historical topics."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What do the top comments say about playoff success?",
        ground_truth=(
            "Should retrieve comments with highest upvotes across all posts. "
            "Tests relative comment boosting within each post."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Show me verified or official perspectives on basketball.",
        ground_truth=(
            "NBA official accounts (is_nba_official=1) should rank highest. "
            "Tests NBA official 2% boost."
        ),
        category=TestCategory.SIMPLE,
    ),

    # ==========================================================================
    # GLOSSARY / TERMINOLOGY QUERIES (8 cases)
    # Based on basketball dictionary/glossary in vector store
    # ==========================================================================
    EvaluationTestCase(
        question="What is a pick and roll?",
        ground_truth=(
            "Basketball glossary should define pick and roll as an offensive play "
            "where a player sets a screen (pick) and moves toward the basket (roll)."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Explain what PER means in basketball.",
        ground_truth=(
            "PER (Player Efficiency Rating) is an advanced statistic. "
            "Glossary should provide definition if available."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What does zone defense mean?",
        ground_truth=(
            "Zone defense is a defensive strategy where players guard areas rather than specific opponents. "
            "Glossary should define this term."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Define true shooting percentage.",
        ground_truth=(
            "True Shooting Percentage (TS%) accounts for 2-pointers, 3-pointers, and free throws. "
            "Glossary should provide formula or explanation."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What is a triple-double?",
        ground_truth=(
            "Triple-double means double-digit totals in three statistical categories "
            "(e.g., points, rebounds, assists). Glossary should define."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Explain the difference between man-to-man and zone defense.",
        ground_truth=(
            "Man-to-man assigns each defender to a specific opponent, "
            "while zone defense assigns defenders to court areas. Glossary should explain."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What basketball terms are important for understanding efficiency?",
        ground_truth=(
            "Terms like TS%, eFG%, PER, and usage rate relate to efficiency. "
            "Glossary may define these advanced metrics."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What does 'first option' mean in basketball?",
        ground_truth=(
            "First option refers to a team's primary scorer or go-to offensive player. "
            "Context from Reggie Miller discussion may clarify this term."
        ),
        category=TestCategory.SIMPLE,
    ),

    # ==========================================================================
    # OUT-OF-SCOPE / TRICK QUESTIONS (12 cases)
    # Test system's ability to recognize irrelevant queries
    # ==========================================================================
    EvaluationTestCase(
        question="What is the weather forecast for Los Angeles tomorrow?",
        ground_truth=(
            "Weather is completely out of scope. Knowledge base only contains "
            "NBA statistics, Reddit discussions, and basketball glossary."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="How do I bake a chocolate cake?",
        ground_truth=(
            "Cooking is out of scope. System should recognize this is unrelated to NBA/basketball."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Tell me about the latest political election results.",
        ground_truth=(
            "Politics is out of scope. Knowledge base contains only NBA-related content."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="What is the stock price of Apple Inc.?",
        ground_truth=(
            "Finance/stocks are out of scope. System should decline or state no information available."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Best strategy for winning in NBA 2K24 video game?",
        ground_truth=(
            "Video game strategies are out of scope. Knowledge base covers real NBA, not video games."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="How to fix my computer's blue screen error?",
        ground_truth=(
            "Tech support is out of scope. System should recognize this is unrelated to basketball."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="What are the best restaurants in New York City?",
        ground_truth=(
            "Restaurant recommendations are out of scope. No food/dining content in knowledge base."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="?",
        ground_truth=(
            "Single punctuation mark is not a meaningful query. "
            "System should handle gracefully (ask for clarification or minimal response)."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question=" ",
        ground_truth=(
            "Single space is minimal input. System should handle edge case gracefully."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="asdfghjkl qwerty12345",
        ground_truth=(
            "Random keyboard mashing is not meaningful. "
            "System should recognize lack of coherent query intent."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Give me a 10000 word essay on the history of the universe.",
        ground_truth=(
            "Unreasonably long request about out-of-scope topic (cosmology). "
            "System should not attempt to generate excessively long responses."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Translate 'hello' to 50 different languages.",
        ground_truth=(
            "Translation service is out of scope. Knowledge base is NBA-specific, not a translation tool."
        ),
        category=TestCategory.NOISY,
    ),

    # ==========================================================================
    # ADVERSARIAL / SECURITY TESTS (5 cases)
    # Test input sanitization and security
    # ==========================================================================
    EvaluationTestCase(
        question="<script>alert('XSS')</script> Who won the MVP?",
        ground_truth=(
            "System should sanitize HTML/JavaScript injection attempts. "
            "Should safely extract the legitimate query (MVP winner) if possible."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="'; DROP TABLE players; --",
        ground_truth=(
            "SQL injection attempt. System should sanitize input and not execute SQL commands."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="../../../etc/passwd",
        ground_truth=(
            "Path traversal attempt. System should sanitize and not access file system."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="{{7*7}} ${7*7} <%= 7*7 %>",
        ground_truth=(
            "Template injection attempts. System should treat as literal text, not execute code."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="A" * 10000,
        ground_truth=(
            "Excessively long input (10,000 characters). "
            "System should handle gracefully, possibly truncate or reject."
        ),
        category=TestCategory.NOISY,
    ),

    # ==========================================================================
    # CONVERSATIONAL / MULTI-STEP QUERIES (12 cases)
    # Test context maintenance across turns
    # ==========================================================================
    # Conversation Thread 1: Lakers
    EvaluationTestCase(
        question="What do fans say about the Lakers?",
        ground_truth=(
            "Reddit discussions may mention Lakers in context of impressive teams or playoff performance. "
            "Should retrieve relevant comments if Lakers are discussed."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What are their biggest strengths?",
        ground_truth=(
            "Follow-up referencing 'their' = Lakers from previous question. "
            "Should maintain context and retrieve Lakers-specific strengths from discussions."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="And their weaknesses?",
        ground_truth=(
            "Second follow-up still referencing Lakers. "
            "Should maintain conversation context across multiple turns."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # Conversation Thread 2: Playoff teams
    EvaluationTestCase(
        question="Tell me about playoff teams that surprised people.",
        ground_truth=(
            "Reddit post 'Who are teams in the playoffs that have impressed you?' "
            "discusses surprising or impressive playoff teams."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Why were they surprising?",
        ground_truth=(
            "Follow-up asking why those teams (from previous answer) were surprising. "
            "Requires maintaining context about which teams were mentioned."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Compare them to the top-seeded teams.",
        ground_truth=(
            "Third-level follow-up comparing surprising teams to top seeds. "
            "Requires maintaining full conversation context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # Conversation Thread 3: Efficiency discussion
    EvaluationTestCase(
        question="What makes a player efficient in the playoffs?",
        ground_truth=(
            "General question about playoff efficiency. "
            "Reddit post about Reggie Miller's efficiency should be relevant."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Who is the most efficient according to fans?",
        ground_truth=(
            "Follow-up asking for specific player. Reggie Miller discussion (1300 upvotes) "
            "should be highly relevant. Tests boosting + context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What do people debate about his efficiency?",
        ground_truth=(
            "Second follow-up referencing 'his' = most efficient player from previous answer. "
            "Should retrieve debate/discussion from comments."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # Conversation Thread 4: Topic switching
    EvaluationTestCase(
        question="Tell me about home court advantage in playoffs.",
        ground_truth=(
            "Reddit post 'Which NBA team did not have home court advantage until NBA Finals' "
            "discusses home court scenarios."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Going back to efficiency, who else is considered efficient?",
        ground_truth=(
            "Switches topic back to efficiency (from earlier conversation). "
            "'Going back to' signals topic change. Should retrieve efficiency discussions."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Returning to home court, which teams historically lacked it?",
        ground_truth=(
            "Another topic switch back to home court. Should handle non-linear conversation flow."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),

    # ==========================================================================
    # NOISY / INFORMAL LANGUAGE QUERIES (8 cases)
    # Test robustness to typos, slang, abbreviations
    # ==========================================================================
    EvaluationTestCase(
        question="whos da best playa in playoffs acording 2 reddit",
        ground_truth=(
            "Despite typos and text-speak, should understand query asks about "
            "best playoff player according to Reddit discussions."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="reggie milr effishency debat",
        ground_truth=(
            "Heavy typos but should recognize Reggie Miller efficiency debate topic "
            "and retrieve high-engagement Reddit post."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="lmao bro playoff teams are wild this year fr fr",
        ground_truth=(
            "Informal slang but expresses opinion about playoff teams. "
            "Should relate to discussions about impressive or surprising teams."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="imho home court dont matter much tbh",
        ground_truth=(
            "Abbreviations (imho=in my humble opinion, tbh=to be honest) "
            "expressing view on home court advantage. Should retrieve related discussions."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="playoff playoff playoff teams teams impressive impressive",
        ground_truth=(
            "Keyword stuffing/repetition. Should recognize query about impressive playoff teams "
            "despite poor formatting."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="reddit nba thoughts???",
        ground_truth=(
            "Extremely vague query. Should either ask for clarification or provide "
            "general NBA discussion content from Reddit."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="yo what ppl saying bout top teams",
        ground_truth=(
            "Casual slang asking about top teams discussions. "
            "Should retrieve Reddit post about 'two best teams in playoffs'."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="nba",
        ground_truth=(
            "Single word, extremely vague. Should either request clarification "
            "or provide general NBA-related content."
        ),
        category=TestCategory.NOISY,
    ),

    # ==========================================================================
    # COMPLEX ANALYTICAL QUERIES (5 cases)
    # Test retrieval for multi-faceted analytical questions
    # ==========================================================================
    EvaluationTestCase(
        question="Analyze the evolution of playoff strategies based on fan discussions.",
        ground_truth=(
            "Complex query requiring synthesis across multiple Reddit discussions. "
            "Should retrieve comments about strategies, adjustments, and tactical evolution."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What patterns emerge from Reddit debates about playoff performance?",
        ground_truth=(
            "Meta-analysis of discussion patterns. Should identify recurring themes "
            "like efficiency, home court, surprising teams across multiple posts."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="How do fan perceptions of efficiency differ from statistical measures?",
        ground_truth=(
            "Requires contrasting Reddit opinions (qualitative) with stats (quantitative). "
            "Should retrieve efficiency discussions and note perception vs reality."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="What controversies exist in evaluating playoff success?",
        ground_truth=(
            "Should identify debated topics across Reddit posts: efficiency metrics, "
            "home court importance, underdog performance, etc."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Synthesize fan wisdom about what makes teams succeed in playoffs.",
        ground_truth=(
            "High-level synthesis requiring retrieval from multiple posts and comments. "
            "Should combine insights about impressive teams, efficiency, strategies."
        ),
        category=TestCategory.COMPLEX,
    ),
]


def get_test_case_statistics() -> dict:
    """Compute statistics about the evaluation test cases.

    Returns:
        Dictionary with category counts, total, and distribution percentages.
    """
    from collections import Counter

    counts = Counter(tc.category for tc in EVALUATION_TEST_CASES)
    total = len(EVALUATION_TEST_CASES)

    return {
        "total": total,
        "by_category": {cat.value: counts.get(cat, 0) for cat in TestCategory},
        "distribution": {
            cat.value: round(counts.get(cat, 0) / total * 100, 1) if total else 0
            for cat in TestCategory
        },
    }


def print_test_case_statistics() -> None:
    """Print formatted test case statistics to stdout."""
    stats = get_test_case_statistics()

    print("\n" + "=" * 50)
    print(f"  PURE VECTOR TEST CASES: {stats['total']} total")
    print("=" * 50)
    print(f"  {'Category':<20} {'Count':>6} {'Distribution':>14}")
    print("  " + "-" * 44)
    for cat in TestCategory:
        count = stats["by_category"][cat.value]
        pct = stats["distribution"][cat.value]
        print(f"  {cat.value:<20} {count:>6} {pct:>12.1f}%")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    print_test_case_statistics()
