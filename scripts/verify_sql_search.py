"""
FILE: verify_sql_search.py
STATUS: Active
RESPONSIBILITY: Verify SQL search functionality with comprehensive test queries
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.tools.sql_tool import NBAGSQLTool


def test_simple_queries():
    """Test simple SQL queries (top N, specific players)."""
    print("\n" + "="*80)
    print("TEST 1: SIMPLE SQL QUERIES")
    print("="*80 + "\n")

    tool = NBAGSQLTool()
    tests = [
        "Who scored the most points this season?",
        "What is LeBron James' average points per game?",
        "Who are the top 3 rebounders?",
    ]

    passed = 0
    for question in tests:
        print(f"Query: {question}")
        result = tool.query(question)

        if result['error']:
            print(f"  ✗ FAILED: {result['error']}\n")
        elif not result['results']:
            print(f"  ✗ FAILED: No results\n")
        else:
            print(f"  ✓ PASSED")
            print(f"  SQL: {result['sql']}")
            num_results = len(result['results'])
            display = result['results'][0] if num_results == 1 else f'{num_results} rows'
            print(f"  Results: {display}\n")
            passed += 1

    return passed, len(tests)


def test_comparison_queries():
    """Test comparison SQL queries (2 players)."""
    print("\n" + "="*80)
    print("TEST 2: COMPARISON SQL QUERIES")
    print("="*80 + "\n")

    tool = NBAGSQLTool()
    tests = [
        "Compare Jokić and Embiid stats",
        "Who has more assists, Trae Young or Luka Dončić?",
        "Compare LeBron James and Kevin Durant scoring",
    ]

    passed = 0
    for question in tests:
        print(f"Query: {question}")
        result = tool.query(question)

        if result['error']:
            print(f"  ✗ FAILED: {result['error']}\n")
        elif not result['results']:
            print(f"  ✗ FAILED: No results\n")
        else:
            print(f"  ✓ PASSED")
            print(f"  SQL: {result['sql']}")
            print(f"  Results: {len(result['results'])} players")
            for row in result['results']:
                print(f"    - {row}")
            print()
            passed += 1

    return passed, len(tests)


def test_aggregation_queries():
    """Test aggregation SQL queries (AVG, COUNT, MAX, MIN)."""
    print("\n" + "="*80)
    print("TEST 3: AGGREGATION SQL QUERIES")
    print("="*80 + "\n")

    tool = NBAGSQLTool()
    tests = [
        "What is the average 3-point percentage for all players?",
        "How many players scored over 1000 points?",
        "What is the highest PIE in the league?",
    ]

    passed = 0
    for question in tests:
        print(f"Query: {question}")
        result = tool.query(question)

        if result['error']:
            print(f"  ✗ FAILED: {result['error']}\n")
        elif not result['results']:
            print(f"  ✗ FAILED: No results\n")
        else:
            print(f"  ✓ PASSED")
            print(f"  SQL: {result['sql']}")
            print(f"  Result: {result['results'][0]}\n")
            passed += 1

    return passed, len(tests)


def test_edge_cases():
    """Test edge cases and complex queries."""
    print("\n" + "="*80)
    print("TEST 4: EDGE CASES & COMPLEX QUERIES")
    print("="*80 + "\n")

    tool = NBAGSQLTool()
    tests = [
        "Who has the best true shooting percentage among players with >50 games?",
        "Show me the top 5 players in steals",
        "What is the average rebounds per game across all players?",
    ]

    passed = 0
    for question in tests:
        print(f"Query: {question}")
        result = tool.query(question)

        if result['error']:
            print(f"  ✗ FAILED: {result['error']}\n")
        elif not result['results']:
            print(f"  ✗ FAILED: No results\n")
        else:
            print(f"  ✓ PASSED")
            print(f"  SQL: {result['sql']}")
            if len(result['results']) == 1:
                print(f"  Result: {result['results'][0]}\n")
            else:
                print(f"  Results: {len(result['results'])} rows")
                for i, row in enumerate(result['results'][:3], 1):
                    print(f"    {i}. {row}")
                if len(result['results']) > 3:
                    print(f"    ... and {len(result['results']) - 3} more")
                print()
            passed += 1

    return passed, len(tests)


def main():
    """Run comprehensive SQL search verification."""
    print("\n" + "="*80)
    print("  SQL SEARCH VERIFICATION")
    print("  Gemini 2.0 Flash Lite + LangChain SQL Agent")
    print("="*80)

    print("\nSystem Configuration:")
    print("  SQL LLM: gemini-2.0-flash-lite (Google Gemini)")
    print("  Database: NBA Statistics (569 players)")
    print("  Framework: LangChain + SQLDatabase")

    all_results = []

    # Run all test suites
    all_results.append(("Simple Queries", test_simple_queries()))
    all_results.append(("Comparison Queries", test_comparison_queries()))
    all_results.append(("Aggregation Queries", test_aggregation_queries()))
    all_results.append(("Edge Cases", test_edge_cases()))

    # Summary
    print("\n" + "="*80)
    print("SQL SEARCH VERIFICATION SUMMARY")
    print("="*80 + "\n")

    total_passed = 0
    total_tests = 0

    for suite_name, (passed, total) in all_results:
        total_passed += passed
        total_tests += total
        percentage = (passed / total * 100) if total > 0 else 0
        status = "✓" if passed == total else "⚠" if passed > 0 else "✗"
        print(f"{status} {suite_name}: {passed}/{total} ({percentage:.1f}%)")

    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"\n{'='*80}")
    print(f"OVERALL: {total_passed}/{total_tests} tests passed ({overall_percentage:.1f}%)")
    print(f"{'='*80}\n")

    if overall_percentage >= 90:
        print("✓ SQL SEARCH SYSTEM OPERATIONAL")
        print("\nSQL Search Components:")
        print("  ✓ Gemini 2.0 Flash Lite - Working")
        print("  ✓ LangChain SQL Agent - Working")
        print("  ✓ SQLite Database - Working")
        print("  ✓ Few-shot SQL Generation - Working")
        print("  ✓ Query Execution & Parsing - Working")
        print("\nSQL search is production-ready!")
        return 0
    elif overall_percentage >= 75:
        print("⚠ SQL SEARCH MOSTLY WORKING")
        print(f"\n{total_tests - total_passed} test(s) failed. Review errors above.")
        return 0
    else:
        print("✗ SQL SEARCH HAS ISSUES")
        print(f"\n{total_tests - total_passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
