"""
FILE: verify_metrics_implementation.py
STATUS: Active
RESPONSIBILITY: Verification script to ensure all metrics are implemented in generated reports
LAST MAJOR UPDATE: 2026-02-12
MAINTAINER: Shahu
"""

import json
import re
from pathlib import Path


def verify_sql_report_completeness(report_path: str) -> dict[str, bool]:
    """Verify that SQL report contains all critical metrics.

    Args:
        report_path: Path to SQL evaluation report (markdown)

    Returns:
        Dictionary of metric_name -> is_present
    """
    if not Path(report_path).exists():
        print(f"❌ Report not found: {report_path}")
        return {}

    content = Path(report_path).read_text(encoding="utf-8")

    # Define critical metrics that MUST be in the report
    required_metrics = {
        "Result Accuracy": "Result Accuracy" in content or "result_accuracy" in content.lower(),
        "Accuracy Percentage": re.search(r"\d+\.\d+%.*accuracy", content, re.IGNORECASE) is not None,
        "SQL Quality Analysis": "SQL Quality" in content,
        "JOIN Correctness": "JOIN Correctness" in content or "join_correctness" in content.lower(),
        "Broken JOINs": "Broken JOINs" in content or "broken.*join" in content.lower(),
        "Missing JOINs": "Missing JOINs" in content or "missing.*join" in content.lower(),
        "Performance Percentiles": ("p50" in content or "p95" in content or "p99" in content),
        "Category Performance": "Category Performance" in content,
        "Performance Outliers": "Performance Outliers" in content or "Outliers" in content,
        "Accuracy Breakdown": "Accuracy Breakdown" in content,
        "Error Analysis": "Error" in content,
    }

    print("\n📊 SQL Report Verification Results:")
    print("=" * 60)

    all_present = True
    for metric, is_present in required_metrics.items():
        status = "✓" if is_present else "❌"
        print(f"{status} {metric:30s} {'Present' if is_present else 'MISSING'}")
        if not is_present:
            all_present = False

    print("=" * 60)
    return required_metrics


def verify_analysis_json_structure(analysis_path: str) -> dict[str, bool]:
    """Verify that analysis JSON has all required structure.

    Args:
        analysis_path: Path to analysis JSON file

    Returns:
        Dictionary of section_name -> is_present
    """
    if not Path(analysis_path).exists():
        print(f"❌ Analysis JSON not found: {analysis_path}")
        return {}

    try:
        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return {}

    # Verify structure
    required_sections = {
        "overall": ["total_queries", "execution_success_rate", "result_accuracy_rate",
                    "p50_processing_time_ms", "p95_processing_time_ms", "p99_processing_time_ms"],
        "accuracy": ["correct_results", "incorrect_results", "accuracy_breakdown"],
        "sql_quality": ["join_correctness_rate", "broken_joins_count", "broken_joins_rate"],
        "performance": ["outlier_count", "outlier_threshold_ms", "outlier_queries"],
        "by_category": [],  # Dictionary, just check it exists
        "errors": ["total_errors", "error_types"],
    }

    print("\n📋 Analysis JSON Structure Verification:")
    print("=" * 60)

    all_valid = True
    for section, required_fields in required_sections.items():
        section_present = section in analysis
        status = "✓" if section_present else "❌"
        print(f"{status} Section: {section:30s} {'Present' if section_present else 'MISSING'}")

        if section_present and required_fields:
            section_data = analysis[section]
            if isinstance(section_data, dict):
                for field in required_fields:
                    field_present = field in section_data
                    field_status = "  ✓" if field_present else "  ❌"
                    print(f"{field_status} Field: {field}")
                    if not field_present:
                        all_valid = False

    print("=" * 60)
    return all_valid


def verify_oracle_initialization() -> bool:
    """Verify that SQLOracle can be initialized without errors.

    Returns:
        True if oracle initializes successfully
    """
    print("\n🔮 Oracle Initialization Test:")
    print("=" * 60)

    try:
        from src.evaluation.sql_test_oracle import SQLOracle

        oracle = SQLOracle()
        stats = oracle.get_statistics()

        print(f"✓ SQLOracle initialized successfully")
        print(f"  - Total test cases: {stats['total_test_cases']}")
        print(f"  - Categories: {len(stats['categories'])}")

        # Verify we have test cases
        if stats["total_test_cases"] > 0:
            print(f"✓ Oracle loaded {stats['total_test_cases']} test cases")
            return True
        else:
            print(f"❌ No test cases loaded in oracle")
            return False

    except Exception as e:
        print(f"❌ Failed to initialize oracle: {e}")
        return False


