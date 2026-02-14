"""
FILE: retry_failed_queries.py
STATUS: Active
RESPONSIBILITY: Retry failed sample evaluation queries and regenerate reports
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu

Retries only the failed queries from the sample evaluation, merges results
back into existing JSON files, and regenerates MD reports.
"""

import io
import json
import logging
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Fix Windows charmap encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient

from src.api.main import create_app
from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES, HYBRID_TEST_CASES
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Very conservative rate limiting for retry (Gemini free tier is 15 RPM)
# Hybrid queries consume 2 Gemini calls, plus internal retries can burn 4+ calls each
RATE_LIMIT_DELAY = 120  # 120s between queries to ensure full rate limit reset
MAX_RETRIES = 3
RETRY_BACKOFF = 60  # 60s between retries within a single query

OUTPUT_DIR = Path("evaluation_results")

# Existing result files to update
HYBRID_JSON = OUTPUT_DIR / "hybrid_sample_evaluation_20260212_024528.json"
VECTOR_JSON = OUTPUT_DIR / "vector_sample_evaluation_20260212_025121.json"


def run_api_query(client, question: str, conversation_id: str | None = None) -> dict:
    """Run a single query through the API with extended retry logic."""
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
        )

        if is_rate_limit and attempt < MAX_RETRIES:
            wait = RETRY_BACKOFF * (attempt + 1)
            logger.warning(f"  Rate limit hit, retry {attempt + 1}/{MAX_RETRIES} after {wait}s...")
            time.sleep(wait)
        else:
            raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

    raise RuntimeError("Max retries exhausted")


def retry_hybrid_failed(client) -> bool:
    """Retry failed hybrid query and update existing JSON."""
    logger.info("=" * 70)
    logger.info("RETRYING HYBRID FAILED QUERY")
    logger.info("=" * 70)

    # Load existing results
    results = json.loads(HYBRID_JSON.read_text(encoding="utf-8"))

    # Find failed entries
    failed_indices = [i for i, r in enumerate(results) if not r.get("success")]
    if not failed_indices:
        logger.info("No failed hybrid queries found!")
        return True

    logger.info(f"Found {len(failed_indices)} failed queries to retry")
    all_ok = True

    for fi, idx in enumerate(failed_indices):
        question = results[idx]["question"]
        category = results[idx]["category"]
        logger.info(f"  Retrying [{category}]: {question[:70]}...")

        if fi > 0:
            logger.info(f"  Waiting {RATE_LIMIT_DELAY}s...")
            time.sleep(RATE_LIMIT_DELAY)

        # Find original test case for ground truth
        original_tc = None
        for tc in HYBRID_TEST_CASES:
            if tc.question == question:
                original_tc = tc
                break

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

            results[idx] = {
                "question": question,
                "category": category,
                "response": api_result.get("answer", ""),
                "routing": routing,
                "generated_sql": generated_sql,
                "sources": sources,
                "sources_count": len(sources),
                "processing_time_ms": api_result.get("processing_time_ms", 0),
                "ground_truth_answer": original_tc.ground_truth_answer if original_tc else "",
                "success": True,
            }
            logger.info(f"  OK | Routing: {routing.upper()} | Sources: {len(sources)} | Time: {api_result.get('processing_time_ms', 0)}ms")

        except Exception as e:
            logger.error(f"  FAILED AGAIN: {e}")
            all_ok = False

    # Always save results (even partial)
    HYBRID_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"  Updated JSON: {HYBRID_JSON}")

    # Regenerate MD report
    md_path = HYBRID_JSON.with_name(
        HYBRID_JSON.name.replace("evaluation_", "evaluation_report_").replace(".json", ".md")
    )
    _generate_hybrid_sample_report(results, md_path, HYBRID_JSON.name)
    logger.info(f"  Updated report: {md_path}")

    return all_ok


