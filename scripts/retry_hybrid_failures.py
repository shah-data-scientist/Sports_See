"""
FILE: retry_hybrid_failures.py
STATUS: Active
RESPONSIBILITY: Retry failed hybrid evaluation queries with conservative rate limiting
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import io
import json
import logging
import sys
import time
from pathlib import Path

# Fix Windows charmap encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient

from src.api.main import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Very conservative rate limiting (hybrid queries consume 3+ Gemini calls each)
RATE_LIMIT_DELAY = 120  # 120s between queries
MAX_RETRIES = 4
RETRY_BACKOFF = 60  # 60s between retries

HYBRID_JSON = Path("evaluation_results/hybrid_evaluation_20260212_070628.json")


def run_api_query(client, question, conversation_id=None):
    """Run a single query with extended retry logic."""
    payload = {
        "query": question,
        "k": 5,
        "include_sources": True,
        "conversation_id": conversation_id,
    }

    for attempt in range(MAX_RETRIES + 1):
        response = client.post("/api/v1/chat", json=payload)

        if response.status_code == 200:
            return response.json()

        is_rate_limit = (
            response.status_code == 429
            or (response.status_code == 500 and "429" in response.text)
            or (response.status_code == 500 and "rate" in response.text.lower())
        )

        if is_rate_limit and attempt < MAX_RETRIES:
            wait = RETRY_BACKOFF * (attempt + 1)
            logger.warning(f"  Rate limit, retry {attempt + 1}/{MAX_RETRIES} after {wait}s...")
            time.sleep(wait)
        else:
            raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

    raise RuntimeError("Max retries exhausted")


def main():
    """Retry failed hybrid queries."""
    data = json.loads(HYBRID_JSON.read_text(encoding="utf-8"))
    results = data["results"]

    failed_indices = [i for i, r in enumerate(results) if not r.get("success")]

    if not failed_indices:
        logger.info("No failures found!")
        return

    logger.info(f"Found {len(failed_indices)} failed queries to retry")
    logger.info(f"Rate limit delay: {RATE_LIMIT_DELAY}s | Estimated time: ~{len(failed_indices) * RATE_LIMIT_DELAY / 60:.0f} min")

    app = create_app()
    all_ok = True

    with TestClient(app) as client:
        for fi, idx in enumerate(failed_indices):
            question = results[idx]["question"]
            category = results[idx].get("category", "unknown")
            logger.info(f"  [{fi + 1}/{len(failed_indices)}] Retrying [{category}]: {question[:70]}...")

            if fi > 0:
                logger.info(f"  Waiting {RATE_LIMIT_DELAY}s...")
                time.sleep(RATE_LIMIT_DELAY)

            try:
                api_result = run_api_query(client, question)

                sources = api_result.get("sources", [])
                generated_sql = api_result.get("generated_sql")
                has_sql = generated_sql is not None and len(generated_sql) > 0
                has_vector = len(sources) > 0

                if has_sql and has_vector:
                    routing = "both"
                elif has_sql:
                    routing = "sql"
                elif has_vector:
                    routing = "vector"
                else:
                    routing = "unknown"

                # Update the result in-place, preserving existing fields
                results[idx].update({
                    "response": api_result.get("answer", ""),
                    "routing": routing,
                    "generated_sql": generated_sql,
                    "sources": sources,
                    "sources_count": len(sources),
                    "processing_time_ms": api_result.get("processing_time_ms", 0),
                    "success": True,
                })
                # Remove error field
                results[idx].pop("error", None)

                logger.info(f"  OK | Routing: {routing.upper()} | Sources: {len(sources)} | Time: {api_result.get('processing_time_ms', 0):.0f}ms")

            except Exception as e:
                logger.error(f"  FAILED AGAIN: {e}")
                all_ok = False

            # Save checkpoint after each query
            data["results"] = results
            HYBRID_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update metadata
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    data["metadata"]["successful"] = successful
    data["metadata"]["failed"] = failed
    data["metadata"]["success_rate"] = round(successful / len(results) * 100, 1)
    HYBRID_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"\nRetry complete: {successful}/{len(results)} successful")
    if all_ok:
        logger.info("All retries succeeded!")
    else:
        logger.warning("Some queries still failed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nInterrupted.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Retry failed: {e}", exc_info=True)
        sys.exit(1)
