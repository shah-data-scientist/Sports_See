"""
FILE: test_evaluation_samples.py
STATUS: Active
RESPONSIBILITY: Run sample evaluations (2 test cases each) for SQL, Vector, and Hybrid to verify metrics
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import json
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from starlette.testclient import TestClient

from src.api.dependencies import set_chat_service
from src.api.main import create_app
from src.core.config import settings
from src.core.observability import logger
from src.services.chat import ChatService
from src.evaluation.analysis.sql_quality_analysis import (
    analyze_column_selection,
    analyze_error_taxonomy,
    analyze_fallback_patterns,
    analyze_query_complexity,
    analyze_query_structure,
    analyze_response_quality,
)
from src.evaluation.analysis.vector_quality_analysis import (
    analyze_ragas_metrics,
    analyze_retrieval_performance,
    analyze_response_patterns,
    analyze_source_quality,
)
from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES

TEST_OUTPUT_DIR = Path("evaluation_results/test_run_2026_02_12")
RATE_LIMIT_DELAY = 15


def run_sql_sample_evaluation():
    """Run SQL evaluation with just 2 test cases."""
    logger.info("=" * 80)
    logger.info("SAMPLE SQL EVALUATION (2 test cases)")
    logger.info("=" * 80)

    # Take just first 2 test cases
    test_cases = SQL_TEST_CASES[:2]
    results = []

    app = create_app()
    client = TestClient(app)

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/2] Testing: {test_case.question}")
        try:
            start_time = time.time()
            response = client.post(
                "/api/v1/chat",
                json={"query": test_case.question},
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "query": test_case.question,
                        "success": True,
                        "response": data.get("answer", ""),
                        "processing_time_ms": elapsed_ms,
                        "test_category": test_case.category,
                    }
                )
                logger.info(f"✓ Success ({elapsed_ms:.0f}ms)")
            else:
                results.append(
                    {
                        "query": test_case.question,
                        "success": False,
                        "response": f"HTTP {response.status_code}",
                        "processing_time_ms": elapsed_ms,
                        "test_category": test_case.category,
                    }
                )
                logger.warning(f"✗ Failed with status {response.status_code}")

        except Exception as e:
            logger.error(f"✗ Error: {e}")
            results.append(
                {
                    "query": test_case.question,
                    "success": False,
                    "response": str(e),
                    "processing_time_ms": 0,
                    "test_category": test_case.category,
                }
            )

        time.sleep(RATE_LIMIT_DELAY)

    # Analyze results
    successful_results = [r for r in results if r["success"]]
    avg_latency = statistics.mean([r["processing_time_ms"] for r in successful_results]) if successful_results else 0

    analysis = {
        "execution_summary": {
            "total_queries": len(results),
            "successful": len(successful_results),
            "failed": len([r for r in results if not r["success"]]),
        },
        "latency": {
            "avg_ms": avg_latency,
        },
        "quality_analysis": {
            "error_taxonomy": analyze_error_taxonomy(results),
            "response_quality": analyze_response_quality(results),
            "query_structure": analyze_query_structure(results),
            "query_complexity": analyze_query_complexity(results),
            "column_selection": analyze_column_selection(results),
            "fallback_patterns": analyze_fallback_patterns(results),
        },
    }

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_file = TEST_OUTPUT_DIR / f"sql_sample_results_{timestamp}.json"
    analysis_file = TEST_OUTPUT_DIR / f"sql_sample_analysis_{timestamp}.json"

    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    analysis_file.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    # Generate markdown report
    report_file = TEST_OUTPUT_DIR / f"sql_sample_report_{timestamp}.md"
    report = _generate_sql_report(results, analysis)
    report_file.write_text(report, encoding="utf-8")

    logger.info(f"\n✓ SQL sample evaluation complete!")
    logger.info(f"  Results: {results_file}")
    logger.info(f"  Analysis: {analysis_file}")
    logger.info(f"  Report: {report_file}")

    return report_file


def run_vector_sample_evaluation():
    """Run Vector evaluation with just 2 test cases."""
    logger.info("\n" + "=" * 80)
    logger.info("SAMPLE VECTOR EVALUATION (2 test cases)")
    logger.info("=" * 80)

    # Take just first 2 test cases
    test_cases = EVALUATION_TEST_CASES[:2]
    results = []

    app = create_app()
    client = TestClient(app)

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n[{i}/2] Testing: {test_case.question}")
        try:
            start_time = time.time()
            response = client.post(
                "/api/v1/chat",
                json={"query": test_case.question},
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                results.append(
                    {
                        "query": test_case.question,
                        "success": True,
                        "response": data.get("answer", ""),
                        "sources": data.get("sources", []),
                        "processing_time_ms": elapsed_ms,
                        "category": test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category),
                    }
                )
                logger.info(f"✓ Success ({elapsed_ms:.0f}ms, {len(data.get('sources', []))} sources)")
            else:
                results.append(
                    {
                        "query": test_case.question,
                        "success": False,
                        "response": f"HTTP {response.status_code}",
                        "sources": [],
                        "processing_time_ms": elapsed_ms,
                        "category": test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category),
                    }
                )
                logger.warning(f"✗ Failed with status {response.status_code}")

        except Exception as e:
            logger.error(f"✗ Error: {e}")
            results.append(
                {
                    "query": test_case.question,
                    "success": False,
                    "response": str(e),
                    "sources": [],
                    "processing_time_ms": 0,
                    "category": test_case.category.value if hasattr(test_case.category, 'value') else str(test_case.category),
                }
            )

        time.sleep(RATE_LIMIT_DELAY)

    # Analyze results
    successful_results = [r for r in results if r["success"]]
    avg_latency = statistics.mean([r["processing_time_ms"] for r in successful_results]) if successful_results else 0

    analysis = {
        "execution_summary": {
            "total_queries": len(results),
            "successful": len(successful_results),
            "failed": len([r for r in results if not r["success"]]),
        },
        "latency": {
            "avg_ms": avg_latency,
        },
        "quality_analysis": {
            "source_quality": analyze_source_quality(results),
            "retrieval_performance": analyze_retrieval_performance(results),
            "response_patterns": analyze_response_patterns(results),
        },
    }

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results_file = TEST_OUTPUT_DIR / f"vector_sample_results_{timestamp}.json"
    analysis_file = TEST_OUTPUT_DIR / f"vector_sample_analysis_{timestamp}.json"

    results_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    analysis_file.write_text(json.dumps(analysis, indent=2), encoding="utf-8")

    # Generate markdown report
    report_file = TEST_OUTPUT_DIR / f"vector_sample_report_{timestamp}.md"
    report = _generate_vector_report(results, analysis)
    report_file.write_text(report, encoding="utf-8")

    logger.info(f"\n✓ Vector sample evaluation complete!")
    logger.info(f"  Results: {results_file}")
    logger.info(f"  Analysis: {analysis_file}")
    logger.info(f"  Report: {report_file}")

    return report_file




def _generate_sql_report(results: list, analysis: dict) -> str:
    """Generate SQL evaluation markdown report."""
    exec_summary = analysis["execution_summary"]
    quality = analysis["quality_analysis"]

    return f"""# SQL Sample Evaluation Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Cases:** 2 samples

