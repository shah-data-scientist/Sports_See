"""Quick script to show vector-only test case examples."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.run_vector_evaluation import get_vector_test_cases

vector_cases = get_vector_test_cases()

# Group by category
by_category = {}
for tc in vector_cases:
    cat = tc.category.value
    if cat not in by_category:
        by_category[cat] = []
    by_category[cat].append(tc.question)

# Show examples from each category
print('=== VECTOR-ONLY TEST CASES (43 total) ===\n')
for category in sorted(by_category.keys()):
    questions = by_category[category]
    print(f'{category.upper()} ({len(questions)} cases):')
    # Show first 5 examples
    for i, q in enumerate(questions[:5], 1):
        display = q[:80] + '...' if len(q) > 80 else q
        print(f'  {i}. {display}')
    if len(questions) > 5:
        print(f'  ... and {len(questions) - 5} more')
    print()
