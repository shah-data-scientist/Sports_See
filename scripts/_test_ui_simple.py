"""
FILE: _test_ui_simple.py
STATUS: Active - Temporary
RESPONSIBILITY: Simple Playwright test with debugging
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

print("\n" + "=" * 80)
print("SIMPLE STREAMLIT UI TEST WITH DEBUGGING")
print("=" * 80)

with sync_playwright() as playwright:
    # Launch browser
    browser = playwright.chromium.launch(headless=False, slow_mo=1000)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    # Navigate to Streamlit
    print("\n[1] Navigating to Streamlit...")
    page.goto("http://localhost:8501")
    time.sleep(3)

    # Check if app loaded
    print("[2] Checking if app loaded...")
    title = page.locator("h1").text_content()
    print(f"    Title: {title}")

    # Find chat input
    print("[3] Finding chat input...")
    chat_input = page.locator("[data-testid='stChatInput']").locator("textarea")
    print(f"    Chat input found: {chat_input.is_visible()}")

    # Submit query
    print("[4] Submitting query: 'Who are the top 5 scorers?'")
    chat_input.fill("Who are the top 5 scorers?")
    chat_input.press("Enter")

    # Wait for response
    print("[5] Waiting for API response (20 seconds)...")
    time.sleep(20)

    # Check messages
    print("[6] Checking messages...")
    messages = page.locator("[data-testid='stChatMessage']").all()
    print(f"    Message count: {len(messages)}")

    # Look for visualization - try multiple selectors
    print("[7] Looking for visualization...")

    selectors_to_try = [
        ".plotly-graph-div",
        "[class*='plotly']",
        "iframe",  # Streamlit might use iframe
        "[data-testid='stPlotlyChart']",
        ".stPlotlyChart",
    ]

    for selector in selectors_to_try:
        elements = page.locator(selector).all()
        if elements:
            print(f"    ✓ Found {len(elements)} elements with selector: {selector}")
        else:
            print(f"    ✗ No elements found with selector: {selector}")

    # Get page HTML to see what's actually there
    print("\n[8] Dumping page HTML (looking for plotly/viz references)...")
    html_content = page.content()

    if "plotly" in html_content.lower():
        print("    ✓ 'plotly' found in page HTML")
    else:
        print("    ✗ 'plotly' NOT found in page HTML")

    if "visualization" in html_content.lower():
        print("    ✓ 'visualization' found in page HTML")
    else:
        print("    ✗ 'visualization' NOT found in page HTML")

    # Check for error messages
    errors = page.locator("[data-testid='stException']").all()
    if errors:
        print(f"\n⚠️  Found {len(errors)} error(s) on page:")
        for error in errors:
            print(f"    {error.text_content()[:200]}")

    # Take screenshot
    screenshot_path = Path(__file__).parent.parent / "test_screenshots" / "debug_ui_test.png"
    screenshot_path.parent.mkdir(exist_ok=True)
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"\n[9] Screenshot saved: {screenshot_path}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE - Press Enter to close browser")
    print("=" * 80)
    input()

    browser.close()
