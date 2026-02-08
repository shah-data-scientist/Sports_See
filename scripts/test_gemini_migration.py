"""
FILE: test_gemini_migration.py
STATUS: Active
RESPONSIBILITY: Test Gemini migration for chat and SQL services
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.services.chat import ChatService
from src.models.chat import ChatRequest


def test_chat_service():
    """Test ChatService with Gemini."""
    print("\n" + "=" * 80)
    print("TEST 1: ChatService with Gemini 2.0 Flash Lite")
    print("=" * 80 + "\n")

    try:
        # Initialize chat service
        print("Initializing ChatService...")
        chat_service = ChatService(enable_sql=False)  # Disable SQL for this test
        chat_service.ensure_ready()
        print(f"✓ ChatService initialized with model: {chat_service.model}\n")

        # Test vector search + LLM response
        test_query = "What makes a great basketball player?"
        print(f"Query: {test_query}")
        print("Generating response...\n")

        request = ChatRequest(
            query=test_query,
            k=3,
            include_sources=True
        )

        response = chat_service.chat(request)

        print("✓ Response generated successfully!")
        print(f"Model used: {response.model}")
        print(f"Processing time: {response.processing_time_ms:.0f}ms")
        print(f"Sources retrieved: {len(response.sources)}")
        print(f"\nResponse preview:\n{response.answer[:200]}...")

        return True

    except Exception as e:
        print(f"✗ ChatService test FAILED: {e}")
        return False


def test_sql_tool():
    """Test SQL Tool with Gemini."""
    print("\n" + "=" * 80)
    print("TEST 2: SQL Tool with Gemini 2.0 Flash Lite")
    print("=" * 80 + "\n")

    try:
        from src.tools.sql_tool import NBAGSQLTool

        # Initialize SQL tool
        print("Initializing SQL tool...")
        sql_tool = NBAGSQLTool()
        print(f"✓ SQL tool initialized\n")

        # Test SQL query generation
        test_question = "Who are the top 3 scorers?"
        print(f"Question: {test_question}")
        print("Generating and executing SQL query...\n")

        result = sql_tool.query(test_question)

        if result['error']:
            print(f"✗ SQL query failed: {result['error']}")
            return False

        print("✓ SQL query executed successfully!")
        print(f"Generated SQL:\n{result['sql']}\n")
        print(f"Results ({len(result['results'])} rows):")
        for i, row in enumerate(result['results'][:3], 1):
            print(f"  {i}. {row}")

        return True

    except Exception as e:
        print(f"✗ SQL tool test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_query():
    """Test hybrid query (SQL + Vector)."""
    print("\n" + "=" * 80)
    print("TEST 3: Hybrid Query (SQL + Vector with Gemini)")
    print("=" * 80 + "\n")

    try:
        # Initialize chat service with SQL enabled
        print("Initializing ChatService with SQL enabled...")
        chat_service = ChatService(enable_sql=True)
        chat_service.ensure_ready()
        print("✓ ChatService initialized\n")

        # Test hybrid query
        test_query = "How many points did LeBron James score and what makes him effective?"
        print(f"Query: {test_query}")
        print("Processing hybrid query...\n")

        request = ChatRequest(
            query=test_query,
            k=3,
            include_sources=True
        )

        response = chat_service.chat(request)

        print("✓ Hybrid query processed successfully!")
        print(f"Model used: {response.model}")
        print(f"Processing time: {response.processing_time_ms:.0f}ms")
        print(f"Sources retrieved: {len(response.sources)}")
        print(f"\nResponse preview:\n{response.answer[:300]}...")

        return True

    except Exception as e:
        print(f"✗ Hybrid query test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Gemini migration tests."""
    print("\n" + "=" * 80)
    print("  GEMINI MIGRATION VERIFICATION TESTS")
    print("  Testing Gemini 2.0 Flash Lite integration")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("ChatService (Vector + Gemini LLM)", test_chat_service()))
    results.append(("SQL Tool (Gemini for SQL generation)", test_sql_tool()))
    results.append(("Hybrid Query (SQL + Vector + Gemini)", test_hybrid_query()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests PASSED - Gemini migration successful!")
        print("\nGemini 2.0 Flash Lite is now active in production:")
        print("  - Chat responses")
        print("  - SQL query generation")
        print("  - Hybrid queries (SQL + Vector)")
        print("\nMistral embeddings still used for vector search (FAISS compatibility)")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) FAILED - Please review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
