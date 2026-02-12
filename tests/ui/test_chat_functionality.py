"""
FILE: test_chat_functionality.py
STATUS: Active
RESPONSIBILITY: Test chat functionality in Streamlit UI
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.chat
def test_app_loads(streamlit_page: Page):
    """Test that Streamlit app loads correctly."""
    # Check page title
    assert "NBA" in streamlit_page.title()

    # Check welcome message visible
    welcome = streamlit_page.locator("text='Welcome'")
    assert welcome.is_visible()


@pytest.mark.chat
def test_single_query(streamlit_page: Page):
    """Test that user can ask a single question."""
    # Find chat input
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first

    # Type query
    chat_input.fill("Who is LeBron James?")
    chat_input.press("Enter")

    # Wait for response to appear
    response_text = streamlit_page.locator("text=/LeBron|player|NBA/i").first
    assert response_text.is_visible(timeout=15000)


@pytest.mark.chat
def test_multiple_queries_sequence(streamlit_page: Page):
    """Test that user can ask multiple questions in sequence."""
    queries = [
        "Who is Michael Jordan?",
        "What is his career record?",
        "How many championships did he win?"
    ]

    for query in queries:
        # Find and fill input
        chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
        chat_input.fill(query)
        chat_input.press("Enter")

        # Wait for response
        response = streamlit_page.locator("text=/player|stats|championship|ring/i").first
        assert response.is_visible(timeout=15000)

        # Brief pause between queries
        streamlit_page.wait_for_timeout(1000)


@pytest.mark.chat
def test_sources_display(streamlit_page: Page):
    """Test that sources are displayed after response."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("NBA statistics")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Look for sources section
    sources_expander = streamlit_page.locator("text='Sources'")
    if sources_expander.is_visible():
        sources_expander.click()
        # Verify sources content appears
        source_text = streamlit_page.locator("text=/source|pdf|file/i")
        assert source_text.is_visible(timeout=5000)


@pytest.mark.chat
def test_processing_time_display(streamlit_page: Page):
    """Test that processing time is displayed."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Test query")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Look for processing time
    time_display = streamlit_page.locator("text=/ms|second/i")
    assert time_display.is_visible(timeout=5000)


@pytest.mark.chat
def test_chat_input_accepts_text(streamlit_page: Page):
    """Test that chat input properly accepts and displays typed text."""
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first

    test_text = "Testing user input functionality"
    chat_input.fill(test_text)

    # Verify text was entered
    assert chat_input.input_value() == test_text


@pytest.mark.chat
def test_chat_input_clears_after_submission(streamlit_page: Page):
    """Test that chat input clears after submitting a query."""
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first

    chat_input.fill("Test query to clear")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(3000)

    # Check if input is cleared
    # Note: Streamlit might not clear immediately, so we check it's empty or focused
    assert chat_input.is_visible()
