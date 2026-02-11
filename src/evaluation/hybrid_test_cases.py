"""
FILE: hybrid_test_cases.py
STATUS: Active
RESPONSIBILITY: Hybrid test cases requiring both SQL and Vector search (curated)
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu

IMPROVEMENTS FROM ORIGINAL:
- Reduced from 23 to 18 high-quality cases
- Removed duplicate/similar queries (multiple MVP comparisons, redundant efficiency queries)
- Enhanced variety: team-level analysis, follow-up queries, correlation studies
- Strengthened hybrid nature: all queries explicitly require BOTH SQL AND context
- Better category distribution: Complex (14), Noisy (4)
- Added multi-player and team comparisons
- More conversational follow-ups
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

# ========================================================================
# TRUE HYBRID TEST CASES (CURATED)
# Each query REQUIRES both SQL statistics AND contextual analysis
# ========================================================================

HYBRID_TEST_CASES: list[EvaluationTestCase] = [
    # ----------------------------------------------------------------
    # STATISTICAL COMPARISON + STYLE ANALYSIS
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Compare Nikola Jokic and Joel Embiid's statistics this season and explain which one is more valuable to their team based on advanced metrics and their playing style."
        ),
        ground_truth=(
            "This requires retrieving both players' statistics from the database (PTS, REB, AST, TS%, PER, etc.) and combining with contextual knowledge about their playing styles from documents/discussions. Jokic excels in playmaking while Embiid dominates in scoring."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Compare Giannis Antetokounmpo and Kevin Durant's scoring efficiency. How do their playing styles differ strategically?"
        ),
        ground_truth=(
            "SQL for PTS, TS%, FG% for both players, combined with strategic analysis of their offensive approaches (paint dominance vs perimeter versatility)."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # EFFICIENCY LEADERS + EXPLANATION
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Who are the most efficient scorers (high TS%) and why are they so effective according to basketball analysis?"
        ),
        ground_truth=(
            "This combines SQL query for TS% leaders with contextual explanation of what makes them effective (shot selection, free throw rate, 3-point shooting, etc.) from basketball analysis documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Who are the most efficient three-point shooters (volume + percentage) and how has the 3-point revolution changed the game?"
        ),
        ground_truth=(
            "Combines SQL query for 3PM and 3P% with historical/strategic context about the evolution of three-point shooting in modern NBA."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # DEFENSIVE ANALYSIS + CONTEXT
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Based on defensive rating and steals/blocks stats, who are the best defenders and what makes elite defense according to experts?"
        ),
        ground_truth=(
            "SQL for defensive metrics (DRtg, STL, BLK) plus expert analysis on defensive principles, positioning, and impact beyond stats."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "What are the common characteristics of teams with top defensive ratings according to defensive schemes discussed in NBA analysis?"
        ),
        ground_truth=(
            "Team DRtg from stats plus document retrieval about defensive systems (switching, drop coverage, help defense, etc.)."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # TEAM-LEVEL ANALYSIS
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Based on the statistics, which teams have the best offensive rating and what strategies do they use according to NBA discussions?"
        ),
        ground_truth=(
            "Requires querying team statistics for offensive rating (ORtg) and then referencing discussions about their offensive systems (pace, ball movement, 3-point emphasis, etc.)."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Compare the pace of play statistics for top teams. How does pace affect their offensive and defensive efficiency?"
        ),
        ground_truth=(
            "SQL for PACE, ORtg, DRtg metrics plus strategic discussion of how tempo impacts game style and success."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Analyze the relationship between three-point attempt volume and offensive efficiency for modern NBA teams."
        ),
        ground_truth=(
            "Stats on 3PA and ORtg, combined with analytical discussion of Moreyball and spacing in contemporary basketball."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # CORRELATION & TREND ANALYSIS
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Analyze the correlation between assist-to-turnover ratio and team wins. Which high-assist players are most valuable?"
        ),
        ground_truth=(
            "Needs SQL for AST/TO ratios and team records, combined with analytical discussion of why this metric matters for winning."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Which teams have the best offensive rebounding percentage and how does this impact their second-chance scoring?"
        ),
        ground_truth=(
            "Team OREB% from stats combined with analysis of how offensive rebounding creates additional possessions and scoring opportunities."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # SPECIAL POPULATIONS + CONTEXT
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Which rookies have the best statistical start to their career, and how do they compare to recent Rookie of the Year winners?"
        ),
        ground_truth=(
            "Requires filtering player stats by rookie status and comparing to historical ROY performance data from discussions/documents."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "Which young players (under 25) have the best advanced stats, and what does this suggest about the future of the league?"
        ),
        ground_truth=(
            "Age-filtered advanced stats query plus trend analysis about youth movement and skill development in modern NBA."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # CONTRARIAN / INEFFICIENCY ANALYSIS
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "Identify players with high usage rate but low efficiency. Why might teams still rely on them based on game context?"
        ),
        ground_truth=(
            "SQL for USG% and efficiency metrics, combined with strategic reasoning about clutch performance, defensive attention, creation for others, etc."
        ),
        category=TestCategory.COMPLEX,
    ),

    # ----------------------------------------------------------------
    # NOISY / CASUAL HYBRID QUERIES
    # ----------------------------------------------------------------
    EvaluationTestCase(
        question=(
            "top scorres and why they good"
        ),
        ground_truth=(
            "Despite typos, should retrieve top scorers from stats and explain what makes them effective (shot selection, efficiency, versatility, etc.)."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question=(
            "jokic stats vs embiid who better???"
        ),
        ground_truth=(
            "Informal hybrid query: retrieve both players' stats and provide comparative analysis despite casual language."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question=(
            "gimme the best 3pt shooters and tell me how they do it"
        ),
        ground_truth=(
            "Casual request for 3PT% leaders plus shooting technique/mechanics explanation from basketball analysis."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question=(
            "which teams play fastest and does that help them win more games?"
        ),
        ground_truth=(
            "Informal query for PACE stats and win correlation, plus strategic context about fast-break vs half-court effectiveness."
        ),
        category=TestCategory.NOISY,
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
