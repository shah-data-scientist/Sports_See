"""
FILE: debug_sql_context.py
STATUS: Active
RESPONSIBILITY: Debug SQL context formatting for LLM
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""
from src.tools.sql_tool import NBAGSQLTool

sql_tool = NBAGSQLTool()

# Test the problematic queries
test_queries = [
    "Who's the best rebounder?",
    "How many players scored over 1000 points?",
]

print("=" * 80)
print("SQL CONTEXT DEBUG")
print("=" * 80)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    print("-" * 80)

    result = sql_tool.query(query)

    print(f"SQL: {result.get('sql', 'N/A')[:100]}...")
    print(f"Error: {result.get('error', 'None')}")

    if result.get("results"):
        num_rows = len(result["results"])
        print(f"Results: {num_rows} rows")
        print(f"First row data: {result['results'][0]}")

        # Show how it would be formatted in chat.py
        if num_rows == 1:
            row = result["results"][0]
            formatted_data = []
            for key, value in row.items():
                formatted_data.append(f"  • {key}: {value}")
            sql_context = "\n".join(formatted_data)
            header = "STATISTICAL DATA (FROM SQL DATABASE):\nFound 1 matching record:\n\n"
        else:
            formatted_rows = []
            for i, row in enumerate(result["results"][:20], 1):
                row_parts = [f"{k}: {v}" for k, v in row.items()]
                formatted_rows.append(f"{i}. {', '.join(row_parts)}")

            sql_context = "\n".join(formatted_rows)

            if num_rows > 20:
                sql_context += f"\n\n(Showing top 20 of {num_rows} total results)"
                header = f"STATISTICAL DATA (FROM SQL DATABASE):\nFound {num_rows} matching records (showing top 20):\n\n"
            else:
                header = f"STATISTICAL DATA (FROM SQL DATABASE):\nFound {num_rows} matching records:\n\n"

        full_context = header + sql_context

        print(f"\nFormatted Context Preview:")
        print(full_context[:400] + "..." if len(full_context) > 400 else full_context)
    else:
        print("No results returned")

print("\n" + "=" * 80)
