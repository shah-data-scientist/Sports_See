"""
Test classification accuracy for all evaluation test cases.
Checks SQL, Vector, and Hybrid test sets.
"""
from src.services.query_classifier import QueryClassifier
from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES as VECTOR_TEST_CASES
from src.evaluation.test_cases.hybrid_test_cases import HYBRID_TEST_CASES

# Initialize classifier
classifier = QueryClassifier()

# Expected routing for each test set
SQL_EXPECTED = "statistical"
VECTOR_EXPECTED = "contextual"
HYBRID_EXPECTED = "hybrid"

print("=" * 80)
print("CLASSIFICATION ACCURACY TEST - ALL EVALUATION SETS")
print("=" * 80)
print()

all_failures = []

# Test 1: SQL Test Cases (should route to STATISTICAL)
print("1. SQL TEST CASES (80 queries)")
print("-" * 80)
sql_failures = []
sql_correct = 0

for i, test_case in enumerate(SQL_TEST_CASES, 1):
    result = classifier.classify(test_case.question)
    actual = result.query_type.value.lower()
    expected = SQL_EXPECTED.lower()

    if actual == expected:
        sql_correct += 1
    else:
        sql_failures.append({
            'id': i,
            'query': test_case.question,
            'expected': SQL_EXPECTED,
            'actual': result.query_type.value,
            'category': test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category)
        })

sql_accuracy = (sql_correct / len(SQL_TEST_CASES)) * 100
print(f"Results: {sql_correct}/{len(SQL_TEST_CASES)} correct ({sql_accuracy:.1f}%)")
print(f"Failures: {len(sql_failures)}")
print()

# Test 2: Vector Test Cases (should route to CONTEXTUAL)
print("2. VECTOR TEST CASES (75 queries)")
print("-" * 80)
vector_failures = []
vector_correct = 0

for i, test_case in enumerate(VECTOR_TEST_CASES, 1):
    result = classifier.classify(test_case.question)
    actual = result.query_type.value.lower()
    expected = VECTOR_EXPECTED.lower()

    if actual == expected:
        vector_correct += 1
    else:
        vector_failures.append({
            'id': i,
            'query': test_case.question,
            'expected': VECTOR_EXPECTED,
            'actual': result.query_type.value,
            'category': test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category)
        })

vector_accuracy = (vector_correct / len(VECTOR_TEST_CASES)) * 100
print(f"Results: {vector_correct}/{len(VECTOR_TEST_CASES)} correct ({vector_accuracy:.1f}%)")
print(f"Failures: {len(vector_failures)}")
print()

# Test 3: Hybrid Test Cases (should route to HYBRID)
print("3. HYBRID TEST CASES (50 queries)")
print("-" * 80)
hybrid_failures = []
hybrid_correct = 0

for i, test_case in enumerate(HYBRID_TEST_CASES, 1):
    result = classifier.classify(test_case.question)
    actual = result.query_type.value.lower()
    expected = HYBRID_EXPECTED.lower()

    if actual == expected:
        hybrid_correct += 1
    else:
        hybrid_failures.append({
            'id': i,
            'query': test_case.question,
            'expected': HYBRID_EXPECTED,
            'actual': result.query_type.value,
            'category': test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category)
        })

hybrid_accuracy = (hybrid_correct / len(HYBRID_TEST_CASES)) * 100
print(f"Results: {hybrid_correct}/{len(HYBRID_TEST_CASES)} correct ({hybrid_accuracy:.1f}%)")
print(f"Failures: {len(hybrid_failures)}")
print()

# Overall Summary
total_queries = len(SQL_TEST_CASES) + len(VECTOR_TEST_CASES) + len(HYBRID_TEST_CASES)
total_correct = sql_correct + vector_correct + hybrid_correct
overall_accuracy = (total_correct / total_queries) * 100

print("=" * 80)
print("OVERALL SUMMARY")
print("=" * 80)
print(f"Total Queries: {total_queries}")
print(f"Correct: {total_correct} ({overall_accuracy:.1f}%)")
print(f"Failures: {total_queries - total_correct}")
print()

# Detailed Failure Report
all_failures = sql_failures + vector_failures + hybrid_failures

if all_failures:
    print("=" * 80)
    print(f"DETAILED FAILURE REPORT ({len(all_failures)} failures)")
    print("=" * 80)
    print()

    # Group by actual routing
    from collections import defaultdict
    by_routing = defaultdict(list)
    for f in all_failures:
        by_routing[(f['expected'], f['actual'])].append(f)

    for (expected, actual), failures in sorted(by_routing.items()):
        print(f"❌ Expected: {expected.upper()} → Got: {actual.upper()} ({len(failures)} cases)")
        print("-" * 80)
        for f in failures[:10]:  # Show first 10 of each type
            print(f"  [{f['id']}] {f['query'][:70]}...")
            print(f"      Category: {f['category']}")
        if len(failures) > 10:
            print(f"  ... and {len(failures) - 10} more")
        print()
else:
    print("🎉 NO FAILURES! All queries classified correctly!")
    print()

# Save results
import json
from datetime import datetime

results = {
    'timestamp': datetime.now().isoformat(),
    'total_queries': total_queries,
    'correct': total_correct,
    'accuracy': overall_accuracy,
    'sql': {
        'total': len(SQL_TEST_CASES),
        'correct': sql_correct,
        'accuracy': sql_accuracy,
        'failures': sql_failures
    },
    'vector': {
        'total': len(VECTOR_TEST_CASES),
        'correct': vector_correct,
        'accuracy': vector_accuracy,
        'failures': vector_failures
    },
    'hybrid': {
        'total': len(HYBRID_TEST_CASES),
        'correct': hybrid_correct,
        'accuracy': hybrid_accuracy,
        'failures': hybrid_failures
    }
}

output_file = f"evaluation_results/classification_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Results saved to: {output_file}")
