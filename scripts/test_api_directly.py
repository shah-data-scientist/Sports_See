#!/usr/bin/env python3
"""
FILE: test_api_directly.py
STATUS: Active
RESPONSIBILITY: Test API endpoint directly without UI layer
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import requests
import json
import time
from pathlib import Path

API_URL = "http://localhost:8000"
LOG_FILE = Path("api_test_results.log")

def log(message: str):
    """Write to console and log file."""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def test_api():
    """Test API directly."""
    LOG_FILE.write_text("")  # Clear log

    log("\n" + "="*80)
    log("DIRECT API TEST (No UI Layer)")
    log("="*80 + "\n")

    test_queries = [
        ("hi", "Greeting"),
        ("Who is LeBron?", "Biographical"),
        ("top 5 scorers", "Statistical"),
        ("which team was the most exciting?", "Opinion"),
    ]

    results = []

    for query, test_name in test_queries:
        log(f"\n[TEST] {test_name}")
        log(f"Query: '{query}'")
        log("-" * 80)

        try:
            # Make direct API request
            log("[API] Sending request to POST /api/v1/chat...")

            payload = {
                "query": query
                # Let API use defaults for conversation_id and k
            }

            start_time = time.time()
            response = requests.post(
                f"{API_URL}/api/v1/chat",
                json=payload,
                timeout=60
            )
            elapsed = time.time() - start_time

            log(f"[API] Response status: {response.status_code} (took {elapsed:.1f}s)")

            if response.status_code == 200:
                data = response.json()
                log(f"[API] Status code: 200 OK")

                # Extract response (API returns 'answer' field)
                if "answer" in data:
                    resp_text = data["answer"][:150]
                    log(f"[RESPONSE] {resp_text}...")

                    if "Searching" in resp_text or "cannot find" in resp_text.lower() or len(resp_text) < 20:
                        status = "FAIL (No useful response)"
                    else:
                        status = "PASS"
                    resp_text_full = data["answer"][:200]  # Store full for logging
                else:
                    log(f"[ERROR] No 'answer' field in JSON: {list(data.keys())}")
                    status = "FAIL"
                    resp_text_full = str(data)[:100]

            else:
                log(f"[ERROR] HTTP {response.status_code}")
                log(f"Response: {response.text[:200]}")
                status = "FAIL"
                resp_text = f"HTTP {response.status_code}"

            log(f"[RESULT] {status}")
            results.append({
                "test": test_name,
                "query": query,
                "status": status,
                "response": resp_text_full if 'resp_text_full' in locals() else str(response.status_code)
            })

        except Exception as e:
            log(f"[ERROR] {str(e)}")
            results.append({
                "test": test_name,
                "query": query,
                "status": "ERROR",
                "response": str(e)
            })

    # Summary
    log("\n" + "="*80)
    log("SUMMARY")
    log("="*80)

    passed = sum(1 for r in results if "PASS" in r["status"])
    log(f"\nPassed: {passed}/{len(test_queries)}")

    for r in results:
        status_icon = "[OK]" if "PASS" in r["status"] else "[FAIL]"
        log(f"{status_icon} {r['test']:<15} | {r['response'][:60]}...")

    with open("api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    log(f"\n[SAVED] Results saved to api_test_results.json")

if __name__ == "__main__":
    test_api()