## Execution Summary
- **Total Queries:** {exec_summary['total_queries']}
- **Successful:** {exec_summary['successful']}
- **Failed:** {exec_summary['failed']}
- **Success Rate:** {exec_summary['successful']/exec_summary['total_queries']*100:.1f}%

## Latency
- **Average:** {analysis['latency']['avg_ms']:.0f}ms

## Quality Metrics

### Error Taxonomy
{json.dumps(quality['error_taxonomy'], indent=2)}

### Response Quality
{json.dumps(quality['response_quality'], indent=2)}

### Query Structure
{json.dumps(quality['query_structure'], indent=2)}

### Query Complexity
{json.dumps(quality['query_complexity'], indent=2)}

### Column Selection
{json.dumps(quality['column_selection'], indent=2)}

### Fallback Patterns
{json.dumps(quality['fallback_patterns'], indent=2)}

## Sample Results
{json.dumps(results, indent=2)}
"""


def _generate_vector_report(results: list, analysis: dict) -> str:
    """Generate Vector evaluation markdown report."""
    exec_summary = analysis["execution_summary"]
    quality = analysis["quality_analysis"]

    return f"""# Vector Sample Evaluation Report
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Test Cases:** 2 samples

## Execution Summary
- **Total Queries:** {exec_summary['total_queries']}
- **Successful:** {exec_summary['successful']}
- **Failed:** {exec_summary['failed']}
- **Success Rate:** {exec_summary['successful']/exec_summary['total_queries']*100:.1f}%

## Latency
- **Average:** {analysis['latency']['avg_ms']:.0f}ms

## Quality Metrics

### Source Quality
{json.dumps(quality['source_quality'], indent=2)}

### Retrieval Performance
{json.dumps(quality['retrieval_performance'], indent=2)}

### Response Patterns
{json.dumps(quality['response_patterns'], indent=2)}

## Sample Results
{json.dumps(results, indent=2)}
"""


if __name__ == "__main__":
    logger.info("Starting sample evaluations...")
    logger.info(f"Output directory: {TEST_OUTPUT_DIR.absolute()}")

    # Initialize ChatService globally before running tests
    logger.info("Initializing ChatService...")
    try:
        service = ChatService()
        service.ensure_ready()
        set_chat_service(service)
        logger.info("✓ ChatService initialized successfully")
    except Exception as e:
        logger.warning(f"⚠ ChatService initialization warning (evaluation may still work): {e}")

    sql_report = run_sql_sample_evaluation()
    vector_report = run_vector_sample_evaluation()

    logger.info("\n" + "=" * 80)
    logger.info("ALL SAMPLE EVALUATIONS COMPLETE")
    logger.info("=" * 80)
    logger.info(f"\nAll files saved to: {TEST_OUTPUT_DIR.absolute()}")
    logger.info("\nGenerated files:")
    logger.info(f"  SQL Report: {sql_report.name}")
    logger.info(f"  Vector Report: {vector_report.name}")
