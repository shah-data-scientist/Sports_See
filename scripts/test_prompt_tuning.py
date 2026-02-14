"""
Quick test: Run 5 diverse vector test cases through the API and compare to ground truth.
Tests the tuned CONTEXTUAL_PROMPT for better ground truth alignment.
"""

import json
import sys
import io
import time
import logging

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(level=logging.WARNING)

from starlette.testclient import TestClient
from src.api.main import create_app
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES

# 5 diverse test indices:
# 0  = Reddit opinion (SIMPLE): "What do Reddit users think about teams that impressed?"
# 2  = Reggie Miller efficiency (SIMPLE): "What do fans debate about Reggie Miller's efficiency?"
# 12 = Glossary definition (SIMPLE): "What is a pick and roll?"
# 15 = Out-of-scope weather (NOISY): "What is the weather forecast for LA?"
# 28 = Fan discussion (CONVERSATIONAL): "What do fans say about the Lakers?"
TEST_INDICES = [0, 2, 12, 15, 28]

DELAY_BETWEEN = 20  # seconds (Gemini rate limit)


def run_test():
    app = create_app()
    results = []

    with TestClient(app) as client:
        for idx in TEST_INDICES:
            tc = EVALUATION_TEST_CASES[idx]
            print(f"\n{'='*80}")
            print(f"TEST {idx}: [{tc.category.value}] {tc.question}")
            print(f"{'='*80}")

            # Rate limit
            if results:
                print(f"  (waiting {DELAY_BETWEEN}s for rate limit...)")
                time.sleep(DELAY_BETWEEN)

            payload = {
                "query": tc.question,
                "k": 5,
                "include_sources": True,
            }

            try:
                resp = client.post("/api/v1/chat", json=payload, timeout=60)
                if resp.status_code != 200:
                    print(f"  ERROR: {resp.status_code} - {resp.text[:300]}")
                    results.append({"index": idx, "success": False, "error": resp.text[:300]})
                    continue

                data = resp.json()
                answer = data.get("answer", "")
                sources = data.get("sources", [])
                proc_time = data.get("processing_time_ms", 0)

                print(f"\nRESPONSE ({proc_time}ms, {len(sources)} sources):")
                print(f"  {answer[:500]}...")

                print(f"\nSOURCES:")
                for s in sources[:3]:
                    print(f"  - {s.get('source', 'unknown')} (score: {s.get('score', 0):.1f}%)")

                print(f"\nGROUND TRUTH EXPECTS:")
                print(f"  {tc.ground_truth[:300]}...")

                # Quick alignment check
                gt_lower = tc.ground_truth.lower()
                answer_lower = answer.lower()

                # Extract key terms from ground truth
                checks = []
                if "reddit 1" in gt_lower or "mannerSuperb" in gt_lower.lower():
                    checks.append(("Magic/Pacers/Wolves mention", any(t in answer_lower for t in ["magic", "pacers", "wolves", "timberwolves"])))
                if "reggie miller" in gt_lower:
                    checks.append(("Reggie Miller mentioned", "reggie" in answer_lower or "miller" in answer_lower))
                if "ts%" in gt_lower:
                    checks.append(("TS% mentioned", "ts%" in answer_lower or "true shooting" in answer_lower))
                if "pick and roll" in gt_lower:
                    checks.append(("Pick and roll defined", "pick" in answer_lower and "roll" in answer_lower))
                if "out-of-scope" in gt_lower or "don't have information" in gt_lower.lower():
                    checks.append(("Declined out-of-scope", any(t in answer_lower for t in ["don't have information", "knowledge base", "nba basketball only", "cannot find"])))
                if "lakers" in gt_lower:
                    checks.append(("Lakers mentioned", "lakers" in answer_lower))

                if checks:
                    print(f"\nALIGNMENT CHECKS:")
                    for check_name, passed in checks:
                        status = "PASS" if passed else "FAIL"
                        print(f"  [{status}] {check_name}")

                results.append({
                    "index": idx,
                    "question": tc.question,
                    "category": tc.category.value,
                    "success": True,
                    "answer_preview": answer[:300],
                    "sources_count": len(sources),
                    "processing_time_ms": proc_time,
                    "checks": {name: passed for name, passed in checks} if checks else {}
                })

            except Exception as e:
                print(f"  EXCEPTION: {e}")
                results.append({"index": idx, "success": False, "error": str(e)})

    # Summary
    print(f"\n\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    total_checks = 0
    passed_checks = 0
    for r in results:
        status = "OK" if r["success"] else "FAIL"
        print(f"  [{status}] Test {r['index']}: {r.get('question', 'N/A')[:50]}")
        for check_name, passed in r.get("checks", {}).items():
            total_checks += 1
            if passed:
                passed_checks += 1
            print(f"    {'PASS' if passed else 'FAIL'}: {check_name}")

    if total_checks:
        print(f"\nAlignment: {passed_checks}/{total_checks} checks passed ({passed_checks/total_checks*100:.0f}%)")


if __name__ == "__main__":
    run_test()
