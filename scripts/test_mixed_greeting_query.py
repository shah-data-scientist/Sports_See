"""
FILE: test_mixed_greeting_query.py
STATUS: Active
RESPONSIBILITY: Test strict greeting detection with mixed query "hi tell me about Lebron"
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Shahu
"""

from src.services.query_classifier import QueryClassifier


def test_mixed_greeting_query():
    """Test that 'hi tell me about Lebron' is NOT treated as pure greeting."""

    query = "hi tell me about Lebron"
    classifier = QueryClassifier()

    print("=" * 80)
    print("Testing Strict Greeting Detection with Mixed Query")
    print("=" * 80)
    print(f"\nQuery: '{query}'")
    print("\n" + "-" * 80)

    # Step 1: Check if detected as greeting
    is_greeting = classifier._is_greeting(query)
    print(f"\n1. Greeting Detection Result: {is_greeting}")

    if is_greeting:
        print("   ❌ FAIL: Query incorrectly detected as pure greeting")
        print("   Expected: False (query contains 'tell me' action request + 'lebron' basketball keyword)")
    else:
        print("   ✅ PASS: Query correctly identified as NON-GREETING")
        print("   Reason: Contains 'tell me' (action request) + 'Lebron' (basketball keyword)")

    # Step 2: Since not a greeting, it should proceed to classification
    print("\n" + "-" * 80)
    print("\n2. Query Classification (since not pure greeting):")

    result = classifier.classify(query)

    print(f"   Query Type: {result.query_type.value}")
    print(f"   Is Biographical: {result.is_biographical}")
    print(f"   Complexity K: {result.complexity_k}")
    print(f"   Query Category: {result.query_category}")
    print(f"   Max Expansions: {result.max_expansions}")

    # Step 3: Verify expected behavior
    print("\n" + "-" * 80)
    print("\n3. Expected Behavior in Full Pipeline:")

    if result.is_biographical:
        print("   ✅ Biographical query detected")
        print("   → Should route to HYBRID path (SQL stats + Vector narrative)")
        print("   → SQL: Fetch LeBron's career statistics")
        print("   → Vector: Retrieve biographical articles/discussions about LeBron")
        print("   → LLM: Synthesize comprehensive response with stats + context")
    else:
        print("   ⚠️ Not detected as biographical")
        print(f"   → Would route to {result.query_type.value} path")

    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)

    # Return results for verification
    return {
        "query": query,
        "is_greeting": is_greeting,
        "query_type": result.query_type.value,
        "is_biographical": result.is_biographical,
        "complexity_k": result.complexity_k,
        "query_category": result.query_category,
    }


if __name__ == "__main__":
    results = test_mixed_greeting_query()

    # Verification
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    if not results["is_greeting"]:
        print("✅ Strict greeting detection working correctly")
        print("   Query with 'hi' + additional content NOT treated as pure greeting")
    else:
        print("❌ Strict greeting detection FAILED")
        print("   Query should not be treated as pure greeting")

    if results["is_biographical"]:
        print("✅ Biographical detection working correctly")
        print("   'tell me about Lebron' correctly identified as biographical query")
    else:
        print("⚠️ Biographical detection may need review")
