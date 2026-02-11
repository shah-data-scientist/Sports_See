"""
FILE: evaluate_hybrid.py
STATUS: Active
RESPONSIBILITY: Master Hybrid evaluation - Tests intelligent SQL + Vector routing via API
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
from src.evaluation.hybrid_test_cases import HYBRID_TEST_CASES
from src.evaluation.models import TestCategory
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES
from src.models.chat import ChatResponse
from src.models.feedback import ChatInteractionCreate

logger = logging.getLogger(__name__)

# Gemini free tier: 15 RPM
RATE_LIMIT_DELAY_SECONDS = 9
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 15


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context."""
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def get_hybrid_test_cases():
    """
    Get test cases suitable for hybrid evaluation.

    Includes:
    - HYBRID_TEST_CASES: Dedicated true hybrid queries (SQL + Vector)
    - COMPLEX from EVALUATION_TEST_CASES: Multi-step queries
    - CONVERSATIONAL: Testing routing with conversation context

    NOTE: SIMPLE cases removed - they are pure SQL queries and belong only in SQL evaluation.
    """
    hybrid_cases = []

    # Add all dedicated hybrid test cases
    hybrid_cases.extend(HYBRID_TEST_CASES)

    # Add COMPLEX and CONVERSATIONAL cases from main evaluation set
    # SIMPLE cases removed - they should only be in SQL evaluation
    for tc in EVALUATION_TEST_CASES:
        if tc.category in [TestCategory.COMPLEX, TestCategory.CONVERSATIONAL]:
            hybrid_cases.append(tc)

    return hybrid_cases


def run_hybrid_evaluation():
    """
    Master Hybrid evaluation.

    Tests intelligent routing between SQL and Vector search.
    Uses COMPLEX, CONVERSATIONAL, and HYBRID test cases.
    Generates results through the FastAPI API (POST /api/v1/chat).
    """
    hybrid_cases = get_hybrid_test_cases()

    print("\n" + "="*80)
    print("  HYBRID EVALUATION (SQL + VECTOR)")
    print("  Tests: Intelligent routing between SQL and Vector search")
    print("  Mode: API (POST /api/v1/chat) - Full HTTP pipeline")
    print(f"  Test Cases: {len(hybrid_cases)} from multiple sources")
    print("="*80 + "\n")

    results = []
    category_counts = {}
    routing_stats = {"sql": 0, "vector": 0, "both": 0, "unknown": 0}

    # Create FastAPI app and run evaluation through HTTP API
    app = create_app()
    with TestClient(app) as client:
        # Access the initialized ChatService for interaction storage
        chat_service = get_chat_service()

        current_conversation_id = None
        current_turn_number = 0

        for i, test_case in enumerate(hybrid_cases, 1):
            category = test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category)
            category_counts[category] = category_counts.get(category, 0) + 1

            logger.info(f"[{i}/{len(hybrid_cases)}] {category}: {test_case.question[:60]}...")

            # Rate limit delay (skip before first query)
            if i > 1:
                logger.info(f"  Rate limit delay: {RATE_LIMIT_DELAY_SECONDS}s...")
                time.sleep(RATE_LIMIT_DELAY_SECONDS)

            # Handle conversational test cases
            is_conversational = (
                (hasattr(test_case.category, 'value') and test_case.category == TestCategory.CONVERSATIONAL) or
                (isinstance(test_case.category, str) and "conversational" in test_case.category.lower())
            )

            if is_conversational:
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

                # Execute via API with retry for rate limits
                http_response = None
                last_error = None
                for attempt in range(MAX_RETRIES + 1):
                    http_response = client.post("/api/v1/chat", json=payload)

                    if http_response.status_code == 200:
                        break

                    # Retry on rate limit (429) or server error containing "429"
                    is_rate_limit = (
                        http_response.status_code == 429
                        or (http_response.status_code == 500 and "429" in http_response.text)
                    )
                    if is_rate_limit and attempt < MAX_RETRIES:
                        wait = RETRY_BACKOFF_SECONDS * (attempt + 1)
                        logger.warning(f"  Rate limit hit, retry {attempt + 1}/{MAX_RETRIES} after {wait}s...")
                        time.sleep(wait)
                    else:
                        last_error = f"API error {http_response.status_code}: {http_response.text[:300]}"
                        break

                if http_response is None or http_response.status_code != 200:
                    raise RuntimeError(last_error or "No response from API")

                # Parse API response into ChatResponse model
                response = ChatResponse.model_validate(http_response.json())

                # Store interaction for conversation context (enables follow-up pronoun resolution)
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

                # Determine which component was used
                has_sql_data = any(
                    kw in response.answer.lower()
                    for kw in ["pts", "reb", "ast", "points", "rebounds", "assists", "ppg", "rpg"]
                )
                has_vector_context = len(response.sources) > 0 if response.sources else False

                if has_sql_data and has_vector_context:
                    routing = "both"
                elif has_sql_data:
                    routing = "sql"
                elif has_vector_context:
                    routing = "vector"
                else:
                    routing = "unknown"

                routing_stats[routing] += 1

                results.append({
                    "question": test_case.question,
                    "category": category,
                    "response": response.answer,
                    "routing": routing,
                    "sources_count": len(response.sources) if response.sources else 0,
                    "processing_time_ms": response.processing_time_ms,
                    "success": True
                })

                logger.info(f"  [PASS] Routing: {routing.upper()} | "
                           f"Sources: {len(response.sources) if response.sources else 0} | "
                           f"Time: {response.processing_time_ms}ms")

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
    print(f"\nTotal Test Cases: {len(hybrid_cases)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    print(f"\nCategory Breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    print(f"\nRouting Statistics:")
    print(f"  SQL only: {routing_stats['sql']}")
    print(f"  Vector only: {routing_stats['vector']}")
    print(f"  Both (Hybrid): {routing_stats['both']}")
    print(f"  Unknown: {routing_stats['unknown']}")

    # Save results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"hybrid_evaluation_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": "api",
        "total_cases": len(hybrid_cases),
        "successful": sum(1 for r in results if r['success']),
        "failed": sum(1 for r in results if not r['success']),
        "category_counts": category_counts,
        "routing_stats": routing_stats,
        "results": results
    }

    output_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == "__main__":
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
        run_hybrid_evaluation()
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
