"""
FILE: test_app.py
STATUS: Active
RESPONSIBILITY: Smoke tests for Streamlit chat interface with mocked services
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

from unittest.mock import MagicMock, patch

import pytest


class TestAppImports:
    @patch("streamlit.set_page_config")
    @patch("streamlit.cache_resource", lambda f: f)
    def test_render_sources_empty(self, mock_config):
        with patch("src.ui.app.st") as mock_st:
            from src.ui.app import render_sources

            render_sources([])
            mock_st.expander.assert_not_called()

    @patch("streamlit.set_page_config")
    @patch("streamlit.cache_resource", lambda f: f)
    def test_render_sources_with_items(self, mock_config):
        with patch("src.ui.app.st") as mock_st:
            mock_expander = MagicMock()
            mock_st.expander.return_value.__enter__ = MagicMock(return_value=mock_expander)
            mock_st.expander.return_value.__exit__ = MagicMock(return_value=False)

            from src.ui.app import render_sources

            source = MagicMock()
            source.source = "test.pdf"
            source.score = 85.0
            source.text = "Short text"

            render_sources([source])
            mock_st.expander.assert_called_once()


class TestRenderMessage:
    @patch("streamlit.set_page_config")
    @patch("streamlit.cache_resource", lambda f: f)
    def test_render_message_calls_st(self, mock_config):
        with patch("src.ui.app.st") as mock_st:
            mock_chat_msg = MagicMock()
            mock_st.chat_message.return_value.__enter__ = MagicMock(return_value=mock_chat_msg)
            mock_st.chat_message.return_value.__exit__ = MagicMock(return_value=False)

            from src.ui.app import render_message

            render_message("user", "Hello!")
            mock_st.chat_message.assert_called_once_with("user")


class TestServiceFactories:
    @patch("streamlit.set_page_config")
    @patch("streamlit.cache_resource", lambda f: f)
    @patch("src.ui.app.FeedbackService")
    def test_get_feedback_service(self, mock_fb_cls, mock_config):
        from src.ui.app import get_feedback_service

        result = get_feedback_service()
        mock_fb_cls.assert_called_once()

    @patch("streamlit.set_page_config")
    @patch("streamlit.cache_resource", lambda f: f)
    @patch("src.ui.app.ConversationRepository")
    @patch("src.ui.app.ConversationService")
    def test_get_conversation_service(self, mock_conv_svc, mock_conv_repo, mock_config):
        from src.ui.app import get_conversation_service

        result = get_conversation_service()
        mock_conv_repo.assert_called_once()
        mock_conv_svc.assert_called_once()
