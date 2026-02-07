"""
FILE: hybrid_test_cases.py
STATUS: Active
RESPONSIBILITY: Extended test cases for Phase 3 - Hybrid SQL+Vector scenarios
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

# Extended test cases focusing on hybrid scenarios (SQL + Vector)
HYBRID_TEST_CASES: list[EvaluationTestCase] = [
    # ========================================================================
    # SIMPLE: Statistical queries requiring SQL database
    # ========================================================================
    EvaluationTestCase(
        question="Who are the top 5 scorers this season?",
        ground_truth=(
            "The top 5 scorers can be found by querying the player statistics "
            "database, sorting by points (PTS) in descending order and taking "
            "the first 5 results."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What is Nikola Jokic's average points per game?",
        ground_truth=(
            "Nikola Jokic's PPG average is stored in the player_stats table "
            "under the 'pts' column divided by games played."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which player has the highest true shooting percentage?",
        ground_truth=(
            "True shooting percentage (TS%) is an advanced metric in the "
            "player statistics. Sorting by ts_pct descending gives the leader."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="How many players average more than 20 points per game?",
        ground_truth=(
            "This requires counting players in the database where pts > 20. "
            "The query filters player_stats by the points column."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What is the average three-point percentage across all players?",
        ground_truth=(
            "The average 3PT% is calculated by taking the mean of the three_pct "
            "column across all player records in the stats table."
        ),
        category=TestCategory.SIMPLE,
    ),
    # ========================================================================
    # COMPLEX: Hybrid queries requiring both SQL and contextual knowledge
    # ========================================================================
    EvaluationTestCase(
        question=(
            "Compare Nikola Jokic and Joel Embiid's statistics this season "
            "and explain which one is more valuable to their team based on "
            "advanced metrics and their playing style."
        ),
        ground_truth=(
            "This requires retrieving both players' statistics from the database "
            "(PTS, REB, AST, TS%, PER, etc.) and combining with contextual "
            "knowledge about their playing styles from documents/discussions. "
            "Jokic excels in playmaking while Embiid dominates in scoring."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Who are the most efficient scorers (high TS%) and why are they "
            "so effective according to basketball analysis?"
        ),
        ground_truth=(
            "This combines SQL query for TS% leaders with contextual explanation "
            "of what makes them effective (shot selection, free throw rate, "
            "3-point shooting, etc.) from basketball analysis documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Based on the statistics, which teams have the best offensive rating "
            "and what strategies do they use according to NBA discussions?"
        ),
        ground_truth=(
            "Requires querying team statistics for offensive rating (ORtg) and "
            "then referencing discussions about their offensive systems (pace, "
            "ball movement, 3-point emphasis, etc.)."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Compare the advanced stats (PER, Win Shares, VORP) of the top MVP "
            "candidates and explain what these metrics reveal about their impact."
        ),
        ground_truth=(
            "This needs SQL to retrieve advanced metrics for MVP candidates, "
            "plus contextual knowledge explaining what each metric measures and "
            "how it reflects player value."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Which players have improved their shooting percentages the most "
            "compared to what was discussed earlier in the season?"
        ),
        ground_truth=(
            "Requires current shooting stats from database and historical "
            "context from season discussions to identify improvement trends."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Analyze the correlation between assist-to-turnover ratio and team "
            "wins. Which high-assist players are most valuable?"
        ),
        ground_truth=(
            "Needs SQL for AST/TO ratios and team records, combined with "
            "analytical discussion of why this metric matters for winning."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Who are the most efficient three-point shooters (volume + percentage) "
            "and how has the 3-point revolution changed the game?"
        ),
        ground_truth=(
            "Combines SQL query for 3PM and 3P% with historical/strategic "
            "context about the evolution of three-point shooting in modern NBA."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Based on defensive rating and steals/blocks stats, who are the "
            "best defenders and what makes elite defense according to experts?"
        ),
        ground_truth=(
            "SQL for defensive metrics (DRtg, STL, BLK) plus expert analysis "
            "on defensive principles, positioning, and impact beyond stats."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Which rookies have the best statistical start to their career, "
            "and how do they compare to recent Rookie of the Year winners?"
        ),
        ground_truth=(
            "Requires filtering player stats by rookie status and comparing "
            "to historical ROY performance data from discussions/documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Identify players with high usage rate but low efficiency. Why "
            "might teams still rely on them based on game context?"
        ),
        ground_truth=(
            "SQL for USG% and efficiency metrics, combined with strategic "
            "reasoning about clutch performance, defensive attention, etc."
        ),
        category=TestCategory.COMPLEX,
    ),
    # ========================================================================
    # COMPLEX: Statistical + Strategic Analysis
    # ========================================================================
    EvaluationTestCase(
        question=(
            "Which teams have the best offensive rebounding percentage and "
            "how does this impact their second-chance scoring?"
        ),
        ground_truth=(
            "Team OREB% from stats combined with analysis of how offensive "
            "rebounding creates additional possessions and scoring opportunities."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Compare the pace of play statistics for top teams. How does "
            "pace affect their offensive and defensive efficiency?"
        ),
        ground_truth=(
            "SQL for PACE, ORtg, DRtg metrics plus strategic discussion of "
            "how tempo impacts game style and success."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Who are the best free throw shooters by percentage, and why "
            "is free throw shooting so important in close games?"
        ),
        ground_truth=(
            "FT% leaders from database combined with clutch performance "
            "analysis and late-game strategy discussions."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Based on plus-minus statistics, which players have the biggest "
            "impact on their team's performance when they're on the court?"
        ),
        ground_truth=(
            "Plus-minus data from stats table, with context about what this "
            "metric captures and its limitations as discussed by analysts."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Which young players (under 25) have the best advanced stats, and "
            "what does this suggest about the future of the league?"
        ),
        ground_truth=(
            "Age-filtered advanced stats query plus trend analysis about "
            "youth movement and skill development in modern NBA."
        ),
        category=TestCategory.COMPLEX,
    ),
    # ========================================================================
    # NOISY: Testing robustness with hybrid intent
    # ========================================================================
    EvaluationTestCase(
        question="top scorres and why they good",
        ground_truth=(
            "Despite typos, should retrieve top scorers from stats and explain "
            "what makes them effective (shot selection, efficiency, etc.)."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="jokic stats vs embiid who better???",
        ground_truth=(
            "Informal hybrid query: retrieve both players' stats and provide "
            "comparative analysis despite casual language."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="gimme the best 3pt shooters and tell me how they do it",
        ground_truth=(
            "Casual request for 3PT% leaders plus shooting technique explanation "
            "from basketball analysis."
        ),
        category=TestCategory.NOISY,
    ),
    # ========================================================================
    # CONVERSATIONAL: Multi-turn hybrid scenarios
    # ========================================================================
    EvaluationTestCase(
        question="Who is the league's leading scorer?",
        ground_truth=(
            "Query player stats for highest PPG. This starts a conversational "
            "thread about the scoring leader."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What are his advanced stats?",
        ground_truth=(
            "Follow-up requiring context from previous answer to retrieve "
            "PER, WS, VORP, etc. for the scoring leader."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="How does his efficiency compare to other top scorers?",
        ground_truth=(
            "Requires comparing the leading scorer's TS% against other high-PPG "
            "players, maintaining conversation context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Show me the best rebounders.",
        ground_truth=(
            "New conversational thread: query for top players by rebounds (REB) "
            "or rebounds per game."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What impact do they have beyond the stats?",
        ground_truth=(
            "Follow-up asking for contextual analysis of top rebounders' value "
            "beyond numbers (positioning, boxing out, etc.)."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
]


def get_hybrid_test_statistics() -> dict:
    """Get statistics about hybrid test cases.

    Returns:
        Dictionary with counts and distribution.
    """
    from collections import Counter

    counts = Counter(tc.category for tc in HYBRID_TEST_CASES)
    total = len(HYBRID_TEST_CASES)

    return {
        "total": total,
        "by_category": {cat.value: counts.get(cat, 0) for cat in TestCategory},
        "distribution": {
            cat.value: round(counts.get(cat, 0) / total * 100, 1) if total else 0
            for cat in TestCategory
        },
    }


def print_hybrid_test_statistics() -> None:
    """Print hybrid test case statistics."""
    stats = get_hybrid_test_statistics()

    print("\n" + "=" * 50)
    print(f"  HYBRID TEST CASES: {stats['total']} total")
    print("=" * 50)
    print(f"  {'Category':<20} {'Count':>6} {'Distribution':>14}")
    print("  " + "-" * 44)
    for cat in TestCategory:
        count = stats["by_category"][cat.value]
        pct = stats["distribution"][cat.value]
        print(f"  {cat.value:<20} {count:>6} {pct:>12.1f}%")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    print_hybrid_test_statistics()
