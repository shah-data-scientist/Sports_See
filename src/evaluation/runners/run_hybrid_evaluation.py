"""
FILE: run_hybrid_evaluation.py
STATUS: Active
RESPONSIBILITY: Master Hybrid evaluation - Tests SQL + Vector integration via API
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from starlette.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.main import create_app
from src.evaluation.analysis.hybrid_quality_analysis import analyze_hybrid_results, generate_markdown_report
from src.evaluation.test_cases.sql_test_cases import HYBRID_TEST_CASES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiting configuration for Gemini free tier
RATE_LIMIT_DELAY_SECONDS = 15
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 15


def _is_followup_question(question: str) -> bool:
    """Check if question is a follow-up requiring conversation context."""
    question_lower = question.lower()
    followup_indicators = [
        "his ", "her ", "their ", "its ", "he ", "she ", "they ",
        "what about", "and what", "how does that", "compare him",
        "which of them", "what are", "and their"
    ]
    return any(indicator in question_lower for indicator in followup_indicators)


def run_hybrid_evaluation(resume: bool = True) -> tuple[list[dict[str, Any]], str]:
    """
    Run Hybrid evaluation on all test cases using FastAPI API.

    Features:
    - API-only: Uses TestClient for full HTTP pipeline
    - Checkpointing: Saves after EACH query for recovery
    - Resume: Auto-resumes from checkpoint if available
    - Quality Analysis: Comprehensive routing, SQL, vector, and combination analysis
    - Output: JSON + MD comprehensive report

    Args:
        resume: If True, resume from checkpoint if available

    Returns:
        Tuple of (results list, output JSON path)
    """
    logger.info("="*80)
    logger.info("HYBRID EVALUATION (SQL + Vector Integration)")
    logger.info(f"Test Cases: {len(HYBRID_TEST_CASES)}")
    logger.info(f"Mode: API-based (POST /api/v1/chat)")
    logger.info("="*80)

    # Checkpoint file
    checkpoint_file = Path("evaluation_results") / "hybrid_evaluation_checkpoint.json"
    checkpoint_file.parent.mkdir(exist_ok=True)

    # Resume from checkpoint
    results = []
    start_index = 0

    if resume and checkpoint_file.exists():
        try:
            checkpoint_data = json.loads(checkpoint_file.read_text(encoding="utf-8"))
            results = checkpoint_data.get("results", [])
            start_index = len(results)
            logger.info(f"✓ Resuming from checkpoint: {start_index}/{len(HYBRID_TEST_CASES)} completed")
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}. Starting fresh.")

    success_count = sum(1 for r in results if r.get("success", False))
    failure_count = len(results) - success_count

    # Create FastAPI app
    app = create_app()

    with TestClient(app) as client:
        current_conversation_id = None
        current_turn_number = 0

        for i in range(start_index, len(HYBRID_TEST_CASES)):
            test_case = HYBRID_TEST_CASES[i]
            test_num = i + 1

            logger.info(f"[{test_num}/{len(HYBRID_TEST_CASES)}] Evaluating: {test_case.question[:80]}...")

            # Rate limit delay (skip before first query)
            if test_num > 1:
                time.sleep(RATE_LIMIT_DELAY_SECONDS)

            # Handle conversational context
            is_followup = _is_followup_question(test_case.question)

            if is_followup:
                if current_conversation_id is None:
                    # Create new conversation for first question in sequence
                    conv_resp = client.post("/api/v1/conversations", json={})
                    if conv_resp.status_code == 200:
                        current_conversation_id = conv_resp.json()["id"]
                        current_turn_number = 1
                else:
                    current_turn_number += 1
            else:
                # Start new conversation for non-followup questions
                conv_resp = client.post("/api/v1/conversations", json={})
                if conv_resp.status_code == 200:
                    current_conversation_id = conv_resp.json()["id"]
                    current_turn_number = 1
                else:
                    current_conversation_id = None
                    current_turn_number = 0

            try:
                # Build API request
                payload = {
                    "query": test_case.question,
                    "k": 5,
                    "include_sources": True,
                    "conversation_id": current_conversation_id,
                }

                # Retry logic for rate limiting
                http_response = None
                last_error = None

                for attempt in range(MAX_RETRIES + 1):
                    http_response = client.post("/api/v1/chat", json=payload)

                    if http_response.status_code == 200:
                        break

                    # Check for rate limit
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
                    raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {last_error}")

                # Parse response — ChatResponse fields: answer, sources, generated_sql
                response_data = http_response.json()
                answer = response_data.get("answer", "")
                sources = response_data.get("sources", [])
                processing_time = response_data.get("processing_time_ms", 0)
                generated_sql = response_data.get("generated_sql")

                # Analyze routing (SQL, Vector, or Both)
                # ChatResponse exposes generated_sql (str|None), not sql_results
                has_sql = generated_sql is not None and len(generated_sql) > 0
                has_vector = len(sources) > 0

                # Determine routing
                if has_sql and has_vector:
                    routing = "both"
                elif has_sql:
                    routing = "sql"
                elif has_vector:
                    routing = "vector"
                else:
                    routing = "unknown"

                category = test_case.category if hasattr(test_case, "category") else "hybrid"

                result = {
                    "question": test_case.question,
                    "category": category,
                    "response": answer,
                    "routing": routing,
                    "generated_sql": generated_sql,
                    "sources": sources,
                    "sources_count": len(sources),
                    "processing_time_ms": processing_time,
                    "conversation_id": current_conversation_id,
                    "turn_number": current_turn_number,
                    "success": True,
                }

                results.append(result)
                success_count += 1

                logger.info(f"  ✓ Success | Routing: {routing.upper()} | Sources: {len(sources)} | Time: {processing_time}ms")

            except Exception as e:
                logger.error(f"  ✗ Failed: {str(e)[:200]}")

                result = {
                    "question": test_case.question,
                    "category": getattr(test_case, "category", "hybrid"),
                    "error": str(e),
                    "success": False,
                }

                results.append(result)
                failure_count += 1

            # Save checkpoint after EACH query
            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "completed": len(results),
                "total": len(HYBRID_TEST_CASES),
                "results": results,
            }
            checkpoint_file.write_text(json.dumps(checkpoint_data, indent=2, ensure_ascii=False), encoding="utf-8")

    # Final summary
    logger.info("")
    logger.info("="*80)
    logger.info("EVALUATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Total: {len(HYBRID_TEST_CASES)}")
    logger.info(f"Success: {success_count} ({success_count/len(HYBRID_TEST_CASES)*100:.1f}%)")
    logger.info(f"Failed: {failure_count}")
    logger.info("="*80)

    # Generate output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    # JSON output
    json_file = output_dir / f"hybrid_evaluation_{timestamp}.json"

    # Run quality analysis
    logger.info("Running quality analysis...")
    analysis = analyze_hybrid_results(results, HYBRID_TEST_CASES)

    output_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "total_test_cases": len(HYBRID_TEST_CASES),
            "successful": success_count,
            "failed": failure_count,
            "success_rate": round(success_count / len(HYBRID_TEST_CASES) * 100, 1),
        },
        "analysis": analysis,
        "results": results,
    }

    json_file.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"✓ JSON report saved: {json_file}")

    # Markdown output
    md_file = output_dir / f"hybrid_evaluation_report_{timestamp}.md"
    generate_markdown_report(results, analysis, HYBRID_TEST_CASES, md_file)
    logger.info(f"✓ Markdown report saved: {md_file}")

    # Clean up checkpoint
    if checkpoint_file.exists():
        checkpoint_file.unlink()
        logger.info("✓ Checkpoint file removed")

    logger.info("")
    logger.info("="*80)
    logger.info("REPORTS GENERATED")
    logger.info("="*80)
    logger.info(f"JSON: {json_file}")
    logger.info(f"MD:   {md_file}")
    logger.info("="*80)

    return results, str(json_file)


def main():
    """Main entry point for hybrid evaluation."""
    try:
        results, output_file = run_hybrid_evaluation(resume=True)
        return 0
    except KeyboardInterrupt:
        logger.info("\n\nEvaluation interrupted by user. Progress saved to checkpoint.")
        return 1
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
