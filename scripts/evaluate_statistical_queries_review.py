"""
FILE: evaluate_statistical_queries_review.py
STATUS: Experimental
RESPONSIBILITY: Evaluate 25 statistical queries from _STATISTICAL_QUERIES_TO_REVIEW.py
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu

Evaluates queries expected to route to SQL to verify they work correctly.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation._STATISTICAL_QUERIES_TO_REVIEW import (
    STATISTICAL_QUERIES_FROM_VECTOR_TESTS,
)

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_CHAT_ENDPOINT = f"{API_BASE_URL}/api/chat"

# Evaluation Configuration
RATE_LIMIT_DELAY_SECONDS = 2  # Delay between requests
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 9  # 9s, 18s, 36s

# Output paths
RESULTS_DIR = Path("evaluation_results")
RESULTS_DIR.mkdir(exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = RESULTS_DIR / f"statistical_queries_review_{timestamp}.json"
REPORT_FILE = RESULTS_DIR / "STATISTICAL_QUERIES_REVIEW_REPORT.md"


def call_chat_api(question: str, conversation_id: str | None = None) -> dict:
    """Call the chat API endpoint.

    Args:
        question: User question
        conversation_id: Optional conversation ID for follow-up queries

    Returns:
        API response dict with 'answer', 'sources', 'conversation_id', 'routing'

    Raises:
        RuntimeError: If API call fails after retries
    """
    payload = {"question": question}
    if conversation_id:
        payload["conversation_id"] = conversation_id

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(API_CHAT_ENDPOINT, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            is_rate_limit = (
                hasattr(e, "response")
                and e.response is not None
                and e.response.status_code == 429
            )

            if is_rate_limit and attempt < MAX_RETRIES:
                wait_time = RETRY_BACKOFF_BASE * (2**attempt)
                print(
                    f"  429 Rate Limit (attempt {attempt + 1}/{MAX_RETRIES}). "
                    f"Waiting {wait_time}s..."
                )
                time.sleep(wait_time)
            elif attempt < MAX_RETRIES:
                wait_time = 5
                print(f"  API error (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(wait_time)
            else:
                raise RuntimeError(f"API call failed after {MAX_RETRIES} retries: {e}")


def evaluate_test_cases() -> dict:
    """Evaluate all 25 statistical queries.

    Returns:
        Dictionary with evaluation results
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(STATISTICAL_QUERIES_FROM_VECTOR_TESTS),
        "test_cases": [],
        "summary": {
            "successful": 0,
            "failed": 0,
            "routing": {"sql_only": 0, "hybrid": 0, "vector_only": 0, "unknown": 0},
            "failures_by_reason": {},
        },
    }

    print(f"\n{'=' * 80}")
    print(f"STATISTICAL QUERIES REVIEW EVALUATION")
    print(f"{'=' * 80}")
    print(f"Total test cases: {results['total_cases']}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'=' * 80}\n")

    for idx, test_case in enumerate(STATISTICAL_QUERIES_FROM_VECTOR_TESTS, 1):
        print(f"[{idx}/{results['total_cases']}] {test_case.category.value.upper()}")
        print(f"  Q: {test_case.question[:80]}...")

        test_result = {
            "index": idx,
            "question": test_case.question,
            "ground_truth": test_case.ground_truth,
            "category": test_case.category.value,
            "expected_routing": "sql_only",  # These are statistical queries
            "status": "pending",
            "failure_reason": None,
            "response": None,
            "actual_routing": None,
            "sources_count": 0,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Call API
            api_response = call_chat_api(test_case.question)

            # Extract response details
            test_result["response"] = api_response.get("answer", "")
            test_result["actual_routing"] = api_response.get("routing", "unknown")
            test_result["sources_count"] = len(api_response.get("sources", []))
            test_result["conversation_id"] = api_response.get("conversation_id")

            # Check routing
            expected = test_result["expected_routing"]
            actual = test_result["actual_routing"]

            if actual == expected:
                test_result["status"] = "success"
                results["summary"]["successful"] += 1
                print(f"  ✓ SUCCESS: Routed to {actual}")
            else:
                test_result["status"] = "routing_mismatch"
                test_result["failure_reason"] = (
                    f"Expected {expected} but got {actual}"
                )
                results["summary"]["failed"] += 1
                print(f"  ✗ ROUTING MISMATCH: Expected {expected}, got {actual}")

            # Count routing
            results["summary"]["routing"][actual] = (
                results["summary"]["routing"].get(actual, 0) + 1
            )

            # Show response preview
            response_preview = test_result["response"][:100]
            print(f"  Response: {response_preview}...")

        except Exception as e:
            test_result["status"] = "error"
            test_result["failure_reason"] = str(e)
            results["summary"]["failed"] += 1

            # Track failure reasons
            reason_key = type(e).__name__
            results["summary"]["failures_by_reason"][reason_key] = (
                results["summary"]["failures_by_reason"].get(reason_key, 0) + 1
            )

            print(f"  ✗ ERROR: {e}")

        results["test_cases"].append(test_result)

        # Rate limiting
        if idx < results["total_cases"]:
            time.sleep(RATE_LIMIT_DELAY_SECONDS)

    return results


def generate_report(results: dict) -> str:
    """Generate markdown report from results.

    Args:
        results: Evaluation results dictionary

    Returns:
        Markdown report string
    """
    total = results["total_cases"]
    successful = results["summary"]["successful"]
    failed = results["summary"]["failed"]
    success_rate = (successful / total * 100) if total > 0 else 0

    # Count routing matches
    sql_only_count = results["summary"]["routing"].get("sql_only", 0)
    routing_accuracy = (sql_only_count / total * 100) if total > 0 else 0

    # Collect failures
    failures = [tc for tc in results["test_cases"] if tc["status"] != "success"]

    report = f"""# Statistical Queries Review - Evaluation Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Evaluation File:** `{OUTPUT_FILE.name}`
**Total Test Cases:** {total}
**Status:** {"✅ ALL PASSING" if failed == 0 else f"⚠️ {failed} FAILURES"}

---

## Executive Summary

These 25 statistical queries were extracted from `vector_test_cases.py` by the classification script. They ask for statistical/factual data (player stats, rankings, team records, etc.) and should route to **SQL-only** processing.

---

## Overall Results

| Metric | Value |
|--------|-------|
| **Total Cases** | {total} |
| **Successful** | {successful} ({success_rate:.1f}%) |
| **Failed** | {failed} ({100 - success_rate:.1f}%) |
| **Routing Accuracy** | {routing_accuracy:.1f}% ({sql_only_count}/{total} routed to SQL) |

### Routing Distribution
- **SQL Only:** {results['summary']['routing'].get('sql_only', 0)}
- **Hybrid:** {results['summary']['routing'].get('hybrid', 0)}
- **Vector Only:** {results['summary']['routing'].get('vector_only', 0)}
- **Unknown:** {results['summary']['routing'].get('unknown', 0)}

---

## Results by Category

"""

    # Count by category
    from collections import Counter

    category_results = Counter()
    category_failures = Counter()

    for tc in results["test_cases"]:
        cat = tc["category"]
        category_results[cat] += 1
        if tc["status"] != "success":
            category_failures[cat] += 1

    report += "| Category | Total | Success | Failed | Success Rate |\n"
    report += "|----------|-------|---------|--------|-------------|\n"

    for cat in sorted(category_results.keys()):
        total_cat = category_results[cat]
        failed_cat = category_failures[cat]
        success_cat = total_cat - failed_cat
        rate = (success_cat / total_cat * 100) if total_cat > 0 else 0
        report += f"| {cat} | {total_cat} | {success_cat} | {failed_cat} | {rate:.1f}% |\n"

    report += "\n---\n\n"

    # Failures section
    if failures:
        report += f"## Failures Analysis ({len(failures)} cases)\n\n"

        # Group by failure reason
        failures_by_reason = {}
        for tc in failures:
            reason = tc.get("failure_reason", "Unknown")
            if reason not in failures_by_reason:
                failures_by_reason[reason] = []
            failures_by_reason[reason].append(tc)

        for reason, cases in failures_by_reason.items():
            report += f"### {reason} ({len(cases)} cases)\n\n"

            for tc in cases:
                report += f"**[{tc['category'].upper()}] {tc['question'][:80]}...**\n\n"
                report += f"- **Expected routing:** {tc['expected_routing']}\n"
                report += f"- **Actual routing:** {tc['actual_routing']}\n"
                if tc["response"]:
                    response_preview = tc["response"][:200].replace("\n", " ")
                    report += f"- **Response:** {response_preview}...\n"
                report += "\n"

        report += "---\n\n"

        # Root causes
        report += "## Root Causes\n\n"

        if any("routing_mismatch" in tc["status"] for tc in failures):
            misrouted = [
                tc for tc in failures if tc["status"] == "routing_mismatch"
            ]
            report += f"### Routing Mismatches ({len(misrouted)} cases)\n\n"
            report += "Queries were classified as statistical but routed differently:\n\n"

            for tc in misrouted[:5]:  # Show first 5
                report += f"- **{tc['question'][:60]}...** → {tc['actual_routing']}\n"

            report += "\n"

        if any("error" in tc["status"] for tc in failures):
            errors = [tc for tc in failures if tc["status"] == "error"]
            report += f"### API Errors ({len(errors)} cases)\n\n"

            for tc in errors:
                report += f"- **{tc['question'][:60]}...** → {tc['failure_reason']}\n"

            report += "\n"

    else:
        report += "## ✅ All Tests Passed\n\n"
        report += "All 25 statistical queries correctly routed to SQL and returned valid responses.\n\n"

    report += "---\n\n"
    report += "## Recommendations\n\n"

    if failed == 0:
        report += "✅ **All queries working correctly.** These 25 queries can be moved to `sql_test_cases.py` with confidence.\n\n"
    else:
        report += f"⚠️ **{failed} failures detected.** Review and fix issues before moving to `sql_test_cases.py`:\n\n"

        if routing_accuracy < 100:
            report += f"1. **Routing accuracy is {routing_accuracy:.1f}%** - Investigate why {total - sql_only_count} queries didn't route to SQL\n"

        report += "2. **Fix API errors** if any occurred\n"
        report += "3. **Review misrouted queries** to improve QueryClassifier patterns\n"

    report += f"\n---\n\n**Generated:** {datetime.now().isoformat()}\n"
    report += f"**Based on:** `{OUTPUT_FILE.name}`\n"

    return report


def main():
    """Run evaluation and generate report."""
    print("\n🔍 Starting evaluation of 25 statistical queries...\n")

    # Run evaluation
    results = evaluate_test_cases()

    # Save results
    OUTPUT_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n✅ Results saved to: {OUTPUT_FILE}")

    # Generate report
    report = generate_report(results)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"✅ Report saved to: {REPORT_FILE}")

    # Print summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total: {results['total_cases']}")
    print(f"Successful: {results['summary']['successful']} ✓")
    print(f"Failed: {results['summary']['failed']} ✗")
    print(
        f"Success Rate: {results['summary']['successful'] / results['total_cases'] * 100:.1f}%"
    )
    print(f"{'=' * 80}\n")

    return 0 if results["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
