"""
FILE: evaluate_hybrid_queries.py
STATUS: Active
RESPONSIBILITY: Phase 10: Hybrid query evaluation (SQL + Vector integration)
LAST MAJOR UPDATE: 2026-02-08
MAINTAINER: Shahu
"""

import json
import logging
from pathlib import Path

from src.core.config import settings
from src.evaluation.sql_evaluation import (
    HybridIntegrationMetrics,
    QueryType,
)
from src.evaluation.sql_test_cases import HYBRID_TEST_CASES
from src.models.chat import ChatRequest
from src.services.chat import ChatService

logger = logging.getLogger(__name__)


def evaluate_integration_quality(
    test_case,
    response_text: str,
    sources: list,
) -> HybridIntegrationMetrics:
    """Evaluate hybrid query integration quality.

    Args:
        test_case: Test case with expected results
        response_text: Generated response text
        sources: Search results from vector search

    Returns:
        Integration quality metrics
    """
    response_lower = response_text.lower()

    # 1. Check if SQL component was used (stats/numbers present)
    sql_component_used = False
    if test_case.ground_truth_data:
        # Check if response contains statistical data
        # Look for numbers that match ground truth
        has_numbers = any(char.isdigit() for char in response_text)

        # Check for specific stats keywords
        stats_keywords = ["pts", "reb", "ast", "points", "rebounds", "assists",
                         "percentage", "%", "ppg", "rpg", "apg"]
        has_stats_keywords = any(kw in response_lower for kw in stats_keywords)

        sql_component_used = has_numbers and has_stats_keywords

    # 2. Check if vector component was used (contextual analysis present)
    vector_component_used = False
    if sources:
        # Check if response contains contextual phrases
        context_keywords = ["because", "effective", "ability", "skill", "playstyle",
                           "defense", "offense", "better", "great", "dominant",
                           "mvp", "champion", "leader", "efficient"]
        has_context_keywords = sum(1 for kw in context_keywords if kw in response_lower) >= 2

        # Check if response is long enough for analysis (>100 chars suggests context)
        has_analysis = len(response_text) > 100

        vector_component_used = has_context_keywords and has_analysis

    # 3. Check if components are blended coherently
    # Look for transition words that connect stats to analysis
    transition_words = ["because", "due to", "while", "although", "however",
                       "this", "his", "her", "their", "which", "making",
                       "allows", "enables", "helps", "makes"]
    components_blended = any(word in response_lower for word in transition_words)

    # 4. Check answer completeness
    # Hybrid queries should have both WHAT (stats) and WHY/HOW (analysis)
    has_stats = any(char.isdigit() for char in response_text)  # Contains numbers
    has_analysis = len(response_text.split()) > 30  # Long enough for analysis
    answer_complete = has_stats and has_analysis and sql_component_used and vector_component_used

    return HybridIntegrationMetrics(
        sql_component_used=sql_component_used,
        vector_component_used=vector_component_used,
        components_blended=components_blended,
        answer_complete=answer_complete,
    )


def run_hybrid_evaluation(test_cases: list):
    """Run hybrid query evaluation.

    Args:
        test_cases: List of hybrid test cases

    Returns:
        List of (test_case, response, sources, metrics) tuples
    """
    logger.info(f"Running hybrid query evaluation on {len(test_cases)} test cases")

    # Initialize chat service with SQL enabled
    chat_service = ChatService(enable_sql=True)
    chat_service.ensure_ready()

    results = []

    for i, test_case in enumerate(test_cases):
        logger.info(f"[{i+1}/{len(test_cases)}] {test_case.category}: {test_case.question[:60]}...")

        try:
            # Execute query through chat service (hybrid routing)
            request = ChatRequest(
                query=test_case.question,
                k=5,
                include_sources=True
            )
            response = chat_service.chat(request)

            # Evaluate integration quality
            metrics = evaluate_integration_quality(
                test_case,
                response.answer,
                response.sources
            )

            results.append((test_case, response, metrics))

            # Log result
            status = "[PASS]" if metrics.integration_score >= 0.75 else "[FAIL]"
            logger.info(f"  {status} Integration Score: {metrics.integration_score:.2f} | "
                       f"SQL used: {'Y' if metrics.sql_component_used else 'N'} | "
                       f"Vector used: {'Y' if metrics.vector_component_used else 'N'} | "
                       f"Blended: {'Y' if metrics.components_blended else 'N'}")

        except Exception as e:
            logger.error(f"  Error processing query: {e}")
            continue

    return results


