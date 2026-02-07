"""
FILE: test_sql_tool.py
STATUS: Active
RESPONSIBILITY: Test script for NBA SQL tool
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

from src.tools.sql_tool import NBAGSQLTool


def test_sql_tool():
    """Test NBA SQL tool with sample questions."""
    print("=" * 80)
    print("NBA SQL TOOL TEST")
    print("=" * 80)

    tool = NBAGSQLTool()

    test_questions = [
        "Who are the top 5 scorers in the league?",
        "What is the average field goal percentage for the Lakers?",
        "Which player has the most rebounds?",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'-' * 80}")
        print(f"Test {i}: {question}")
        print(f"{'-' * 80}")

        result = tool.query(question)

        if result["error"]:
            print(f"\n❌ ERROR: {result['error']}")
        else:
            print(f"\n✅ SQL Generated:")
            print(result["sql"])
            print(f"\n📊 Results ({len(result['results'])} rows):")
            print(tool.format_results(result["results"]))


if __name__ == "__main__":
    test_sql_tool()
