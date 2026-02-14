"""
FILE: run_vector_sample_4_cases.py
STATUS: Active
RESPONSIBILITY: Run vector evaluation on 4-case sample (2 CONVERSATIONAL + 2 SIMPLE)
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Sample evaluation to demonstrate the consolidated vector evaluation system.
"""

import io
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

from starlette.testclient import TestClient
from src.api.main import create_app
from src.evaluation.vector_test_cases import EVALUATION_TEST_CASES
from src.evaluation.models import TestCategory
from src.evaluation.run_vector_evaluation import calculate_ragas_metrics
from src.evaluation.vector_quality_analysis import (
    analyze_category_performance,
    analyze_ragas_metrics,
    analyze_response_patterns,
    analyze_retrieval_performance,
    analyze_source_quality,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def select_sample_cases():
    """Select 2 CONVERSATIONAL + 2 SIMPLE test cases."""
    conversational = [tc for tc in EVALUATION_TEST_CASES if tc.category == TestCategory.CONVERSATIONAL]
    simple = [tc for tc in EVALUATION_TEST_CASES if tc.category == TestCategory.SIMPLE]

    # Select first 2 of each category
    sample = conversational[:2] + simple[:2]

    logger.info(f"Selected {len(sample)} test cases:")
    for i, tc in enumerate(sample, 1):
        logger.info(f"  [{i}] {tc.category.value}: {tc.question[:60]}...")

    return sample


def run_sample_evaluation():
    """Run vector evaluation on 4-case sample."""
    print("\n" + "="*100)
    print("  VECTOR EVALUATION - 4-CASE SAMPLE (2 CONVERSATIONAL + 2 SIMPLE)")
    print("="*100)
    print()

    # Select sample cases
    test_cases = select_sample_cases()

    # Initialize results
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Run evaluation via API
    app = create_app()

    print("\n" + "="*100)
    print("  RUNNING EVALUATION")
    print("="*100)
    print()

    with TestClient(app) as client:
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"[{i}/{len(test_cases)}] {test_case.category.value}: {test_case.question[:60]}...")

            try:
                # API call
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "query": test_case.question,
                        "k": 5,
                        "include_sources": True
                    },
                    timeout=30
                )

                if response.status_code != 200:
                    raise RuntimeError(f"API error {response.status_code}: {response.text[:300]}")

                api_result = response.json()

                # Record result
                results.append({
                    "question": test_case.question,
                    "category": test_case.category.value,
                    "response": api_result.get("answer", ""),
                    "sources": [
                        {
                            "text": s.get("text", "")[:500],
                            "score": s.get("score", 0),
                            "source": s.get("source", "unknown")
                        }
                        for s in api_result.get("sources", [])
                    ],
                    "sources_count": len(api_result.get("sources", [])),
                    "processing_time_ms": api_result.get("processing_time_ms", 0),
                    "ground_truth": test_case.ground_truth,
                    "success": True
                })

                logger.info(f"  ✓ Success (sources: {len(api_result.get('sources', []))}, time: {api_result.get('processing_time_ms', 0)}ms)")

            except Exception as e:
                logger.error(f"  ✗ Failed: {str(e)}")
                results.append({
                    "question": test_case.question,
                    "category": test_case.category.value,
                    "error": str(e),
                    "success": False
                })

            # Small delay between requests (not needed for 4 cases, but good practice)
            if i < len(test_cases):
                time.sleep(1)

    # Calculate RAGAS metrics for successful results
    successful_results = [r for r in results if r.get("success")]

    if successful_results:
        print("\n" + "="*100)
        print("  CALCULATING RAGAS METRICS")
        print("="*100)
        print()

        try:
            logger.info("Calculating RAGAS metrics...")
            ragas_scores = calculate_ragas_metrics(results)

            # Merge RAGAS scores back into results
            for i, result in enumerate(results):
                if result.get("success") and i < len(ragas_scores):
                    result["ragas_metrics"] = ragas_scores[i]

            logger.info("✓ RAGAS metrics calculated successfully")

        except Exception as e:
            logger.warning(f"⚠️ RAGAS calculation failed: {e}")
            logger.info("Continuing without RAGAS metrics...")

    # Save JSON results
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"vector_sample_4_cases_{timestamp}.json"

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(test_cases),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "sample_description": "2 CONVERSATIONAL + 2 SIMPLE test cases",
        "results": results
    }

    json_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"\n✅ Results saved to: {json_path}")

    # Run analysis functions
    print("\n" + "="*100)
    print("  RUNNING QUALITY ANALYSIS")
    print("="*100)
    print()

    ragas_analysis = analyze_ragas_metrics(results)
    source_analysis = analyze_source_quality(results)
    response_analysis = analyze_response_patterns(results)
    retrieval_analysis = analyze_retrieval_performance(results)
    category_analysis = analyze_category_performance(results)

    # Generate simplified report
    report_lines = []

    report_lines.extend([
        "# Vector Evaluation - 4-Case Sample Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Sample:** 2 CONVERSATIONAL + 2 SIMPLE test cases",
        f"**Results JSON:** `{json_path.name}`",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **Total Queries:** {len(test_cases)}",
        f"- **Successful:** {sum(1 for r in results if r.get('success'))} ({sum(1 for r in results if r.get('success'))/len(test_cases)*100:.1f}%)",
        f"- **Failed:** {sum(1 for r in results if not r.get('success'))}",
        "",
    ])

    # Add RAGAS metrics summary if available
    overall_ragas = ragas_analysis.get("overall", {})
    if overall_ragas and overall_ragas.get("avg_faithfulness"):
        report_lines.extend([
            "### RAGAS Metrics (Average)",
            "",
            f"- **Faithfulness:** {overall_ragas.get('avg_faithfulness', 'N/A')}",
            f"- **Answer Relevancy:** {overall_ragas.get('avg_answer_relevancy', 'N/A')}",
            f"- **Context Precision:** {overall_ragas.get('avg_context_precision', 'N/A')}",
            f"- **Context Recall:** {overall_ragas.get('avg_context_recall', 'N/A')}",
            "",
        ])

    report_lines.extend([
        "---",
        "",
        "## Test Cases Evaluated",
        "",
        "| # | Category | Question | Success |",
        "|---|----------|----------|---------|",
    ])

    for i, result in enumerate(results, 1):
        question = result.get("question", "")[:60]
        category = result.get("category", "unknown")
        success = "✅" if result.get("success") else "❌"
        report_lines.append(f"| {i} | {category} | {question}... | {success} |")

    report_lines.extend(["", "---", ""])

    # Detailed Results
    report_lines.extend([
        "## Detailed Results",
        "",
    ])

    for i, result in enumerate(results, 1):
        report_lines.extend([
            f"### Test Case {i}: {result.get('category', 'unknown').upper()}",
            "",
            f"**Question:** {result.get('question', '')}",
            "",
        ])

        if result.get("success"):
            report_lines.extend([
                f"**Response ({len(result.get('response', ''))} chars):**",
                "",
                result.get('response', '')[:500] + ("..." if len(result.get('response', '')) > 500 else ""),
                "",
                f"**Sources Retrieved:** {result.get('sources_count', 0)}",
                "",
            ])

            if result.get('sources'):
                report_lines.append("| # | Source | Score |")
                report_lines.append("|---|--------|-------|")
                for j, src in enumerate(result['sources'][:5], 1):
                    source_name = src.get('source', 'unknown')[:40]
                    score = src.get('score', 0)
                    report_lines.append(f"| {j} | {source_name} | {score:.1f}% |")
                report_lines.extend(["", ""])

            report_lines.append(f"**Processing Time:** {result.get('processing_time_ms', 0)}ms")

            # Add RAGAS metrics if available
            if result.get('ragas_metrics'):
                ragas = result['ragas_metrics']
                report_lines.extend([
                    "",
                    "**RAGAS Metrics:**",
                    "",
                    f"- Faithfulness: {ragas.get('faithfulness', 'N/A')}",
                    f"- Answer Relevancy: {ragas.get('answer_relevancy', 'N/A')}",
                    f"- Context Precision: {ragas.get('context_precision', 'N/A')}",
                    f"- Context Recall: {ragas.get('context_recall', 'N/A')}",
                    ""
                ])
        else:
            report_lines.append(f"**Error:** {result.get('error', 'Unknown error')}")

        report_lines.extend(["", "---", ""])

    # Quality Analysis Summary
    report_lines.extend([
        "## Quality Analysis Summary",
        "",
        "### Source Quality",
        "",
    ])

    retrieval_stats = source_analysis.get("retrieval_stats", {})
    report_lines.extend([
        f"- **Average Sources per Query:** {retrieval_stats.get('avg_sources_per_query', 0)}",
        f"- **Total Unique Sources:** {retrieval_stats.get('total_unique_sources', 0)}",
        f"- **Average Similarity Score:** {retrieval_stats.get('avg_similarity_score', 0):.2f}%",
        "",
    ])

    # Top sources
    top_sources = source_analysis.get("source_diversity", {}).get("top_sources", [])
    if top_sources:
        report_lines.extend([
            "**Top Sources:**",
            "",
            "| Source | Count | Avg Score |",
            "|--------|-------|-----------|",
        ])
        for src in top_sources[:5]:
            report_lines.append(f"| {src['source'][:40]} | {src['count']} | {src['avg_score']:.1f}% |")
        report_lines.extend(["", ""])

    # Retrieval Performance
    perf_metrics = retrieval_analysis.get("performance_metrics", {})
    report_lines.extend([
        "### Retrieval Performance",
        "",
        f"- **Average Processing Time:** {perf_metrics.get('avg_processing_time_ms', 0):.0f}ms",
        f"- **Retrieval Success Rate:** {perf_metrics.get('retrieval_success_rate', 0):.1%}",
        "",
        "---",
        "",
    ])

    # Category Performance
    category_breakdown = category_analysis.get("category_breakdown", {})
    if category_breakdown:
        report_lines.extend([
            "### Performance by Category",
            "",
            "| Category | Count | Success Rate | Avg Sources | Avg Score |",
            "|----------|-------|--------------|-------------|-----------|",
        ])

        for category, stats in sorted(category_breakdown.items()):
            count = stats.get("count", 0)
            success_rate = stats.get("success_rate", 0)
            sources = stats.get("avg_sources", 0)
            score = stats.get("avg_retrieval_score", 0)
            report_lines.append(f"| {category} | {count} | {success_rate:.1%} | {sources:.1f} | {score:.1f}% |")

        report_lines.extend(["", ""])

    # Footer
    report_lines.extend([
        "---",
        "",
        f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Generated by Sports_See Vector Evaluation System (4-Case Sample)",
        ""
    ])

    # Save report
    report_path = output_dir / f"vector_sample_4_cases_report_{timestamp}.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    logger.info(f"✅ Report saved to: {report_path}")

    # Print summary
    print("\n" + "="*100)
    print("  EVALUATION COMPLETE")
    print("="*100)
    print()
    print(f"📊 Results Summary:")
    print(f"   - Successful: {sum(1 for r in results if r.get('success'))}/{len(test_cases)}")
    print(f"   - Failed: {sum(1 for r in results if not r.get('success'))}/{len(test_cases)}")
    print()
    print(f"📁 Output Files:")
    print(f"   - JSON: {json_path}")
    print(f"   - Report: {report_path}")
    print()

    return results, str(json_path), str(report_path)


if __name__ == "__main__":
    try:
        run_sample_evaluation()
    except KeyboardInterrupt:
        print("\n\n⚠️ Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
