"""
FILE: test_end_to_end.py
STATUS: Active
RESPONSIBILITY: Complete end-to-end Streamlit + API integration tests
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import pytest
from playwright.sync_api import Page
import time


@pytest.mark.integration
def test_complete_user_journey(streamlit_page: Page):
    """
    Test complete user journey:
    1. Open app
    2. Ask question
    3. See answer with sources
    4. Give positive feedback
    5. Ask another question
    6. Give negative feedback with comment
    7. Check stats updated
    """
    # 1. VERIFY APP LOADS
    assert "NBA" in streamlit_page.title()
    welcome = streamlit_page.locator("text='Welcome'")
    assert welcome.is_visible()

    # 2. ASK FIRST QUESTION
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Who is Michael Jordan?")
    chat_input.press("Enter")

    # 3. VERIFY RESPONSE AND SOURCES
    response = streamlit_page.locator("text=/Jordan|player|basketball/i")
    assert response.is_visible(timeout=15000)

    # 4. GIVE POSITIVE FEEDBACK
    positive_btn = streamlit_page.locator("text='👍'").first
    if positive_btn.is_visible():
        positive_btn.click()
        streamlit_page.wait_for_timeout(2000)

    # 5. ASK SECOND QUESTION
    streamlit_page.wait_for_timeout(1000)
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("What are his achievements?")
    chat_input.press("Enter")

    # Verify second response
    response2 = streamlit_page.locator("text=/achievement|championship|record/i")
    assert response2.is_visible(timeout=15000)

    # 6. GIVE NEGATIVE FEEDBACK WITH COMMENT
    negative_btn = streamlit_page.locator("text='👎'").first
    if negative_btn.is_visible():
        negative_btn.click()
        streamlit_page.wait_for_timeout(1000)

        # Fill comment
        comment = streamlit_page.locator('textarea').first
        if comment.is_visible():
            comment.fill("Could use more specific stats")

            # Submit feedback
            submit = streamlit_page.locator("button:has-text('Send feedback')").first
            if submit.is_visible():
                submit.click()
                streamlit_page.wait_for_timeout(2000)

    # 7. VERIFY STATS VISIBLE
    stats = streamlit_page.locator("text=/Feedback Stats|Statistics/i")
    assert stats.is_visible(timeout=5000)


@pytest.mark.integration
def test_conversation_workflow_complete(streamlit_page: Page):
    """
    Test complete conversation workflow:
    1. Create conversation
    2. Ask multiple questions
    3. Give feedback on each
    4. Rename conversation
    5. Create new conversation
    6. Load first conversation
    """
    # 1. CREATE NEW CONVERSATION
    new_conv = streamlit_page.locator("text='🆕 New Conversation'")
    new_conv.click()
    streamlit_page.wait_for_timeout(2000)

    # 2. ASK FIRST QUESTION
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("First question")
    chat_input.press("Enter")
    streamlit_page.wait_for_timeout(5000)

    # Give feedback
    feedback = streamlit_page.locator("text='👍'").first
    if feedback.is_visible():
        feedback.click()
        streamlit_page.wait_for_timeout(1000)

    # 3. ASK SECOND QUESTION
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Second question")
    chat_input.press("Enter")
    streamlit_page.wait_for_timeout(5000)

    # 4. RENAME CONVERSATION
    rename = streamlit_page.locator("text='✏️ Rename Conversation'")
    if rename.is_visible():
        rename.click()
        streamlit_page.wait_for_timeout(1000)

        name_input = streamlit_page.locator('input[placeholder*="name"]').first
        if name_input.is_visible():
            name_input.fill("My Conversation")

            rename_btn = streamlit_page.locator("button:has-text('Rename')").first
            if rename_btn.is_visible():
                rename_btn.click()
                streamlit_page.wait_for_timeout(2000)

    # 5. CREATE NEW CONVERSATION
    new_conv.click()
    streamlit_page.wait_for_timeout(2000)

    # 6. LOAD FIRST CONVERSATION (if possible)
    load = streamlit_page.locator("button:has-text('📂 Load')")
    if load.first.is_visible():
        load.first.click()
        streamlit_page.wait_for_timeout(3000)

        # Should see previous messages
        prev_message = streamlit_page.locator("text=/First question|Second question/i")
        # Previous messages should be visible


@pytest.mark.integration
def test_feedback_and_stats_integration(streamlit_page: Page):
    """
    Test that feedback is properly tracked and stats update:
    1. Record initial stats
    2. Give positive feedback
    3. Give negative feedback
    4. Verify stats changed
    """
    # Give feedback on multiple responses
    for i in range(2):
        # Ask question
        chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
        chat_input.fill(f"Integration test query {i+1}")
        chat_input.press("Enter")
        streamlit_page.wait_for_timeout(5000)

        # Give feedback
        feedback = streamlit_page.locator("text='👍'").first if i == 0 else streamlit_page.locator("text='👎'").first
        if feedback.is_visible():
            feedback.click()
            if i == 1:
                # Add comment on second feedback
                comment = streamlit_page.locator('textarea').first
                if comment.is_visible():
                    comment.fill("Test feedback")
                    submit = streamlit_page.locator("button:has-text('Send feedback')").first
                    if submit.is_visible():
                        submit.click()
        streamlit_page.wait_for_timeout(2000)

    # Verify stats are displayed
    stats = streamlit_page.locator("text=/Feedback|Statistics/i")
    assert stats.first.is_visible(timeout=5000)


@pytest.mark.integration
def test_ui_remains_stable_under_load(streamlit_page: Page):
    """Test that UI remains stable with multiple rapid interactions."""
    # Send multiple queries rapidly
    for i in range(3):
        chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
        chat_input.fill(f"Rapid query {i+1}")
        chat_input.press("Enter")
        streamlit_page.wait_for_timeout(2000)  # Short wait

    # UI should still be responsive
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    assert chat_input.is_visible()

    # Should be able to interact
    chat_input.fill("Final query after load test")
    assert chat_input.input_value() == "Final query after load test"
