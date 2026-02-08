"""
FILE: test_classification.py
STATUS: Active
RESPONSIBILITY: Test query classification patterns
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""
from src.services.query_classifier import QueryClassifier

classifier = QueryClassifier()

test_queries = [
    "Who's the best rebounder?",
    "Who is the best rebounder?",
    "How many players scored over 1000 points?",
    "Who has the best free throw percentage?",
    "Who are the top 3 rebounders in the league?",
]

print("QUERY CLASSIFICATION TEST")
print("=" * 80)

for query in test_queries:
    result = classifier.classify(query)
    query_lower = query.lower()

    # Count pattern matches
    stat_matches = sum(1 for pattern in classifier.statistical_regex if pattern.search(query))
    context_matches = sum(1 for pattern in classifier.contextual_regex if pattern.search(query))

    print(f"\nQuery: '{query}'")
    print(f"  Result: {result.value.upper()}")
    print(f"  Matches: stat={stat_matches}, context={context_matches}")

    if result.value == "contextual" and stat_matches > 0:
        print(f"  [WARNING] Should be STATISTICAL but classified as CONTEXTUAL!")

print("\n" + "=" * 80)
