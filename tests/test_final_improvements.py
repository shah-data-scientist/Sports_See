"""
FILE: test_final_improvements.py
STATUS: Active
RESPONSIBILITY: Test final improvements to SQL formatting and classification
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import logging
import sys
from pathlib import Path

# Ensure we're using the latest modules (no caching)
for module in list(sys.modules.keys()):
    if module.startswith('src.'):
        del sys.modules[module]

from src.models.chat import ChatRequest
from src.services.chat import ChatService

# Enable INFO logging to see routing
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(message)s'
)

# Initialize service
print("Initializing ChatService...")
chat_service = ChatService(enable_sql=True)
chat_service.ensure_ready()

# Test problematic queries from the evaluation
test_cases = [
    {
        "query": "Who's the best rebounder?",
        "expected": "Should use SQL and return Ivica Zubac (1008 rebounds)",
    },
    {
        "query": "How many players scored over 1000 points?",
        "expected": "Should use SQL and return a count",
    },
    {
        "query": "Who has the best free throw percentage?",
        "expected": "Should use SQL and return a player name + percentage",
    },
    {
        "query": "Show me the top scorer",
        "expected": "Should use SQL and return Shai Gilgeous-Alexander (2485 points)",
    },
]

print("\n" + "=" * 80)
print("TESTING FINAL SQL IMPROVEMENTS")
print("=" * 80)

results = {"pass": 0, "fail": 0}

for i, test_case in enumerate(test_cases, 1):
    query = test_case["query"]
    expected = test_case["expected"]

    print(f"\n[{i}/{len(test_cases)}] {query}")
    print(f"Expected: {expected}")
    print("-" * 80)

    try:
        request = ChatRequest(query=query, k=5, include_sources=False)
        response = chat_service.chat(request)

        # Check if it actually found an answer
        has_cannot_find = "cannot find" in response.answer.lower()

        if has_cannot_find:
            print(f"[FAIL] Response: {response.answer[:150]}...")
            results["fail"] += 1
        else:
            print(f"[PASS] Response: {response.answer[:150]}...")
            results["pass"] += 1

    except Exception as e:
        print(f"[ERROR] {e}")
        results["fail"] += 1

print("\n" + "=" * 80)
print(f"RESULTS: {results['pass']}/{len(test_cases)} passed, {results['fail']}/{len(test_cases)} failed")
print("=" * 80)

# Success threshold
success_rate = results["pass"] / len(test_cases)
if success_rate >= 0.75:
    print("\n[SUCCESS] Improvements are working! (>= 75% pass rate)")
    sys.exit(0)
else:
    print(f"\n[NEEDS WORK] Pass rate: {success_rate:.1%}")
    sys.exit(1)