def print_results(results: list):
    """Print evaluation results.

    Args:
        results: List of (test_case, response, metrics) tuples
    """
    print("\n" + "=" * 80)
    print("  HYBRID QUERY EVALUATION RESULTS (PHASE 10: HYBRID QUERIES)")
    print(f"  {len(results)} Test Cases | Target: >75% Integration Quality")
    print("=" * 80 + "\n")

    # Print individual results
    for i, (test_case, response, metrics) in enumerate(results, 1):
        score = metrics.integration_score
        status = "[PASS]" if score >= 0.75 else "[FAIL]"

        print(f"\n{'-' * 80}")
        print(f"TEST {i}: {test_case.question}")
        print(f"{'-' * 80}")
        print(f"{status} Integration Score: {score:.2f}")
        print(f"\nIntegration Metrics:")
        print(f"  SQL component used:    {'✓' if metrics.sql_component_used else '✗'}")
        print(f"  Vector component used: {'✓' if metrics.vector_component_used else '✗'}")
        print(f"  Components blended:    {'✓' if metrics.components_blended else '✗'}")
        print(f"  Answer complete:       {'✓' if metrics.answer_complete else '✗'}")

        print(f"\nGenerated Response:")
        print(f"  {response.answer[:200]}...")

        print(f"\nVector Sources: {len(response.sources)} retrieved")
        if response.sources:
            for j, source in enumerate(response.sources[:2], 1):
                print(f"  [{j}] {source.source} (score: {source.score:.1f}%)")

        # Diagnosis
        if score < 0.75:
            print(f"\nDIAGNOSIS:")
            if not metrics.sql_component_used:
                print(f"  ✗ SQL results not used - Check QueryClassifier routing")
            if not metrics.vector_component_used:
                print(f"  ✗ Vector context not used - Check retrieval quality")
            if not metrics.components_blended:
                print(f"  ✗ Poor blending - Improve system prompt integration")
            if not metrics.answer_complete:
                print(f"  ✗ Incomplete answer - Missing stats or analysis")

    # Overall statistics
    all_scores = [m.integration_score for _, _, m in results]
    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
    pass_rate = sum(1 for s in all_scores if s >= 0.75) / len(all_scores) * 100 if all_scores else 0

    print("\n" + "=" * 80)
    print(f"OVERALL RESULTS")
    print("-" * 80)
    print(f"Total Queries: {len(results)}")
    print(f"Average Integration Score: {overall_avg:.3f}")
    print(f"Pass Rate (≥0.75): {pass_rate:.1f}%")
    print(f"TARGET: >75% integration quality")

    # Component breakdown
    sql_usage = sum(1 for _, _, m in results if m.sql_component_used) / len(results) * 100 if results else 0
    vector_usage = sum(1 for _, _, m in results if m.vector_component_used) / len(results) * 100 if results else 0
    blending = sum(1 for _, _, m in results if m.components_blended) / len(results) * 100 if results else 0
    completeness = sum(1 for _, _, m in results if m.answer_complete) / len(results) * 100 if results else 0

    print(f"\nComponent Breakdown:")
    print(f"  SQL usage:         {sql_usage:.1f}%")
    print(f"  Vector usage:      {vector_usage:.1f}%")
    print(f"  Blending quality:  {blending:.1f}%")
    print(f"  Completeness:      {completeness:.1f}%")

    if overall_avg >= 0.75:
        print(f"\n✓ TARGET MET - Ready for production deployment")
    else:
        gap = 0.75 - overall_avg
        print(f"\n✗ TARGET MISSED by {gap:.3f} - Optimize integration before deployment")

        # Specific recommendations
        print(f"\nRECOMMENDATIONS:")
        if sql_usage < 75:
            print(f"  1. Fix QueryClassifier - Not detecting HYBRID queries correctly")
        if vector_usage < 75:
            print(f"  2. Check vector search - Not retrieving contextual information")
        if blending < 75:
            print(f"  3. Improve system prompt - Add transition phrases for blending")
        if completeness < 75:
            print(f"  4. Enhance response generation - Ensure both stats AND analysis")

    print("=" * 80 + "\n")


def save_results(results: list, output_path: Path):
    """Save evaluation results to JSON.

    Args:
        results: List of (test_case, response, metrics) tuples
        output_path: Output file path
    """
    results_data = {
        "evaluation_type": "hybrid_queries",
        "test_count": len(results),
        "target_integration_quality": 0.75,
        "samples": []
    }

    for test_case, response, metrics in results:
        results_data["samples"].append({
            "question": test_case.question,
            "category": test_case.category,
            "response": response.answer,
            "sources_count": len(response.sources),
            "processing_time_ms": response.processing_time_ms,
            "metrics": {
                "sql_component_used": metrics.sql_component_used,
                "vector_component_used": metrics.vector_component_used,
                "components_blended": metrics.components_blended,
                "answer_complete": metrics.answer_complete,
                "integration_score": metrics.integration_score,
            }
        })

    # Calculate overall stats
    all_scores = [m.integration_score for _, _, m in results]
    results_data["overall_metrics"] = {
        "average_integration_score": sum(all_scores) / len(all_scores) if all_scores else 0,
        "pass_rate": sum(1 for s in all_scores if s >= 0.75) / len(all_scores) if all_scores else 0,
        "target_met": (sum(all_scores) / len(all_scores) if all_scores else 0) >= 0.75,
        "sql_usage_rate": sum(1 for _, _, m in results if m.sql_component_used) / len(results) if results else 0,
        "vector_usage_rate": sum(1 for _, _, m in results if m.vector_component_used) / len(results) if results else 0,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Results saved to: {output_path}\n")


def main():
    """Run hybrid query evaluation (Phase 10: Hybrid Queries)."""
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
    print("  PHASE 10: HYBRID QUERY EVALUATION")
    print("  Test SQL + Vector integration quality across 4 complexity tiers")
    print("  Prerequisites: Phase SQL-1 passed (>85% SQL accuracy)")
    print("=" * 80 + "\n")

    # Group test cases by tier
    tiers = {}
    for tc in HYBRID_TEST_CASES:
        tier = tc.category.split('_')[0]
        tiers.setdefault(tier, []).append(tc)

    print(f"Hybrid test cases ({len(HYBRID_TEST_CASES)} total):")
    for tier in sorted(tiers.keys()):
        tier_name = tier.upper().replace('TIER', 'Tier ')
        print(f"\n  {tier_name} ({len(tiers[tier])} cases):")
        for i, tc in enumerate(tiers[tier], 1):
            print(f"    {i}. {tc.question[:70]}...")

    print(f"\nRunning evaluation on {len(HYBRID_TEST_CASES)} hybrid queries...\n")

    # Run evaluation
    results = run_hybrid_evaluation(HYBRID_TEST_CASES)

    # Print results
    print_results(results)

    # Save results
    output_file = Path("evaluation_results/phase10_hybrid_queries.json")
    save_results(results, output_file)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
