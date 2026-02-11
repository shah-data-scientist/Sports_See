"""
FILE: conftest.py
STATUS: Active
RESPONSIBILITY: Pytest configuration for Playwright UI tests
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import time
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context arguments."""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def page(browser_context_args):
    """Provide a Playwright page for each test."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,  # Run in IDE, not user's PC
            slow_mo=500,  # Slow down by 500ms for visibility
        )
        context = browser.new_context(**browser_context_args)
        page = context.new_page()

        yield page

        # Cleanup
        context.close()
        browser.close()

        # Rate limit protection: Wait 5 seconds between tests
        # Gemini free tier: 15 RPM = 1 request per 4 seconds
        time.sleep(5)
