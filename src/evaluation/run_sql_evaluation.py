"""
FILE: run_sql_evaluation.py
STATUS: Active
RESPONSIBILITY: Main entry point for SQL evaluation - runs tests, analyzes results, generates comprehensive report
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import json
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from starlette.testclient import TestClient

from src.api.main import create_app
from src.core.config import settings
from src.core.observability import logger
from src.evaluation.sql_quality_analysis import (
    analyze_column_selection,
    analyze_error_taxonomy,
    analyze_fallback_patterns,
    analyze_query_complexity,
    analyze_query_structure,
    analyze_response_quality,
)
from src.evaluation.sql_test_cases import SQL_TEST_CASES

# Rate limiting configuration for Gemini free tier
RATE_LIMIT_DELAY_SECONDS = 15  # Increased from 9 to 15 seconds
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
    return False


def run_sql_evaluation() -> tuple[list[dict[str, Any]], str]:
    """Run SQL evaluation on all test cases using FastAPI API.

    Returns:
        Tuple of (results list, output JSON path)
    """
    logger.info(f"Starting SQL evaluation with {len(SQL_TEST_CASES)} test cases")

    results = []
    success_count = 0
    failure_count = 0

    # Create FastAPI app and run evaluation through API
    app = create_app()
    with TestClient(app) as client:
        current_conversation_id = None
        current_turn_number = 0

        for i, test_case in enumerate(SQL_TEST_CASES, 1):
            logger.info(f"[{i}/{len(SQL_TEST_CASES)}] Evaluating: {test_case.question}")

            # Rate limit delay (skip before first query)
            if i > 1:
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

                # Parse response
                response_data = http_response.json()

                # Determine routing
                sources = response_data.get("sources", [])
                actual_routing = "sql_only" if len(sources) == 0 else "fallback_to_vector"
                expected_routing = test_case.query_type.value

                is_misclassified = (
                    (expected_routing == "sql_only" and actual_routing != "sql_only") or
                    (expected_routing in ["contextual_only", "hybrid"] and actual_routing == "sql_only")
                )

                category = test_case.category if hasattr(test_case, "category") else "unknown"

                results.append({
                    "question": test_case.question,
                    "category": category,
                    "response": response_data.get("answer", ""),
                    "expected_routing": expected_routing,
                    "actual_routing": actual_routing,
                    "is_misclassified": is_misclassified,
                    "sources_count": len(sources),
                    "processing_time_ms": response_data.get("processing_time_ms", 0.0),
                    "generated_sql": response_data.get("generated_sql"),
                    "conversation_id": current_conversation_id,
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
                    "conversation_id": current_conversation_id,
                    "success": False,
                    "error": str(e)
                })
                failure_count += 1

    logger.info(f"\nEvaluation complete: {success_count} success, {failure_count} failures")

    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"sql_evaluation_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"Results saved to: {json_path}")

    return results, str(json_path)


def generate_comprehensive_report(results: list[dict[str, Any]], json_path: str) -> str:
    """Generate comprehensive evaluation report with all metrics.

    Args:
        results: Evaluation results
        json_path: Path to JSON results file

    Returns:
        Path to generated markdown report
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    report_path = output_dir / f"sql_evaluation_report_{timestamp}.md"

    # Run all analyses
    error_taxonomy = analyze_error_taxonomy(results)
    fallback_patterns = analyze_fallback_patterns(results)
    response_quality = analyze_response_quality(results)
    query_structure = analyze_query_structure(results)
    query_complexity = analyze_query_complexity(results)
    column_selection = analyze_column_selection(results)

    # Calculate summary statistics
    total_queries = len(results)
    successful_queries = sum(1 for r in results if r.get("success", False))
    failed_queries = total_queries - successful_queries
    success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0

    misclassifications = sum(1 for r in results if r.get("is_misclassified", False))
    classification_accuracy = ((total_queries - misclassifications) / total_queries * 100) if total_queries > 0 else 0

    # Processing times
    processing_times = [r["processing_time_ms"] for r in results if r.get("success", False)]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    min_processing_time = min(processing_times) if processing_times else 0
    max_processing_time = max(processing_times) if processing_times else 0

    # Generate report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# SQL Evaluation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Dataset:** {total_queries} SQL test cases\n\n")
        f.write(f"**Results JSON:** `{json_path}`\n\n")
        f.write("---\n\n")

        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Queries:** {total_queries}\n")
        f.write(f"- **Successful Executions:** {successful_queries} ({success_rate:.1f}%)\n")
        f.write(f"- **Failed Executions:** {failed_queries}\n")
        f.write(f"- **Classification Accuracy:** {classification_accuracy:.1f}%\n")
        f.write(f"- **Misclassifications:** {misclassifications}\n")
        f.write(f"- **Avg Processing Time:** {avg_processing_time:.0f}ms\n\n")

        # Failure Analysis
        f.write("## Failure Analysis\n\n")

        # Execution failures
        execution_failures = [r for r in results if not r.get("success", True)]
        if execution_failures:
            f.write(f"### Execution Failures ({len(execution_failures)})\n\n")
            f.write("| Question | Category | Error |\n")
            f.write("|----------|----------|-------|\n")
            for failure in execution_failures:
                question = failure["question"][:60] + "..." if len(failure["question"]) > 60 else failure["question"]
                category = failure.get("category", "unknown")
                error = failure.get("error", "Unknown error")[:50]
                f.write(f"| {question} | {category} | {error} |\n")
            f.write("\n")
        else:
            f.write("### Execution Failures\n\n")
            f.write("✓ No execution failures detected.\n\n")

        # Misclassifications
        misclassified = [r for r in results if r.get("is_misclassified", False) and r.get("success", True)]
        if misclassified:
            f.write(f"### Routing Misclassifications ({len(misclassified)})\n\n")
            f.write("| Question | Category | Expected | Actual |\n")
            f.write("|----------|----------|----------|--------|\n")
            for mc in misclassified:
                question = mc["question"][:60] + "..." if len(mc["question"]) > 60 else mc["question"]
                category = mc.get("category", "unknown")
                expected = mc["expected_routing"]
                actual = mc["actual_routing"]
                f.write(f"| {question} | {category} | {expected} | {actual} |\n")
            f.write("\n")
        else:
            f.write("### Routing Misclassifications\n\n")
            f.write("✓ No routing misclassifications detected.\n\n")

        # Performance Metrics
        f.write("### Performance Metrics\n\n")
        f.write(f"- **Average Processing Time:** {avg_processing_time:.0f}ms\n")
        f.write(f"- **Min Processing Time:** {min_processing_time:.0f}ms\n")
        f.write(f"- **Max Processing Time:** {max_processing_time:.0f}ms\n\n")

        # Response Quality Analysis
        f.write("## Response Quality Analysis\n\n")

        f.write("### Error Taxonomy\n\n")
        f.write(f"- **Total Errors:** {error_taxonomy['total_errors']}\n")
        f.write(f"- **LLM Declined:** {len(error_taxonomy['llm_declined'])}\n")
        f.write(f"- **Syntax Errors:** {len(error_taxonomy['syntax_error'])}\n")
        f.write(f"- **Empty Responses:** {len(error_taxonomy['empty_response'])}\n\n")

        if error_taxonomy['llm_declined']:
            f.write("#### LLM Declined Examples\n\n")
            for case in error_taxonomy['llm_declined'][:3]:
                f.write(f"**Q:** {case['question']}\n\n")
                f.write(f"**Response:** {case['response'][:150]}...\n\n")

        f.write("### Fallback Patterns\n\n")
        f.write(f"- **SQL Only:** {fallback_patterns['sql_only']} ({100 - fallback_patterns['fallback_rate']:.1f}%)\n")
        f.write(f"- **Fallback to Vector:** {fallback_patterns['fallback_to_vector']} ({fallback_patterns['fallback_rate']:.1f}%)\n\n")

        f.write("#### Fallback by Category\n\n")
        f.write("| Category | Total | Fallbacks | Rate |\n")
        f.write("|----------|-------|-----------|------|\n")
        for category, stats in fallback_patterns['by_category'].items():
            f.write(f"| {category} | {stats['total']} | {stats['fallbacks']} | {stats['rate']:.1f}% |\n")
        f.write("\n")

        f.write("### Response Quality Metrics\n\n")
        f.write(f"- **Avg Response Length:** {response_quality['verbosity']['avg_length']:.0f} chars\n")
        f.write(f"- **Min/Max Length:** {response_quality['verbosity']['min_length']} / {response_quality['verbosity']['max_length']} chars\n")
        f.write(f"- **Responses with Hedging:** {response_quality['confidence_indicators']['total_with_hedging']}\n")
        f.write(f"- **Complete Responses:** {response_quality['completeness']['complete']}\n")
        f.write(f"- **Incomplete Responses:** {response_quality['completeness']['incomplete']}\n\n")

        # Query Quality Analysis
        f.write("## Query Quality Analysis\n\n")

        f.write("### Query Structure\n\n")
        if query_structure['total_queries'] > 0:
            f.write(f"- **Total SQL Queries Generated:** {query_structure['total_queries']}\n")
            f.write(f"- **Queries with JOIN:** {query_structure['queries_with_join']} ({query_structure['queries_with_join']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with Aggregation:** {query_structure['queries_with_aggregation']} ({query_structure['queries_with_aggregation']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with Filter (WHERE):** {query_structure['queries_with_filter']} ({query_structure['queries_with_filter']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with ORDER BY:** {query_structure['queries_with_ordering']} ({query_structure['queries_with_ordering']/query_structure['total_queries']*100:.1f}%)\n")
            f.write(f"- **Queries with LIMIT:** {query_structure['queries_with_limit']} ({query_structure['queries_with_limit']/query_structure['total_queries']*100:.1f}%)\n\n")

            f.write("#### JOIN Correctness\n\n")
            f.write(f"- **Correct JOINs:** {query_structure['correctness']['correct_joins']}\n")
            f.write(f"- **Missing JOINs:** {query_structure['correctness']['missing_joins']}\n\n")
        else:
            f.write("No SQL queries were captured for analysis.\n\n")

        f.write("### Query Complexity\n\n")
        if query_complexity['total_queries'] > 0:
            f.write(f"- **Avg JOINs per Query:** {query_complexity['avg_joins_per_query']:.2f}\n")
            f.write(f"- **Avg WHERE Conditions:** {query_complexity['avg_where_conditions']:.2f}\n")
            f.write(f"- **Queries with Subqueries:** {query_complexity['queries_with_subqueries']}\n")
            f.write(f"- **Queries with GROUP BY:** {query_complexity['queries_with_group_by']}\n")
            f.write(f"- **Queries with HAVING:** {query_complexity['queries_with_having']}\n\n")

            f.write("#### Complexity Distribution\n\n")
            f.write("| Level | Count | Percentage |\n")
            f.write("|-------|-------|------------|\n")
            for level, count in query_complexity['complexity_distribution'].items():
                pct = (count / query_complexity['total_queries'] * 100) if query_complexity['total_queries'] > 0 else 0
                f.write(f"| {level.replace('_', ' ').title()} | {count} | {pct:.1f}% |\n")
            f.write("\n")
        else:
            f.write("No SQL queries were captured for complexity analysis.\n\n")

        f.write("### Column Selection\n\n")
        if column_selection['total_queries'] > 0:
            f.write(f"- **Avg Columns Selected:** {column_selection['avg_columns_selected']:.2f}\n")
            f.write(f"- **SELECT * Usage:** {column_selection['select_star_count']} queries\n")
            f.write(f"- **Over-selection Rate:** {column_selection['over_selection_rate']:.1f}%\n")
            f.write(f"- **Under-selection Rate:** {column_selection['under_selection_rate']:.1f}%\n\n")
        else:
            f.write("No SQL queries were captured for column selection analysis.\n\n")

        # Key Findings
        f.write("## Key Findings\n\n")
        findings = []

        if success_rate >= 95:
            findings.append(f"✓ **Excellent execution reliability** ({success_rate:.1f}% success rate)")
        elif success_rate >= 80:
            findings.append(f"⚠ **Good execution reliability** ({success_rate:.1f}% success rate) with room for improvement")
        else:
            findings.append(f"❌ **Poor execution reliability** ({success_rate:.1f}% success rate) - needs attention")

        if classification_accuracy >= 95:
            findings.append(f"✓ **High classification accuracy** ({classification_accuracy:.1f}%)")
        elif classification_accuracy >= 80:
            findings.append(f"⚠ **Moderate classification accuracy** ({classification_accuracy:.1f}%) - could be improved")
        else:
            findings.append(f"❌ **Low classification accuracy** ({classification_accuracy:.1f}%) - needs improvement")

        if fallback_patterns['fallback_rate'] < 10:
            findings.append(f"✓ **Low fallback rate** ({fallback_patterns['fallback_rate']:.1f}%) indicates good SQL routing")
        elif fallback_patterns['fallback_rate'] < 25:
            findings.append(f"⚠ **Moderate fallback rate** ({fallback_patterns['fallback_rate']:.1f}%)")
        else:
            findings.append(f"❌ **High fallback rate** ({fallback_patterns['fallback_rate']:.1f}%) suggests classifier needs tuning")

        if error_taxonomy['total_errors'] == 0:
            findings.append("✓ **No LLM errors detected** - excellent response quality")
        elif error_taxonomy['total_errors'] < 5:
            findings.append(f"⚠ **Few LLM errors** ({error_taxonomy['total_errors']}) detected")
        else:
            findings.append(f"❌ **Multiple LLM errors** ({error_taxonomy['total_errors']}) detected - review prompts")

        if query_structure['total_queries'] > 0:
            if query_structure['correctness']['missing_joins'] == 0:
                findings.append("✓ **All player queries use correct JOINs**")
            else:
                findings.append(f"❌ **{query_structure['correctness']['missing_joins']} queries missing required JOINs**")

        for finding in findings:
            f.write(f"{finding}\n\n")

        # Detailed Test Results
        f.write("## Detailed Test Results\n\n")

        # Group by category
        by_category = defaultdict(list)
        for result in results:
            category = result.get("category", "unknown")
            by_category[category].append(result)

        for category in sorted(by_category.keys()):
            category_results = by_category[category]
            f.write(f"### {category.replace('_', ' ').title()} ({len(category_results)} tests)\n\n")

            for result in category_results:
                status = "✓" if result.get("success", False) and not result.get("is_misclassified", False) else "✗"
                f.write(f"**{status} {result['question']}**\n\n")
                f.write(f"- **Expected Routing:** {result['expected_routing']}\n")
                f.write(f"- **Actual Routing:** {result['actual_routing']}\n")
                f.write(f"- **Processing Time:** {result['processing_time_ms']:.0f}ms\n")

                if result.get("generated_sql"):
                    f.write(f"- **Generated SQL:** `{result['generated_sql'][:100]}...`\n")

                if not result.get("success", True):
                    f.write(f"- **Error:** {result.get('error', 'Unknown')}\n")

                f.write(f"- **Response:** {result['response'][:200]}{'...' if len(result['response']) > 200 else ''}\n\n")

        # Report sections
        f.write("---\n\n")
        f.write("## Report Sections\n\n")
        f.write("1. Executive Summary - Overall metrics and success rates\n")
        f.write("2. Failure Analysis - Execution failures, misclassifications, performance\n")
        f.write("3. Response Quality Analysis - Error patterns, fallback behavior, response metrics\n")
        f.write("4. Query Quality Analysis - SQL structure, complexity, column selection\n")
        f.write("5. Key Findings - Actionable insights and recommendations\n")
        f.write("6. Detailed Test Results - Complete test-by-test breakdown\n\n")

    logger.info(f"Report saved to: {report_path}")
    return str(report_path)


def main():
    """Main entry point for SQL evaluation."""
    try:
        # Run evaluation
        results, json_path = run_sql_evaluation()

        # Generate comprehensive report
        report_path = generate_comprehensive_report(results, json_path)

        print("\n" + "="*80)
        print("SQL EVALUATION COMPLETE")
        print("="*80)
        print(f"\nResults saved to:")
        print(f"  - JSON: {json_path}")
        print(f"  - Report: {report_path}")
        print("\n" + "="*80)

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
