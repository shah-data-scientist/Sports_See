"""
FILE: show_query_examples.py
STATUS: Active
RESPONSIBILITY: Demonstrate SQL query execution and result formatting examples
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.tools.sql_tool import NBAGSQLTool

tool = NBAGSQLTool()

print('='*80)
print('EXAMPLE 1: Simple Query - Top Scorer')
print('='*80)

result1 = tool.query('Who scored the most points this season?')
print(f'\nQuestion: {result1["question"]}')
print(f'\nGenerated SQL:')
print(result1['sql'])
print(f'\nRaw Results (dict):')
for i, row in enumerate(result1['results'], 1):
    print(f'  {i}. {row}')
print(f'\nFormatted Results:')
print(tool.format_results(result1['results']))

print()
print('='*80)
print('EXAMPLE 2: Comparison Query - Jokić vs Embiid')
print('='*80)

result2 = tool.query('Compare Jokić and Embiid stats')
print(f'\nQuestion: {result2["question"]}')
print(f'\nGenerated SQL:')
print(result2['sql'])
print(f'\nRaw Results (list of dicts):')
for i, row in enumerate(result2['results'], 1):
    print(f'  {i}. {row}')
print(f'\nFormatted Results:')
print(tool.format_results(result2['results']))
