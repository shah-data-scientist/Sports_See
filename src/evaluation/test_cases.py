"""
FILE: test_cases.py
STATUS: Active
RESPONSIBILITY: NBA business question test cases for RAGAS evaluation
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

EVALUATION_TEST_CASES: list[EvaluationTestCase] = [
    # ========================================================================
    # SIMPLE: Direct factual questions (single-hop retrieval)
    # ========================================================================
    EvaluationTestCase(
        question="Which player has the best 3-point percentage over the last 5 games?",
        ground_truth=(
            "The player with the best 3-point percentage over the last 5 games "
            "can be found in the regular NBA statistics. This requires checking "
            "the 3PT% column for recent game logs."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What are LeBron James' average points per game this season?",
        ground_truth=(
            "LeBron James' season averages can be found in the NBA regular season "
            "statistics table, showing his points per game average."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which team leads the league in rebounds per game?",
        ground_truth=(
            "The team leading in rebounds per game is determined by the team "
            "statistics in the regular NBA data, sorting by RPG column."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="How many assists does the league leader have this season?",
        ground_truth=(
            "The assists leader's total can be found in the player statistics, "
            "checking the AST column sorted descending."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What is Stephen Curry's free throw percentage this season?",
        ground_truth=(
            "Stephen Curry's free throw percentage can be found in the player "
            "statistics table under the FT% column."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which team has the best win-loss record in the Eastern Conference?",
        ground_truth=(
            "The Eastern Conference standings show each team's win-loss record. "
            "The team at the top of the standings has the best record."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="How many points per game does Nikola Jokic average?",
        ground_truth=(
            "Nikola Jokic's scoring average is listed in the player statistics "
            "under the PPG column for the current season."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which player leads the league in steals per game?",
        ground_truth=(
            "The steals leader can be found by sorting player statistics "
            "by the STL column in descending order."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="What is the average attendance for NBA games this season?",
        ground_truth=(
            "Average attendance figures can be found in the league or team "
            "statistics if available in the knowledge base."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Who won the NBA Most Valuable Player award last season?",
        ground_truth=(
            "The NBA MVP award winner from last season is documented in the "
            "awards and accolades data within the knowledge base."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="How many games has the longest current winning streak lasted?",
        ground_truth=(
            "The longest current winning streak can be found in the team "
            "standings or recent game results data."
        ),
        category=TestCategory.SIMPLE,
    ),
    EvaluationTestCase(
        question="Which rookie has scored the most total points this season?",
        ground_truth=(
            "Rookie scoring leaders can be identified by filtering player "
            "statistics for first-year players and sorting by total points."
        ),
        category=TestCategory.SIMPLE,
    ),
    # ========================================================================
    # COMPLEX: Multi-hop reasoning / analytical / cross-source
    # ========================================================================
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
            "Analyze the correlation between a team's pace of play and their "
            "defensive rating. Which teams break the typical pattern?"
        ),
        ground_truth=(
            "Typically faster-paced teams have worse defensive ratings. "
            "Analyzing team statistics for pace and defensive rating reveals "
            "outliers that maintain strong defense despite high tempo."
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
            "Identify the teams that are most dependent on a single player "
            "for scoring and evaluate the risk this creates for playoff success."
        ),
        ground_truth=(
            "Teams with high single-player scoring dependency can be identified "
            "by analyzing the percentage of total team points from their top scorer. "
            "Historical playoff data suggests balanced scoring leads to more success."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question=(
            "How do the advanced analytics (PER, Win Shares, VORP) compare "
            "between this season's MVP candidates? Provide a statistical argument "
            "for each candidate."
        ),
        ground_truth=(
            "MVP candidates can be compared using advanced metrics like PER, "
            "Win Shares, and VORP from the statistics data. Each metric captures "
            "different aspects of player value and efficiency."
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
            "Cross-reference injury reports with team performance dips to "
            "determine which teams are most affected by their star player's absence."
        ),
        ground_truth=(
            "Injury impact analysis requires comparing team records with and "
            "without key players. The largest win-rate differentials indicate "
            "the most critical players to their team's success."
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
    # ========================================================================
    # NOISY: Ambiguous, typos, slang, out-of-scope, adversarial
    # ========================================================================
    EvaluationTestCase(
        question="who iz the best player ever??? lebron or jordan",
        ground_truth=(
            "This is a subjective debate. The documents may contain Reddit "
            "discussions about GOAT debates but there is no definitive statistical "
            "answer to who is the best player ever."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="stats for that tall guy from milwaukee",
        ground_truth=(
            "This likely refers to Giannis Antetokounmpo of the Milwaukee Bucks. "
            "His stats would be in the regular NBA statistics data."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="What is the best strategy for winning in NBA 2K video game?",
        ground_truth=(
            "This question is about a video game, not real NBA data. "
            "The knowledge base contains real NBA statistics and discussions, "
            "not video game strategies."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="lmao bro did u see that dunk last nite it was insane fr fr",
        ground_truth=(
            "This is informal slang asking about a recent dunk. The system should "
            "attempt to find recent highlight discussions or game recaps despite "
            "the casual language."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="waht are teh top 10 plyers in teh leage rite now??",
        ground_truth=(
            "Despite heavy typos, this asks about the top 10 NBA players. "
            "The system should recognize the intent and provide current "
            "player rankings based on statistics."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Tell me about the weather forecast for tomorrow in New York",
        ground_truth=(
            "This is completely out of scope. The knowledge base only contains "
            "NBA statistics and basketball discussions, not weather data."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="?",
        ground_truth=(
            "A single punctuation mark is not a meaningful query. The system "
            "should handle minimal-content queries gracefully."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Curry Curry Curry Curry points points points average",
        ground_truth=(
            "This repetitive query likely asks about Stephen Curry's scoring "
            "average. The system should handle keyword-stuffed queries."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="<script>alert('xss')</script> SELECT * FROM players",
        ground_truth=(
            "This is an injection attempt. The system should sanitize input "
            "and not execute any embedded code or SQL."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Give me a 5000 word essay on the history of basketball",
        ground_truth=(
            "This requests excessively long output. The system should provide "
            "a concise answer based on available knowledge base content "
            "rather than generating an essay."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="nba",
        ground_truth=(
            "This single-word query is too vague. The system should either "
            "ask for clarification or provide a general NBA overview."
        ),
        category=TestCategory.NOISY,
    ),
    # ========================================================================
    # CONVERSATIONAL: Follow-up questions testing context maintenance
    # ========================================================================
    EvaluationTestCase(
        question="Who is the leading scorer in the NBA this season?",
        ground_truth=(
            "The leading scorer can be found in the player statistics table "
            "sorted by points per game descending."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What about his assist numbers?",
        ground_truth=(
            "This follow-up references the previously mentioned leading scorer. "
            "The system needs context from the prior question to resolve 'his'. "
            "The assists data is in the same player statistics table."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="How does that compare to last season?",
        ground_truth=(
            "This second follow-up asks for a season-over-season comparison "
            "of the leading scorer's assists. Requires maintaining context "
            "across multiple turns."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Which team does Giannis play for?",
        ground_truth=(
            "Giannis Antetokounmpo plays for the Milwaukee Bucks. "
            "This starts a new conversational thread."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="How are they doing in the standings?",
        ground_truth=(
            "This follow-up asks about the Milwaukee Bucks' standing. "
            "The pronoun 'they' references Giannis's team from the prior question."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="And what about their biggest rival in the division?",
        ground_truth=(
            "This asks about the Milwaukee Bucks' divisional rival. "
            "Requires knowing 'their' refers to the Bucks and understanding "
            "NBA divisional structure."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Tell me about the Lakers' recent performance.",
        ground_truth=(
            "The Lakers' recent performance can be found in their game logs "
            "and team statistics for the current season."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Who is their best player statistically?",
        ground_truth=(
            "This follow-up asks about the Lakers' best player. 'Their' "
            "references the Lakers from the previous question. The answer "
            "depends on which statistical metric is used."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Is he in the MVP race?",
        ground_truth=(
            "This asks whether the Lakers' top player is an MVP candidate. "
            "'He' refers to the player identified in the previous answer. "
            "MVP candidacy involves advanced stats and team record."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Compare his numbers to the other top candidates.",
        ground_truth=(
            "This asks for a statistical comparison between the previously "
            "discussed player and other MVP candidates. Requires maintaining "
            "full conversation context and cross-referencing multiple players."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Going back to the Bucks, what are their weaknesses?",
        ground_truth=(
            "This redirects the conversation back to the Milwaukee Bucks "
            "discussed earlier. 'Going back to' signals a topic switch. "
            "Team weaknesses can be inferred from stats and discussions."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Could they address those in a trade?",
        ground_truth=(
            "This follow-up asks whether the Bucks could fix their weaknesses "
            "via trades. 'They' refers to the Bucks, 'those' refers to the "
            "weaknesses identified in the previous answer."
        ),
        category=TestCategory.CONVERSATIONAL,
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
    print(f"  EVALUATION TEST CASES: {stats['total']} total")
    print("=" * 50)
    print(f"  {'Category':<20} {'Count':>6} {'Distribution':>14}")
    print("  " + "-" * 44)
    for cat in TestCategory:
        count = stats["by_category"][cat.value]
        pct = stats["distribution"][cat.value]
        print(f"  {cat.value:<20} {count:>6} {pct:>12.1f}%")
    print("=" * 50 + "\n")
