"""
FILE: test_classifier_debug.py
STATUS: Active
RESPONSIBILITY: Debug query classifier pattern matching
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""
import re
from src.services.query_classifier import QueryClassifier

classifier = QueryClassifier()

# Test the problematic queries
test_queries = [
    "Who's the best rebounder?",
    "Who is the best rebounder?",
    "Show the assist leaders",
    "Show me the top scorer",
]

print("=" * 80)
print("QUERY CLASSIFIER DEBUG TEST")
print("=" * 80)

for query in test_queries:
    result = classifier.classify(query)
    query_lower = query.lower()

    # Count matches
    stat_matches = sum(1 for pattern in classifier.statistical_regex if pattern.search(query))
    context_matches = sum(1 for pattern in classifier.contextual_regex if pattern.search(query))

    print(f"\nQuery: '{query}'")
    print(f"  Classification: {result.value}")
    print(f"  Stat matches: {stat_matches}, Context matches: {context_matches}")

    # Test specific pattern
    pattern = r"\b(who\s+is|who.?s|which player|which team)\b.*\b(best|better)\b.*\b(scorer|rebounder|passer|defender|shooter|player)\b"
    compiled = re.compile(pattern, re.IGNORECASE)
    match = compiled.search(query)
    print(f"  Best/better pattern match: {match is not None}")
    if match:
        print(f"    Matched text: '{match.group()}'")

print("\n" + "=" * 80)
