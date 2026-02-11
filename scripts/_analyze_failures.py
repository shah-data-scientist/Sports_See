"""
FILE: _analyze_failures.py
STATUS: Experimental
RESPONSIBILITY: Analyze ground truth failures from SQL evaluation
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Analyze the 8 ground truth failures from the previous SQL evaluation.
"""
import io
import json
import sys

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

with open("evaluation_results/sql_evaluation_20260211_031415.json", encoding="utf-8") as f:
    data = json.load(f)

from src.evaluation.sql_test_cases import SQL_TEST_CASES

# Build ground truth lookup (using the OLD test cases from before our update)
# The failures are based on the OLD ground truth, so let's use the actual responses
# and the NEW ground truth we just defined to understand root causes

failures = []
for r in data["results"]:
    if not r.get("success"):
        continue
    q = r["question"]
    resp = r["response"]

    # Check for common failure indicators
    resp_lower = resp.lower()
    failure_phrases = [
        "available context doesn't contain",
        "cannot find", "no information", "i don't have",
    ]
    is_no_data = any(p in resp_lower for p in failure_phrases)

    # Find matching test case
    tc = None
    for t in SQL_TEST_CASES:
        if t.question == q:
            tc = t
            break

    # Identify failures by comparing response to known ground truth
    # These are the 8 cases that failed ground truth matching in the matrix report
    failure_cases = {
        "Who has the highest true shooting percentage?",
        "Compare Jayson Tatum and Kevin Durant scoring efficiency",
        "Who are the top 2 players by true shooting percentage?",
        "What is the average rebounds per game league-wide?",
        "How many players have a true shooting percentage over 60%?",
        "Find players averaging double-digits in points, rebounds, and assists",
        "What about his assists?",
        "How many games did he play?",
    }

    if q in failure_cases:
        failures.append({
            "question": q,
            "category": r["category"],
            "response": resp.strip(),
            "ground_truth": tc.ground_truth_answer if tc else "N/A",
            "ground_truth_data": str(tc.ground_truth_data) if tc else "N/A",
            "is_no_data": is_no_data,
            "routing": r["actual_routing"],
            "time_ms": r.get("processing_time_ms", 0),
        })

print("=" * 80)
print("  FAILURE ANALYSIS: 8 Ground Truth Mismatches")
print("=" * 80)

for i, f in enumerate(failures, 1):
    print(f"\n{'─' * 80}")
    print(f"FAILURE #{i}: {f['category']}")
    print(f"  Question:     {f['question']}")
    print(f"  LLM Response: {f['response'][:200]}")
    print(f"  Ground Truth: {f['ground_truth'][:200]}")
    print(f"  GT Data:      {f['ground_truth_data'][:200]}")
    print(f"  Routing:      {f['routing']}")
    print(f"  No-data resp: {f['is_no_data']}")
    print(f"  Time:         {f['time_ms']:.0f}ms")

# Categorize root causes
print(f"\n{'=' * 80}")
print("  ROOT CAUSE ANALYSIS")
print("=" * 80)

categories = {
    "SQL_NO_FILTER": [],
    "SQL_WRONG_CALCULATION": [],
    "CONVERSATION_NO_CONTEXT": [],
    "MISCLASSIFIED": [],
}

for f in failures:
    q = f["question"]
    resp = f["response"]

    if f["is_no_data"]:
        categories["MISCLASSIFIED"].append(f)
    elif "his assists" in q or "did he play" in q:
        categories["CONVERSATION_NO_CONTEXT"].append(f)
    elif "Alondes Williams" in resp or "125" in resp or "560" in resp or "190.79" in resp:
        categories["SQL_NO_FILTER"].append(f)
    else:
        categories["SQL_WRONG_CALCULATION"].append(f)

for cat, items in categories.items():
    if items:
        print(f"\n{cat} ({len(items)} cases):")
        for f in items:
            print(f"  - {f['question'][:70]}")
            print(f"    Response: {f['response'][:100]}")