def verify_analysis_module() -> bool:
    """Verify that analysis module can be imported and called.

    Returns:
        True if analysis module works correctly
    """
    print("\n🔍 Analysis Module Test:")
    print("=" * 60)

    try:
        from src.evaluation.analysis.sql_analysis_v2 import analyze_sql_results

        # Create dummy results
        dummy_results = [
            {
                "question": "Who scored the most points this season?",
                "category": "simple_sql_top_n",
                "response": "Shai Gilgeous-Alexander scored the most points with 2485 PTS.",
                "success": True,
                "processing_time_ms": 5000,
                "generated_sql": "SELECT * FROM player_stats",
            }
        ]

        analysis = analyze_sql_results(dummy_results)

        print(f"✓ analyze_sql_results() executed successfully")
        print(f"  - Overall metrics present: {'overall' in analysis}")
        print(f"  - Accuracy metrics present: {'accuracy' in analysis}")
        print(f"  - SQL quality metrics present: {'sql_quality' in analysis}")
        print(f"  - Performance metrics present: {'performance' in analysis}")
        print(f"  - Category metrics present: {'by_category' in analysis}")

        if all(key in analysis for key in ["overall", "accuracy", "sql_quality", "performance", "by_category", "errors"]):
            print(f"✓ All analysis sections present")
            return True
        else:
            print(f"❌ Some analysis sections missing")
            return False

    except Exception as e:
        print(f"❌ Analysis module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def find_latest_files() -> tuple[str | None, str | None, str | None]:
    """Find latest evaluation files.

    Returns:
        Tuple of (json_path, analysis_path, report_path) or (None, None, None)
    """
    eval_dir = Path("evaluation_results")

    if not eval_dir.exists():
        return None, None, None

    # Find latest SQL evaluation files
    json_files = list(eval_dir.glob("sql_evaluation_*.json"))
    analysis_files = list(eval_dir.glob("sql_evaluation_analysis_*.json"))
    report_files = list(eval_dir.glob("sql_evaluation_report_*.md"))

    json_path = str(sorted(json_files)[-1]) if json_files else None
    analysis_path = str(sorted(analysis_files)[-1]) if analysis_files else None
    report_path = str(sorted(report_files)[-1]) if report_files else None

    return json_path, analysis_path, report_path


def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("SQL METRICS IMPLEMENTATION VERIFICATION")
    print("=" * 80)

    # Test 1: Oracle initialization
    oracle_ok = verify_oracle_initialization()

    # Test 2: Analysis module
    analysis_ok = verify_analysis_module()

    # Test 3: Check for latest evaluation files
    json_path, analysis_path, report_path = find_latest_files()

    report_ok = True
    analysis_json_ok = True

    if report_path:
        print(f"\n📄 Found latest report: {report_path}")
        report_metrics = verify_sql_report_completeness(report_path)
        report_ok = all(report_metrics.values())
    else:
        print("\n⚠️  No recent SQL evaluation report found")
        print("   Run evaluation with: poetry run python -m src.evaluation.runners.run_sql_evaluation")

    if analysis_path:
        print(f"\n📄 Found latest analysis: {analysis_path}")
        analysis_json_ok = verify_analysis_json_structure(analysis_path)
    else:
        print("\n⚠️  No recent analysis JSON found")

    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    checks = [
        ("Oracle Initialization", oracle_ok),
        ("Analysis Module", analysis_ok),
        ("Report Completeness", report_ok if report_path else None),
        ("Analysis JSON Structure", analysis_json_ok if analysis_path else None),
    ]

    for check_name, result in checks:
        if result is None:
            status = "⚠️  SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status:15s} - {check_name}")

    # Overall status
    all_passed = all(r for r in [oracle_ok, analysis_ok] if r is not None)
    if report_path and analysis_path:
        all_passed = all_passed and report_ok and analysis_json_ok

    print("=" * 80)
    if all_passed:
        print("\n✓ All core components verified successfully!")
        if not report_path or not analysis_path:
            print("⚠️  No recent evaluation found. Run evaluation to verify full pipeline.")
    else:
        print("\n❌ Some verifications failed. See details above.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
