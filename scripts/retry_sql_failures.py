"""Retry the 3 SQL queries that failed due to API rate limits.

Usage:
    poetry run python scripts/retry_sql_failures.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.api.dependencies import set_chat_service
from src.services.chat import ChatService


# 3 queries that failed due to API 500 errors (rate limits)
FAILED_QUERIES = [
    {
        "query": "Who is more efficient goal maker, Jokić or Embiid?",
        "category": "comparison_sql_players",
    },
    {
        "query": "Find players between 25 and 30 years old with more than 1500 points",
        "category": "complex_sql_range",
    },
    {
        "query": "gimme the assist leaders plz",
        "category": "conversational_casual",
    },
]


def main():
    """Run retry tests."""
    print("\n" + "=" * 80)
    print("RETRY FAILED QUERIES (API Rate Limit Errors)")
    print("=" * 80)
    print(f"\nRetrying {len(FAILED_QUERIES)} queries...")

    # Initialize
    service = ChatService()
    set_chat_service(service)
    try:
        service.ensure_ready()
        print("✓ Vector index loaded\n")
    except:
        pass

    app = create_app()
    client = TestClient(app)

    # Run tests
    results = []
    for i, test in enumerate(FAILED_QUERIES, 1):
        query = test["query"]
        category = test["category"]

        print(f"[{i}/3] {query}")
        print(f"  Category: {category}")

        try:
            resp = client.post("/api/v1/chat", json={"query": query, "include_sources": False})
            resp.raise_for_status()
            data = resp.json()

            answer = data.get("answer", "")
            query_type = data.get("query_type", "unknown")
            sql = data.get("generated_sql")
            time_ms = data.get("processing_time_ms", 0)

            has_decline = any(p in answer.lower() for p in ["i can't", "i cannot", "unable to"])

            status = "✅" if not has_decline else "⚠️"

            print(f"  {status} Type: {query_type} | SQL: {'Yes' if sql else 'No'} | Time: {time_ms:.0f}ms")
            print(f"  Decline: {'❌' if has_decline else '✅'}")
            print(f"  Answer: {answer[:120]}...\n")

            results.append({"success": True, "has_decline": has_decline})

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)[:80]}\n")
            results.append({"success": False, "has_decline": True})

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    no_decline = sum(1 for r in results if not r["has_decline"])

    print(f"\n✓ Successful: {successful}/3 ({successful/3*100:.0f}%)")
    print(f"✓ No Declines: {no_decline}/3 ({no_decline/3*100:.0f}%)")

    if successful == 3 and no_decline == 3:
        print("\n🎉 ALL QUERIES SUCCESSFUL!")
    elif successful == 3:
        print("\n✓ All queries executed (some response issues)")
    else:
        print(f"\n⚠️ {3 - successful} queries still failing")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
