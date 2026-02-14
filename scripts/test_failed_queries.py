"""
FILE: test_failed_queries.py
STATUS: Active
RESPONSIBILITY: Test the 10 previously-failed SQL evaluation queries after fixes
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import io
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.query_classifier import QueryClassifier, QueryType
from src.services.chat import ChatService


def test_classifier_fixes():
    """Test that all 10 previously-failed queries now classify as STATISTICAL."""
    classifier = QueryClassifier()

    # These are the 10 queries that were misclassified as fallback_to_vector
    failed_queries = [
        # Conversational follow-ups (will be fixed by query rewriting, not classifier)
        # But after rewriting, they should classify as STATISTICAL
        ("What about his assists?", QueryType.STATISTICAL, "conversational_followup"),
        ("Only from the Lakers", QueryType.STATISTICAL, "conversational_progressive_filtering"),
        ("Sort them by attempts", QueryType.STATISTICAL, "conversational_progressive_filtering"),
        ("Actually, I meant the Celtics", QueryType.STATISTICAL, "conversational_correction"),

        # These should classify correctly with new patterns
        ("Who is the MVP this season?", QueryType.STATISTICAL, "conversational_ambiguous"),
        ("Show me stats for the Warriors", QueryType.STATISTICAL, "conversational_correction"),
        ("How does LeBron James compare?", QueryType.STATISTICAL, "conversational_multi_entity"),
        ("show me currys 3 pt pct", QueryType.STATISTICAL, "noisy_sql_abbreviation"),
        ("whats the avg fg% in da league lol", QueryType.STATISTICAL, "noisy_sql_slang"),

        # Complex SQL - classifier should route to SQL
        ("Which teams have at least 3 players with more than 1000 points?", QueryType.STATISTICAL, "complex_sql_having"),
    ]

    print("=" * 90)
    print("CLASSIFIER FIX VERIFICATION - 10 Previously-Failed Queries")
    print("=" * 90)
    print()

    correct = 0
    for query, expected, category in failed_queries:
        result = classifier.classify(query)
        ok = result.query_type == expected
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {category:40s} | {result.query_type.value:12s} | {query}")
        if ok:
            correct += 1

    print()
    print(f"Result: {correct}/{len(failed_queries)} correct")
    print()
    return correct == len(failed_queries)


def test_followup_detection():
    """Test that follow-up queries are correctly detected."""
    print("=" * 90)
    print("FOLLOW-UP DETECTION TEST")
    print("=" * 90)
    print()

    followup_queries = [
        ("What about his assists?", True),
        ("Only from the Lakers", True),
        ("Sort them by attempts", True),
        ("Actually, I meant the Celtics", True),
        ("How does LeBron James compare?", False),  # Has explicit entity
        ("Show me stats for the Warriors", False),  # Self-contained
        ("Who scored the most points?", False),  # Self-contained
    ]

    correct = 0
    for query, expected in followup_queries:
        result = ChatService._is_followup_query(query)
        ok = result == expected
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] followup={str(result):5s} (expected={str(expected):5s}) | {query}")
        if ok:
            correct += 1

    print()
    print(f"Result: {correct}/{len(followup_queries)} correct")
    print()
    return correct == len(followup_queries)


def test_broader_patterns():
    """Test that broader patterns catch similar queries (not just exact failing ones)."""
    classifier = QueryClassifier()

    print("=" * 90)
    print("BROADER PATTERN COVERAGE TEST")
    print("=" * 90)
    print()

    # Similar queries that should also be caught by the new broad patterns
    broader_tests = [
        # MVP variations
        ("Who won MVP?", QueryType.STATISTICAL),
        ("Who should be the mvp?", QueryType.STATISTICAL),
        ("Is Jokic the MVP?", QueryType.STATISTICAL),

        # Stats/statistics variations
        ("show me his stats", QueryType.STATISTICAL),
        ("what are curry's averages?", QueryType.STATISTICAL),
        ("get me lebron's numbers", QueryType.STATISTICAL),

        # Team name detection
        ("show me lakers roster", QueryType.STATISTICAL),
        ("celtics stats", QueryType.STATISTICAL),
        ("warriors record", QueryType.STATISTICAL),

        # 3-point variations
        ("curry 3pt percentage", QueryType.STATISTICAL),
        ("who leads in 3 pt makes?", QueryType.STATISTICAL),
        ("best 3-pt shooter", QueryType.STATISTICAL),

        # Noisy/slang variations
        ("whats lebrons ppg bro", QueryType.STATISTICAL),
        ("gimme the rebound leaders plz", QueryType.STATISTICAL),
        ("yo who got the most blocks", QueryType.STATISTICAL),

        # Compare without "to/vs"
        ("compare curry", QueryType.STATISTICAL),
        ("compare the top scorers", QueryType.STATISTICAL),

        # HAVING/group queries
        ("Which teams have multiple all-stars?", QueryType.STATISTICAL),

        # Should still be contextual
        ("Why did LeBron leave Cleveland?", QueryType.CONTEXTUAL),
        ("What is the debate about the GOAT?", QueryType.CONTEXTUAL),
        ("How has basketball strategy evolved?", QueryType.CONTEXTUAL),
    ]

    correct = 0
    for query, expected in broader_tests:
        result = classifier.classify(query)
        ok = result.query_type == expected
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {result.query_type.value:12s} (expected: {expected.value:12s}) | {query}")
        if ok:
            correct += 1

    print()
    print(f"Result: {correct}/{len(broader_tests)} correct")
    print()
    return correct == len(broader_tests)


if __name__ == "__main__":
    all_pass = True

    all_pass &= test_classifier_fixes()
    all_pass &= test_followup_detection()
    all_pass &= test_broader_patterns()

    print("=" * 90)
    if all_pass:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED - Review output above")
    print("=" * 90)
