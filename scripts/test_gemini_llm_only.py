"""
FILE: test_gemini_llm_only.py
STATUS: Active
RESPONSIBILITY: Test Gemini LLM integration (no embeddings required)
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

# UTF-8 encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_gemini_chat_llm():
    """Test Gemini LLM for chat responses (no embeddings)."""
    print("\n" + "=" * 80)
    print("TEST 1: Gemini 2.0 Flash Lite - Direct LLM Test")
    print("=" * 80 + "\n")

    try:
        from google import genai
        from src.core.config import settings

        # Initialize Gemini client
        print("Initializing Gemini client...")
        client = genai.Client(api_key=settings.google_api_key)
        print("✓ Gemini client initialized\n")

        # Test LLM generation
        test_prompt = "What are the key skills of a great basketball player? Answer in 2-3 sentences."
        print(f"Prompt: {test_prompt}")
        print("Generating response...\n")

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=test_prompt,
            config={
                "temperature": 0.0,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 200,
            },
        )

        print("✓ Response generated successfully!\n")
        print(f"Response:\n{response.text}\n")

        return True

    except Exception as e:
        print(f"✗ Gemini LLM test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_sql_generation():
    """Test Gemini for SQL generation via LangChain."""
    print("\n" + "=" * 80)
    print("TEST 2: Gemini 2.0 Flash Lite - SQL Generation")
    print("=" * 80 + "\n")

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from src.core.config import settings

        # Initialize Gemini LLM
        print("Initializing Gemini LLM for SQL...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.0,
            google_api_key=settings.google_api_key,
        )
        print("✓ Gemini LLM initialized\n")

        # Test SQL generation with explicit prompt
        test_prompt = """You are an NBA statistics SQL expert. Generate a SQLite query to answer this question.

Question: Who are the top 3 scorers?

Database schema:
- players(id, name, team_abbr)
- player_stats(id, player_id, pts, gp, reb, ast)

Generate ONLY the SQL query, nothing else. Start with SELECT."""

        print("Generating SQL query...")
        response = llm.invoke(test_prompt)

        sql = response.content.strip()

        # Clean up SQL
        if "```sql" in sql:
            start = sql.find("```sql") + 6
            end = sql.find("```", start)
            sql = sql[start:end].strip()
        elif "```" in sql:
            start = sql.find("```") + 3
            end = sql.find("```", start)
            sql = sql[start:end].strip()

        # Remove leading text before SELECT
        if "SELECT" in sql.upper():
            idx = sql.upper().find("SELECT")
            sql = sql[idx:]

        print("✓ SQL query generated!\n")
        print(f"Generated SQL:\n{sql}\n")

        # Verify it's valid SQL
        if sql.upper().startswith("SELECT") and "FROM" in sql.upper():
            print("✓ SQL structure looks valid")
            return True
        else:
            print("✗ SQL structure invalid - doesn't contain SELECT...FROM")
            return False

    except Exception as e:
        print(f"✗ SQL generation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run Gemini LLM tests (no embeddings required)."""
    print("\n" + "=" * 80)
    print("  GEMINI LLM VERIFICATION TESTS")
    print("  Testing Gemini 2.0 Flash Lite without embeddings")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Gemini LLM - Direct generation", test_gemini_chat_llm()))
    results.append(("Gemini LLM - SQL generation", test_gemini_sql_generation()))

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
        print("\n✓ All LLM tests PASSED - Gemini integration successful!")
        print("\nGemini 2.0 Flash Lite is working correctly for:")
        print("  ✓ Chat response generation")
        print("  ✓ SQL query generation")
        print("\nNOTE: To test full system (with embeddings), set MISTRAL_API_KEY in .env")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) FAILED")
        print("\nPossible issues:")
        print("  - GOOGLE_API_KEY not set in .env")
        print("  - Invalid Google API key")
        print("  - Network connectivity issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
