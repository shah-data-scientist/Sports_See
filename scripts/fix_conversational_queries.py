"""
FILE: fix_conversational_queries.py
STATUS: Active
RESPONSIBILITY: Re-run conversational queries with proper conversation context
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path

from src.core.observability import logger
from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.models.chat import ChatRequest
from src.services.chat import ChatService
from src.services.embedding import EmbeddingService

# Rate limiting
RATE_LIMIT_DELAY = 15
MAX_RETRIES = 2
RETRY_BACKOFF = 15

# Conversation sequences - these queries must run in order with context
CONVERSATION_SEQUENCES = [
    # Sequence 1: Top scorer follow-ups
    [
        "Show me the top scorer",  # Initial query
        "What about his assists?",  # Follow-up (Shai)
    ],
    # Sequence 2: LeBron queries
    [
        "Tell me about LeBron's stats",  # Casual reference
        "How many games did he play?",  # Follow-up
        "Compare him to Curry",  # Follow-up comparison
    ],
    # Sequence 3: Best rebounder follow-ups
    [
        "Who's the best rebounder?",  # Initial
        # "How many games did he play?" would follow (Zubac)
    ],
]


def run_conversation_sequence(chat_service: ChatService, questions: list[str]) -> list[dict]:
    """Run a sequence of questions with shared conversation context.

    Args:
        chat_service: Chat service instance
        questions: List of questions in conversation order

    Returns:
        List of results for each question
    """
    conversation_id = str(uuid.uuid4())
    results = []

    logger.info(f"Starting conversation sequence: {conversation_id}")
    logger.info(f"Questions: {questions}")

    for i, question in enumerate(questions, 1):
        logger.info(f"[{i}/{len(questions)}] {question}")

        try:
            request = ChatRequest(
                query=question,
                conversation_id=conversation_id,  # CRITICAL: Share context
                k=5,
                include_sources=True
            )

            # Retry logic
            response = None
            last_error = None

            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = chat_service.chat(request)
                    break

                except Exception as api_error:
                    error_str = str(api_error)
                    is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str

                    if is_rate_limit and attempt < MAX_RETRIES:
                        wait = RETRY_BACKOFF * (attempt + 1)
                        logger.warning(f"  Rate limit, retry {attempt + 1}/{MAX_RETRIES} after {wait}s")
                        time.sleep(wait)
                        last_error = error_str
                    else:
                        raise api_error

            if response is None:
                raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {last_error}")

            # Determine routing
            actual_routing = "sql_only" if (not response.sources or len(response.sources) == 0) else "fallback_to_vector"

            result = {
                "question": question,
                "response": response.answer,
                "actual_routing": actual_routing,
                "sources_count": len(response.sources) if response.sources else 0,
                "processing_time_ms": response.processing_time_ms,
                "generated_sql": response.generated_sql if hasattr(response, 'generated_sql') else None,
                "conversation_id": conversation_id,
                "sequence_position": i,
                "success": True
            }

            results.append(result)
            logger.info(f"  OK: {response.answer[:100]}...")

            # Rate limiting
            time.sleep(RATE_LIMIT_DELAY)

        except Exception as e:
            logger.error(f"  ERROR: {str(e)}")
            results.append({
                "question": question,
                "response": "",
                "actual_routing": "error",
                "sources_count": 0,
                "processing_time_ms": 0.0,
                "generated_sql": None,
                "conversation_id": conversation_id,
                "sequence_position": i,
                "success": False,
                "error": str(e)
            })

            # Continue with sequence even if one fails
            time.sleep(RATE_LIMIT_DELAY)

    return results


def main():
    """Main entry point."""
    print("="*80)
    print("FIXING CONVERSATIONAL QUERIES WITH CONVERSATION CONTEXT")
    print("="*80)
    print()

    # Initialize services
    embedding_service = EmbeddingService()
    chat_service = ChatService(
        embedding_service=embedding_service,
        enable_vector_fallback=False  # Keep fix in place
    )

    all_results = []

    # Run each conversation sequence
    for seq_num, sequence in enumerate(CONVERSATION_SEQUENCES, 1):
        print(f"\n--- Sequence {seq_num}/{len(CONVERSATION_SEQUENCES)} ---")
        results = run_conversation_sequence(chat_service, sequence)
        all_results.extend(results)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"conversational_fix_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # Summary
    success_count = sum(1 for r in all_results if r["success"])
    print("\n" + "="*80)
    print("CONVERSATIONAL QUERIES COMPLETE")
    print("="*80)
    print(f"\nTotal queries: {len(all_results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(all_results) - success_count}")
    print(f"\nResults saved to: {output_path}")
    print("="*80)

    # Display results
    print("\n--- RESULTS ---\n")
    for result in all_results:
        status = "[OK]" if result["success"] else "[FAIL]"
        print(f"{status} Q: {result['question']}")
        print(f"     A: {result['response'][:80]}...")
        if result.get("generated_sql"):
            sql_preview = result["generated_sql"].replace("\n", " ")[:60]
            print(f"     SQL: {sql_preview}...")
        print()


if __name__ == "__main__":
    main()
