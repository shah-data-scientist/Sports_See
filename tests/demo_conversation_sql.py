"""
FILE: demo_conversation_sql.py
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


def main():
    print("\n" + "="*80)
    print("DEMONSTRATION: SQL Queries WITH Conversation History")
    print("="*80)

    # Setup temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "demo.db"

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
            print(f"\n[INFO] Vector index not loaded: {e}")
            print("[INFO] Continuing with SQL-only demonstration...\n")

        # Create a conversation
        conversation = conv_service.start_conversation()
        conv_id = conversation.id

        print(f"\n[CREATED] Conversation: {conv_id[:12]}...\n")

        # ========================================================================
        # Turn 1: Initial SQL query
        # ========================================================================
        print("="*80)
        print("TURN 1: Initial Query")
        print("="*80)

        query1 = "Who has the most points?"
        print(f"\nUser: {query1}")

        request1 = ChatRequest(
            query=query1,
            conversation_id=conv_id,
            turn_number=1,
            k=3,
        )

        print("\n[PROCESSING] Sending to chat service with SQL tool...")
        response1 = chat_service.chat(request1)

        print(f"\nAssistant: {response1.answer}")
        print(f"\n[TIMING] Response generated in {response1.processing_time_ms:.0f}ms")

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
        print(f"[SAVED] Interaction logged: {interaction1.id[:12]}...")

        # ========================================================================
        # Turn 2: Follow-up with pronoun (requires conversation context)
        # ========================================================================
        print("\n" + "="*80)
        print("TURN 2: Follow-up Query with Pronoun")
        print("="*80)

        query2 = "What about his assists?"
        print(f"\nUser: {query2}")
        print("\n[CONTEXT] Building conversation history...")

        # Build context to show what's happening
        context = chat_service._build_conversation_context(conv_id, 2)

        if context:
            print("[OK] Conversation history retrieved:")
            print("-" * 80)
            print(context)
            print("-" * 80)
        else:
            print("[WARNING] No conversation history found!")

        request2 = ChatRequest(
            query=query2,
            conversation_id=conv_id,
            turn_number=2,
            k=3,
        )

        print("\n[PROCESSING] Sending query with conversation context...")
        response2 = chat_service.chat(request2)

        print(f"\nAssistant: {response2.answer}")
        print(f"\n[TIMING] Response generated in {response2.processing_time_ms:.0f}ms")

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
        print(f"[SAVED] Interaction logged: {interaction2.id[:12]}...")

        # ========================================================================
        # Turn 3: Another follow-up
        # ========================================================================
        print("\n" + "="*80)
        print("TURN 3: Another Follow-up with Pronoun")
        print("="*80)

        query3 = "How many rebounds did he get?"
        print(f"\nUser: {query3}")

        request3 = ChatRequest(
            query=query3,
            conversation_id=conv_id,
            turn_number=3,
            k=3,
        )

        print("\n[PROCESSING] Sending query (pronoun 'he' should resolve)...")
        response3 = chat_service.chat(request3)

        print(f"\nAssistant: {response3.answer}")
        print(f"\n[TIMING] Response generated in {response3.processing_time_ms:.0f}ms")

        # ========================================================================
        # Summary
        # ========================================================================
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)

        conversation_history = conv_service.get_conversation_history(conv_id)
        print(f"\n[STATS] Conversation Statistics:")
        print(f"  Total turns: {len(conversation_history.messages)}")
        print(f"  Title: {conversation_history.title}")
        print(f"  Status: {conversation_history.status}")

        print("\n[KEY POINTS]")
        print("  [+] Turn 1: SQL query identifies the player")
        print("  [+] Turn 2: 'his' resolves to player from Turn 1 via context")
        print("  [+] Turn 3: 'he' still refers to the same player")
        print("  [+] Without conversation history, pronouns would FAIL!")

        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETE")
        print("="*80)

        # Proper cleanup
        conv_repo.close()
        feedback_repo.close()

    print("\n[OK] Cleanup complete\n")


def baseline_demo():
    """Show what happens WITHOUT conversation history."""
    print("\n" + "="*80)
    print("BASELINE: SQL Query WITHOUT Conversation History")
    print("="*80)

    # Create chat service without conversation support
    chat_service = ChatService(enable_sql=True)

    try:
        chat_service.ensure_ready()
    except Exception as e:
        print(f"\n[INFO] Vector index not loaded: {e}")

    print("\nUser: 'What about his assists?'")
    print("\n[X] NO conversation context available")
    print("[X] LLM cannot resolve 'his' - query will fail!\n")

    request = ChatRequest(
        query="What about his assists?",
        conversation_id=None,  # No conversation!
        turn_number=1,
        k=3,
    )

    response = chat_service.chat(request)
    print(f"Assistant: {response.answer}\n")

    print("[INFO] Without context, 'his' cannot be resolved.")
    print("[INFO] This is why conversation history is essential!")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("CONVERSATION HISTORY + SQL DEMONSTRATION")
    print("="*80)

    # Run with conversation history
    main()

    # Run baseline without history
    baseline_demo()

    print("[OK] All demonstrations complete!\n")
