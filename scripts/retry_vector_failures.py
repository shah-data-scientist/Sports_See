"""
FILE: retry_vector_failures.py
STATUS: Active
RESPONSIBILITY: Retry failed vector evaluation queries (excluding expected failures like >2000 char)
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import io
import json
import logging
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RATE_LIMIT_DELAY = 120
MAX_RETRIES = 4
RETRY_BACKOFF = 60

VECTOR_JSON = Path("evaluation_results/vector_evaluation_20260212_055129.json")


def run_api_query(client, question):
    """Run a single query with extended retry logic."""
    payload = {"query": question, "k": 5, "include_sources": True}

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
    """Retry retryable vector failures (skip expected failures like >2000 char queries)."""
    data = json.loads(VECTOR_JSON.read_text(encoding="utf-8"))
    results = data["results"]

    # Find retryable failures (skip 422 which is expected for >2000 char queries)
    retryable = []
    for i, r in enumerate(results):
        if not r.get("success"):
            error = r.get("error", "")
            if "422" not in error and "string_too_long" not in error:
                retryable.append(i)
            else:
                logger.info(f"  Skipping expected failure [{i}]: {r['question'][:50]}... (422 validation)")

    if not retryable:
        logger.info("No retryable failures found!")
        return

    logger.info(f"Found {len(retryable)} retryable failures")

    app = create_app()
    with TestClient(app) as client:
        for fi, idx in enumerate(retryable):
            question = results[idx]["question"]
            category = results[idx].get("category", "unknown")
            logger.info(f"  [{fi + 1}/{len(retryable)}] Retrying [{category}]: {question[:70]}...")

            if fi > 0:
                time.sleep(RATE_LIMIT_DELAY)

            try:
                api_result = run_api_query(client, question)
                sources = api_result.get("sources", [])

                results[idx].update({
                    "response": api_result.get("answer", ""),
                    "actual_routing": "vector_only" if len(sources) > 0 else "unknown",
                    "sources": [
                        {"text": s.get("text", "")[:500], "score": s.get("score", 0), "source": s.get("source", "unknown")}
                        for s in sources
                    ],
                    "sources_count": len(sources),
                    "processing_time_ms": api_result.get("processing_time_ms", 0),
                    "success": True,
                })
                results[idx].pop("error", None)
                logger.info(f"  OK | Sources: {len(sources)} | Time: {api_result.get('processing_time_ms', 0):.0f}ms")

            except Exception as e:
                logger.error(f"  FAILED AGAIN: {e}")

            # Save checkpoint
            data["results"] = results
            VECTOR_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update metadata
    successful = sum(1 for r in results if r.get("success"))
    data["metadata"]["successful_queries"] = successful
    data["metadata"]["failed_queries"] = len(results) - successful
    VECTOR_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"\nDone: {successful}/{len(results)} successful")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
