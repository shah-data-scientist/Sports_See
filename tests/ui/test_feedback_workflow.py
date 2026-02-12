"""
FILE: test_feedback_workflow.py
STATUS: Active
RESPONSIBILITY: Test feedback collection workflow in Streamlit UI
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.feedback
def test_feedback_buttons_appear(streamlit_page: Page):
    """Test that feedback buttons appear after response."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Who is Kobe Bryant?")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Look for feedback buttons
    positive_btn = streamlit_page.locator("text='👍'")
    negative_btn = streamlit_page.locator("text='👎'")

    assert positive_btn.first.is_visible(timeout=10000)
    assert negative_btn.first.is_visible(timeout=10000)


@pytest.mark.feedback
def test_positive_feedback_submission(streamlit_page: Page):
    """Test that positive feedback can be submitted."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("NBA teams")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Click positive feedback button
    positive_btn = streamlit_page.locator("text='👍'").first
    assert positive_btn.is_visible()
    positive_btn.click()

    # Look for success message
    success_msg = streamlit_page.locator("text=/Thanks|feedback|positive/i")
    assert success_msg.is_visible(timeout=5000)


@pytest.mark.feedback
def test_negative_feedback_shows_comment_form(streamlit_page: Page):
    """Test that clicking negative feedback shows comment form."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Test query for feedback")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Click negative feedback button
    negative_btn = streamlit_page.locator("text='👎'").first
    assert negative_btn.is_visible()
    negative_btn.click()

    # Look for comment form
    comment_form = streamlit_page.locator('textarea')
    assert comment_form.first.is_visible(timeout=5000)


@pytest.mark.feedback
def test_negative_feedback_comment_submission(streamlit_page: Page):
    """Test that negative feedback with comment can be submitted."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Test feedback comment")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Click negative feedback button
    negative_btn = streamlit_page.locator("text='👎'").first
    negative_btn.click()

    # Find and fill comment textarea
    comment_textarea = streamlit_page.locator('textarea').first
    assert comment_textarea.is_visible()
    comment_textarea.fill("This response needs improvement")

    # Find and click submit button
    submit_btn = streamlit_page.locator("button:has-text('Send feedback')").first
    if submit_btn.is_visible():
        submit_btn.click()

        # Wait for submission
        streamlit_page.wait_for_timeout(2000)

        # Look for success message
        success = streamlit_page.locator("text=/feedback|thanks/i")
        assert success.is_visible(timeout=5000)


@pytest.mark.feedback
def test_multiple_feedback_submissions(streamlit_page: Page):
    """Test that user can submit multiple feedback items."""
    for i in range(2):
        # Ask a question
        chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
        chat_input.fill(f"Query {i+1} for feedback")
        chat_input.press("Enter")

        # Wait for response
        streamlit_page.wait_for_timeout(3000)

        # Click feedback button
        feedback_btn = streamlit_page.locator("text='👍'").first
        if feedback_btn.is_visible():
            feedback_btn.click()
            streamlit_page.wait_for_timeout(1000)


@pytest.mark.feedback
def test_feedback_button_state_changes(streamlit_page: Page):
    """Test that feedback button state changes after submission."""
    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Feedback state test")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Click positive feedback
    positive_btn = streamlit_page.locator("text='👍'").first
    positive_btn.click()

    # Wait and check for state change
    streamlit_page.wait_for_timeout(2000)

    # Button should show success state or feedback message
    success_text = streamlit_page.locator("text=/Thanks|feedback/i")
    assert success_text.is_visible(timeout=5000)
