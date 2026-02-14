"""Quick test for JOIN auto-correction fix."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.api.dependencies import set_chat_service
from src.services.chat import ChatService


def test_count_queries():
    """Test COUNT queries that previously failed due to ambiguous column names."""
    print("\n" + "=" * 80)
    print("JOIN AUTO-CORRECTION FIX TEST")
    print("=" * 80)

    # Initialize service
    print("\nInitializing chat service...")
    service = ChatService()
    set_chat_service(service)

    try:
        service.ensure_ready()
        print("✓ Vector index loaded")
    except Exception as e:
        print(f"⚠️ Vector index not loaded (will use SQL only): {e}")

    # Create client
    app = create_app()
    client = TestClient(app)

    test_queries = [
        "How many players have more than 500 assists?",
        "How many players played more than 50 games?",
    ]

    results = []
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print(f"{'='*80}")

        payload = {"query": query, "include_sources": False}

        try:
            response = client.post("/api/v1/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            answer = data.get("answer", "")
            query_type = data.get("query_type", "unknown")
            sql = data.get("generated_sql", None)
            processing_time = data.get("processing_time_ms", 0)

            # Check for SQL success (no fallback to vector)
            sql_success = query_type == "statistical" and sql is not None

            # Check for decline
            has_decline = any(phrase in answer.lower() for phrase in ["i can't", "i cannot", "unable to"])

            print(f"\n✓ Response received ({processing_time:.0f}ms)")
            print(f"  Query Type: {query_type}")
            print(f"  SQL Generated: {sql[:100] if sql else 'None'}...")
            print(f"  SQL Success: {'✅' if sql_success else '❌ (fell back to vector)'}")
            print(f"  Decline: {'❌' if has_decline else '✅'}")
            print(f"\nAnswer Preview:")
            print(f"  {answer[:200]}...")

            results.append({
                "query": query,
                "sql_success": sql_success,
                "has_decline": has_decline,
            })

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                "query": query,
                "sql_success": False,
                "has_decline": True,
            })

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    sql_successes = sum(1 for r in results if r["sql_success"])
    no_declines = sum(1 for r in results if not r["has_decline"])

    print(f"\n✓ SQL Success (no fallback): {sql_successes}/{len(results)}")
    print(f"✓ No Declines: {no_declines}/{len(results)}")

    if sql_successes == len(results) and no_declines == len(results):
        print("\n🎉 JOIN AUTO-CORRECTION FIX WORKING!")
    else:
        print("\n⚠️ Some issues remain")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    test_count_queries()
