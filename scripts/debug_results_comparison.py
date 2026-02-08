"""
FILE: debug_results_comparison.py
STATUS: Active
RESPONSIBILITY: Debug SQL query results comparison for test case validation
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.tools.sql_tool import NBAGSQLTool
from src.evaluation.sql_only_test_cases import SQL_ONLY_TEST_CASES

tool = NBAGSQLTool()

# Test first 3 cases
for i in range(min(3, len(SQL_ONLY_TEST_CASES))):
    test_case = SQL_ONLY_TEST_CASES[i]
    print('='*80)
    print(f'TEST CASE {i+1}: {test_case.question}')
    print('='*80)
    print(f'Expected ground truth: {test_case.ground_truth_data}')

    result = tool.query(test_case.question)
    print(f'\nGenerated SQL:\n{result["sql"]}')

    if result['results']:
        print(f'\nActual results (first row): {result["results"][0]}')

        print(f'\nKey comparison:')
        for key, expected in test_case.ground_truth_data.items():
            actual = result['results'][0].get(key, 'KEY_NOT_FOUND')
            match = actual == expected
            print(f'  {key}: expected={expected} ({type(expected).__name__}), actual={actual} ({type(actual).__name__}), match={match}')
    else:
        print(f'\nNo results! Error: {result["error"]}')

    print()
