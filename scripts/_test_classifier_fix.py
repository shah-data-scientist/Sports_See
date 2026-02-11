"""
FILE: _test_classifier_fix.py
STATUS: Experimental
RESPONSIBILITY: Quick test for classifier fixes on misclassified queries
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Quick test for classifier fixes on the 7 misclassified queries.
"""
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.services.query_classifier import QueryClassifier, QueryType

c = QueryClassifier()
queries = [
    "List all players on the Golden State Warriors.",
    "Who shoots better from 3, Curry or Lillard?",
    "What is the maximum number of blocks recorded by any player?",
    "Which players have better than 50% field goal percentage AND 35%+ from three?",
    "What percentage of players have a true shooting percentage above 60%?",
    "What about his assists?",
    "Which of them plays for the Hawks?",
]
passed = 0
for q in queries:
    r = c.classify(q)
    ok = "PASS" if r == QueryType.STATISTICAL else "FAIL"
    if r == QueryType.STATISTICAL:
        passed += 1
    print(f"{ok}: {r.value:15} | {q[:65]}")

print(f"\nResult: {passed}/{len(queries)} pass")
