#!/usr/bin/env python3
"""
FILE: test_ui_proper.py
STATUS: Active
RESPONSIBILITY: Proper UI testing that correctly extracts full responses
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import subprocess
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

LOG_FILE = Path("ui_test_proper.log")
JSON_FILE = Path("ui_test_proper.json")

def log(message: str):
    """Write to console and log file."""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def start_services():
    """Start services."""
    log("[SERVICES] Starting API...")
    subprocess.Popen(
        "poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(8)

    log("[SERVICES] Starting UI...")
    subprocess.Popen(
        "poetry run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=error",
        shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(10)
    log("[SERVICES] Both services started\n")

def run_tests():
    """Run UI tests with proper response extraction."""
    LOG_FILE.write_text("")

    log("="*80)
    log("UI TESTING - PROPER RESPONSE EXTRACTION")
    log("="*80 + "\n")

    start_services()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        test_cases = [
            ("hi", "Greeting"),
            ("Who is LeBron?", "Biographical"),
            ("top 5 scorers", "Statistical"),
            ("which team was the most exciting?", "Opinion"),
        ]

        results = []

        for i, (query, test_name) in enumerate(test_cases, 1):
            log(f"\n[TEST {i}/4] {test_name}: '{query}'")
            log("-" * 80)

            try:
                page = context.new_page()
                page.goto("http://localhost:8501", wait_until="load", timeout=30000)
                time.sleep(2)

                # Find textarea and submit query
                textarea = page.locator('textarea[placeholder*="Ask about"]').first
                if not textarea.is_visible():
                    log("[ERROR] Textarea not found")
                    results.append({"test": test_name, "query": query, "status": "FAIL", "response": "Textarea not found"})
                    continue

                textarea.fill(query)
                textarea.press("Enter")
                log("[INPUT] Query submitted")

                # Wait for response (30 seconds)
                log("[WAIT] Waiting 30s for response...")
                time.sleep(30)

                # Extract ALL text from the page
                page_text = page.locator("body").inner_text()

                # Find the response by locating query and extracting text after it
                response_text = ""
                if query.lower() in page_text.lower():
                    # Find where query appears
                    query_lower_idx = page_text.lower().rfind(query.lower())
                    after_query = page_text[query_lower_idx + len(query):].strip()

                    # Get all lines after query
                    lines = after_query.split('\n')
                    response_lines = []

                    for line in lines:
                        line = line.strip()
                        # Skip empty lines, buttons, feedback UI elements
                        if not line:
                            continue
                        if line.startswith(('👍', '👎', 'Feedback', 'New Conversation', 'Settings')):
                            continue
                        if any(x in line for x in ['⏱️', 'Model:', 'Results:', 'Temperature:', 'API:']):
                            continue

                        response_lines.append(line)
                        if len(response_lines) >= 5:  # Get first 5 meaningful lines
                            break

                    response_text = ' '.join(response_lines)

                if response_text:
                    log(f"[RESPONSE] {response_text[:100]}...")
                    status = "PASS"
                else:
                    log("[RESPONSE] No response found")
                    status = "FAIL"

                log(f"[RESULT] {status}")
                results.append({
                    "test": test_name,
                    "query": query,
                    "status": status,
                    "response": response_text[:200]
                })

                page.close()

            except Exception as e:
                log(f"[ERROR] {str(e)}")
                results.append({
                    "test": test_name,
                    "query": query,
                    "status": "ERROR",
                    "response": str(e)[:100]
                })

        context.close()
        browser.close()

        # Summary
        log("\n" + "="*80)
        log("SUMMARY")
        log("="*80)

        passed = sum(1 for r in results if r["status"] == "PASS")
        log(f"\nPassed: {passed}/{len(test_cases)}\n")

        for r in results:
            icon = "[OK]" if r["status"] == "PASS" else "[FAIL]"
            log(f"{icon} {r['test']:<15} | {r['response'][:60]}...")

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        log(f"\nResults saved to: {JSON_FILE}")

if __name__ == "__main__":
    run_tests()
