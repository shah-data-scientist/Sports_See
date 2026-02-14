#!/usr/bin/env python3
"""
FILE: test_ui_fixed.py
STATUS: Active
RESPONSIBILITY: Fixed UI testing with correct textarea input and response verification
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import subprocess
import time
import sys
from playwright.sync_api import sync_playwright


def kill_processes():
    """Kill processes on specific ports."""
    subprocess.run("for /f \"tokens=5\" %%a in ('netstat -ano ^| findstr :8000') do taskkill /PID %%a /F 2>nul",
                  shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run("for /f \"tokens=5\" %%a in ('netstat -ano ^| findstr :8501') do taskkill /PID %%a /F 2>nul",
                  shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)


def start_services():
    """Start API and UI."""
    subprocess.Popen(
        "poetry run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(8)

    subprocess.Popen(
        "poetry run streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0 --logger.level=error",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    time.sleep(10)


def run_tests():
    """Run tests with separate tab for each query - FIXED VERSION."""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        test_cases = [
            ("hi", "Greeting", True),
            ("Who is LeBron?", "Biographical", True),
            ("top 5 scorers", "Statistical", True),
            ("which team was the most exciting?", "Opinion", True),
            ("What about Lakers?", "Contextual", False),
        ]

        results = []
        pages = []

        print("\n" + "="*80)
        print("FIXED UI TEST - CORRECT TEXTAREA INPUT - SEPARATE TAB FOR EACH QUERY")
        print("="*80 + "\n")

        # Create separate page/tab for each test
        for i, (query, test_name, reset_conv) in enumerate(test_cases, 1):
            print(f"\n[{i}/5] Opening Tab: {test_name}")
            print(f"Query: '{query}'")

            # Create new tab
            page = context.new_page()
            pages.append(page)

            # Navigate to UI
            page.goto("http://localhost:8501", wait_until="load", timeout=30000)
            time.sleep(3)

            try:
                # FIXED: Use correct textarea input with "Ask about" placeholder
                # Streamlit's chat_input creates a textarea element
                textarea = page.locator('textarea[placeholder*="Ask about"]').first

                if not textarea.is_visible():
                    raise Exception("Chat input textarea not found!")

                # Submit query to CORRECT input
                textarea.fill(query)
                textarea.press("Enter")

                # Wait for response
                print("Waiting for response...")
                time.sleep(6)

                # Get page content CORRECTLY
                try:
                    page_content = page.locator("body").inner_text()
                except Exception as e:
                    page_content = page.content()

                # Extract response text
                response_text = "No response captured"
                try:
                    # Look for chat messages (Streamlit stores them in divs)
                    # Try to get text after the query
                    if query.lower() in page_content.lower():
                        query_idx = page_content.lower().rfind(query.lower())
                        after_query = page_content[query_idx + len(query):].strip()
                        lines = [l.strip() for l in after_query.split('\n') if l.strip()]

                        # Filter out UI elements
                        response_lines = []
                        for line in lines:
                            # Skip buttons, emojis only, and short noise
                            if (len(line) > 3 and
                                not line.startswith('👍') and
                                not line.startswith('👎') and
                                not line.startswith('Feedback') and
                                not line.startswith('New Conversation')):
                                response_lines.append(line)

                            if len(response_lines) >= 2:
                                break

                        if response_lines:
                            response_text = ' '.join(response_lines)[:200]
                except Exception:
                    pass

                # Check for violations
                violations = []

                # Check if response actually exists (not just checking for absence of [SQL])
                if "No response captured" in response_text or len(page_content) < 200:
                    violations.append("No response generated")

                if "[SQL]" in page_content:
                    violations.append("[SQL] notation present")

                if "[Source:" in page_content:
                    violations.append("Inline citations found")

                # Check for chart/visualization
                has_chart = "plotly" in page_content.lower() or "<svg" in page_content.lower()

                passed = not bool(violations)
                status = "✅ PASS" if passed else "❌ FAIL"
                chart_text = "📊 Chart" if has_chart else ""

                print(f"Result: {status} {chart_text}")
                print(f"Response: {response_text[:100]}...")

                if violations:
                    print("Issues:")
                    for v in violations:
                        print(f"  ❌ {v}")

                results.append({
                    "test": test_name,
                    "query": query,
                    "passed": passed,
                    "violations": violations,
                    "response": response_text,
                    "has_chart": has_chart
                })

            except Exception as e:
                print(f"Error: {str(e)}")
                results.append({
                    "test": test_name,
                    "query": query,
                    "passed": False,
                    "violations": [str(e)],
                    "response": "Error occurred"
                })

        # Keep browser open indefinitely for user review
        print(f"\n{'='*80}")
        print("All tabs open - review the responses in your browser")
        print(f"{'='*80}")
        print("Browser will stay open - close it yourself when done")
        print("\nPress Ctrl+C in this console to close the test when you're ready...\n")

        try:
            # Keep the process running indefinitely
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nClosing browser...")
            context.close()
            browser.close()

        # Print summary
        passed_count = sum(1 for r in results if r["passed"])
        print(f"\n{'='*80}")
        print("FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Passed: {passed_count}/5")
        print(f"Failed: {5-passed_count}/5\n")

        for result in results:
            status = "✅" if result["passed"] else "❌"
            chart = "📊" if result.get("has_chart") else ""
            violations_str = ", ".join(result.get("violations", [])) if result.get("violations") else "None"
            print(f"{status} {result['test']:<15} {chart}")
            print(f"   Issues: {violations_str}")
            print(f"   Response: {result.get('response', 'N/A')[:80]}...")

        print(f"{'='*80}\n")

        return 0 if passed_count == 5 else 1


def main():
    """Main entry point."""
    try:
        print("Killing processes...")
        kill_processes()

        print("Starting services...")
        start_services()

        print("Opening browser with separate tabs for each test - WATCH THE SCREEN!\n")
        return run_tests()

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
