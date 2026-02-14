"""Test the subquery JOIN auto-correction fix.

Usage:
    poetry run python scripts/test_subquery_fix.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.api.dependencies import set_chat_service
from src.services.chat import ChatService


def main():
    """Test subquery query."""
    print("\n" + "=" * 80)
    print("TEST SUBQUERY JOIN AUTO-CORRECTION FIX")
    print("=" * 80)

    query = "Find players between 25 and 30 years old with more than 1500 points"
    
    print(f"\nQuery: {query}\n")

    # Initialize
    service = ChatService()
    set_chat_service(service)
    try:
        service.ensure_ready()
    except:
        pass

    app = create_app()
    client = TestClient(app)

    try:
        resp = client.post("/api/v1/chat", json={"query": query, "include_sources": False})
        resp.raise_for_status()
        data = resp.json()

        answer = data.get("answer", "")
        query_type = data.get("query_type", "unknown")
        sql = data.get("generated_sql")
        time_ms = data.get("processing_time_ms", 0)

        has_decline = any(p in answer.lower() for p in ["i can't", "i cannot", "unable to", "cannot identify"])
        has_sql_error = "sql" in answer.lower() and "error" in answer.lower()

        print(f"✓ Response received ({time_ms:.0f}ms)")
        print(f"  Query Type: {query_type}")
        print(f"  SQL Generated: {'Yes' if sql else 'No'}")
        
        if sql:
            print(f"\n  Generated SQL:")
            print(f"  {sql}\n")
        
        print(f"  SQL Error: {'❌ YES' if has_sql_error else '✅ NO'}")
        print(f"  Decline: {'❌ YES' if has_decline else '✅ NO'}")
        print(f"\n  Answer Preview:")
        print(f"  {answer[:250]}...\n")

        if not has_decline and not has_sql_error and sql:
            print("🎉 SUBQUERY FIX WORKING!")
        elif has_decline and not sql:
            print("✅ SQL correctly skipped (LLM couldn't generate valid SQL)")
        else:
            print("⚠️ Still has issues")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
