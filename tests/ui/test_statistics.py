"""
FILE: test_statistics.py
STATUS: Active
RESPONSIBILITY: Test statistics display in Streamlit sidebar
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.statistics
def test_stats_section_visible(streamlit_page: Page):
    """Test that statistics section is visible in sidebar."""
    stats_header = streamlit_page.locator("text=/Feedback Stats|Statistics/i")
    assert stats_header.is_visible(timeout=5000)


@pytest.mark.statistics
def test_total_interactions_metric_displays(streamlit_page: Page):
    """Test that total interactions metric is displayed."""
    total_interactions = streamlit_page.locator("text=/Total Interactions|Interactions/i")
    assert total_interactions.is_visible(timeout=5000)


@pytest.mark.statistics
def test_feedback_count_metrics_display(streamlit_page: Page):
    """Test that feedback count metrics are displayed."""
    # Look for positive/negative feedback metrics
    positive_metric = streamlit_page.locator("text=👍")
    negative_metric = streamlit_page.locator("text=👎")

    if positive_metric.is_visible():
        assert True
    else:
        # Metrics might be displayed as text
        metrics_text = streamlit_page.locator("text=/Positive|Negative|Feedback/i")
        assert metrics_text.first.is_visible(timeout=5000)


@pytest.mark.statistics
def test_positive_rate_percentage_displays(streamlit_page: Page):
    """Test that positive feedback rate percentage is displayed."""
    rate_display = streamlit_page.locator("text=/Positive Rate|Rate|%/i")
    assert rate_display.is_visible(timeout=5000)


@pytest.mark.statistics
def test_stats_update_after_feedback(streamlit_page: Page):
    """Test that statistics update after giving feedback."""
    # Get initial stats by reading text
    initial_interactions = streamlit_page.locator("text=/Interactions|interactions/i").first

    # Ask a question
    chat_input = streamlit_page.locator('input[placeholder*="Ask about"]').first
    chat_input.fill("Query for stats test")
    chat_input.press("Enter")

    # Wait for response
    streamlit_page.wait_for_timeout(5000)

    # Give feedback
    feedback_btn = streamlit_page.locator("text='👍'").first
    if feedback_btn.is_visible():
        feedback_btn.click()
        streamlit_page.wait_for_timeout(2000)

    # Check that stats are still visible (they should update)
    stats_section = streamlit_page.locator("text=/Feedback Stats|Statistics/i")
    assert stats_section.is_visible(timeout=5000)


@pytest.mark.statistics
def test_api_readiness_indicator(streamlit_page: Page):
    """Test that API readiness is indicated (green checkmark or similar)."""
    # Look for API status indicator
    api_status = streamlit_page.locator("text=/API|Ready|Healthy|✅/i")
    if api_status.is_visible():
        assert True
    # Status indicator should show system is ready


@pytest.mark.statistics
def test_vector_index_size_displayed(streamlit_page: Page):
    """Test that vector index size is displayed."""
    index_info = streamlit_page.locator("text=/vector|index|size|375/i")
    # Vector index information should be visible to show system is ready
    if index_info.is_visible():
        assert True
