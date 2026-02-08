"""
FILE: verify_complete_system.py
STATUS: Active
RESPONSIBILITY: Comprehensive verification of vector search + SQL search + hybrid integration
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pathlib import Path
from src.core.config import settings
from src.services.chat import ChatService
from src.tools.sql_tool import NBAGSQLTool


def test_vector_search():
    """Test FAISS vector search with Mistral embeddings."""
    print("\n" + "="*80)
    print("TEST 1: VECTOR SEARCH (FAISS + Mistral Embeddings)")
    print("="*80 + "\n")

    try:
        chat_service = ChatService()

        # Test query about NBA rules/strategies (should use vector search)
        question = "What are the key principles of basketball defense?"
        print(f"Query: {question}\n")

        print("Performing vector search...")
        results = chat_service.search(question, k=3)

        if not results:
            print("✗ FAILED - No results returned from vector search")
            return False

        print(f"✓ Vector search successful - Retrieved {len(results)} chunks\n")

        print("Top result preview:")
        print(f"  Content: {results[0].text[:200]}...")
        print(f"  Score: {results[0].score:.4f}")
        print(f"  Source: {Path(results[0].source).name}\n")

        # Test response generation
        print("Generating response with Gemini LLM...")
        response = chat_service.generate_response(question, results)

        if not response or len(response) < 20:
            print("✗ FAILED - Invalid response generated")
            return False

        print(f"✓ Response generated successfully ({len(response)} chars)\n")
        print(f"Response preview:\n{response[:300]}...\n")

        return True

    except Exception as e:
        print(f"✗ FAILED - Vector search error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sql_search():
    """Test SQL search with Gemini SQL generation."""
    print("\n" + "="*80)
    print("TEST 2: SQL SEARCH (Gemini SQL Generation + Execution)")
    print("="*80 + "\n")

    try:
        sql_tool = NBAGSQLTool()

        # Test SQL query
        question = "Who are the top 3 scorers this season?"
        print(f"Query: {question}\n")

        print("Generating SQL with Gemini...")
        result = sql_tool.query(question)

        if result['error']:
            print(f"✗ FAILED - SQL execution error: {result['error']}")
            return False

        print(f"✓ SQL generated successfully\n")
        print(f"Generated SQL:\n{result['sql']}\n")

        if not result['results']:
            print("✗ FAILED - No results returned")
            return False

        print(f"✓ SQL execution successful - Retrieved {len(result['results'])} rows\n")

        print("Results:")
        for i, row in enumerate(result['results'], 1):
            print(f"  {i}. {row}")

        print(f"\n✓ Formatted results:\n{sql_tool.format_results(result['results'])}\n")

        return True

    except Exception as e:
        print(f"✗ FAILED - SQL search error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_integration():
    """Test hybrid system with both vector and SQL search."""
    print("\n" + "="*80)
    print("TEST 3: HYBRID INTEGRATION (Vector + SQL)")
    print("="*80 + "\n")

    try:
        chat_service = ChatService()

        # Test 1: Pure vector query (basketball concepts)
        print("Test 3a: Pure Vector Query")
        print("-"*80)
        question1 = "What is the pick and roll strategy?"
        print(f"Query: {question1}\n")

        response1 = chat_service.chat(question1)

        if not response1 or len(response1) < 20:
            print("✗ FAILED - Invalid response for vector query")
            return False

        print(f"✓ Vector query successful ({len(response1)} chars)")
        print(f"Response: {response1[:200]}...\n\n")

        # Test 2: Pure SQL query (statistics)
        print("Test 3b: Pure SQL Query")
        print("-"*80)
        question2 = "Who has the most assists this season?"
        print(f"Query: {question2}\n")

        response2 = chat_service.chat(question2)

        if not response2 or len(response2) < 20:
            print("✗ FAILED - Invalid response for SQL query")
            return False

        print(f"✓ SQL query successful ({len(response2)} chars)")
        print(f"Response: {response2[:200]}...\n\n")

        # Test 3: Hybrid query (may need both)
        print("Test 3c: Hybrid Query")
        print("-"*80)
        question3 = "How does LeBron James' scoring compare to the league average?"
        print(f"Query: {question3}\n")

        response3 = chat_service.chat(question3)

        if not response3 or len(response3) < 20:
            print("✗ FAILED - Invalid response for hybrid query")
            return False

        print(f"✓ Hybrid query successful ({len(response3)} chars)")
        print(f"Response: {response3[:300]}...\n")

        return True

    except Exception as e:
        print(f"✗ FAILED - Hybrid integration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run comprehensive system verification."""
    print("\n" + "="*80)
    print("  SPORTS_SEE SYSTEM VERIFICATION")
    print("  Vector Search (FAISS + Mistral) + SQL Search (Gemini)")
    print("="*80)

    # Check configuration
    print("\nSystem Configuration:")
    print(f"  Vector Store: FAISS")
    print(f"  Embedding Model: {settings.embedding_model} (Mistral)")
    print(f"  Chat Model: gemini-2.0-flash-lite (Gemini)")
    print(f"  SQL Model: gemini-2.0-flash-lite (Gemini)")
    print(f"  Database: {settings.database_dir}/nba_stats.db")

    results = []

    # Run tests
    results.append(("Vector Search", test_vector_search()))
    results.append(("SQL Search", test_sql_search()))
    results.append(("Hybrid Integration", test_hybrid_integration()))

    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL SYSTEMS OPERATIONAL")
        print("\nSystem Components:")
        print("  ✓ FAISS Vector Store - Working")
        print("  ✓ Mistral Embeddings - Working")
        print("  ✓ Gemini 2.0 Flash Lite (Chat) - Working")
        print("  ✓ Gemini 2.0 Flash Lite (SQL) - Working")
        print("  ✓ NBA Statistics Database - Working")
        print("  ✓ Hybrid Query Integration - Working")
        print("\nThe system is ready for production use!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
