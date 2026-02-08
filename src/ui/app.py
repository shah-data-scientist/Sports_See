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
                "L'index vectoriel n'est pas chargé. "
                "Exécutez `poetry run python src/indexer.py` pour créer la base de connaissances."
            )

        return service

    except Exception as e:
        logger.error("Failed to initialize ChatService: %s", e)
        st.error(f"Erreur d'initialisation: {e}")
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
            st.success("👍 Merci pour votre feedback positif !")
        else:
            st.info("👎 Merci pour votre feedback.")
        return

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("👍", key=f"pos_{index}_{interaction_id}", help="Bonne réponse"):
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
        if st.button("👎", key=f"neg_{index}_{interaction_id}", help="Mauvaise réponse"):
            st.session_state[f"show_comment_{interaction_id}"] = True
            st.rerun()

    # Show comment input for negative feedback
    if st.session_state.get(f"show_comment_{interaction_id}"):
        with st.form(key=f"comment_form_{interaction_id}"):
            comment = st.text_area(
                "Qu'est-ce qui n'allait pas avec cette réponse ? (optionnel)",
                key=comment_key,
                max_chars=2000,
            )
            submitted = st.form_submit_button("Envoyer le feedback")

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
    if st.button("🆕 Nouvelle conversation", use_container_width=True):
        # Create new conversation
        new_conv = conversation_service.start_conversation()
        st.session_state.current_conversation_id = new_conv.id
        st.session_state.turn_number = 1
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Nouvelle conversation démarrée ! Comment puis-je vous aider ?",
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
                    st.caption(f"Actuelle: {current_conv.title or 'Sans titre'}")

            # Conversation selector
            st.selectbox(
                "Charger une conversation",
                options=[""] + [c.id for c in conversations],
                format_func=lambda x: "Sélectionner..." if x == "" else next(
                    (c.title or f"Conversation {c.id[:8]}..." for c in conversations if c.id == x), x
                ),
                key="conversation_selector",
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📂 Charger", disabled=not st.session_state.get("conversation_selector")):
                    conv_id = st.session_state.conversation_selector
                    history = conversation_service.get_conversation_history(conv_id)
                    if history:
                        # Load conversation messages
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.turn_number = len(history.messages) + 1
                        st.session_state.messages = [
                            {
                                "role": "assistant",
                                "content": f"Conversation chargée: {history.title or 'Sans titre'}",
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
                if st.button("🗄️ Archiver", disabled=not current_id):
                    if current_id:
                        conversation_service.archive(current_id)
                        st.session_state.pop("current_conversation_id", None)
                        st.session_state.turn_number = 1
                        st.session_state.messages = [
                            {
                                "role": "assistant",
                                "content": "Conversation archivée. Démarrez-en une nouvelle !",
                                "interaction_id": None,
                            }
                        ]
                        st.rerun()

    except Exception as e:
        logger.error("Error loading conversations: %s", e)
        st.error("Erreur de chargement des conversations")


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
    st.caption(f"Assistant IA pour {settings.app_name} | Modèle: {settings.chat_model}")

    # Initialize services
    service = get_chat_service()
    feedback_service = get_feedback_service()

    if service is None:
        st.error("Service non disponible. Vérifiez la configuration.")
        st.stop()

    # Initialize conversation service
    conversation_service = get_conversation_service()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Bonjour ! Je suis votre analyste IA pour la {settings.app_name}. "
                "Posez-moi vos questions sur les équipes, les joueurs ou les statistiques.",
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
    if prompt := st.chat_input(f"Posez votre question sur la {settings.app_name}..."):
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
                "L'index vectoriel n'est pas chargé. "
                "Veuillez exécuter l'indexation d'abord."
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
            with st.spinner("Recherche en cours..."):
                try:
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
                    response = service.chat(request)

                    # Display answer
                    st.write(response.answer)

                    # Display sources
                    render_sources(response.sources)

                    # Display processing time
                    st.caption(f"⏱️ {response.processing_time_ms:.0f}ms")

                    # Log interaction to database with conversation context
                    source_names = [s.source for s in response.sources] if response.sources else []
                    interaction = feedback_service.log_interaction(
                        query=prompt,
                        response=response.answer,
                        sources=source_names,
                        processing_time_ms=int(response.processing_time_ms),
                        conversation_id=st.session_state.current_conversation_id,
                        turn_number=st.session_state.turn_number,
                    )

                    # Update conversation title after first message
                    if st.session_state.turn_number == 1:
                        conversation_service.update_conversation_after_message(
                            st.session_state.current_conversation_id,
                            prompt
                        )

                    # Increment turn number for next message
                    st.session_state.turn_number += 1

                    # Add to history with interaction_id
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.answer,
                        "interaction_id": interaction.id,
                    })

                    # Rerun to show feedback buttons
                    st.rerun()

                except AppException as e:
                    error_msg = f"Erreur: {e.message}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "interaction_id": None,
                    })

                except Exception as e:
                    logger.exception("Unexpected error: %s", e)
                    error_msg = "Une erreur inattendue s'est produite. Veuillez réessayer."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "interaction_id": None,
                    })

    # Sidebar
    with st.sidebar:
        st.header("Configuration")

        # Display service status
        if service.is_ready:
            st.success(f"✅ Index chargé ({service.vector_store.index_size} vecteurs)")
        else:
            st.warning("⚠️ Index non chargé")

        st.divider()

        # Conversation controls
        render_conversation_controls()

        st.divider()

        # Settings display
        st.subheader("Paramètres")
        st.text(f"Modèle: {settings.chat_model}")
        st.text(f"Résultats: {settings.search_k}")
        st.text(f"Température: {settings.temperature}")

        st.divider()

        # Feedback statistics
        st.subheader("Statistiques Feedback")
        try:
            stats = feedback_service.get_stats()
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total interactions", stats.total_interactions)
                st.metric("👍 Positifs", stats.positive_count)
            with col2:
                st.metric("Avec feedback", stats.total_feedback)
                st.metric("👎 Négatifs", stats.negative_count)

            if stats.total_feedback > 0:
                st.progress(stats.positive_rate / 100, text=f"Taux positif: {stats.positive_rate}%")
        except Exception as e:
            logger.error("Error getting feedback stats: %s", e)

        st.divider()

        # Clear chat button
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Historique effacé. Comment puis-je vous aider ?",
                    "interaction_id": None,
                }
            ]
            st.rerun()

    # Footer
    st.markdown("---")
    st.caption("Powered by Mistral AI & FAISS | Data-driven Insights")


if __name__ == "__main__":
    main()
