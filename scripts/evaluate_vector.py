"""
FILE: evaluate_vector.py
STATUS: Active
RESPONSIBILITY: Master Vector-only evaluation - Tests FAISS vector search with Mistral embeddings via API
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import io
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from starlette.testclient import TestClient

from src.api.dependencies import get_chat_service
from src.api.main import create_app
from src.evaluation.models import TestCategory
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES
from src.models.chat import ChatResponse
from src.models.feedback import ChatInteractionCreate

logger = logging.getLogger(__name__)

# Gemini free tier: 15 RPM
RATE_LIMIT_DELAY_SECONDS = 12  # Increased from 5 to 12 seconds
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 15  # Start with 15s, then 30s, then 60s


def _retry_with_backoff(func, max_retries=MAX_RETRIES):
    """Retry function with exponential backoff on 429 errors.

    Args:
        func: Function to retry (should return result or raise exception)
        max_retries: Maximum number of retry attempts

    Returns:
        Result from func() if successful

    Raises:
        Last exception if all retries exhausted
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except RuntimeError as e:
            error_msg = str(e)

            # Check if it's a 429 rate limit error
            is_rate_limit = "429" in error_msg and ("RESOURCE_EXHAUSTED" in error_msg or "rate" in error_msg.lower())

            if is_rate_limit and attempt < max_retries:
                # Exponential backoff: 15s, 30s, 60s
                wait_time = RETRY_BACKOFF_BASE * (2 ** attempt)
                logger.warning(f"  ⚠️ 429 Rate Limit (attempt {attempt + 1}/{max_retries + 1}). "
                             f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                # Non-rate-limit error or final attempt - re-raise
                raise
        except Exception as e:
            # Non-retryable error - re-raise immediately
            raise

    # Should never reach here, but just in case
    raise RuntimeError("Max retries exhausted")


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context."""
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def get_vector_test_cases():
    """
    Get test cases suitable for vector-only evaluation.

    Includes:
    - NOISY: Contextual, opinion-based queries
    - CONVERSATIONAL: Follow-up questions
    - Some COMPLEX: Queries needing contextual understanding

    Excludes:
    - SIMPLE: Statistical queries (better for SQL)
    """
    vector_cases = []

    for tc in EVALUATION_TEST_CASES:
        # Include NOISY (contextual/opinion queries)
        if tc.category == TestCategory.NOISY:
            vector_cases.append(tc)
        # Include CONVERSATIONAL (follow-up questions)
        elif tc.category == TestCategory.CONVERSATIONAL:
            vector_cases.append(tc)
        # Include COMPLEX queries that need context (not just stats)
        elif tc.category == TestCategory.COMPLEX:
            # Filter: Include if question has contextual keywords
            contextual_keywords = [
                "why", "explain", "analysis", "discuss", "opinion",
                "strategy", "style", "valuable", "effective", "impact"
            ]
            if any(kw in tc.question.lower() for kw in contextual_keywords):
                vector_cases.append(tc)

    return vector_cases


def run_vector_evaluation(limit=None, offset=0):
    """
    Master Vector-only evaluation with classification verification.

    Tests FAISS vector search with conversation support.
    Uses NOISY, CONVERSATIONAL, and contextual COMPLEX test cases.
    Generates results through the FastAPI API (POST /api/v1/chat).
    """
    vector_cases = get_vector_test_cases()

    # Apply batch limiting (for running 10 at a time)
    total_cases = len(vector_cases)
    if offset > 0:
        vector_cases = vector_cases[offset:]
    if limit is not None:
        vector_cases = vector_cases[:limit]

    batch_info = f" (batch: {offset + 1}-{offset + len(vector_cases)} of {total_cases})" if (offset > 0 or limit) else ""

    print("\n" + "="*80)
    print("  VECTOR-ONLY EVALUATION WITH CLASSIFICATION VERIFICATION")
    print("  Tests: FAISS vector search + Mistral embeddings + routing accuracy")
    print("  Mode: API (POST /api/v1/chat) - Full HTTP pipeline")
    print(f"  Test Cases: {len(vector_cases)}{batch_info}")
    print("="*80 + "\n")

    results = []
    category_counts = {}
    routing_stats = {"sql_only": 0, "vector_only": 0, "hybrid": 0, "unknown": 0}
    misclassifications = []

    # Create FastAPI app and run evaluation through HTTP API
    app = create_app()
    with TestClient(app) as client:
        # Access the initialized ChatService for interaction storage
        chat_service = get_chat_service()

        current_conversation_id = None
        current_turn_number = 0

        for i, test_case in enumerate(vector_cases, 1):
            category = test_case.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

            logger.info(f"[{i}/{len(vector_cases)}] {category}: {test_case.question[:60]}...")

            # Rate limit delay (skip before first query)
            if i > 1:
                logger.info(f"  Rate limit delay: {RATE_LIMIT_DELAY_SECONDS}s...")
                time.sleep(RATE_LIMIT_DELAY_SECONDS)

            # Handle conversational test cases
            if test_case.category == TestCategory.CONVERSATIONAL:
                if _is_followup_question(test_case.question):
                    if current_conversation_id is None:
                        conv_resp = client.post("/api/v1/conversations", json={})
                        current_conversation_id = conv_resp.json()["id"]
                        current_turn_number = 1
                    else:
                        current_turn_number += 1
                else:
                    conv_resp = client.post("/api/v1/conversations", json={})
                    current_conversation_id = conv_resp.json()["id"]
                    current_turn_number = 1
            else:
                current_conversation_id = None
                current_turn_number = 0

            try:
                # Build API request payload
                payload = {
                    "query": test_case.question,
                    "k": 5,
                    "include_sources": True,
                    "conversation_id": current_conversation_id,
                    "turn_number": current_turn_number if current_conversation_id else 1,
                }

                # Execute via API with retry logic
                def api_call():
                    http_response = client.post("/api/v1/chat", json=payload)
                    if http_response.status_code != 200:
                        raise RuntimeError(
                            f"API error {http_response.status_code}: {http_response.text[:300]}"
                        )
                    return ChatResponse.model_validate(http_response.json())

                response = _retry_with_backoff(api_call)

                # Store interaction for conversation context
                if current_conversation_id:
                    interaction = ChatInteractionCreate(
                        query=test_case.question,
                        response=response.answer,
                        sources=[s.source for s in response.sources] if response.sources else [],
                        processing_time_ms=int(response.processing_time_ms) if response.processing_time_ms else None,
                        conversation_id=current_conversation_id,
                        turn_number=current_turn_number,
                    )
                    chat_service.feedback_repository.save_interaction(interaction)

                # Determine actual routing based on response characteristics
                has_sql_data = any(
                    kw in response.answer.lower()
                    for kw in ["pts", "reb", "ast", "points", "rebounds", "assists", "ppg", "rpg", "apg"]
                )
                has_vector_context = len(response.sources) > 0 if response.sources else False

                if has_sql_data and has_vector_context:
                    actual_routing = "hybrid"
                elif has_sql_data:
                    actual_routing = "sql_only"
                elif has_vector_context:
                    actual_routing = "vector_only"
                else:
                    actual_routing = "unknown"

                routing_stats[actual_routing] += 1

                # For Vector test cases, we EXPECT vector_only routing
                expected_routing = "vector_only"
                is_misclassified = actual_routing != expected_routing

                if is_misclassified:
                    misclassifications.append({
                        "question": test_case.question,
                        "category": category,
                        "expected": expected_routing,
                        "actual": actual_routing,
                        "response_preview": response.answer[:150]
                    })

                results.append({
                    "question": test_case.question,
                    "category": category,
                    "response": response.answer,
                    "expected_routing": expected_routing,
                    "actual_routing": actual_routing,
                    "is_misclassified": is_misclassified,
                    "sources_count": len(response.sources) if response.sources else 0,
                    "processing_time_ms": response.processing_time_ms,
                    "success": True
                })

                status = "[PASS]" if not is_misclassified else "[MISCLASS]"
                logger.info(f"  {status} Expected: {expected_routing} | Actual: {actual_routing} | "
                           f"Sources: {len(response.sources) if response.sources else 0} | Time: {response.processing_time_ms}ms")

            except Exception as e:
                logger.error(f"  [FAIL] Error: {e}")
                results.append({
                    "question": test_case.question,
                    "category": category,
                    "error": str(e),
                    "success": False
                })

    # Print summary
    print("\n" + "="*80)
    print("  EVALUATION SUMMARY")
    print("="*80)
    print(f"\nTotal Test Cases: {len(vector_cases)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    print(f"\nCategory Breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    print(f"\nRouting Statistics:")
    print(f"  SQL only: {routing_stats['sql_only']} (MISCLASSIFICATION)")
    print(f"  Vector only: {routing_stats['vector_only']} (EXPECTED)")
    print(f"  Hybrid: {routing_stats['hybrid']} (MISCLASSIFICATION)")
    print(f"  Unknown: {routing_stats['unknown']}")

    classification_accuracy = (routing_stats['vector_only'] / len(vector_cases) * 100) if vector_cases else 0
    print(f"\nClassification Accuracy: {classification_accuracy:.1f}%")
    print(f"Misclassifications: {len(misclassifications)}")

    if misclassifications:
        print(f"\nTop Misclassifications (showing first 10):")
        for i, misc in enumerate(misclassifications[:10], 1):
            print(f"\n  [{i}] Expected: {misc['expected']} | Actual: {misc['actual']}")
            print(f"      Question: {misc['question']}")
            print(f"      Response: {misc['response_preview']}...")

    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"vector_evaluation_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": "api",
        "total_cases": len(vector_cases),
        "successful": sum(1 for r in results if r['success']),
        "failed": sum(1 for r in results if not r['success']),
        "category_counts": category_counts,
        "routing_stats": routing_stats,
        "classification_accuracy": classification_accuracy,
        "misclassifications": misclassifications,
        "results": results
    }

    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Vector-only evaluation with batch support")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit evaluation to first N queries (for batching)")
    parser.add_argument("--offset", type=int, default=0,
                       help="Start from query N (for batching)")
    args = parser.parse_args()

    # Fix Windows charmap encoding (Jokić etc.)
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    # Prevent FAISS/OpenMP DLL conflict crash on Windows
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        run_vector_evaluation(limit=args.limit, offset=args.offset)
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
