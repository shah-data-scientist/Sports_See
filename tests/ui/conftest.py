"""
FILE: conftest.py
STATUS: Active
RESPONSIBILITY: Playwright fixtures and configuration for UI tests
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import pytest
import time
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context arguments."""
    return {
        "ignore_https_errors": True,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def streamlit_page(page: Page) -> Page:
    """
    Fixture that opens Streamlit app and waits for it to load.

    Args:
        page: Playwright page fixture

    Yields:
        Page object with Streamlit app loaded
    """
    # Navigate to Streamlit app
    page.goto("http://localhost:8505", wait_until="networkidle")

    # Wait for main content to load
    page.wait_for_selector("text='Ask about'", timeout=10000)

    # Small delay to ensure Streamlit is fully ready
    time.sleep(1)

    yield page


@pytest.fixture
def api_base_url() -> str:
    """
    Return API base URL for direct API tests.

    Returns:
        API base URL
    """
    return "http://localhost:8000/api/v1"


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "chat: Chat functionality tests")
    config.addinivalue_line("markers", "feedback: Feedback workflow tests")
    config.addinivalue_line("markers", "conversation: Conversation management tests")
    config.addinivalue_line("markers", "error_handling: Error handling tests")
    config.addinivalue_line("markers", "statistics: Statistics display tests")
    config.addinivalue_line("markers", "rich_conversation: Rich conversation tests")
    config.addinivalue_line("markers", "sources: Source verification tests")
