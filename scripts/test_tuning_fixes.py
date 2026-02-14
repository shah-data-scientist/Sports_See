"""Test script to verify tuning fixes on problematic queries from evaluation.

Tests the 10 problematic queries that had issues:
- 9 routing fallbacks (should now route correctly)
- 2 LLM declines (should now answer confidently)

Usage:
    poetry run python scripts/test_tuning_fixes.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.api.dependencies import set_chat_service
from src.services.chat import ChatService


# 10 problematic queries from evaluation
PROBLEMATIC_QUERIES = [
    {
        "query": "Who is more efficient goal maker, Jokić or Embiid?",
        "category": "comparison_sql_players",
        "expected_type": "sql_only",
        "issue": "Routing fallback",
    },
    {
        "query": "How many players have more than 500 assists?",
        "category": "aggregation_sql_count",
        "expected_type": "sql_only",
        "issue": "LLM decline + routing fallback",
    },
    {
        "query": "How many players played more than 50 games?",
        "category": "aggregation_sql_count",
        "expected_type": "sql_only",
        "issue": "Routing fallback",
    },
    {
        "query": "Which teams have at least 3 players with more than 1000 points?",
        "category": "complex_sql_having",
        "expected_type": "sql_only",
        "issue": "LLM decline (correct - data limitation)",
    },
    {
        "query": "Tell me about LeBron's stats",
        "category": "conversational_casual",
        "expected_type": "hybrid",  # Should be biographical HYBRID
        "issue": "Should route to HYBRID (biographical query)",
    },
    {
        "query": "What about his assists?",
        "category": "conversational_followup",
        "expected_type": "sql_only",
        "issue": "Routing fallback (conversational context)",
    },
    {
        "query": "Who is the MVP this season?",
        "category": "conversational_ambiguous",
        "expected_type": "contextual",  # EXPECTED per Issue #7
        "issue": "Expected behavior (ambiguous query)",
    },
    {
        "query": "Who is their top scorer?",
        "category": "conversational_correction",
        "expected_type": "sql_only",
        "issue": "Routing fallback (conversational context)",
    },
    {
        "query": "Tell me about Jayson Tatum's scoring",
        "category": "conversational_multi_entity",
        "expected_type": "hybrid",  # Should be biographical HYBRID
        "issue": "Should route to HYBRID (biographical query)",
    },
    {
        "query": "jokic rebounds total plzz",
        "category": "noisy_sql_informal",
        "expected_type": "sql_only",
        "issue": "Routing fallback + special character normalization",
    },
]


def test_query(client: TestClient, test_case: dict) -> dict:
    """Test a single query and return results."""
    query = test_case["query"]
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"Category: {test_case['category']}")
    print(f"Expected Type: {test_case['expected_type']}")
    print(f"Issue: {test_case['issue']}")
    print(f"{'='*80}")

    # Make API request
    payload = {
        "query": query,
        "include_sources": True,
    }

    try:
        response = client.post("/api/v1/chat", json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract key fields
        answer = data.get("answer", "")
        query_type = data.get("query_type", "unknown")
        sql = data.get("generated_sql", None)
        sources = data.get("sources", [])
        processing_time = data.get("processing_time_ms", 0)

        # Check for decline phrases
        decline_phrases = [
            "i can't provide",
            "i cannot",
            "i'm unable to",
            "i don't have",
        ]
        has_decline = any(phrase in answer.lower() for phrase in decline_phrases)

        # Check for hedging phrases
        hedging_phrases = [
            "appears to",
            "seems to",
            "approximately",
            "i think",
            "i believe",
            "kind of",
        ]
        has_hedging = any(phrase in answer.lower() for phrase in hedging_phrases)

        # Check routing
        routing_match = query_type == test_case["expected_type"]

        # Print results
        print(f"\n✓ Response received ({processing_time:.0f}ms)")
        print(f"  Query Type: {query_type} {'✅' if routing_match else '❌'} (expected: {test_case['expected_type']})")
        print(f"  SQL Generated: {'Yes' if sql else 'No'}")
        print(f"  Sources: {len(sources)}")
        print(f"  Decline Detected: {'❌' if has_decline else '✅'}")
        print(f"  Hedging Detected: {'⚠️' if has_hedging else '✅'}")
        print(f"\nAnswer Preview:")
        print(f"  {answer[:200]}...")

        return {
            "query": query,
            "success": True,
            "routing_match": routing_match,
            "has_decline": has_decline,
            "has_hedging": has_hedging,
            "query_type": query_type,
            "sql_generated": bool(sql),
            "processing_time": processing_time,
        }

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {
            "query": query,
            "success": False,
            "error": str(e),
        }


def main():
    """Run all tests and report results."""
    print("\n" + "=" * 80)
    print("TUNING FIXES VALIDATION TEST")
    print("=" * 80)
    print(f"\nTesting {len(PROBLEMATIC_QUERIES)} problematic queries...")

    # Initialize chat service
    print("\nInitializing chat service...")
    service = ChatService()
    set_chat_service(service)

    # Try to load index
    try:
        service.ensure_ready()
        print("✓ Vector index loaded")
    except Exception as e:
        print(f"⚠️ Vector index not loaded (will use SQL only): {e}")

    # Create test client
    app = create_app()
    client = TestClient(app)

    # Run tests
    results = []
    for test_case in PROBLEMATIC_QUERIES:
        result = test_query(client, test_case)
        results.append(result)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    routing_correct = sum(1 for r in results if r.get("routing_match", False))
    no_declines = sum(1 for r in results if not r.get("has_decline", True))
    no_hedging = sum(1 for r in results if not r.get("has_hedging", True))

    print(f"\n✓ Successful Requests: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"✓ Correct Routing: {routing_correct}/{len(results)} ({routing_correct/len(results)*100:.1f}%)")
    print(f"✓ No Declines: {no_declines}/{len(results)} ({no_declines/len(results)*100:.1f}%)")
    print(f"✓ No Hedging: {no_hedging}/{len(results)} ({no_hedging/len(results)*100:.1f}%)")

    # Detailed breakdown
    print(f"\n{'Query':<50} {'Route':<10} {'Decline':<8} {'Hedge':<8}")
    print("-" * 80)
    for i, result in enumerate(results):
        if not result["success"]:
            print(f"{PROBLEMATIC_QUERIES[i]['query'][:47]:<50} {'ERROR':<10} {'❌':<8} {'❌':<8}")
        else:
            route_icon = "✅" if result.get("routing_match", False) else "❌"
            decline_icon = "✅" if not result.get("has_decline", True) else "❌"
            hedge_icon = "✅" if not result.get("has_hedging", True) else "⚠️"
            print(f"{PROBLEMATIC_QUERIES[i]['query'][:47]:<50} {route_icon:<10} {decline_icon:<8} {hedge_icon:<8}")

    print("\n" + "=" * 80)
    if successful == len(results) and routing_correct >= 9 and no_declines >= 8:
        print("🎉 TUNING FIXES WORKING! Most queries now routing correctly and answering confidently.")
    else:
        print("⚠️ Some issues remain - review output above for details.")
    print("=" * 80 + "\n")

    return successful == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
