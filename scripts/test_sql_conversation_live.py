"""
Test SQL conversational thread with live API.
Demonstrates conversation context and pronoun resolution.

Thread: correction_celtics (3 queries)
1. "Show me stats for the Warriors" → Initial query
2. "Actually, I meant the Celtics" → User correction
3. "Who is their top scorer?" → Pronoun resolution ("their" = Celtics)
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000/api/v1"

def print_separator(title=""):
    """Print a separator line."""
    print("\n" + "="*80)
    if title:
        print(f" {title}")
        print("="*80)
    else:
        print("="*80)

def print_response(query_num, question, response_data):
    """Pretty print a chat response."""
    print(f"\n{'─'*80}")
    print(f"QUERY {query_num}: {question}")
    print(f"{'─'*80}")

    print(f"\n📝 RESPONSE:")
    print(response_data.get("response", "No response"))

    print(f"\n🔍 QUERY TYPE: {response_data.get('query_type', 'Unknown')}")
    print(f"⏱️  PROCESSING TIME: {response_data.get('processing_time_ms', 0):.0f}ms")
    print(f"🤖 MODEL: {response_data.get('model', 'Unknown')}")

    # Show SQL if present
    sql_data = response_data.get("sql_data", {})
    if sql_data and sql_data.get("query_generated"):
        print(f"\n💾 SQL QUERY:")
        print(f"   {sql_data['query_generated']}")

        if sql_data.get("results"):
            print(f"\n📊 SQL RESULTS ({len(sql_data['results'])} rows):")
            for i, row in enumerate(sql_data["results"][:5], 1):  # Show first 5
                print(f"   {i}. {row}")

    # Show sources if present
    sources = response_data.get("sources", [])
    if sources:
        print(f"\n📚 SOURCES ({len(sources)}):")
        for i, src in enumerate(sources[:3], 1):  # Show first 3
            print(f"   {i}. {src.get('file_path', 'Unknown')}")

def test_conversation_thread():
    """Run a complete conversational thread."""

    print_separator("SQL CONVERSATIONAL THREAD TEST")
    print(f"Thread: correction_celtics")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_separator()

    # Step 1: Create conversation
    print("\n🔧 Creating new conversation...")
    try:
        conv_resp = requests.post(f"{API_BASE}/conversations", json={})
        conv_resp.raise_for_status()
        conversation_id = conv_resp.json()["id"]
        print(f"✅ Conversation created: {conversation_id}")
    except Exception as e:
        print(f"❌ Failed to create conversation: {e}")
        return

    # Define the 3-query conversation thread
    queries = [
        {
            "query": "Show me stats for the Warriors",
            "expected": "Should return Warriors (Golden State) stats"
        },
        {
            "query": "Actually, I meant the Celtics",
            "expected": "Should understand correction and return Celtics stats"
        },
        {
            "query": "Who is their top scorer?",
            "expected": "Should resolve 'their' to Celtics and return top scorer"
        }
    ]

    # Execute each query in the conversation
    for i, query_info in enumerate(queries, 1):
        question = query_info["query"]

        print(f"\n\n{'🔷'*40}")
        print(f"TURN {i}/3: {question}")
        print(f"Expected: {query_info['expected']}")
        print(f"{'🔷'*40}")

        # Make chat request with conversation_id
        payload = {
            "query": question,
            "k": 5,
            "include_sources": True,
            "conversation_id": conversation_id,
            "turn_number": i
        }

        try:
            chat_resp = requests.post(f"{API_BASE}/chat", json=payload)
            chat_resp.raise_for_status()
            response_data = chat_resp.json()

            # Print the response
            print_response(i, question, response_data)

        except Exception as e:
            print(f"\n❌ Query {i} failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Response: {e.response.text}")
            continue

    # Summary
    print_separator("CONVERSATION SUMMARY")
    print(f"✅ Completed 3-turn conversational thread")
    print(f"📋 Conversation ID: {conversation_id}")
    print(f"🎯 Thread: correction_celtics (Warriors → Celtics correction + pronoun)")
    print_separator()

if __name__ == "__main__":
    # Check if API is running
    try:
        health_resp = requests.get("http://localhost:8000/health", timeout=2)
        health_resp.raise_for_status()
        print("✅ API server is running")
    except Exception as e:
        print(f"❌ API server not reachable at http://localhost:8000")
        print(f"   Please start the API server first:")
        print(f"   poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        exit(1)

    # Run the test
    test_conversation_thread()
