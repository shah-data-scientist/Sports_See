#!/usr/bin/env python3
"""
FILE: test_ui_with_logging.py
STATUS: Active
RESPONSIBILITY: UI testing with detailed file logging so results can be verified
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import subprocess
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

# Log file for results - use UTF-8 encoding
LOG_FILE = Path("test_results.log")
JSON_FILE = Path("test_results.json")


def log(message: str):
    """Write to both console and log file with UTF-8 encoding."""
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def start_services():
    """Start API and UI."""
    log("[SERVICES] Starting API on port 8000...")
    subprocess.Popen(
        "poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(8)
    log("[SERVICES] ✓ API started")

    log("[SERVICES] Starting UI on port 8501...")
    subprocess.Popen(
        "poetry run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=error",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(10)
    log("[SERVICES] ✓ UI started")


def run_tests():
    """Run tests with detailed logging."""

    # Clear previous logs
    LOG_FILE.write_text("")

    log("\n" + "="*80)
    log("DETAILED UI TEST WITH LOGGING")
    log("="*80 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        test_cases = [
            ("hi", "Greeting", False),
            ("Who is LeBron?", "Biographical", False),
            ("top 5 scorers", "Statistical", False),
            ("which team was the most exciting?", "Opinion", False),
            ("What about Lakers?", "Follow-up (in same conversation)", True),  # True = follow-up to previous
        ]

        results = []
        opinion_page = None  # Will store the page from Opinion test for follow-up

        for i, (query, test_name, is_followup) in enumerate(test_cases, 1):
            log(f"\n[TAB {i}/5] {test_name}")
            log(f"Query: '{query}'")
            log("-" * 80)

            try:
                # Use same page for follow-up, new page for initial queries
                if is_followup and opinion_page:
                    page = opinion_page
                    log("[PAGE] Using same conversation (follow-up)")
                else:
                    page = context.new_page()
                    page.goto("http://localhost:8501", wait_until="load", timeout=30000)
                    log("[PAGE] Loaded UI at http://localhost:8501")

                    # Save opinion page for follow-up
                    if test_name == "Opinion":
                        opinion_page = page

                time.sleep(3)

                # Find and fill the textarea
                textarea = page.locator('textarea[placeholder*="Ask about"]').first

                if not textarea.is_visible():
                    log("[ERROR] FAIL: Textarea not found!")
                    results.append({"test": test_name, "query": query, "status": "FAIL", "error": "Textarea not found"})
                    continue

                log("[INPUT] Found textarea, entering query...")
                textarea.fill(query)
                textarea.press("Enter")
                log("[INPUT] PASS: Query submitted")

                # Wait for response (30 seconds to allow LLM to generate)
                log("[WAIT] Waiting 30 seconds for LLM response...")
                time.sleep(30)

                # Get page content
                try:
                    page_text = page.locator("body").inner_text()
                except:
                    page_text = page.content()

                # Extract response
                log("[EXTRACT] Extracting response from page...")

                # Look for response after the query
                response_found = False
                response_text = ""

                if query.lower() in page_text.lower():
                    query_idx = page_text.lower().rfind(query.lower())
                    after_query = page_text[query_idx + len(query):].strip()
                    lines = [l.strip() for l in after_query.split('\n') if l.strip()]

                    # Get first substantial line after query
                    for line in lines:
                        if len(line) > 10 and not line.startswith(('👍', '👎', 'Feedback', 'New')):
                            response_text = line[:150]
                            response_found = True
                            break

                # Check if we got actual response or just loading indicator
                if "Searching" in response_text or "searching" in response_text or len(response_text) < 20:
                    log(f"[RESPONSE] FAIL: Got loading state, not actual response: '{response_text}'")
                    status = "FAIL"
                elif response_found:
                    log(f"[RESPONSE] PASS: Found real response: '{response_text}...'")
                    status = "PASS"
                else:
                    log("[RESPONSE] FAIL: No response found!")
                    status = "FAIL"

                # Check for violations
                violations = []
                if "[SQL]" in page_text:
                    violations.append("[SQL] notation present")
                if "[Source:" in page_text:
                    violations.append("Inline citations found")

                if violations:
                    log(f"[VIOLATIONS] Issues found: {', '.join(violations)}")
                    status = "FAIL"

                log(f"[RESULT] Status: {status}")

                results.append({
                    "test": test_name,
                    "query": query,
                    "status": status,
                    "response": response_text,
                    "violations": violations
                })

            except Exception as e:
                log(f"❌ ERROR: {str(e)}")
                results.append({
                    "test": test_name,
                    "query": query,
                    "status": "ERROR",
                    "error": str(e)
                })

        # Close browser
        context.close()
        browser.close()

        # Write summary
        log("\n" + "="*80)
        log("SUMMARY")
        log("="*80)

        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        errors = sum(1 for r in results if r["status"] == "ERROR")

        log(f"\nPassed: {passed}/5")
        log(f"Failed: {failed}/5")
        log(f"Errors: {errors}/5\n")

        for r in results:
            status_icon = "[OK]" if r["status"] == "PASS" else ("[FAIL]" if r["status"] == "FAIL" else "[ERR]")
            log(f"{status_icon} {r['test']:<15} | {r['query']:<30} | {r['status']}")
            if "response" in r and r["response"]:
                log(f"   Response: {r['response'][:80]}...")

        # Save JSON results
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        log(f"\n[SAVED] Full results saved to: {JSON_FILE}")

        return 0 if failed == 0 else 1


def main():
    """Main entry point."""
    try:
        log("Starting fresh services...")
        start_services()

        log("\nRunning tests...")
        return run_tests()

    except Exception as e:
        log(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
