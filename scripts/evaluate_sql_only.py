"""
FILE: evaluate_sql_only.py
STATUS: Active
RESPONSIBILITY: SQL-only query evaluation (Phase SQL-1: 21 test cases)
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import json
import logging
from pathlib import Path

from src.evaluation.sql_evaluation import (
    QueryType,
    SQLAccuracyMetrics,
    SQLExecutionResult,
)
from src.evaluation.sql_only_test_cases import (
    AGGREGATION_SQL_CASES,
    COMPARISON_SQL_CASES,
    SIMPLE_SQL_CASES,
    SQL_ONLY_TEST_CASES,
)
from src.tools.sql_tool import NBAGSQLTool

logger = logging.getLogger(__name__)


def evaluate_sql_accuracy(test_case, sql_result) -> SQLAccuracyMetrics:
    """Evaluate SQL component accuracy.

    Args:
        test_case: Test case with expected SQL and ground truth
        sql_result: SQL execution result from SQL tool

    Returns:
        SQL accuracy metrics
    """
    # Check syntax correctness (did it execute?)
    sql_syntax_correct = not sql_result["error"]

    # Check semantic correctness (is the query logically correct?)
    # Compare generated SQL with expected SQL keywords
    sql_semantic_correct = False
    if sql_result["sql"] and test_case.expected_sql:
        expected_keywords = set(test_case.expected_sql.lower().split())
        generated_keywords = set(sql_result["sql"].lower().split())
        # At least 60% keyword overlap (handles different formatting)
        overlap = len(expected_keywords & generated_keywords) / max(len(expected_keywords), 1)
        sql_semantic_correct = overlap >= 0.6

    # Check results accuracy (do results match ground truth?)
    results_accurate = False
    if sql_result["results"] and test_case.ground_truth_data:
        # For single-row results
        if isinstance(test_case.ground_truth_data, dict):
            if len(sql_result["results"]) >= 1:
                result = sql_result["results"][0]
                # Check if key values match (allowing some tolerance for numeric values)
                matches = []
                for key, expected_val in test_case.ground_truth_data.items():
                    if key in result:
                        actual_val = result[key]
                        if isinstance(expected_val, (int, float)):
                            # 5% tolerance for numeric values
                            tolerance = abs(expected_val) * 0.05 if expected_val != 0 else 0.01
                            matches.append(abs(actual_val - expected_val) <= tolerance)
                        else:
                            matches.append(str(actual_val).lower() == str(expected_val).lower())
                results_accurate = len(matches) > 0 and all(matches)

        # For multi-row results
        elif isinstance(test_case.ground_truth_data, list):
            if len(sql_result["results"]) >= len(test_case.ground_truth_data):
                # Check if top results contain expected players
                result_names = {r.get("name", "").lower() for r in sql_result["results"][:len(test_case.ground_truth_data)]}
                expected_names = {gt.get("name", "").lower() for gt in test_case.ground_truth_data}
                results_accurate = len(result_names & expected_names) >= len(expected_names) * 0.8  # 80% match

    # Execution success
    execution_success = not sql_result["error"]

    return SQLAccuracyMetrics(
        sql_syntax_correct=sql_syntax_correct,
        sql_semantic_correct=sql_semantic_correct,
        results_accurate=results_accurate,
        execution_success=execution_success,
    )


def run_sql_only_evaluation(test_cases: list):
    """Run SQL-only evaluation.

    Args:
        test_cases: List of SQL evaluation test cases

    Returns:
        List of (test_case, sql_result, metrics) tuples
    """
    logger.info(f"Running SQL-only evaluation on {len(test_cases)} test cases")

    # Initialize SQL tool
    sql_tool = NBAGSQLTool()

    results = []

    for i, test_case in enumerate(test_cases):
        logger.info(f"[{i+1}/{len(test_cases)}] {test_case.category}: {test_case.question[:60]}...")

        try:
            # Execute SQL query
            sql_result = sql_tool.query(test_case.question)

            # Evaluate accuracy
            metrics = evaluate_sql_accuracy(test_case, sql_result)

            results.append((test_case, sql_result, metrics))

            # Log result
            status = "[PASS]" if metrics.overall_score >= 0.75 else "[FAIL]"
            logger.info(f"  {status} Score: {metrics.overall_score:.2f} | "
                       f"Syntax: {'Y' if metrics.sql_syntax_correct else 'N'} | "
                       f"Semantic: {'Y' if metrics.sql_semantic_correct else 'N'} | "
                       f"Results: {'Y' if metrics.results_accurate else 'N'}")

            if sql_result["error"]:
                logger.warning(f"  SQL Error: {sql_result['error']}")

        except Exception as e:
            logger.error(f"  Error processing query: {e}")
            continue

    return results


def print_results(results: list):
    """Print evaluation results by category.

    Args:
        results: List of (test_case, sql_result, metrics) tuples
    """
    print("\n" + "=" * 80)
    print("  SQL-ONLY QUERY EVALUATION RESULTS (PHASE SQL-1)")
    print("  21 Test Cases | Target: >85% SQL Accuracy")
    print("=" * 80 + "\n")

    # Group by category
    by_category = {}
    for test_case, sql_result, metrics in results:
        category = test_case.category.split("_")[0]  # simple, comparison, aggregation
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((test_case, sql_result, metrics))

    # Print results by category
    category_scores = {}
    for category in ["simple", "comparison", "aggregation"]:
        if category not in by_category:
            continue

        items = by_category[category]
        print(f"\n{category.upper()} SQL QUERIES ({len(items)} cases)")
        print("-" * 80)

        scores = []
        for test_case, sql_result, metrics in items:
            score = metrics.overall_score
            scores.append(score)
            status = "[PASS]" if score >= 0.75 else "[FAIL]"

            print(f"{status} {test_case.question[:55]:<55} | Score: {score:.2f}")
            print(f"       SQL: {sql_result['sql'][:70] if sql_result['sql'] else 'N/A'}...")
            print(f"       Metrics: Syntax={'Y' if metrics.sql_syntax_correct else 'N'} | "
                  f"Semantic={'Y' if metrics.sql_semantic_correct else 'N'} | "
                  f"Results={'Y' if metrics.results_accurate else 'N'} | "
                  f"Exec={'Y' if metrics.execution_success else 'N'}")

            if sql_result["error"]:
                print(f"       ERROR: {sql_result['error']}")

        avg_score = sum(scores) / len(scores) if scores else 0
        category_scores[category] = avg_score
        pass_rate = sum(1 for s in scores if s >= 0.75) / len(scores) * 100 if scores else 0

        print(f"\n  Category Average: {avg_score:.3f} | Pass Rate: {pass_rate:.1f}%")

    # Overall statistics
    all_scores = [m.overall_score for _, _, m in results]
    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
    overall_pass_rate = sum(1 for s in all_scores if s >= 0.75) / len(all_scores) * 100 if all_scores else 0

    print("\n" + "=" * 80)
    print(f"OVERALL RESULTS")
    print("-" * 80)
    print(f"Total Queries: {len(results)}")
    print(f"Average SQL Accuracy: {overall_avg:.3f}")
    print(f"Pass Rate (≥0.75): {overall_pass_rate:.1f}%")
    print(f"TARGET: >85% accuracy")

    if overall_avg >= 0.85:
        print(f"\n✓ TARGET MET - Ready for Phase SQL-2 (Hybrid queries)")
    else:
        gap = 0.85 - overall_avg
        print(f"\n✗ TARGET MISSED by {gap:.3f} - Optimize SQL tool before Phase SQL-2")

    print("=" * 80 + "\n")

    # Category breakdown summary
    print("\nCATEGORY BREAKDOWN:")
    print("-" * 80)
    for category, score in category_scores.items():
        status = "✓ PASS" if score >= 0.85 else "✗ FAIL"
        print(f"  {category.upper():<15} {score:.3f}  {status}")


def save_results(results: list, output_path: Path):
    """Save evaluation results to JSON.

    Args:
        results: List of (test_case, sql_result, metrics) tuples
        output_path: Output file path
    """
    results_data = {
        "evaluation_type": "sql_only",
        "test_count": len(results),
        "target_accuracy": 0.85,
        "samples": []
    }

    for test_case, sql_result, metrics in results:
        results_data["samples"].append({
            "question": test_case.question,
            "category": test_case.category,
            "expected_sql": test_case.expected_sql,
            "generated_sql": sql_result["sql"],
            "execution_error": sql_result["error"],
            "results_count": len(sql_result["results"]) if sql_result["results"] else 0,
            "metrics": {
                "sql_syntax_correct": metrics.sql_syntax_correct,
                "sql_semantic_correct": metrics.sql_semantic_correct,
                "results_accurate": metrics.results_accurate,
                "execution_success": metrics.execution_success,
                "overall_score": metrics.overall_score,
            }
        })

    # Calculate overall stats
    all_scores = [m.overall_score for _, _, m in results]
    results_data["overall_metrics"] = {
        "average_accuracy": sum(all_scores) / len(all_scores) if all_scores else 0,
        "pass_rate": sum(1 for s in all_scores if s >= 0.75) / len(all_scores) if all_scores else 0,
        "target_met": (sum(all_scores) / len(all_scores) if all_scores else 0) >= 0.85,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results saved to: {output_path}\n")


def main():
    """Run SQL-only evaluation (Phase SQL-1)."""
    # Configure UTF-8 encoding for Windows console
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("\n" + "=" * 80)
    print("  PHASE SQL-1: SQL-ONLY QUERY EVALUATION")
    print("  Optimize SQL tool accuracy before tackling hybrid queries")
    print("=" * 80 + "\n")

    # Choose test set
    print("Available test sets:")
    print("  1. Simple SQL (7 cases) - single-table queries")
    print("  2. Comparison SQL (7 cases) - multi-player comparisons")
    print("  3. Aggregation SQL (7 cases) - league-wide stats")
    print("  4. All SQL queries (21 cases) - comprehensive evaluation")

    choice = input("\nSelect test set (1-4, default=4): ").strip() or "4"

    test_cases = {
        "1": SIMPLE_SQL_CASES,
        "2": COMPARISON_SQL_CASES,
        "3": AGGREGATION_SQL_CASES,
        "4": SQL_ONLY_TEST_CASES,
    }.get(choice, SQL_ONLY_TEST_CASES)

    print(f"\nRunning evaluation on {len(test_cases)} SQL-only test cases...\n")

    # Run evaluation
    results = run_sql_only_evaluation(test_cases)

    # Print results
    print_results(results)

    # Save results
    output_file = Path("evaluation_results/sql_only_phase1.json")
    save_results(results, output_file)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
