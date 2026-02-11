"""
FILE: evaluate_sql.py
STATUS: Active
RESPONSIBILITY: Master SQL-only evaluation - Tests SQL query generation and execution via API
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
from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.models.chat import ChatResponse
from src.models.feedback import ChatInteractionCreate
from src.services.query_classifier import QueryClassifier, QueryType

logger = logging.getLogger(__name__)

# Gemini free tier: 15 RPM, but each SQL query uses ~2 API calls
# (SQL generation + LLM response) → effective 7.5 queries/min → 8s minimum
RATE_LIMIT_DELAY_SECONDS = 9
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 15  # Wait 15s on 429 before retry


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context."""
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him",
        "which of them", "how many games did he"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def _is_conversational_case(test_case) -> bool:
    """Check if test case is conversational."""
    if hasattr(test_case, 'category') and isinstance(test_case.category, str):
        return "conversational" in test_case.category.lower()
    if hasattr(test_case, 'category') and isinstance(test_case.category, TestCategory):
        return test_case.category == TestCategory.CONVERSATIONAL
    return False


def run_sql_evaluation():
    """
    Master SQL-only evaluation with classification verification.

    Tests SQL query generation and execution with conversation support.
    Uses ALL SQL test cases including conversational ones.
    Generates results through the FastAPI API (POST /api/v1/chat).
    """
    print("\n" + "="*80)
    print("  SQL-ONLY EVALUATION WITH CLASSIFICATION VERIFICATION")
    print("  Tests: SQL query generation, execution, and routing accuracy")
    print("  Mode: API (POST /api/v1/chat) - Full HTTP pipeline")
    print(f"  Test Cases: {len(SQL_TEST_CASES)} total")
    print("="*80 + "\n")

    # Use QueryClassifier directly for accurate routing detection
    classifier = QueryClassifier()

    results = []
    category_counts = {}
    routing_stats = {"sql_only": 0, "vector_only": 0, "hybrid": 0, "unknown": 0}
    misclassifications = []

    # Create FastAPI app and run evaluation through HTTP API
    app = create_app()
    with TestClient(app) as client:
        # Access the initialized ChatService for interaction storage
        # (The chat API endpoint does not store interactions;
        #  this mirrors the Streamlit UI which also stores separately)
        chat_service = get_chat_service()

        current_conversation_id = None
        current_turn_number = 0

        for i, test_case in enumerate(SQL_TEST_CASES, 1):
            category = test_case.category if hasattr(test_case, 'category') else 'unknown'
            category_counts[category] = category_counts.get(category, 0) + 1

            logger.info(f"[{i}/{len(SQL_TEST_CASES)}] {category}: {test_case.question[:60]}...")

            # Rate limit delay (skip before first query)
            if i > 1:
                logger.info(f"  Rate limit delay: {RATE_LIMIT_DELAY_SECONDS}s...")
                time.sleep(RATE_LIMIT_DELAY_SECONDS)

            # Handle conversational test cases
            if _is_conversational_case(test_case):
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

                # Determine actual routing using QueryClassifier directly
                query_type = classifier.classify(test_case.question)
                has_vector_context = len(response.sources) > 0 if response.sources else False

                if query_type == QueryType.HYBRID:
                    actual_routing = "hybrid"
                elif query_type == QueryType.STATISTICAL:
                    actual_routing = "sql_only"
                elif query_type == QueryType.CONTEXTUAL and has_vector_context:
                    actual_routing = "vector_only"
                elif query_type == QueryType.CONTEXTUAL:
                    actual_routing = "vector_only"
                else:
                    actual_routing = "unknown"

                routing_stats[actual_routing] += 1

                # For SQL test cases, we EXPECT sql_only routing
                expected_routing = "sql_only"
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
                logger.info(f"  {status} Expected: {expected_routing} | Actual: {actual_routing} | Time: {response.processing_time_ms}ms")

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
    print(f"\nTotal Test Cases: {len(SQL_TEST_CASES)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")

    print(f"\nCategory Breakdown:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")

    print(f"\nRouting Statistics:")
    print(f"  SQL only: {routing_stats['sql_only']} (EXPECTED)")
    print(f"  Vector only: {routing_stats['vector_only']} (MISCLASSIFICATION)")
    print(f"  Hybrid: {routing_stats['hybrid']} (MISCLASSIFICATION)")
    print(f"  Unknown: {routing_stats['unknown']}")

    classification_accuracy = (routing_stats['sql_only'] / len(SQL_TEST_CASES) * 100) if SQL_TEST_CASES else 0
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
    output_file = output_dir / f"sql_evaluation_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "mode": "api",
        "total_cases": len(SQL_TEST_CASES),
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
        run_sql_evaluation()
    except KeyboardInterrupt:
        print("\n\n[!] Evaluation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
