"""
FILE: retry_failed_sql_tests.py
STATUS: Active
RESPONSIBILITY: Retry only failed test cases from previous SQL evaluation
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import json
import time
from datetime import datetime
from pathlib import Path

from src.core.config import settings
from src.core.observability import logger
from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.models.chat import ChatRequest
from src.services.chat import ChatService
from src.services.embedding import EmbeddingService

# Rate limiting configuration
RATE_LIMIT_DELAY_SECONDS = 15
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 15

# Failed test case questions from the report
FAILED_QUESTIONS = [
    "How many assists did Chris Paul record?",
    "List all players on the Golden State Warriors.",
    "Who is more efficient goal maker, Jokić or Embiid?",
    "Compare blocks between the top 2 leaders",
    "What is the maximum number of blocks recorded by any player?",
    "Find players with both high scoring (1500+ points) and high assists (400+)",
    "Tell me about LeBron's stats",
    "What about his assists?",
]


def retry_failed_tests():
    """Retry only the failed test cases."""
    logger.info(f"Retrying {len(FAILED_QUESTIONS)} failed test cases")

    # Initialize services with keyword argument fix
    embedding_service = EmbeddingService()
    chat_service = ChatService(
        embedding_service=embedding_service,
        enable_vector_fallback=False  # Disable fallback to prevent FAISS loading
    )

    # Find the test cases to retry
    tests_to_retry = []
    for test_case in SQL_TEST_CASES:
        if test_case.question in FAILED_QUESTIONS:
            tests_to_retry.append(test_case)

    logger.info(f"Found {len(tests_to_retry)} test cases to retry")

    results = []
    success_count = 0
    failure_count = 0

    for i, test_case in enumerate(tests_to_retry, 1):
        logger.info(f"[{i}/{len(tests_to_retry)}] Retrying: {test_case.question}")

        try:
            request = ChatRequest(
                query=test_case.question,
                k=5,
                include_sources=True
            )

            # Retry logic for rate limiting
            response = None
            last_error = None

            for attempt in range(MAX_RETRIES + 1):
                try:
                    response = chat_service.chat(request)
                    break  # Success, exit retry loop

                except Exception as api_error:
                    error_str = str(api_error)

                    # Check if it's a rate limit error (429)
                    is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str

                    if is_rate_limit and attempt < MAX_RETRIES:
                        wait = RETRY_BACKOFF_SECONDS * (attempt + 1)
                        logger.warning(f"  Rate limit hit, retry {attempt + 1}/{MAX_RETRIES} after {wait}s...")
                        time.sleep(wait)
                        last_error = error_str
                    else:
                        # Not a rate limit or out of retries
                        raise api_error

            if response is None:
                raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {last_error}")

            # Determine routing
            actual_routing = "sql_only" if (not response.sources or len(response.sources) == 0) else "fallback_to_vector"
            expected_routing = test_case.query_type.value

            is_misclassified = (
                (expected_routing == "sql_only" and actual_routing != "sql_only") or
                (expected_routing in ["contextual_only", "hybrid"] and actual_routing == "sql_only")
            )

            category = test_case.category if hasattr(test_case, "category") else "unknown"

            results.append({
                "question": test_case.question,
                "category": category,
                "response": response.answer,
                "expected_routing": expected_routing,
                "actual_routing": actual_routing,
                "is_misclassified": is_misclassified,
                "sources_count": len(response.sources) if response.sources else 0,
                "processing_time_ms": response.processing_time_ms,
                "generated_sql": response.generated_sql,
                "success": True
            })

            success_count += 1
            logger.info(f"✓ Success (routing: {actual_routing})")

        except Exception as e:
            logger.error(f"✗ Failed: {str(e)}")
            results.append({
                "question": test_case.question,
                "category": test_case.category if hasattr(test_case, "category") else "unknown",
                "response": "",
                "expected_routing": test_case.query_type.value,
                "actual_routing": "error",
                "is_misclassified": True,
                "sources_count": 0,
                "processing_time_ms": 0.0,
                "generated_sql": None,
                "success": False,
                "error": str(e)
            })
            failure_count += 1

        # Rate limiting delay
        time.sleep(RATE_LIMIT_DELAY_SECONDS)

    logger.info(f"\nRetry complete: {success_count} success, {failure_count} failures")

    # Save retry results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"sql_retry_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Retry results saved to: {json_path}")

    # Print summary
    print("\n" + "="*80)
    print("SQL EVALUATION RETRY COMPLETE")
    print("="*80)
    print(f"\nRetried: {len(tests_to_retry)} test cases")
    print(f"Success: {success_count}")
    print(f"Failures: {failure_count}")
    print(f"\nResults: {json_path}")
    print("="*80)

    return results, str(json_path)


if __name__ == "__main__":
    retry_failed_tests()
