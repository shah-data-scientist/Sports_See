"""
FILE: app.py
STATUS: Active
RESPONSIBILITY: Streamlit chat interface with feedback collection and statistics
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import logging
import sys
from pathlib import Path

import streamlit as st

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.core.exceptions import AppException, IndexNotFoundError
from src.models.chat import ChatRequest
from src.models.conversation import ConversationStatus
from src.models.feedback import FeedbackRating
from src.repositories.conversation import ConversationRepository
from src.services.chat import ChatService
from src.services.conversation import ConversationService
from src.services.feedback import FeedbackService

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


@st.cache_resource
def get_chat_service() -> ChatService | None:
    """Get cached ChatService instance.

    Returns:
        Initialized ChatService or None if initialization fails
    """
    try:
        logger.info("Initializing ChatService...")
        service = ChatService()

        # Try to load the index
        try:
            service.ensure_ready()
            logger.info("ChatService ready with %d vectors", service.vector_store.index_size)
        except IndexNotFoundError:
            logger.warning("Index not found - service will be limited")
            st.warning(
                "⚠️ Vector index not loaded.\n\n"
                "Run `poetry run python src/indexer.py` to build the knowledge base."
            )

        return service

    except Exception as e:
        logger.error("Failed to initialize ChatService: %s", e)
        st.error(f"❌ Initialization Error: {e}")
        return None


@st.cache_resource
def get_feedback_service() -> FeedbackService:
    """Get cached FeedbackService instance.

    Returns:
        Initialized FeedbackService
    """
    return FeedbackService()


@st.cache_resource
def get_conversation_service() -> ConversationService:
    """Get cached ConversationService instance.

    Returns:
        Initialized ConversationService
    """
    repository = ConversationRepository()
    return ConversationService(repository=repository)


def render_message(role: str, content: str) -> None:
    """Render a chat message.

    Args:
        role: Message role (user or assistant)
        content: Message content
    """
    with st.chat_message(role):
        st.write(content)


def render_sources(sources: list) -> None:
    """Render source documents in an expander.

    Args:
        sources: List of SearchResult objects
    """
    if not sources:
        return

    with st.expander(f"Sources ({len(sources)})"):
        for i, source in enumerate(sources, 1):
            st.markdown(f"**{i}. {source.source}** (Score: {source.score:.1f}%)")
            st.caption(source.text[:300] + "..." if len(source.text) > 300 else source.text)
            st.divider()


def render_feedback_buttons(interaction_id: str, index: int) -> None:
    """Render feedback buttons for an interaction.

    Args:
        interaction_id: ID of the chat interaction
        index: Index for unique key generation
    """
    feedback_service = get_feedback_service()
    feedback_key = f"feedback_{interaction_id}"
    comment_key = f"comment_{interaction_id}"

    # Check if feedback already given
    if feedback_key in st.session_state:
        existing = st.session_state[feedback_key]
        if existing == "positive":
            st.success("👍 Thanks for positive feedback!")
        else:
            st.info("👎 Thanks for your feedback.")
        return

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("👍", key=f"pos_{index}_{interaction_id}", help="Good answer"):
            try:
                feedback_service.submit_feedback(
                    interaction_id=interaction_id,
                    rating=FeedbackRating.POSITIVE,
                )
                st.session_state[feedback_key] = "positive"
                st.rerun()
            except ValueError as e:
                logger.warning("Feedback error: %s", e)

    with col2:
        if st.button("👎", key=f"neg_{index}_{interaction_id}", help="Bad answer"):
            st.session_state[f"show_comment_{interaction_id}"] = True
            st.rerun()

    # Show comment input for negative feedback
    if st.session_state.get(f"show_comment_{interaction_id}"):
        with st.form(key=f"comment_form_{interaction_id}"):
            comment = st.text_area(
                "What was wrong with this answer? (optional)",
                key=comment_key,
                max_chars=2000,
            )
            submitted = st.form_submit_button("Send feedback")

            if submitted:
                try:
                    feedback_service.submit_feedback(
                        interaction_id=interaction_id,
                        rating=FeedbackRating.NEGATIVE,
                        comment=comment if comment.strip() else None,
                    )
                    st.session_state[feedback_key] = "negative"
                    st.session_state.pop(f"show_comment_{interaction_id}", None)
                    st.rerun()
                except ValueError as e:
                    logger.warning("Feedback error: %s", e)


def render_conversation_controls() -> None:
    """Render conversation management controls in sidebar."""
    conversation_service = get_conversation_service()

    st.subheader("Conversations")

    # New Conversation button
    if st.button("🆕 New Conversation", use_container_width=True):
        # Create new conversation
        new_conv = conversation_service.start_conversation()
        st.session_state.current_conversation_id = new_conv.id
        st.session_state.turn_number = 1
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "New conversation started! How can I help?",
                "interaction_id": None,
            }
        ]
        st.rerun()

    # Load existing conversations
    try:
        conversations = conversation_service.list_conversations(
            status=ConversationStatus.ACTIVE,
            limit=20
        )

        if conversations:
            # Current conversation indicator
            current_id = st.session_state.get("current_conversation_id")
            if current_id:
                current_conv = conversation_service.get_conversation(current_id)
                if current_conv:
                    st.caption(f"Current: {current_conv.title or 'Untitled'}")

            # Conversation selector
            st.selectbox(
                "Load Conversation",
                options=[""] + [c.id for c in conversations],
                format_func=lambda x: "Select..." if x == "" else next(
                    (c.title or f"Conversation {c.id[:8]}..." for c in conversations if c.id == x), x
                ),
                key="conversation_selector",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📂 Load", disabled=not st.session_state.get("conversation_selector")):
                    conv_id = st.session_state.conversation_selector
                    history = conversation_service.get_conversation_history(conv_id)
                    if history:
                        # Load conversation messages
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.turn_number = len(history.messages) + 1
                        st.session_state.messages = [
                            {
                                "role": "assistant",
                                "content": f"Conversation loaded: {history.title or 'Untitled'}",
                                "interaction_id": None,
                            }
                        ]
                        # Add all previous messages
                        for msg in history.messages:
                            st.session_state.messages.append({
                                "role": "user",
                                "content": msg.query,
                                "interaction_id": None,
                            })
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg.response,
                                "interaction_id": msg.id,
                            })
                        st.rerun()

            with col2:
                if st.button("🗄️ Archive", disabled=not current_id):
                    if current_id:
                        conversation_service.archive(current_id)
                        st.session_state.pop("current_conversation_id", None)
                        st.session_state.turn_number = 1
                        st.session_state.messages = [
                            {
                                "role": "assistant",
                                "content": "Conversation archived. Start a new one!",
                                "interaction_id": None,
                            }
                        ]
                        st.rerun()

    except Exception as e:
        logger.error("Error loading conversations: %s", e)
        st.error("Error loading conversations")


def main() -> None:
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title=settings.app_title,
        page_icon="🏀",
        layout="centered",
    )

    # Header
    st.title(f"🏀 {settings.app_title}")
    st.caption(f"AI Assistant for {settings.app_name} | Model: {settings.chat_model}")

    # Welcome message
    st.markdown("""
    ---
    **Welcome! 🎉**

    Drop your {app_name} questions anytime - we'll dig up the stats, the drama, the highlights.
    No question too random. (Well, *almost* no question too random.) 😎
    """.format(app_name=settings.app_name))
    st.markdown("---")
    service = get_chat_service()
    feedback_service = get_feedback_service()

    if service is None:
        st.error("❌ Service unavailable. Check configuration.")
        st.stop()

    # Initialize conversation service
    conversation_service = get_conversation_service()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Hello! I'm your AI analyst for {settings.app_name}. "
                "Ask me about teams, players, or statistics.",
                "interaction_id": None,
            }
        ]

    # Initialize conversation tracking
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if "turn_number" not in st.session_state:
        st.session_state.turn_number = 1

    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        render_message(message["role"], message["content"])

        # Show feedback buttons for assistant messages with interaction_id
        if message["role"] == "assistant" and message.get("interaction_id"):
            render_feedback_buttons(message["interaction_id"], i)

    # Chat input
    if prompt := st.chat_input(f"Ask about {settings.app_name}..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "interaction_id": None,
        })
        render_message("user", prompt)

        # Check if service is ready
        if not service.is_ready:
            error_msg = (
                "Vector index not loaded. Run indexing first."
            )
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "interaction_id": None,
            })
            render_message("assistant", error_msg)
            st.stop()

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                try:
                    import time as time_module

                    # Auto-create conversation on first message
                    if st.session_state.current_conversation_id is None:
                        new_conv = conversation_service.start_conversation()
                        st.session_state.current_conversation_id = new_conv.id
                        st.session_state.turn_number = 1
                        logger.info(f"Created new conversation: {new_conv.id}")

                    # Create request with conversation context
                    request = ChatRequest(
                        query=prompt,
                        k=settings.search_k,
                        include_sources=True,
                        conversation_id=st.session_state.current_conversation_id,
                        turn_number=st.session_state.turn_number,
                    )

                    # Get response (with conversation context!)
                    logger.info(f"[UI-DEBUG] Calling service.chat() for query: '{prompt}'")
                    start_service = time_module.time()
                    response = service.chat(request)
                    service_elapsed = time_module.time() - start_service
                    logger.info(f"[UI-DEBUG] service.chat() returned in {service_elapsed:.2f}s")
                    logger.info(f"[UI-DEBUG] Response answer length: {len(response.answer) if response.answer else 0}")
                    logger.info(f"[UI-DEBUG] Response sources count: {len(response.sources) if response.sources else 0}")

                    # Display answer
                    logger.info(f"[UI-DEBUG] About to display answer with st.write()")
                    st.write(response.answer)
                    logger.info(f"[UI-DEBUG] Answer displayed successfully")

                    # Display sources
                    logger.info(f"[UI-DEBUG] About to render sources")
                    render_sources(response.sources)
                    logger.info(f"[UI-DEBUG] Sources rendered successfully")

                    # Display processing time
                    logger.info(f"[UI-DEBUG] About to display processing time")
                    st.caption(f"⏱️ {response.processing_time_ms:.0f}ms")
                    logger.info(f"[UI-DEBUG] Processing time displayed successfully")

                    # Log interaction to database
                    logger.info(f"[UI-DEBUG] About to log interaction to database")
                    source_names = [s.source for s in response.sources] if response.sources else []
                    interaction = feedback_service.log_interaction(
                        query=prompt,
                        response=response.answer,
                        sources=source_names,
                        processing_time_ms=int(response.processing_time_ms),
                    )
                    logger.info(f"[UI-DEBUG] Interaction logged with id: {interaction.id}")

                    # Update conversation title after first message
                    if st.session_state.turn_number == 1:
                        logger.info(f"[UI-DEBUG] Updating conversation title for first message")
                        conversation_service.update_conversation_after_message(
                            st.session_state.current_conversation_id,
                            prompt
                        )
                        logger.info(f"[UI-DEBUG] Conversation title updated")

                    # Increment turn number for next message
                    st.session_state.turn_number += 1
                    logger.info(f"[UI-DEBUG] Turn number incremented to {st.session_state.turn_number}")

                    # Add to history with interaction_id
                    logger.info(f"[UI-DEBUG] About to add message to session state")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.answer,
                        "interaction_id": interaction.id,
                    })
                    logger.info(f"[UI-DEBUG] Message added to session state")

                    # Display feedback buttons without rerun to avoid hanging
                    logger.info(f"[UI-DEBUG] About to render feedback buttons")
                    render_feedback_buttons(interaction.id, len(st.session_state.messages) - 1)
                    logger.info(f"[UI-DEBUG] Feedback buttons rendered successfully")

                except AppException as e:
                    error_msg = f"❌ Error: {e.message}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "interaction_id": None,
                    })

                except Exception as e:
                    logger.exception("Unexpected error: %s", e)
                    error_msg = "An unexpected error occurred. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "interaction_id": None,
                    })

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        # Display service status
        if service.is_ready:
            st.success(f"✅ Index loaded ({service.vector_store.index_size} vectors)")
        else:
            st.warning("⚠️ Index not loaded")

        st.divider()

        # Conversation controls
        render_conversation_controls()

        st.divider()

        # Settings display
        st.subheader("Settings")
        st.text(f"Model: {settings.chat_model}")
        st.text(f"Results: {settings.search_k}")
        st.text(f"Temperature: {settings.temperature}")

        st.divider()

        # Feedback statistics
        st.subheader("Feedback Stats")
        try:
            stats = feedback_service.get_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Interactions", stats.total_interactions)
                st.metric("👍 Positive", stats.positive_count)
            with col2:
                st.metric("With Feedback", stats.total_feedback)
                st.metric("👎 Negative", stats.negative_count)

            if stats.total_feedback > 0:
                st.progress(stats.positive_rate / 100, text=f"Positive Rate: {stats.positive_rate}%")
        except Exception as e:
            logger.error("Error getting feedback stats: %s", e)

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear History"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "History cleared. How can I help?",
                    "interaction_id": None,
                }
            ]
            st.rerun()

    # Footer
    st.markdown("---")
    st.caption("Powered by Mistral AI & FAISS | Data-driven Insights")


if __name__ == "__main__":
    main()
