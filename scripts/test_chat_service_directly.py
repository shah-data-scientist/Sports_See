"""
FILE: test_chat_service_directly.py
STATUS: Active
RESPONSIBILITY: Test ChatService directly (what Streamlit UI uses)
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu

Tests the ChatService class directly to see if there's a difference between
direct API calls and the service used by Streamlit. This helps identify if
the hanging is caused by the service layer rather than the API.

Usage:
    poetry run python scripts/test_chat_service_directly.py
"""

import logging
import time
from pathlib import Path
import sys

# Setup path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.models.chat import ChatRequest
from src.services.chat import ChatService
from src.services.conversation import ConversationService
from src.repositories.conversation import ConversationRepository

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def test_chat_service():
    """Test ChatService directly with problematic queries."""

    logger.info("\n" + "=" * 60)
    logger.info("TESTING CHATSERVICE DIRECTLY")
    logger.info("=" * 60)

    try:
        # Initialize services (same as Streamlit does)
        logger.info("\nInitializing ChatService...")
        service = ChatService()

        logger.info("Checking service readiness...")
        service.ensure_ready()

        if not service.is_ready:
            logger.error("❌ Service not ready")
            return

        logger.info(f"✅ Service ready with {service.vector_store.index_size} vectors")

        # Initialize conversation service
        logger.info("\nInitializing ConversationService...")
        conversation_repo = ConversationRepository()
        conversation_service = ConversationService(repository=conversation_repo)

        # Create a test conversation
        logger.info("Creating test conversation...")
        conversation = conversation_service.start_conversation()
        logger.info(f"✅ Created conversation: {conversation.id}")

        # Test queries
        test_queries = [
            ("top 5 scorers", "SQL"),
            ("high in the chart", "HYBRID"),
            ("who is at the top", "VECTOR"),
        ]

        for query_text, expected_type in test_queries:
            logger.info("\n" + "-" * 60)
            logger.info(f"Testing query: '{query_text}' (expected: {expected_type})")
            logger.info("-" * 60)

            try:
                # Create request (same as Streamlit does)
                request = ChatRequest(
                    query=query_text,
                    k=settings.search_k,
                    include_sources=True,
                    conversation_id=conversation.id,
                    turn_number=1,
                )

                logger.info("Calling service.chat()...")
                start = time.time()

                # This is what hangs in Streamlit
                response = service.chat(request)

                elapsed = time.time() - start
                logger.info(f"✅ Service responded in {elapsed:.3f}s")

                # Check response structure
                logger.info(f"   Chat type: {response.chat_type}")
                logger.info(f"   Answer length: {len(response.answer)} chars")
                logger.info(f"   Sources count: {len(response.sources) if response.sources else 0}")
                logger.info(f"   Processing time: {response.processing_time_ms:.0f}ms")

                if not response.answer:
                    logger.warning("⚠️  Empty answer!")

                if response.chat_type not in ["sql", "vector", "hybrid"]:
                    logger.warning(
                        f"⚠️  Unexpected chat_type: {response.chat_type}"
                    )

            except KeyboardInterrupt:
                logger.error("⏱️ Request interrupted by user")
                raise

            except TimeoutError as e:
                logger.error(f"⏱️ TIMEOUT: {e}")

            except Exception as e:
                logger.error(f"❌ Error: {type(e).__name__}: {e}", exc_info=True)

            time.sleep(2)  # Rate limiting

        logger.info("\n" + "=" * 60)
        logger.info("TEST COMPLETE")
        logger.info("=" * 60)

        # Cleanup
        logger.info("\nCleaning up...")
        try:
            conversation_repo.close()
            logger.info("✅ Cleanup complete")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


def test_service_with_detailed_steps():
    """Test service with detailed logging at each step."""

    logger.info("\n" + "=" * 60)
    logger.info("DETAILED SERVICE STEP-BY-STEP TEST")
    logger.info("=" * 60)

    try:
        # Step 1: Initialize
        logger.info("\n[STEP 1] Initializing services...")
        service = ChatService()
        conversation_repo = ConversationRepository()
        conversation_service = ConversationService(repository=conversation_repo)
        logger.info("✅ Services initialized")

        # Step 2: Ensure ready
        logger.info("\n[STEP 2] Ensuring service is ready...")
        service.ensure_ready()
        logger.info(f"✅ Service ready ({service.vector_store.index_size} vectors)")

        # Step 3: Create conversation
        logger.info("\n[STEP 3] Creating conversation...")
        conversation = conversation_service.start_conversation()
        logger.info(f"✅ Conversation created: {conversation.id}")

        # Step 4: Test problematic query with timing at each step
        query = "high in the chart"
        logger.info(f"\n[STEP 4] Testing query: '{query}'")

        request = ChatRequest(
            query=query,
            k=settings.search_k,
            include_sources=True,
            conversation_id=conversation.id,
            turn_number=1,
        )

        # Step 5: Call service.chat
        logger.info("[STEP 5] Calling service.chat()...")
        start = time.time()

        try:
            response = service.chat(request)
            elapsed = time.time() - start

            logger.info(f"✅ service.chat() returned in {elapsed:.3f}s")

            # Step 6: Process response
            logger.info("[STEP 6] Processing response...")

            # Check answer
            logger.info(f"  • Answer: {len(response.answer)} chars")
            if not response.answer:
                logger.error("    ❌ EMPTY ANSWER!")

            # Check sources
            logger.info(f"  • Sources: {len(response.sources) if response.sources else 0}")

            # Check timing
            logger.info(f"  • API processing time: {response.processing_time_ms:.0f}ms")

            logger.info("✅ Response looks valid")

            # Step 7: Summary
            logger.info("\n[STEP 7] Summary")
            logger.info(f"  Total time: {elapsed:.3f}s")
            logger.info(f"  API time: {response.processing_time_ms}ms")
            logger.info(f"  Overhead: {(elapsed - response.processing_time_ms/1000)*1000:.0f}ms")

            if elapsed > 10:
                logger.warning(f"⚠️  Total time is high ({elapsed:.1f}s)")
                if response.processing_time_ms / 1000 < elapsed * 0.8:
                    logger.warning(
                        "    Overhead might be in post-processing or network latency"
                    )

        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"❌ service.chat() FAILED after {elapsed:.3f}s")
            logger.error(f"   Error: {type(e).__name__}: {e}", exc_info=True)
            raise

        # Cleanup
        logger.info("\n[CLEANUP] Closing services...")
        conversation_repo.close()
        logger.info("✅ Complete")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        # Run both tests
        test_chat_service()
        print("\n\n")
        test_service_with_detailed_steps()

        print("\n" + "=" * 60)
        print("KEY FINDINGS:")
        print("=" * 60)
        print("""
If all queries completed successfully:
  → Issue is likely in Streamlit UI rendering/state management
  → Not in the service layer

If "high in the chart" hung or failed:
  → Issue is in ChatService.chat() method
  → May need to check query classification or vector search

If response came back but was empty:
  → Issue might be in LLM response formatting
  → Check if answer contains any content
        """)

    except KeyboardInterrupt:
        logger.info("\n\nTest stopped by user")
    except Exception as e:
        logger.error(f"\n\nFatal error: {e}")
        sys.exit(1)
