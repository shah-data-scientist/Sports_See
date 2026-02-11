"""
FILE: _STATISTICAL_QUERIES_TO_REVIEW.py
STATUS: Experimental
RESPONSIBILITY: 25 statistical queries extracted from vector_test_cases.py for review
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

NOTES:
- These queries ask for statistical/factual data
- System correctly routes them to SQL
- User to review and decide whether to move to sql_test_cases.py
- Classification done by _classify_vector_test_cases.py
"""

from src.evaluation.models import EvaluationTestCase, TestCategory

# ALL 25 STATISTICAL QUERIES FROM VECTOR_TEST_CASES.PY
STATISTICAL_QUERIES_FROM_VECTOR_TESTS = [
    # SIMPLE category - All statistical (12 queries)
    EvaluationTestCase(
        question="Which player has the best 3-point percentage over the last 5 games?",
        ground_truth=(
            "The player with the best 3-point percentage over the last 5 games "
            "can be found in the regular NBA statistics."
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
            "The rookie scoring leader can be identified by filtering player "
            "statistics by rookie status and sorting by total points."
        ),
        category=TestCategory.SIMPLE,
    ),

    # COMPLEX category - Statistical (3 queries)
    EvaluationTestCase(
        question="Identify the teams that are most dependent on a single player for scoring and evaluate the risk this creates for playoff success.",
        ground_truth=(
            "Team scoring dependency can be calculated by comparing the top "
            "scorer's points to team total points."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="How do the advanced analytics (PER, Win Shares, VORP) compare between this season's MVP candidates? Provide a statistical argument for each candidate.",
        ground_truth=(
            "MVP candidates' advanced statistics can be compared using PER, "
            "Win Shares, and VORP columns from player statistics."
        ),
        category=TestCategory.COMPLEX,
    ),
    EvaluationTestCase(
        question="Cross-reference injury reports with team performance dips to determine which teams are most affected by their star player's absence.",
        ground_truth=(
            "Injury impact requires correlating player absence data with team "
            "win-loss records before and after injuries."
        ),
        category=TestCategory.COMPLEX,
    ),

    # NOISY category - Statistical with typos/informal (4 queries)
    EvaluationTestCase(
        question="who iz the best player ever??? lebron or jordan",
        ground_truth=(
            "Historical comparison of LeBron James and Michael Jordan based on "
            "career statistics and accomplishments."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="stats for that tall guy from milwaukee",
        ground_truth=(
            "Giannis Antetokounmpo plays for Milwaukee Bucks. His statistics "
            "can be found in the player stats table."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="waht are teh top 10 plyers in teh leage rite now??",
        ground_truth=(
            "Top 10 players can be determined by sorting player statistics by "
            "total points, assists, or other metrics."
        ),
        category=TestCategory.NOISY,
    ),
    EvaluationTestCase(
        question="Curry Curry Curry Curry points points points average",
        ground_truth=(
            "Stephen Curry's points per game average can be found in the "
            "player statistics table."
        ),
        category=TestCategory.NOISY,
    ),

    # CONVERSATIONAL category - Statistical (6 queries)
    EvaluationTestCase(
        question="Who is the leading scorer in the NBA this season?",
        ground_truth=(
            "The leading scorer is the player with the most total points this "
            "season, found by sorting player statistics by points descending."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="What about his assist numbers?",
        ground_truth=(
            "Follow-up question requiring conversation context to resolve 'his' "
            "to the previously mentioned player, then retrieve assist stats."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="How does that compare to last season?",
        ground_truth=(
            "Comparison with previous season requires historical statistics data "
            "for the player mentioned in conversation context."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Tell me about the Lakers' recent performance.",
        ground_truth=(
            "Lakers' recent performance can be found in team statistics showing "
            "win-loss record and recent game results."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Who is their best player statistically?",
        ground_truth=(
            "Requires resolving 'their' from conversation context (which team), "
            "then finding player with best statistics for that team."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
    EvaluationTestCase(
        question="Compare his numbers to the other top candidates.",
        ground_truth=(
            "Comparison of statistical performance between multiple players. "
            "Requires resolving 'his' from conversation context, then SQL comparison."
        ),
        category=TestCategory.CONVERSATIONAL,
    ),
]

# Current behavior:
# - System routes these to SQL → Returns accurate statistical answers ✅
# - Tests expect vector_only → Marks as MISCLASSIFICATION ❌
#
# Recommendation: Move to sql_test_cases.py with expected_routing="sql_only"
