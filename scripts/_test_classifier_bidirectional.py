"""
FILE: _test_classifier_bidirectional.py
STATUS: Experimental
RESPONSIBILITY: Test bidirectional patterns and dictionary names in classifier
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Test bidirectional patterns and dictionary names in classifier.
"""
import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.services.query_classifier import QueryClassifier, QueryType

c = QueryClassifier()

# Bidirectional tests: both directions should be STATISTICAL
bidirectional_tests = [
    # better/worse than X%
    ("Who has better than 50% field goal percentage?", QueryType.STATISTICAL),
    ("Who has worse than 40% field goal percentage?", QueryType.STATISTICAL),
    # higher/lower than X
    ("Which players have higher than 60% true shooting?", QueryType.STATISTICAL),
    ("Which players have lower than 30% three-point percentage?", QueryType.STATISTICAL),
    # more/fewer than X
    ("Who scored more than 2000 points?", QueryType.STATISTICAL),
    ("Who has fewer than 100 assists?", QueryType.STATISTICAL),
    # above/below X
    ("Players with usage rate above 30%?", QueryType.STATISTICAL),
    ("Players with defensive rating below 110?", QueryType.STATISTICAL),
    # over/under
    ("Players over 25 points per game?", QueryType.STATISTICAL),
    ("Who averaged under 20 minutes?", QueryType.STATISTICAL),
    # most/fewest (superlative pairs)
    ("Who has the most steals?", QueryType.STATISTICAL),
    ("Who has the fewest turnovers?", QueryType.STATISTICAL),
    # highest/lowest
    ("Who has the highest player impact estimate?", QueryType.STATISTICAL),
    ("Who has the lowest turnover ratio?", QueryType.STATISTICAL),
    # best/worst
    ("Who has the best assist-to-turnover ratio?", QueryType.STATISTICAL),
    ("Who has the worst defensive rating?", QueryType.STATISTICAL),
]

# Dictionary full name tests (words from data_dictionary table)
dict_name_tests = [
    ("What is Curry's free throw percentage?", QueryType.STATISTICAL),
    ("Who leads in offensive rebounds?", QueryType.STATISTICAL),
    ("Show me players with high effective field goal percentage", QueryType.STATISTICAL),
    ("What is the average defensive rating in the league?", QueryType.STATISTICAL),
    ("Who has the highest player impact estimate?", QueryType.STATISTICAL),
    ("Games played by LeBron this season?", QueryType.STATISTICAL),
    ("Who has the most double-doubles?", QueryType.STATISTICAL),
    ("Show the triple-double leaders", QueryType.STATISTICAL),
    ("What is the league average for true shooting percentage?", QueryType.STATISTICAL),
    ("Who has the best assist percentage?", QueryType.STATISTICAL),
    ("Compare offensive rating vs defensive rating for top teams", QueryType.STATISTICAL),
    ("Who has the highest usage rate?", QueryType.STATISTICAL),
    ("Minutes per game leaders?", QueryType.STATISTICAL),
    ("Net rating of the top 5 teams?", QueryType.STATISTICAL),
]

# Contextual queries should still be contextual (no regression)
contextual_tests = [
    ("Why is LeBron the GOAT?", QueryType.CONTEXTUAL),
    ("What strategy do the Warriors use?", QueryType.CONTEXTUAL),
    ("How has basketball evolved?", QueryType.CONTEXTUAL),
    ("What do fans think about the trade?", QueryType.CONTEXTUAL),
]

all_tests = [
    ("BIDIRECTIONAL", bidirectional_tests),
    ("DICTIONARY NAMES", dict_name_tests),
    ("CONTEXTUAL (no regression)", contextual_tests),
]

total_pass = 0
total_count = 0
for group_name, tests in all_tests:
    print(f"\n{'='*70}")
    print(f"  {group_name} ({len(tests)} tests)")
    print(f"{'='*70}")
    group_pass = 0
    for q, expected in tests:
        result = c.classify(q)
        ok = "PASS" if result == expected else "FAIL"
        if result == expected:
            group_pass += 1
        print(f"  {ok}: {result.value:15} | {q[:60]}")
    print(f"  → {group_pass}/{len(tests)} pass")
    total_pass += group_pass
    total_count += len(tests)

print(f"\n{'='*70}")
print(f"  TOTAL: {total_pass}/{total_count} ({100*total_pass/total_count:.1f}%)")
print(f"{'='*70}")
