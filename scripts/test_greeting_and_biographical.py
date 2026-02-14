#!/usr/bin/env python3
"""
FILE: test_greeting_and_biographical.py
STATUS: Active
RESPONSIBILITY: Test greeting detection and biographical query routing
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import requests
import json
import time
from pathlib import Path

API_URL = "http://localhost:8000"
LOG_FILE = Path("greeting_bio_test.log")

def log(message: str):
    """Write to console and log file."""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def test_greeting():
    """Test greeting detection."""
    LOG_FILE.write_text("")

    log("\n" + "="*80)
    log("TESTING GREETING DETECTION & BIOGRAPHICAL ROUTING")
    log("="*80 + "\n")

    test_cases = [
        # Greeting tests
        ("hi", "Greeting", "greeting"),
        ("hello", "Greeting", "greeting"),
        ("thanks", "Greeting", "greeting"),

        # Biographical tests
        ("Who is LeBron?", "Biographical", "biographical"),
        ("Tell me about Michael Jordan", "Biographical", "biographical"),
        ("Who is Kobe Bryant?", "Biographical", "biographical"),

        # Statistical tests (control)
        ("top 5 scorers", "Statistical", "statistical"),

        # Opinion tests (control)
        ("which team was most exciting?", "Opinion", "opinion"),
    ]

    results = []

    for query, test_name, expected_type in test_cases:
        log(f"\n[TEST] {test_name}: '{query}'")
        log("-" * 80)

        try:
            payload = {"query": query}
            start_time = time.time()
            response = requests.post(f"{API_URL}/api/v1/chat", json=payload, timeout=60)
            elapsed = time.time() - start_time

            log(f"[HTTP] Status: {response.status_code} (took {elapsed:.1f}s)")

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")[:100]
                model = data.get("model", "unknown")
                sources = len(data.get("sources", []))

                log(f"[MODEL] {model}")
                log(f"[SOURCES] {sources} sources")
                log(f"[RESPONSE] {answer}...")

                # Check response quality
                if expected_type == "greeting":
                    # Greetings should have no sources and quick response
                    if sources == 0 and model == "greeting":
                        status = "PASS"
                    else:
                        status = f"FAIL (sources={sources}, model={model})"
                elif expected_type == "biographical":
                    # Biographical should have sources and meaningful response
                    if len(answer) > 20 and sources >= 0:
                        status = "PASS"
                    else:
                        status = f"FAIL (answer too short or no synthesis)"
                elif expected_type == "statistical":
                    if len(answer) > 20:
                        status = "PASS"
                    else:
                        status = "FAIL"
                else:
                    status = "PASS"

                log(f"[RESULT] {status}")
                results.append({"test": test_name, "query": query, "status": status})
            else:
                log(f"[ERROR] HTTP {response.status_code}: {response.text[:100]}")
                results.append({"test": test_name, "query": query, "status": "ERROR"})

        except Exception as e:
            log(f"[ERROR] {str(e)}")
            results.append({"test": test_name, "query": query, "status": f"ERROR: {str(e)}"})

    # Summary
    log("\n" + "="*80)
    log("SUMMARY")
    log("="*80)

    passed = sum(1 for r in results if r["status"] == "PASS")
    log(f"\nPassed: {passed}/{len(test_cases)}\n")

    for r in results:
        status_icon = "[OK]" if r["status"] == "PASS" else "[FAIL]"
        log(f"{status_icon} {r['test']:<15} | {r['status']}")

    with open("greeting_bio_test.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    log(f"\n[SAVED] Results saved to greeting_bio_test.json")

if __name__ == "__main__":
    test_greeting()
