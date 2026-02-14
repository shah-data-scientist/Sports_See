"""
FILE: merge_evaluation_results.py
STATUS: Active
RESPONSIBILITY: Merge retry results into full evaluation and generate comprehensive report
LAST MAJOR UPDATE: 2026-02-11
MAINTAINER: Shahu
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluation.run_sql_evaluation import generate_comprehensive_report


def merge_results(full_path: str, retry_path: str, output_path: str) -> dict:
    """Merge retry results into full evaluation results.

    Args:
        full_path: Path to full evaluation JSON
        retry_path: Path to retry results JSON
        output_path: Path to save merged results

    Returns:
        Merged results dictionary
    """
    # Load both files
    with open(full_path, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    with open(retry_path, 'r', encoding='utf-8') as f:
        retry_results = json.load(f)

    # Create mapping of retry results by question
    retry_map = {result['question']: result for result in retry_results}

    # Update full results with retry data
    updated_count = 0
    for i, result in enumerate(full_data['results']):
        question = result['question']
        if question in retry_map:
            retry_result = retry_map[question]

            # Update the result with retry data
            full_data['results'][i] = retry_result
            updated_count += 1

            # Safe printing with ASCII fallback
            try:
                print(f"[OK] Updated: {question[:60]}...")
            except UnicodeEncodeError:
                print(f"[OK] Updated: {question.encode('ascii', 'replace').decode('ascii')[:60]}...")
            print(f"     Old sources_count: {result['sources_count']} -> New: {retry_result['sources_count']}")

    print(f"\n[OK] Merged {updated_count} retry results into full evaluation")

    # Recalculate statistics
    results = full_data['results']
    total = len(results)
    successful = sum(1 for r in results if r.get('success', False))

    # Count by routing
    routing_stats = {'sql_only': 0, 'vector_only': 0, 'hybrid': 0, 'unknown': 0}
    for r in results:
        routing = r.get('actual_routing', 'unknown')
        if routing == 'fallback_to_vector':
            routing = 'hybrid'
        routing_stats[routing] = routing_stats.get(routing, 0) + 1

    # Classification accuracy
    misclassifications = [r for r in results if r.get('is_misclassified', False)]
    classification_accuracy = ((total - len(misclassifications)) / total * 100) if total > 0 else 0

    # Update metadata
    full_data['timestamp'] = datetime.now().isoformat()
    full_data['total_cases'] = total
    full_data['successful'] = successful
    full_data['failed'] = total - successful
    full_data['routing_stats'] = routing_stats
    full_data['classification_accuracy'] = classification_accuracy
    full_data['misclassifications'] = [
        {'question': m['question'], 'expected': m['expected_routing'], 'actual': m['actual_routing']}
        for m in misclassifications
    ]
    full_data['merged_from_retry'] = True
    full_data['retry_count'] = updated_count

    # Save merged results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(full_data, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Saved merged results to: {output_path}")

    return full_data


def main():
    """Main entry point."""
    # File paths
    full_path = "evaluation_results/sql_evaluation_20260211_061045.json"
    retry_path = "evaluation_results/sql_retry_20260211_172824.json"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_path = f"evaluation_results/sql_evaluation_merged_{timestamp}.json"

    print("="*80)
    print("MERGING SQL EVALUATION RESULTS")
    print("="*80)
    print(f"\nFull evaluation: {full_path}")
    print(f"Retry results: {retry_path}")
    print(f"Output: {merged_path}\n")

    # Merge results
    merged_data = merge_results(full_path, retry_path, merged_path)

    # Generate comprehensive report
    print("\n" + "="*80)
    print("GENERATING COMPREHENSIVE REPORT")
    print("="*80 + "\n")

    # Extract just the results list for the report generator
    results_list = merged_data['results']
    report_path = generate_comprehensive_report(results_list, merged_path)

    print("\n" + "="*80)
    print("MERGE AND REPORT COMPLETE")
    print("="*80)
    print(f"\nMerged JSON: {merged_path}")
    print(f"Report: {report_path}")
    print(f"\nStatistics:")
    print(f"  Total: {merged_data['total_cases']}")
    print(f"  Success: {merged_data['successful']}")
    print(f"  Failed: {merged_data['failed']}")
    print(f"  Classification Accuracy: {merged_data['classification_accuracy']:.1f}%")
    print(f"  Updated from retry: {merged_data['retry_count']}")
    print("="*80)


if __name__ == "__main__":
    main()
