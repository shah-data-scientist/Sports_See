"""
Test that hybrid test cases work correctly with HybridEvaluationTestCase model.
"""
from src.evaluation.test_cases.hybrid_test_cases import HYBRID_TEST_CASES
from src.evaluation.models.hybrid_models import HybridEvaluationTestCase
from src.evaluation.models.sql_models import SQLEvaluationTestCase

# Test 1: Import successful
print(f"✅ Successfully imported {len(HYBRID_TEST_CASES)} hybrid test cases")

# Test 2: Correct type
first_case = HYBRID_TEST_CASES[0]
print(f"✅ First test case type: {type(first_case).__name__}")

# Test 3: HybridEvaluationTestCase inherits from SQLEvaluationTestCase
assert isinstance(first_case, HybridEvaluationTestCase), "Test case should be HybridEvaluationTestCase"
assert isinstance(first_case, SQLEvaluationTestCase), "HybridEvaluationTestCase should inherit from SQLEvaluationTestCase"
print(f"✅ HybridEvaluationTestCase correctly inherits from SQLEvaluationTestCase")

# Test 4: All required fields present
assert hasattr(first_case, 'question'), "Missing question field"
assert hasattr(first_case, 'query_type'), "Missing query_type field"
assert hasattr(first_case, 'expected_sql'), "Missing expected_sql field"
assert hasattr(first_case, 'ground_truth_answer'), "Missing ground_truth_answer field"
assert hasattr(first_case, 'category'), "Missing category field"
assert hasattr(first_case, 'conversation_thread'), "Missing conversation_thread field"
print(f"✅ All required fields present")

# Test 5: Conversation thread fields work
conv_cases = [tc for tc in HYBRID_TEST_CASES if tc.conversation_thread is not None]
print(f"✅ {len(conv_cases)} hybrid test cases have conversation_thread set")

# Test 6: Show conversation threads
threads = set(tc.conversation_thread for tc in conv_cases)
print(f"✅ Conversation threads found: {sorted(threads)}")

# Test 7: Verify each thread
for thread_id in sorted(threads):
    thread_cases = [tc for tc in HYBRID_TEST_CASES if tc.conversation_thread == thread_id]
    print(f"   - {thread_id}: {len(thread_cases)} queries")
    for i, tc in enumerate(thread_cases, 1):
        print(f"     {i}. {tc.question[:70]}...")

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - Hybrid model consistency verified")
print("="*80)
