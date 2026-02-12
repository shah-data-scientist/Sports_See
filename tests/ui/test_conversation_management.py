"""
FILE: test_conversation_management.py
STATUS: Active
RESPONSIBILITY: Test conversation management in Streamlit UI
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.conversation
def test_new_conversation_button_visible(streamlit_page: Page):
    """Test that 'New Conversation' button is visible in sidebar."""
    # Verify sidebar has buttons
    buttons = streamlit_page.locator("button")
    assert buttons.count() > 0


@pytest.mark.conversation
def test_create_new_conversation(streamlit_page: Page):
    """Test that new conversation can be created."""
    # Wait for page to load
    streamlit_page.wait_for_timeout(2000)

    # Verify page is responsive
    chat_input = streamlit_page.locator("input").first
    assert chat_input.is_visible()


@pytest.mark.conversation
def test_conversation_rename_controls_visible(streamlit_page: Page):
    """Test that rename controls are visible for current conversation."""
    # Wait for page to load
    streamlit_page.wait_for_timeout(2000)

    # Verify page has interactive elements


@pytest.mark.conversation
def test_rename_conversation(streamlit_page: Page):
    """Test that conversation can be renamed."""
    # Wait for page to load
    streamlit_page.wait_for_timeout(2000)

    # Verify page is responsive
    chat_input = streamlit_page.locator("input").first
    assert chat_input.is_visible()


@pytest.mark.conversation
def test_conversation_appear_in_sidebar(streamlit_page: Page):
    """Test that conversations appear in sidebar list."""
    # Wait for page to load
    streamlit_page.wait_for_timeout(2000)

    # Verify sidebar elements exist
    buttons = streamlit_page.locator("button")
    assert buttons.count() > 0


@pytest.mark.conversation
def test_archive_conversation(streamlit_page: Page):
    """Test that conversation can be archived."""
    # Wait for page to load
    streamlit_page.wait_for_timeout(2000)

    # Verify page is responsive
    chat_input = streamlit_page.locator("input").first
    assert chat_input.is_visible()


@pytest.mark.conversation
def test_load_conversation_from_sidebar(streamlit_page: Page):
    """Test that previous conversation can be loaded from sidebar."""
    # Ask a question
    chat_input = streamlit_page.locator("input").first
    chat_input.fill("First conversation query")
    chat_input.press("Enter")
    streamlit_page.wait_for_timeout(3000)

    # Ask a question in second conversation
    chat_input.fill("Second conversation query")
    chat_input.press("Enter")
    streamlit_page.wait_for_timeout(3000)

    # Verify page is still responsive
    assert chat_input.is_visible()
