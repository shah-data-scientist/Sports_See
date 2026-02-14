"""
Extract and retry the 8 failed test cases by creating a temporary test file.
"""
import json
from pathlib import Path

# Load previous results
results_file = Path("evaluation_results/vector_evaluation_20260213_185715.json")
with open(results_file) as f:
    previous_results = json.load(f)

# Extract failed queries
failed_results = [r for r in previous_results['results'] if 'error' in r]
failed_questions = [r['question'] for r in failed_results]

print(f"Found {len(failed_questions)} failed queries:")
for i, q in enumerate(failed_questions, 1):
    print(f"{i}. {q[:80]}")

# Load all test cases
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES

# Find matching test cases
failed_test_cases = [tc for tc in EVALUATION_TEST_CASES if tc.question in failed_questions]

print(f"\nMatched {len(failed_test_cases)} test cases")

# Create temporary test file with only failed cases
temp_test_file = Path("src/evaluation/test_cases/_retry_failed.py")
temp_test_file.write_text(f"""
# Temporary file with 8 failed test cases for retry
from src.evaluation.test_cases.vector_test_cases import EvaluationTestCase, TestCategory

RETRY_TEST_CASES = {[repr(tc) for tc in failed_test_cases]}
""", encoding='utf-8')

print(f"\n✅ Created temp test file: {temp_test_file}")
print("\nNow run:")
print("poetry run python src/evaluation/runners/run_vector_evaluation.py --delay 30")
