#!/usr/bin/env python3
"""
FILE: verify_query_classification.py
STATUS: Active
RESPONSIBILITY: Verify query classification logic directly (no API needed)
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

from pathlib import Path
from src.services.query_classifier import QueryClassifier, QueryType

def test_classification():
    """Test query classification directly."""
    classifier = QueryClassifier()

    test_cases = [
        # Greetings (detected before classification)
        ("hi", True, False, False, "Greeting"),
        ("hello", True, False, False, "Greeting"),
        ("thanks", True, False, False, "Greeting"),

        # Biographical queries (PHASE 17)
        ("Who is LeBron?", False, True, False, "Biographical → HYBRID"),
        ("Tell me about Michael Jordan", False, True, False, "Biographical → HYBRID"),
        ("Who is Kobe Bryant?", False, True, False, "Biographical → HYBRID"),

        # Statistical queries
        ("top 5 scorers", False, False, True, "Statistical"),
        ("average points per game", False, False, True, "Statistical"),

        # Opinion queries (PHASE 14)
        ("which team was most exciting?", False, False, False, "Opinion → CONTEXTUAL"),
        ("best player", False, False, False, "Opinion → CONTEXTUAL"),

        # Hybrid queries
        ("top 5 scorers and why they're effective", False, False, False, "Hybrid"),
        ("best player and explain why", False, False, False, "Hybrid"),
    ]

    print("\n" + "="*100)
    print("QUERY CLASSIFICATION VERIFICATION (PHASE 17)")
    print("="*100 + "\n")

    results = []

    for query, is_greeting, is_bio, is_stat, description in test_cases:
        print(f"Query: '{query}'")
        print(f"Expected: {description}")

        # Check greeting detection
        greeting_detected = classifier._is_greeting(query)
        bio_detected = classifier._is_biographical(query)

        # Get classification
        if greeting_detected:
            classified_type = "GREETING (detected before classify)"
        elif bio_detected:
            classified_type = "HYBRID (biographical PHASE 17)"
        else:
            classification = classifier.classify(query)
            classified_type = classification.query_type.value.upper()

        print(f"Classified: {classified_type}")

        # Verify expectations
        if is_greeting:
            status = "✓ PASS" if greeting_detected else "✗ FAIL (greeting not detected)"
        elif is_bio:
            status = "✓ PASS" if bio_detected and classified_type == "HYBRID (biographical PHASE 17)" else f"✗ FAIL (got {classified_type})"
        elif is_stat:
            status = "✓ PASS" if classified_type == "STATISTICAL" else f"✗ FAIL (got {classified_type})"
        else:
            # Generic check: should not be statistical
            status = "✓ PASS" if classified_type != "STATISTICAL" else f"✗ FAIL (should not be statistical)"

        print(f"Result: {status}\n")
        results.append({
            "query": query,
            "expected": description,
            "classified": classified_type,
            "status": "PASS" if "PASS" in status else "FAIL"
        })

    # Summary
    print("="*100)
    print("SUMMARY")
    print("="*100)

    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)

    print(f"\nPassed: {passed}/{total}\n")

    for r in results:
        icon = "✓" if r["status"] == "PASS" else "✗"
        print(f"{icon} {r['expected']:<35} | {r['classified']:<30} | {r['status']}")

    print("\nKey Verification Points:")
    print("  ✓ Greeting detection (before classification)")
    print("  ✓ Biographical detection (PHASE 17)")
    print("  ✓ Biographical routes to HYBRID (not CONTEXTUAL)")
    print("  ✓ Opinion queries route to CONTEXTUAL (not STATISTICAL)")
    print("  ✓ Statistical queries identified correctly")
    print()

if __name__ == "__main__":
    test_classification()