def retry_vector_failed(client) -> bool:
    """Retry failed vector queries and update existing JSON."""
    logger.info("=" * 70)
    logger.info("RETRYING VECTOR FAILED QUERIES")
    logger.info("=" * 70)

    # Load existing results
    results = json.loads(VECTOR_JSON.read_text(encoding="utf-8"))

    # Find failed entries
    failed_indices = [i for i, r in enumerate(results) if not r.get("success")]
    if not failed_indices:
        logger.info("No failed vector queries found!")
        return True

    logger.info(f"Found {len(failed_indices)} failed queries to retry")
    all_ok = True

    for fi, idx in enumerate(failed_indices):
        question = results[idx]["question"]
        category = results[idx]["category"]
        logger.info(f"  Retrying [{category}]: {question[:70]}...")

        if fi > 0:
            logger.info(f"  Waiting {RATE_LIMIT_DELAY}s...")
            time.sleep(RATE_LIMIT_DELAY)

        # Find original test case for ground truth
        original_tc = None
        for tc in EVALUATION_TEST_CASES:
            if tc.question == question:
                original_tc = tc
                break

        try:
            api_result = run_api_query(client, question)

            sources = api_result.get("sources", [])
            has_vector = len(sources) > 0
            actual_routing = "vector_only" if has_vector else "unknown"

            results[idx] = {
                "question": question,
                "category": category,
                "response": api_result.get("answer", ""),
                "actual_routing": actual_routing,
                "sources": [
                    {
                        "text": s.get("text", "")[:500],
                        "score": s.get("score", 0),
                        "source": s.get("source", "unknown"),
                    }
                    for s in sources
                ],
                "sources_count": len(sources),
                "processing_time_ms": api_result.get("processing_time_ms", 0),
                "ground_truth": original_tc.ground_truth if original_tc else "",
                "success": True,
            }
            logger.info(f"  OK | Sources: {len(sources)} | Time: {api_result.get('processing_time_ms', 0)}ms")

        except Exception as e:
            logger.error(f"  FAILED AGAIN: {e}")
            all_ok = False

        # Save checkpoint after each query (even if failed)
        VECTOR_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Regenerate MD report
    md_path = VECTOR_JSON.with_name(
        VECTOR_JSON.name.replace("evaluation_", "evaluation_report_").replace(".json", ".md")
    )
    _generate_vector_sample_report(results, md_path, VECTOR_JSON.name)
    logger.info(f"  Updated JSON: {VECTOR_JSON}")
    logger.info(f"  Updated report: {md_path}")

    return all_ok


# ==========================================================================
# REPORT GENERATORS (same as run_sample_evaluation.py)
# ==========================================================================


