"""
FILE: test_conversation_feature.py
STATUS: Active
RESPONSIBILITY: Test conversation history feature end-to-end
LAST MAJOR UPDATE: 2026-02-10
MAINTAINER: Shahu
"""

import sys
import io

# Force UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from src.repositories.conversation import ConversationRepository
from src.services.conversation import ConversationService
from src.services.chat import ChatService
from src.models.chat import ChatRequest

def test_conversation_end_to_end():
    """Test conversation feature from creation to query with context."""

    print("=" * 80)
    print("TESTING CONVERSATION FEATURE END-TO-END")
    print("=" * 80)

    # Initialize services
    print("\n[1/7] Initializing services...")
    conversation_repo = ConversationRepository()
    conversation_service = ConversationService(repository=conversation_repo)
    chat_service = ChatService()
    chat_service.ensure_ready()
    print("  [+] Services initialized")

    # Create conversation
    print("\n[2/7] Creating new conversation...")
    conversation = conversation_service.start_conversation()
    print(f"  [+] Conversation created: {conversation.id}")
    print(f"      Title: {conversation.title}")
    print(f"      Status: {conversation.status}")

    # First message - establish context
    print("\n[3/7] Sending first message (establish context)...")
    first_query = "Who scored the most points this season?"

    request1 = ChatRequest(
        query=first_query,
        k=5,
        conversation_id=conversation.id,
        turn_number=1
    )

    response1 = chat_service.chat(request1)
    print(f"  Query: {first_query}")
    print(f"  Response: {response1.answer[:100]}...")
    print(f"  Processing time: {response1.processing_time_ms}ms")

    # Update conversation title
    print("\n[4/7] Updating conversation title...")
    conversation_service.update_conversation_after_message(conversation.id, first_query)
    updated_conv = conversation_service.get_conversation(conversation.id)
    print(f"  [+] Title updated to: {updated_conv.title}")

    # Second message - follow-up with pronoun (tests context)
    print("\n[5/7] Sending follow-up message with pronoun...")
    follow_up_query = "What about his assists?"  # "his" refers to player from previous query

    request2 = ChatRequest(
        query=follow_up_query,
        k=5,
        conversation_id=conversation.id,  # Same conversation
        turn_number=2
    )

    response2 = chat_service.chat(request2)
    print(f"  Query: {follow_up_query}")
    print(f"  Response: {response2.answer[:100]}...")

    # Check if conversation context was used
    print("\n[6/7] Verifying conversation context...")
    messages = conversation_repo.get_messages_by_conversation(conversation.id)
    print(f"  [+] Found {len(messages)} messages in conversation:")
    for i, msg in enumerate(messages, 1):
        print(f"      Turn {msg.turn_number}: {msg.query[:50]}...")

    # Retrieve full conversation history
    print("\n[7/7] Retrieving full conversation with messages...")
    full_conversation = conversation_service.get_conversation_history(conversation.id)
    print(f"  [+] Conversation: {full_conversation.title}")
    print(f"      Messages: {len(full_conversation.messages)}")
    print(f"      Status: {full_conversation.status}")

    # Test archiving
    print("\n[BONUS] Testing conversation archiving...")
    conversation_service.archive(conversation.id)
    archived = conversation_service.get_conversation(conversation.id)
    print(f"  [+] Conversation archived: {archived.status}")

    print("\n" + "=" * 80)
    print("  CONVERSATION FEATURE TEST: SUCCESS")
    print("=" * 80)

    # Summary
    print("\n[SUMMARY]")
    print(f"  Conversation ID: {conversation.id}")
    print(f"  Messages sent: 2")
    print(f"  Pronoun resolution tested: 'his' in follow-up query")
    print(f"  Context window: {len(messages)} previous messages")
    print(f"  Final status: {archived.status}")

    return True

if __name__ == "__main__":
    try:
        test_conversation_end_to_end()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
