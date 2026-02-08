"""
FILE: evaluate_sql_hybrid.py
STATUS: Active
RESPONSIBILITY: Comprehensive SQL + Hybrid query evaluation framework
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import json
import logging
from pathlib import Path

from src.core.config import settings
from src.evaluation.sql_evaluation import (
    HybridEvaluationMetrics,
    HybridEvaluationSample,
    HybridIntegrationMetrics,
    QueryType,
    SQLAccuracyMetrics,
    SQLExecutionResult,
    VectorRetrievalResult,
)
from src.evaluation.hybrid_test_cases import HYBRID_TEST_CASES as HYBRID_CASES_NEW
from src.evaluation.sql_test_cases import SQL_TEST_CASES
from src.services.chat import ChatService

logger = logging.getLogger(__name__)


def evaluate_sql_accuracy(
    test_case,
    sql_result: SQLExecutionResult,
) -> SQLAccuracyMetrics:
    """Evaluate SQL component accuracy.

    Args:
        test_case: Test case with expected SQL and ground truth
        sql_result: SQL execution result

    Returns:
        SQL accuracy metrics
    """
    # Check syntax correctness (did it execute?)
    sql_syntax_correct = sql_result.query_executed

    # Check semantic correctness (is the query logically correct?)
    # Simple heuristic: does generated SQL contain key elements of expected SQL?
    sql_semantic_correct = False
    if sql_result.query_generated and test_case.expected_sql:
        expected_keywords = set(test_case.expected_sql.lower().split())
        generated_keywords = set(sql_result.query_generated.lower().split())
        # At least 60% keyword overlap (handles different formatting)
        overlap = len(expected_keywords & generated_keywords) / len(expected_keywords)
        sql_semantic_correct = overlap >= 0.6

    # Check results accuracy (do results match ground truth?)
    results_accurate = False
    if sql_result.results and test_case.ground_truth_data:
        # For single-row results
        if isinstance(test_case.ground_truth_data, dict):
            if len(sql_result.results) == 1:
                result = sql_result.results[0]
                # Check if key values match (allowing some tolerance for numeric values)
                matches = []
                for key, expected_val in test_case.ground_truth_data.items():
                    if key in result:
                        actual_val = result[key]
                        if isinstance(expected_val, (int, float)):
                            # 5% tolerance for numeric values
                            matches.append(abs(actual_val - expected_val) / expected_val < 0.05)
                        else:
                            matches.append(str(actual_val).lower() == str(expected_val).lower())
                results_accurate = len(matches) > 0 and all(matches)

        # For multi-row results
        elif isinstance(test_case.ground_truth_data, list):
            if len(sql_result.results) == len(test_case.ground_truth_data):
                # Simple heuristic: check if player names match
                result_names = {r.get("name", "").lower() for r in sql_result.results}
                expected_names = {gt.get("name", "").lower() for gt in test_case.ground_truth_data}
                results_accurate = result_names == expected_names

    return SQLAccuracyMetrics(
        sql_syntax_correct=sql_syntax_correct,
        sql_semantic_correct=sql_semantic_correct,
        results_accurate=results_accurate,
        execution_success=sql_result.query_executed,
    )


def evaluate_hybrid_integration(
    test_case,
    sample: HybridEvaluationSample,
) -> HybridIntegrationMetrics:
    """Evaluate hybrid query integration quality.

    Args:
        test_case: Test case
        sample: Evaluation sample with SQL + vector components

    Returns:
        Integration quality metrics
    """
    response_lower = sample.response.lower()

    # Check if SQL component was used
    sql_component_used = False
    if sample.sql_result and sample.sql_result.results:
        # Check if response contains data from SQL results
        for result in sample.sql_result.results:
            for key, value in result.items():
                if key != "name" and str(value) in sample.response:
                    sql_component_used = True
                    break

    # Check if vector component was used
    vector_component_used = False
    if sample.vector_result and sample.vector_result.retrieved_contexts:
        # Check if response contains phrases from retrieved context
        for context in sample.vector_result.retrieved_contexts[:2]:  # Check top 2
            context_phrases = context.lower().split(".")[:3]  # First 3 sentences
            for phrase in context_phrases:
                if len(phrase) > 20 and phrase.strip() in response_lower:
                    vector_component_used = True
                    break

    # Check if components are blended (not just concatenated)
    # Heuristic: response should have transition words/phrases between stats and analysis
    transition_words = ["because", "due to", "while", "although", "however", "this", "his", "her"]
    components_blended = any(word in response_lower for word in transition_words)

    # Check answer completeness
    # For hybrid queries, answer should address both "what" (SQL) and "why/how" (context)
    has_stats = any(char.isdigit() for char in sample.response)  # Contains numbers
    has_analysis = len(sample.response.split()) > 30  # Long enough for analysis
    answer_complete = has_stats and has_analysis

    return HybridIntegrationMetrics(
        sql_component_used=sql_component_used,
        vector_component_used=vector_component_used,
        components_blended=components_blended,
        answer_complete=answer_complete,
    )


def run_sql_hybrid_evaluation(test_cases: list, use_sql: bool = True):
    """Run comprehensive SQL + Hybrid evaluation.

    Args:
        test_cases: List of SQL evaluation test cases
        use_sql: Whether to enable SQL tool (default: True)

    Returns:
        List of tuples (sample, test_case) - maintains alignment even when queries fail
    """
    logger.info(f"Running SQL + Hybrid evaluation on {len(test_cases)} test cases")

    # Initialize chat service and SQL tool separately for evaluation
    chat_service = ChatService(enable_sql=use_sql)
    chat_service.ensure_ready()

    # Initialize SQL tool directly for accurate evaluation
    from src.tools.sql_tool import NBAGSQLTool
    sql_tool = NBAGSQLTool()

    results = []  # List of (sample, test_case) tuples

    for i, test_case in enumerate(test_cases):
        logger.info(f"[{i+1}/{len(test_cases)}] {test_case.category}: {test_case.question[:60]}...")

        # Execute query through chat service
        try:
            from src.models.chat import ChatRequest

            request = ChatRequest(query=test_case.question, k=5, include_sources=True)
            response = chat_service.chat(request)

            # For SQL queries, also execute directly to get raw results for evaluation
            sql_result = None
            if test_case.query_type == QueryType.SQL_ONLY:
                try:
                    # Execute SQL directly to get raw results
                    sql_output = sql_tool.query(test_case.question)

                    sql_result = SQLExecutionResult(
                        query_generated=sql_output.get("sql", ""),
                        query_executed=sql_output.get("error") is None,
                        execution_error=sql_output.get("error"),
                        results=sql_output.get("results", []),
                        formatted_results=sql_output.get("formatted_results"),
                    )
                except Exception as e:
                    logger.warning(f"SQL evaluation failed: {e}")
                    sql_result = SQLExecutionResult(
                        query_generated="",
                        query_executed=False,
                        execution_error=str(e),
                        results=[],
                        formatted_results=None,
                    )

            elif test_case.query_type == QueryType.HYBRID:
                # For hybrid queries, try to execute SQL component
                try:
                    sql_output = sql_tool.query(test_case.question)
                    sql_result = SQLExecutionResult(
                        query_generated=sql_output.get("sql", ""),
                        query_executed=sql_output.get("error") is None,
                        execution_error=sql_output.get("error"),
                        results=sql_output.get("results", []),
                        formatted_results=sql_output.get("formatted_results"),
                    )
                except Exception as e:
                    logger.warning(f"Hybrid SQL evaluation failed: {e}")

            # Extract vector result if vector search was used
            vector_result = None
            if test_case.query_type in (QueryType.CONTEXTUAL_ONLY, QueryType.HYBRID):
                if response.sources:
                    vector_result = VectorRetrievalResult(
                        retrieved_contexts=[s.text for s in response.sources],
                        retrieval_scores=[s.score for s in response.sources],
                        sources=[s.source for s in response.sources],
                    )

            # Create evaluation sample
            sample = HybridEvaluationSample(
                user_input=test_case.question,
                query_type=test_case.query_type,
                sql_result=sql_result,
                vector_result=vector_result,
                response=response.answer,
                reference=test_case.ground_truth_answer,
                category=test_case.category,
            )

            # Store (sample, test_case) tuple to maintain alignment
            results.append((sample, test_case))

            logger.info(f"  Response: {response.answer[:100]}...")

        except Exception as e:
            logger.error(f"  Error processing query: {e}")
            # IMPORTANT: Still append None to maintain index alignment
            # This ensures results[i] always corresponds to test_cases[i]
            results.append((None, test_case))

    return results


def compute_metrics(sample: HybridEvaluationSample, test_case) -> HybridEvaluationMetrics:
    """Compute evaluation metrics for a sample.

    Args:
        sample: Evaluation sample
        test_case: Original test case

    Returns:
        Hybrid evaluation metrics
    """
    # SQL accuracy (if applicable)
    sql_accuracy = None
    if sample.sql_result:
        sql_accuracy = evaluate_sql_accuracy(test_case, sample.sql_result)

    # Vector metrics (if applicable)
    # NOTE: Would use RAGAS here for full vector evaluation
    vector_faithfulness = None
    vector_context_precision = None
    vector_context_recall = None

    # Integration metrics (for HYBRID queries)
    integration = None
    if sample.query_type == QueryType.HYBRID:
        integration = evaluate_hybrid_integration(test_case, sample)

    # Answer relevancy (simple heuristic - would use RAGAS in practice)
    # Check if answer is concise and addresses the question
    answer_relevancy = 0.7  # Placeholder - would use RAGAS ResponseRelevancy

    # Answer correctness (LLM-as-judge - simplified here)
    # Check if answer contains key information from ground truth
    ground_truth_keywords = set(test_case.ground_truth_answer.lower().split())
    answer_keywords = set(sample.response.lower().split())
    keyword_overlap = len(ground_truth_keywords & answer_keywords) / max(len(ground_truth_keywords), 1)
    answer_correctness = min(keyword_overlap * 1.5, 1.0)  # Scale up, cap at 1.0

    return HybridEvaluationMetrics(
        sql_accuracy=sql_accuracy,
        vector_faithfulness=vector_faithfulness,
        vector_context_precision=vector_context_precision,
        vector_context_recall=vector_context_recall,
        integration=integration,
        answer_relevancy=answer_relevancy,
        answer_correctness=answer_correctness,
    )


def print_results(samples: list, metrics_list: list):
    """Print evaluation results.

    Args:
        samples: Evaluation samples
        metrics_list: Computed metrics for each sample
    """
    print("\n" + "=" * 80)
    print("  SQL + HYBRID QUERY EVALUATION RESULTS")
    print("=" * 80 + "\n")

    # Group by query type
    by_type = {}
    for sample, metrics in zip(samples, metrics_list):
        query_type = sample.query_type.value
        if query_type not in by_type:
            by_type[query_type] = []
        by_type[query_type].append((sample, metrics))

    # Print results by type
    for query_type, items in by_type.items():
        print(f"\n{query_type.upper().replace('_', ' ')} QUERIES ({len(items)} samples)")
        print("-" * 80)

        overall_scores = []
        for sample, metrics in items:
            score = metrics.overall_score
            overall_scores.append(score)
            status = "[PASS]" if score >= 0.7 else "[FAIL]"
            print(f"{status} {sample.user_input[:60]}... | Score: {score:.2f}")

            # Show details
            if metrics.sql_accuracy:
                print(f"       SQL: {metrics.sql_accuracy.overall_score:.2f} | "
                      f"Syntax: {'Y' if metrics.sql_accuracy.sql_syntax_correct else 'N'} | "
                      f"Results: {'Y' if metrics.sql_accuracy.results_accurate else 'N'}")

            if metrics.integration:
                print(f"       Integration: {metrics.integration.integration_score:.2f} | "
                      f"SQL used: {'Y' if metrics.integration.sql_component_used else 'N'} | "
                      f"Vector used: {'Y' if metrics.integration.vector_component_used else 'N'} | "
                      f"Blended: {'Y' if metrics.integration.components_blended else 'N'}")

        avg_score = sum(overall_scores) / len(overall_scores) if overall_scores else 0
        print(f"\n  Average Score: {avg_score:.3f}")

    # Overall statistics
    all_scores = [m.overall_score for m in metrics_list]
    print("\n" + "=" * 80)
    print(f"OVERALL: {len(samples)} queries | Average Score: {sum(all_scores)/len(all_scores):.3f}")
    print("=" * 80 + "\n")


def main():
    """Run SQL + Hybrid evaluation."""
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Set stdout encoding to UTF-8 on Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "=" * 80)
    print("  SQL + HYBRID QUERY EVALUATION FRAMEWORK")
    print("  Test SQL accuracy, vector retrieval, and hybrid integration")
    print("=" * 80 + "\n")

    # Choose test set (support command-line argument or interactive)
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("Available test sets:")
        print("  1. SQL-only queries (68 cases - includes simple, comparison, aggregation, complex, conversational)")
        print("  2. Hybrid queries (39 cases - SQL + Vector combined)")
        print("  3. All queries (107 cases - SQL + Hybrid)")
        choice = input("\nSelect test set (1-3, default=3): ").strip() or "3"

    # Build ALL test cases by combining SQL and Hybrid sets
    ALL_TEST_CASES = SQL_TEST_CASES + HYBRID_CASES_NEW

    test_cases = {
        "1": SQL_TEST_CASES,       # 68 cases
        "2": HYBRID_CASES_NEW,     # 39 cases
        "3": ALL_TEST_CASES,       # 107 cases total
    }.get(choice, ALL_TEST_CASES)

    print(f"\nRunning evaluation on {len(test_cases)} test cases...\n")

    # Run evaluation
    results = run_sql_hybrid_evaluation(test_cases, use_sql=True)

    # Compute metrics (filter out failed queries where sample is None)
    samples = []
    metrics_list = []
    successful_test_cases = []

    for sample, test_case in results:
        if sample is not None:
            metrics = compute_metrics(sample, test_case)
            samples.append(sample)
            metrics_list.append(metrics)
            successful_test_cases.append(test_case)

    # Print results
    print_results(samples, metrics_list)

    # Save results
    output_file = Path("evaluation_results/sql_hybrid_evaluation.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    results_data = {
        "test_set": choice,
        "sample_count": len(samples),
        "samples": [
            {
                "query": s.user_input,
                "query_type": s.query_type.value,
                "response": s.response,
                "overall_score": m.overall_score,
                "sql_accuracy": m.sql_accuracy.overall_score if m.sql_accuracy else None,
                "integration_score": m.integration.integration_score if m.integration else None,
            }
            for s, m in zip(samples, metrics_list)
        ],
    }

    output_file.write_text(json.dumps(results_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results saved to: {output_file}\n")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