def _generate_hybrid_sample_report(results: list[dict], md_path: Path, json_name: str) -> None:
    """Generate Hybrid sample evaluation markdown report."""
    total = len(results)
    successful = sum(1 for r in results if r.get("success"))
    times = [r["processing_time_ms"] for r in results if r.get("success")]

    routing_counts = defaultdict(int)
    for r in results:
        routing_counts[r.get("routing", "unknown")] += 1

    lines = [
        "# Hybrid Sample Evaluation Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Sample Size:** {total} queries (from {len(HYBRID_TEST_CASES)} total)",
        f"**Results JSON:** `{json_name}`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Total Queries:** {total}",
        f"- **Successful:** {successful}/{total} ({successful / total * 100:.0f}%)",
        f"- **Avg Processing Time:** {sum(times) / len(times):.0f}ms" if times else "- **Avg Processing Time:** N/A",
        "",
        "### Routing Distribution",
        "",
        "| Routing | Count |",
        "|---------|-------|",
    ]

    for routing, count in sorted(routing_counts.items()):
        lines.append(f"| {routing.upper()} | {count} |")

    lines.extend(["", "## Query-by-Query Results", ""])

    for i, r in enumerate(results, 1):
        status = "PASS" if r.get("success") else "FAIL"
        lines.extend([
            f"### {i}. [{status}] {r['question'][:80]}",
            "",
            f"- **Category:** {r.get('category', 'unknown')}",
            f"- **Routing:** {r.get('routing', 'N/A').upper()}",
            f"- **Sources:** {r.get('sources_count', 0)}",
            f"- **Processing Time:** {r.get('processing_time_ms', 0):.0f}ms",
        ])

        if r.get("generated_sql"):
            lines.append(f"- **Generated SQL:** `{r['generated_sql'][:150]}`")

        if r.get("ground_truth_answer"):
            lines.append(f"- **Expected Answer:** {r['ground_truth_answer'][:200]}")

        lines.extend([
            f"- **Response:** {r.get('response', '')[:400]}{'...' if len(r.get('response', '')) > 400 else ''}",
            "",
        ])

        sources = r.get("sources", [])
        if sources:
            lines.extend([
                "**Sources Retrieved:**",
                "",
                "| # | Source | Score |",
                "|---|--------|-------|",
            ])
            for si, s in enumerate(sources[:5], 1):
                source_name = s.get("source", "unknown") if isinstance(s, dict) else str(s)
                score = s.get("score", 0) if isinstance(s, dict) else 0
                lines.append(f"| {si} | {source_name[:40]} | {score:.1f}% |")
            lines.append("")

        if r.get("error"):
            lines.append(f"- **Error:** {r['error']}")
            lines.append("")

    lines.extend([
        "---",
        "",
        f"*Report generated from {total}-case sample of {len(HYBRID_TEST_CASES)} Hybrid test cases*",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")


def _generate_vector_sample_report(results: list[dict], md_path: Path, json_name: str) -> None:
    """Generate Vector sample evaluation markdown report."""
    total = len(results)
    successful = sum(1 for r in results if r.get("success"))
    times = [r["processing_time_ms"] for r in results if r.get("success")]

    lines = [
        "# Vector Sample Evaluation Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Sample Size:** {total} queries (from {len(EVALUATION_TEST_CASES)} total)",
        f"**Results JSON:** `{json_name}`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Total Queries:** {total}",
        f"- **Successful:** {successful}/{total} ({successful / total * 100:.0f}%)",
        f"- **Avg Processing Time:** {sum(times) / len(times):.0f}ms" if times else "- **Avg Processing Time:** N/A",
        "",
        "## Query-by-Query Results",
        "",
    ]

    for i, r in enumerate(results, 1):
        status = "PASS" if r.get("success") else "FAIL"
        lines.extend([
            f"### {i}. [{status}] {r['question'][:80]}",
            "",
            f"- **Category:** {r.get('category', 'unknown')}",
            f"- **Routing:** {r.get('actual_routing', 'N/A')}",
            f"- **Sources Retrieved:** {r.get('sources_count', 0)}",
            f"- **Processing Time:** {r.get('processing_time_ms', 0):.0f}ms",
        ])

        lines.extend([
            f"- **Response:** {r.get('response', '')[:400]}{'...' if len(r.get('response', '')) > 400 else ''}",
            "",
        ])

        sources = r.get("sources", [])
        if sources:
            lines.extend([
                "**Sources Retrieved:**",
                "",
                "| # | Source | Score | Text Preview |",
                "|---|--------|-------|--------------|",
            ])
            for si, s in enumerate(sources[:5], 1):
                source_name = s.get("source", "unknown")[:30]
                score = s.get("score", 0)
                text_preview = s.get("text", "")[:60].replace("|", " ").replace("\n", " ")
                lines.append(f"| {si} | {source_name} | {score:.1f}% | {text_preview}... |")
            lines.append("")

        if r.get("ground_truth"):
            lines.append(f"- **Ground Truth:** {r['ground_truth'][:200]}...")
            lines.append("")

        if r.get("error"):
            lines.append(f"- **Error:** {r['error']}")
            lines.append("")

    lines.extend([
        "---",
        "",
        f"*Report generated from {total}-case sample of {len(EVALUATION_TEST_CASES)} Vector test cases*",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")


# ==========================================================================
# MAIN
# ==========================================================================


def main():
    """Retry failed queries from sample evaluation."""
    logger.info("=" * 70)
    logger.info("RETRY FAILED QUERIES (1 hybrid + 2 vector)")
    logger.info(f"Rate limit delay: {RATE_LIMIT_DELAY}s between queries")
    logger.info(f"Estimated time: ~{3 * RATE_LIMIT_DELAY / 60:.0f} minutes")
    logger.info("=" * 70)

    app = create_app()

    with TestClient(app) as client:
        # 1. Retry hybrid
        hybrid_ok = retry_hybrid_failed(client)

        # Always wait between datasets
        logger.info(f"Waiting {RATE_LIMIT_DELAY}s before vector retries...")
        time.sleep(RATE_LIMIT_DELAY)

        # 2. Retry vector
        vector_ok = retry_vector_failed(client)

    logger.info("")
    logger.info("=" * 70)
    logger.info("RETRY COMPLETE")
    logger.info(f"  Hybrid: {'OK' if hybrid_ok else 'STILL FAILED'}")
    logger.info(f"  Vector: {'OK' if vector_ok else 'STILL FAILED'}")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Retry failed: {e}", exc_info=True)
        sys.exit(1)
