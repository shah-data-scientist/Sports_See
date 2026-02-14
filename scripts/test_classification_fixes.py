"""
Test the Phase 2A classification fixes.

Tests the 10 misclassified queries to verify they now route correctly.
"""
from src.services.query_classifier import QueryClassifier

# Initialize classifier
classifier = QueryClassifier()

# Test cases from misclassification report
test_cases = [
    # Biographical fixes (should NOT trigger biographical anymore)
    ("Tell me about the most discussed playoff efficiency topic.", "CONTEXTUAL or HYBRID", "Was routing to HYBRID via biographical"),

    # Hybrid pattern additions (should now route to HYBRID)
    ("Do fans debate about historical playoff performances?", "HYBRID", "Was CONTEXTUAL, should be HYBRID"),
    ("What do authoritative voices say about playoff basketball?", "HYBRID", "Was CONTEXTUAL, should be HYBRID"),
    ("What are the consensus views on playoff performance?", "HYBRID", "Was CONTEXTUAL, should be HYBRID"),
    ("Compare opinions on efficiency from high-engagement vs low-engagement posts.", "HYBRID", "Was SQL, should be HYBRID"),

    # These should still be CONTEXTUAL (subjective/opinion)
    ("Explain the difference between man-to-man and zone defense.", "HYBRID or CONTEXTUAL", "Strategy explanation"),
    ("What basketball terms are important for understanding efficiency?", "HYBRID", "Was SQL, should be HYBRID"),

    # These should be CONTEXTUAL (glossary/definitional)
    ("What does 'first option' mean in basketball?", "CONTEXTUAL", "Was SQL, should be CONTEXTUAL"),

    # Conversational (context-dependent)
    ("What are their biggest strengths?", "CONTEXTUAL or STATISTICAL", "Context-dependent"),
    ("And their weaknesses?", "CONTEXTUAL or STATISTICAL", "Context-dependent"),
]

print("Testing Phase 2A Classification Fixes")
print("=" * 80)
print()

results = []
for query, expected, note in test_cases:
    result = classifier.classify(query)
    routing = result.query_type.value

    # Check if it matches expectations (case-insensitive)
    expected_options = [e.strip().lower() for e in expected.split(" or ")]
    is_correct = routing.lower() in expected_options

    status = "✓" if is_correct else "✗"

    print(f"{status} Query: {query[:70]}")
    print(f"  Expected: {expected}")
    print(f"  Actual: {routing}")
    print(f"  Note: {note}")
    print()

    results.append({
        "query": query,
        "expected": expected,
        "actual": routing,
        "correct": is_correct
    })

# Summary
correct_count = sum(1 for r in results if r["correct"])
total_count = len(results)
accuracy = (correct_count / total_count) * 100

print("=" * 80)
print(f"Results: {correct_count}/{total_count} correct ({accuracy:.1f}%)")
print()

if correct_count < total_count:
    print("Failed cases:")
    for r in results:
        if not r["correct"]:
            print(f"  - {r['query'][:60]}")
            print(f"    Expected: {r['expected']}, Got: {r['actual']}")
