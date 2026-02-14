#!/usr/bin/env python3
"""
FILE: test_ui_simple.py
STATUS: Active
RESPONSIBILITY: Simple automated UI testing with Playwright
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import subprocess
import time
import sys
import os

def run_test():
    """Run automated UI testing."""
    print("\n" + "="*80)
    print("AUTOMATED UI TESTING - Sports_See")
    print("="*80 + "\n")

    # Step 1: Kill all Python
    print("[1/5] Killing all Python processes...")
    subprocess.run("taskkill /F /IM python.exe 2>nul", shell=True,
                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)

    # Step 2: Start services
    print("[2/5] Starting API (port 8000)...")
    subprocess.Popen(
        "poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
    )
    time.sleep(8)

    print("[3/5] Starting UI (port 8501)...")
    subprocess.Popen(
        "poetry run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=error",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
    )
    time.sleep(10)

    # Step 3: Run Playwright tests
    print("[4/5] Running UI tests with Playwright...")

    try:
        from playwright.sync_api import sync_playwright

        test_cases = [
            ("hi", "Greeting"),
            ("Who is LeBron?", "Biographical"),
            ("top 5 scorers", "Statistical"),
            ("which team was the most exciting?", "Opinion"),
            ("What about Lakers?", "Contextual"),
        ]

        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print(f"Opening http://localhost:8501...")
            page.goto("http://localhost:8501", wait_until="load", timeout=30000)
            time.sleep(5)

            for query, test_name in test_cases:
                print(f"\n  Testing: {test_name}")
                print(f"  Query: '{query}'")

                try:
                    # Find input
                    input_box = page.locator("input").first
                    input_box.fill(query, timeout=5000)
                    input_box.press("Enter")

                    # Wait for response
                    time.sleep(5)

                    # Get response
                    page_content = page.content()

                    # Check for issues
                    issues = []

                    if "[SQL]" in page_content or "[sql]" in page_content.lower():
                        issues.append("Contains [SQL] notation")

                    if "[Source:" in page_content:
                        issues.append("Inline citations found")

                    if len(page_content) < 100:
                        issues.append("Response too short")

                    status = "✅ PASS" if not issues else f"❌ FAIL"
                    print(f"  Result: {status}")

                    if issues:
                        for issue in issues:
                            print(f"    - {issue}")

                    results.append({
                        "test": test_name,
                        "passed": not bool(issues),
                        "issues": issues
                    })

                except Exception as e:
                    print(f"  Result: ❌ ERROR - {str(e)}")
                    results.append({
                        "test": test_name,
                        "passed": False,
                        "issues": [str(e)]
                    })

            browser.close()

        # Step 4: Report
        print("\n" + "="*80)
        print("[5/5] TEST REPORT")
        print("="*80)

        passed = sum(1 for r in results if r["passed"])
        total = len(results)

        print(f"\nResults: {passed}/{total} tests passed\n")

        for result in results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"   - {issue}")

        print("\n" + "="*80)

        return 0 if passed == total else 1

    except ImportError:
        print("❌ Playwright not installed")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_test())
