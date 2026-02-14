"""
FILE: run_sql_sample_5.py
STATUS: Active
RESPONSIBILITY: Run SQL evaluation on 5 sample test cases for quick testing
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.run_sql_evaluation import run_sql_evaluation, generate_comprehensive_report
from src.evaluation.sql_test_cases import SQL_TEST_CASES

# Temporarily override SQL_TEST_CASES with 5 samples
# Pick diverse samples: simple, comparison, aggregation, complex, conversational
SAMPLE_INDICES = [0, 10, 20, 30, 40]  # 5 diverse test cases
ORIGINAL_TEST_CASES = SQL_TEST_CASES.copy()

# Override with sample
SQL_TEST_CASES.clear()
for idx in SAMPLE_INDICES:
    if idx < len(ORIGINAL_TEST_CASES):
        SQL_TEST_CASES.append(ORIGINAL_TEST_CASES[idx])

print(f"\n{'='*80}")
print(f"RUNNING SQL EVALUATION ON 5 SAMPLE TEST CASES")
print(f"{'='*80}")
print(f"\nSample test cases:")
for i, tc in enumerate(SQL_TEST_CASES, 1):
    print(f"{i}. [{tc.category}] {tc.question}")
print(f"\n{'='*80}\n")

if __name__ == "__main__":
    try:
        # Run evaluation
        results, json_path = run_sql_evaluation()

        # Generate report
        report_path = generate_comprehensive_report(results, json_path)

        print("\n" + "="*80)
        print("5-SAMPLE SQL EVALUATION COMPLETE")
        print("="*80)
        print(f"\nResults saved to:")
        print(f"  - JSON: {json_path}")
        print(f"  - Report: {report_path}")
        print("\n" + "="*80)

    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {str(e)}")
        sys.exit(1)
