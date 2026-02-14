"""
FILE: test_metrics_pipeline.py
STATUS: Active
RESPONSIBILITY: Test the complete metrics pipeline with actual evaluation data
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import json
from pathlib import Path

from src.evaluation.analysis.sql_analysis_v2 import analyze_sql_results
from src.evaluation.sql_test_oracle import SQLOracle


def test_pipeline_with_actual_data():
    """Test the metrics pipeline using actual evaluation results."""
    print("\n" + "=" * 80)
    print("TESTING METRICS PIPELINE WITH ACTUAL EVALUATION DATA")
    print("=" * 80)

    # Find latest SQL evaluation JSON
    eval_dir = Path("evaluation_results")
    json_files = sorted(eval_dir.glob("sql_evaluation_*.json"), reverse=True)

    if not json_files:
        print("\n❌ No evaluation results found in evaluation_results/")
        print("   Run: poetry run python -m src.evaluation.runners.run_sql_evaluation")
        return False

    latest_json = json_files[0]
    print(f"\n📄 Found evaluation data: {latest_json.name}")

    try:
        # Load results
        with open(latest_json, "r", encoding="utf-8") as f:
            results = json.load(f)

        print(f"✓ Loaded {len(results)} evaluation results")

        # Initialize oracle
        print("\n🔮 Initializing SQLOracle...")
        oracle = SQLOracle()
        print(f"✓ Oracle loaded with {oracle.get_statistics()['total_test_cases']} test cases")

        # Run analysis
        print("\n📊 Running comprehensive analysis...")
        analysis = analyze_sql_results(results, oracle)
        print("✓ Analysis complete")

        # Display key metrics
        print("\n" + "=" * 80)
        print("KEY METRICS FROM ANALYSIS")
        print("=" * 80)

        overall = analysis["overall"]
        print(f"\n📈 OVERALL PERFORMANCE:")
        print(f"   Total Queries:           {overall['total_queries']}")
        print(f"   Execution Success:       {overall['execution_success_count']}/{overall['total_queries']} ({overall['execution_success_rate']:.1f}%)")
        print(f"   Result Accuracy:         {overall['result_accuracy_count']}/{overall['execution_success_count']} ({overall['result_accuracy_rate']:.1f}%)")
        print(f"   Average Latency:         {overall['avg_processing_time_ms']:.0f}ms")
        print(f"   Latency p50 (median):    {overall['p50_processing_time_ms']:.0f}ms")
        print(f"   Latency p95:             {overall['p95_processing_time_ms']:.0f}ms")
        print(f"   Latency p99:             {overall['p99_processing_time_ms']:.0f}ms")

        accuracy = analysis["accuracy"]
        print(f"\n✅ RESULT ACCURACY:")
        print(f"   Correct Results:         {accuracy['correct_results']}")
        print(f"   Incorrect Results:       {accuracy['incorrect_results']}")
        print(f"   Unknown (Not in Oracle): {accuracy['unknown_results']}")
        if accuracy["accuracy_breakdown"]:
            print(f"   Breakdown:")
            for accuracy_type, count in accuracy["accuracy_breakdown"].items():
                print(f"      - {accuracy_type}: {count}")

        sql_quality = analysis["sql_quality"]
        print(f"\n🔗 SQL QUALITY:")
        print(f"   Queries with SQL:        {sql_quality['total_queries_with_sql']}")
        print(f"   Queries with JOINs:      {sql_quality['queries_with_joins']}")
        print(f"   JOIN Correctness Rate:   {sql_quality['join_correctness_rate']:.1f}% ({sql_quality['join_correctness_count']}/{sql_quality['queries_with_joins']})")
        print(f"   Broken JOINs:            {sql_quality['broken_joins_count']} ({sql_quality['broken_joins_rate']:.1f}%)")
        print(f"   Missing JOINs (est):     {sql_quality['missing_joins_estimated']}")

        performance = analysis["performance"]
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        print(f"   Fast Queries (<5s):      {performance['fast_queries_count']}")
        print(f"   Moderate Queries (5-30s):{performance['moderate_queries_count']}")
        print(f"   Slow Queries (>30s):     {performance['slow_queries_count']}")
        print(f"   Outliers (>{performance['outlier_threshold_ms']:.0f}ms): {performance['outlier_count']}")

        print(f"\n📊 CATEGORY PERFORMANCE:")
        print(f"   Categories: {len(analysis['by_category'])}")
        print(f"\n   Category                   | Count | Success | Accuracy | Avg Time | Fallback")
        print(f"   {'-' * 85}")
        for category, stats in sorted(analysis["by_category"].items()):
            print(
                f"   {category[:26]:26s} | {stats['count']:5d} | "
                f"{stats['success_rate']:6.1f}% | {stats['accuracy_rate']:8.1f}% | "
                f"{stats['avg_processing_time_ms']:7.0f}ms | {stats['fallback_rate']:6.1f}%"
            )

        errors = analysis["errors"]
        print(f"\n❌ ERROR ANALYSIS:")
        print(f"   Total Errors: {errors['total_errors']}")
        if errors["error_types"]:
            print(f"   Error Types:")
            for error_type, count in errors["error_types"].items():
                print(f"      - {error_type}: {count}")

        # Save analysis to JSON
        print("\n" + "=" * 80)
        print("SAVING ANALYSIS...")
        print("=" * 80)

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_path = eval_dir / f"sql_evaluation_analysis_{timestamp}.json"

        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"✓ Analysis saved to: {analysis_path.name}")

        # Verification
        print("\n" + "=" * 80)
        print("METRICS VERIFICATION")
        print("=" * 80)

        required_metrics = {
            "Result Accuracy Rate": overall["result_accuracy_rate"] > 0,
            "Latency Percentiles": all(
                key in overall
                for key in ["p50_processing_time_ms", "p95_processing_time_ms", "p99_processing_time_ms"]
            ),
            "JOIN Correctness": sql_quality["join_correctness_rate"] >= 0,
            "Broken JOINs Count": sql_quality["broken_joins_count"] >= 0,
            "Category Performance": len(analysis["by_category"]) > 0,
            "Accuracy Breakdown": len(accuracy["accuracy_breakdown"]) > 0,
        }

        print("\n✓ METRICS IMPLEMENTATION CHECK:")
        all_present = True
        for metric, is_present in required_metrics.items():
            status = "✓" if is_present else "❌"
            print(f"   {status} {metric}")
            if not is_present:
                all_present = False

        print("\n" + "=" * 80)
        if all_present:
            print("✓ PIPELINE TEST PASSED - All metrics implemented successfully!")
        else:
            print("❌ PIPELINE TEST FAILED - Some metrics missing")
        print("=" * 80)

        return all_present

    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline_with_actual_data()
    exit(0 if success else 1)
