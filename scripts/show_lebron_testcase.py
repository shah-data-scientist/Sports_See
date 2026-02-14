"""Show the new 'Who is LeBron?' hybrid test case."""
from src.evaluation.test_cases.hybrid_test_cases import HYBRID_TEST_CASES

tc = [t for t in HYBRID_TEST_CASES if t.question == "Who is LeBron?"][0]

print("=" * 70)
print("NEW HYBRID TEST CASE: Who is LeBron?")
print("=" * 70)
print()
print(f"Question:     {tc.question}")
print(f"Query Type:   {tc.query_type.value}")
print(f"Category:     {tc.category}")
print()
print("Expected SQL:")
print(f"  {tc.expected_sql}")
print()
print("Ground Truth Answer:")
print(f"  {tc.ground_truth_answer}")
print()
print("Ground Truth Data (verified from database):")
for k, v in tc.ground_truth_data.items():
    print(f"  {k:12s}: {v}")
print()
print(f"Total hybrid test cases: {len(HYBRID_TEST_CASES)}")
