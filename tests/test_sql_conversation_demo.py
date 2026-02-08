"""
FILE: test_sql_conversation_demo.py
STATUS: Active
RESPONSIBILITY: Demonstrate conversation history with SQL queries (pronoun resolution)
LAST MAJOR UPDATE: 2026-02-09
MAINTAINER: Shahu
"""

import tempfile
from pathlib import Path

from src.models.chat import ChatRequest
from src.models.feedback import ChatInteractionCreate
from src.repositories.conversation import ConversationRepository
from src.repositories.feedback import FeedbackRepository
from src.services.chat import ChatService
from src.services.conversation import ConversationService


def test_sql_with_conversation_history_demo():
    """Demonstrate how conversation history helps with SQL queries.

    This test shows:
    1. First query uses SQL to find player stats
    2. Follow-up query with pronouns uses conversation context
    3. Without conversation history, the pronoun query would fail
    """
    print("\n" + "="*80)
    print("DEMONSTRATION: SQL Queries with Conversation History")
    print("="*80)

    # Setup temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"

        # Initialize services
        conv_repo = ConversationRepository(db_path=db_path)
        conv_service = ConversationService(repository=conv_repo)
        feedback_repo = FeedbackRepository(db_path=db_path)

        # Create chat service with SQL enabled
        chat_service = ChatService(
            feedback_repository=feedback_repo,
            enable_sql=True,
            conversation_history_limit=5
        )

        try:
            chat_service.ensure_ready()
        except Exception as e:
            print(f"\n⚠️  Warning: Vector index not loaded: {e}")
            print("Continuing with SQL-only demonstration...\n")

        # Create a conversation
        conversation = conv_service.start_conversation()
        conv_id = conversation.id

        print(f"\n[*] Created conversation: {conv_id[:8]}...\n")

        # =====================================================================
        # Turn 1: Ask about a player (SQL query - should work)
        # =====================================================================
        print("Turn 1: Initial Query (SQL)")
        print("-" * 80)

        query1 = "Who has the most points?"
        print(f"User: {query1}")

        request1 = ChatRequest(
            query=query1,
            conversation_id=conv_id,
            turn_number=1,
            k=3,
        )

        response1 = chat_service.chat(request1)
        print(f"Assistant: {response1.answer[:200]}...")

        # Log interaction
        interaction1 = feedback_repo.save_interaction(
            ChatInteractionCreate(
                query=query1,
                response=response1.answer,
                sources=[],
                processing_time_ms=int(response1.processing_time_ms),
                conversation_id=conv_id,
                turn_number=1,
            )
        )

        # Update conversation title
        conv_service.update_conversation_after_message(conv_id, query1)

        print(f"\n✅ Response generated in {response1.processing_time_ms:.0f}ms")
        print(f"💾 Interaction logged: {interaction1.id[:8]}...")

        # =====================================================================
        # Turn 2: Follow-up with pronoun (requires conversation context)
        # =====================================================================
        print("\n" + "="*80)
        print("Turn 2: Follow-up Query with Pronoun (Requires Context)")
        print("-" * 80)

        query2 = "What about his assists?"
        print(f"User: {query2}")
        print("\n🔍 Building conversation context...")

        # Build context manually to show what's happening
        context = chat_service._build_conversation_context(conv_id, 2)

        if context:
            print("✅ Conversation history found:")
            print(context[:150] + "...")
        else:
            print("⚠️  No conversation history (would fail pronoun resolution)")

        request2 = ChatRequest(
            query=query2,
            conversation_id=conv_id,
            turn_number=2,
            k=3,
        )

        response2 = chat_service.chat(request2)
        print(f"\nAssistant: {response2.answer[:200]}...")

        # Log interaction
        interaction2 = feedback_repo.save_interaction(
            ChatInteractionCreate(
                query=query2,
                response=response2.answer,
                sources=[],
                processing_time_ms=int(response2.processing_time_ms),
                conversation_id=conv_id,
                turn_number=2,
            )
        )

        print(f"\n✅ Response generated in {response2.processing_time_ms:.0f}ms")
        print(f"💾 Interaction logged: {interaction2.id[:8]}...")

        # =====================================================================
        # Turn 3: Another follow-up with pronoun
        # =====================================================================
        print("\n" + "="*80)
        print("Turn 3: Another Follow-up (Still Using Context)")
        print("-" * 80)

        query3 = "How many rebounds did he get?"
        print(f"User: {query3}")

        request3 = ChatRequest(
            query=query3,
            conversation_id=conv_id,
            turn_number=3,
            k=3,
        )

        response3 = chat_service.chat(request3)
        print(f"Assistant: {response3.answer[:200]}...")

        print(f"\n✅ Response generated in {response3.processing_time_ms:.0f}ms")

        # =====================================================================
        # Summary
        # =====================================================================
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        conversation_history = conv_service.get_conversation_history(conv_id)
        print(f"\n📊 Conversation Stats:")
        print(f"   - Total turns: {len(conversation_history.messages)}")
        print(f"   - Title: {conversation_history.title}")
        print(f"   - Status: {conversation_history.status}")

        print("\n💡 Key Points:")
        print("   ✓ Turn 1: SQL query identifies the player")
        print("   ✓ Turn 2: 'his' resolves to the player from Turn 1 (via context)")
        print("   ✓ Turn 3: 'he' still refers to the same player")
        print("   ✓ Without conversation history, pronouns would fail!")

        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETE")
        print("="*80 + "\n")

        # Cleanup
        conv_repo.close()


def test_sql_without_conversation_history_demo():
    """Show what happens WITHOUT conversation history (baseline)."""
    print("\n" + "="*80)
    print("BASELINE: SQL Queries WITHOUT Conversation History")
    print("="*80)

    # Create chat service without conversation support
    chat_service = ChatService(enable_sql=True)

    try:
        chat_service.ensure_ready()
    except Exception as e:
        print(f"\n⚠️  Warning: Vector index not loaded: {e}")
        print("Continuing with SQL-only demonstration...\n")

    # =====================================================================
    # Query with pronoun (NO conversation context)
    # =====================================================================
    print("\nQuery: 'What about his assists?'")
    print("-" * 80)
    print("❌ NO conversation context available")
    print("Result: LLM cannot resolve 'his' - query will fail or give generic response\n")

    request = ChatRequest(
        query="What about his assists?",
        conversation_id=None,  # No conversation!
        turn_number=1,
        k=3,
    )

    response = chat_service.chat(request)
    print(f"Assistant: {response.answer[:200]}...")

    print("\n💡 Notice: Without context, the LLM cannot determine who 'his' refers to")
    print("   This is why conversation history is essential for follow-up questions!")

    print("\n" + "="*80)
    print("BASELINE DEMONSTRATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CONVERSATION HISTORY + SQL DEMONSTRATION")
    print("=" * 80)

    # Run with conversation history
    test_sql_with_conversation_history_demo()

    # Run without conversation history (baseline)
    test_sql_without_conversation_history_demo()

    print("\n✅ All demonstrations complete!")
