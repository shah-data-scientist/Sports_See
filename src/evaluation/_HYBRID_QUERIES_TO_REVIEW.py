"""
FILE: _HYBRID_QUERIES_TO_REVIEW.py
STATUS: Experimental
RESPONSIBILITY: 9 hybrid queries extracted from vector_test_cases.py for review
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

NOTES:
- These queries require BOTH SQL statistics AND vector context
- System should route them to hybrid (SQL + Vector)
- User to review and decide whether to add to hybrid_test_cases.py
- Classification done by _classify_vector_test_cases.py
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

# ALL 9 HYBRID QUERIES FROM VECTOR_TEST_CASES.PY
HYBRID_QUERIES_FROM_VECTOR_TESTS = [
    # COMPLEX category - All hybrid (8 queries)
    EvaluationTestCase(
        question=(
            "Compare the offensive efficiency of the top 3 scoring teams "
            "and explain what makes them effective."
        ),
        ground_truth=(
            "Comparing offensive efficiency requires analyzing multiple metrics "
            "including points per game, field goal percentage, 3-point percentage, "
            "and pace. The top scoring teams typically combine high shooting "
            "efficiency with fast pace of play."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Based on the Reddit discussions and stats, what are the most debated "
            "player comparisons this season and what do the numbers say?"
        ),
        ground_truth=(
            "Reddit NBA discussions frequently debate player comparisons. "
            "The statistics can provide objective context for these debates "
            "by comparing key metrics like PER, Win Shares, and box score stats."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Which players have shown the most improvement in their shooting "
            "percentages compared to earlier discussions about their performance?"
        ),
        ground_truth=(
            "Player improvement can be assessed by comparing current shooting "
            "percentages (FG%, 3PT%, FT%) against earlier discussions and "
            "historical performance data in the documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "What impact has the 3-point revolution had on the playing style "
            "of traditional centers according to the stats and discussions?"
        ),
        ground_truth=(
            "The 3-point revolution has led centers to expand their range. "
            "This can be seen in increased 3-point attempts by centers and "
            "Reddit discussions about the evolution of the center position."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "What trends in player salary vs performance efficiency can be "
            "identified from the data? Are the highest-paid players providing "
            "proportional value?"
        ),
        ground_truth=(
            "Salary-to-performance analysis requires cross-referencing salary data "
            "with efficiency metrics. Not all high-salary players provide "
            "proportional on-court value as measured by advanced stats."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Based on home vs away records, travel schedules, and Reddit fan "
            "discussions, which teams struggle the most on the road and why?"
        ),
        ground_truth=(
            "Road performance analysis combines win-loss records for away games, "
            "travel distances, and fan observations from Reddit. Teams from "
            "the West Coast often face more travel-related challenges."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Evaluate the trade deadline moves this season. Which trades have "
            "had the biggest positive and negative impacts on team performance "
            "according to pre and post-trade statistics?"
        ),
        ground_truth=(
            "Trade impact can be measured by comparing team statistics before "
            "and after trade deadline acquisitions. Reddit discussions provide "
            "qualitative context for the quantitative performance changes."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "How has the rise of analytics-driven coaching changed timeout "
            "usage and rotation patterns compared to what Reddit fans discuss?"
        ),
        ground_truth=(
            "Analytics-driven coaching has influenced timeout strategy and "
            "player rotation lengths. Reddit discussions often debate whether "
            "data-driven decisions conflict with traditional coaching wisdom."
        ),
        category=TestCategory.COMPLEX,
    ),

    # NOISY category - Hybrid but out-of-scope (1 query)
    EvaluationTestCase(
        question="What is the best strategy for winning in NBA 2K video game?",
        ground_truth=(
            "This question is about a video game, not real NBA data. "
            "The knowledge base contains real NBA statistics and discussions, "
            "not video game strategies."
        ),
        category=TestCategory.NOISY,
    ),
]

# Current behavior:
# - Classification detects hybrid keywords ("based on", "explain", "according to", etc.)
# - System should route to hybrid (SQL + Vector) for comprehensive answers
#
# Recommendation: Review these queries and add relevant ones to hybrid_test_cases.py
