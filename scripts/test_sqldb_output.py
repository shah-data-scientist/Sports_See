"""
FILE: test_sqldb_output.py
STATUS: Active
RESPONSIBILITY: Test and verify SQLDatabase.run() output format for debugging
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri('sqlite:///database/nba_stats.db')

sql = "SELECT p.name, ps.pts FROM players p JOIN player_stats ps ON p.id = ps.player_id ORDER BY ps.pts DESC LIMIT 1;"

print('='*80)
print('Testing SQLDatabase.run() output format')
print('='*80)

print(f'\nSQL: {sql}')

result = db.run(sql, include_columns=True)

print(f'\nResult type: {type(result).__name__}')
print(f'Result: {result}')

if isinstance(result, str):
    print('\n⚠️  BUG FOUND: Result is a STRING, not a list!')
    print(f'String length: {len(result)}')
    print(f'First 300 chars:\n{result[:300]}')

    # Try to parse it
    import ast
    try:
        parsed = ast.literal_eval(result)
        print(f'\nParsed as: {type(parsed).__name__}')
        print(f'Parsed value: {parsed}')
        if parsed:
            print(f'First element: {parsed[0]}')
            if len(parsed) > 1:
                print(f'Second element: {parsed[1]}')
    except Exception as e:
        print(f'\nFailed to parse: {e}')
else:
    print(f'\n✓ Result is {type(result).__name__}')
    if result:
        print(f'  Length: {len(result)}')
        print(f'  First element: {result[0]}')
