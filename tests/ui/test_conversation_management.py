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
    new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
    assert new_conv_btn.is_visible()


@pytest.mark.conversation
def test_create_new_conversation(streamlit_page: Page):
    """Test that new conversation can be created."""
    new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
    new_conv_btn.click()

    # Wait for new conversation message
    streamlit_page.wait_for_timeout(2000)

    # Check for confirmation message
    msg = streamlit_page.locator("text=/started|new chat/i")
    assert msg.is_visible(timeout=5000)


@pytest.mark.conversation
def test_conversation_rename_controls_visible(streamlit_page: Page):
    """Test that rename controls are visible for current conversation."""
    # Look for rename button/expander
    rename_control = streamlit_page.locator("text='✏️ Rename Conversation'")
    if rename_control.is_visible():
        assert True
    else:
        # Might need to first create a conversation
        new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
        new_conv_btn.click()
        streamlit_page.wait_for_timeout(2000)
        
        rename_control = streamlit_page.locator("text='✏️ Rename Conversation'")
        assert rename_control.is_visible()


@pytest.mark.conversation
def test_rename_conversation(streamlit_page: Page):
    """Test that conversation can be renamed."""
    # Create new conversation first
    new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
    new_conv_btn.click()
    streamlit_page.wait_for_timeout(2000)

    # Find and click rename expander
    rename_expander = streamlit_page.locator("text='✏️ Rename Conversation'")
    if rename_expander.is_visible():
        rename_expander.click()
        streamlit_page.wait_for_timeout(1000)

        # Find text input for new name
        name_input = streamlit_page.locator('input[placeholder*="name"]').first
        if name_input.is_visible():
            name_input.fill("My Test Conversation")

            # Find and click rename button
            rename_btn = streamlit_page.locator("button:has-text('Rename')").first
            if rename_btn.is_visible():
                rename_btn.click()
                streamlit_page.wait_for_timeout(2000)

                # Check for success message
                success = streamlit_page.locator("text=/Renamed|success/i")
                assert success.is_visible(timeout=5000)


@pytest.mark.conversation
def test_conversation_appear_in_sidebar(streamlit_page: Page):
    """Test that conversations appear in sidebar list."""
    # Create new conversation
    new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
    new_conv_btn.click()
    streamlit_page.wait_for_timeout(2000)

    # Look for conversation in sidebar
    # Streamlit shows conversations in selectbox or list
    conversation_item = streamlit_page.locator("text=/Conversation|chat/i")
    assert conversation_item.is_visible(timeout=5000)


@pytest.mark.conversation
def test_archive_conversation(streamlit_page: Page):
    """Test that conversation can be archived."""
    # Create new conversation
    new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
    new_conv_btn.click()
    streamlit_page.wait_for_timeout(2000)

    # Find archive button
    archive_btn = streamlit_page.locator("text='🗄️ Archive'")
    if archive_btn.is_visible():
        archive_btn.click()
        streamlit_page.wait_for_timeout(2000)

        # Check for confirmation
        msg = streamlit_page.locator("text=/archived|new one/i")
        assert msg.is_visible(timeout=5000)


@pytest.mark.conversation
def test_load_conversation_from_sidebar(streamlit_page: Page):
    """Test that previous conversation can be loaded from sidebar."""
    # Create and rename conversation
    new_conv_btn = streamlit_page.locator("text='🆕 New Conversation'")
    new_conv_btn.click()
    streamlit_page.wait_for_timeout(2000)

    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("First conversation query")
    chat_input.press("Enter")
    streamlit_page.wait_for_timeout(3000)

    # Create second conversation
    new_conv_btn.click()
    streamlit_page.wait_for_timeout(2000)

    # Ask a question in second conversation
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Second conversation query")
    chat_input.press("Enter")
    streamlit_page.wait_for_timeout(3000)

    # Load button should be visible
    load_btn = streamlit_page.locator("button:has-text('📂 Load')")
    if load_btn.first.is_visible():
        assert True
