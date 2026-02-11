"""
FILE: _check_all_sql_classification.py
STATUS: Experimental
RESPONSIBILITY: Quick check to classify all 48 SQL test cases
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Quick check: classify all 48 SQL test cases.
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.services.query_classifier import QueryClassifier, QueryType

c = QueryClassifier()
correct = 0
total = 0
fails = []

for tc in SQL_TEST_CASES:
    if tc.query_type.value == "sql_only":
        total += 1
        r = c.classify(tc.question)
        if r == QueryType.STATISTICAL:
            correct += 1
        else:
            fails.append((tc.question, r.value))

print(f"Classification accuracy: {correct}/{total} ({100*correct/total:.1f}%)")
if fails:
    print("Failures:")
    for q, r in fails:
        print(f"  {r:15} | {q}")
else:
    print("All SQL test cases correctly classified as STATISTICAL!")
