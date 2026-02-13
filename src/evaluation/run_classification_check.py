"""
FILE: run_classification_check.py
STATUS: Active
RESPONSIBILITY: Validates QueryClassifier routing accuracy across all test datasets
LAST MAJOR UPDATE: 2026-02-13
MAINTAINER: Development Team
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from src.evaluation.test_cases.hybrid_test_cases import HYBRID_TEST_CASES
from src.evaluation.test_cases.sql_test_cases import SQL_TEST_CASES
from src.evaluation.test_cases.vector_test_cases import EVALUATION_TEST_CASES
from src.services.query_classifier import QueryClassifier, QueryType

# Mapping: classifier enum values → evaluation enum values
# Classifier: statistical, contextual, hybrid
# Evaluation: sql_only, contextual_only, hybrid
CLASSIFIER_TO_EVAL = {
    "statistical": "sql_only",
    "contextual": "contextual_only",
    "hybrid": "hybrid",
}

# Acceptable classifications per dataset
# SQL test cases: expect sql_only (classifier: statistical) or hybrid
# Vector test cases: expect contextual_only (classifier: contextual) or hybrid
# Hybrid test cases: uses per-case query_type for expected classification
SQL_ACCEPTABLE = {"statistical"}  # Must be statistical
VECTOR_ACCEPTABLE = {"contextual"}  # Must be contextual

# Reverse mapping: evaluation enum value → classifier enum value
EVAL_TO_CLASSIFIER = {
    "sql_only": "statistical",
    "contextual_only": "contextual",
    "hybrid": "hybrid",
}


class ClassificationChecker:
    """Validates query classification accuracy across all test datasets."""

    def __init__(self):
        self.classifier = QueryClassifier()
        self.results = {
            "sql": {"total": 0, "correct": 0, "misclassified": []},
            "vector": {"total": 0, "correct": 0, "misclassified": []},
            "hybrid": {"total": 0, "correct": 0, "misclassified": []},
        }

    def _check_dataset(self, dataset_name: str, test_cases, expected_classifier_values: set, get_question, get_category) -> None:
        """Generic dataset checker."""
        print(f"\n=== Checking {dataset_name.upper()} Test Cases ===")
        self.results[dataset_name]["total"] = len(test_cases)

        for tc in test_cases:
            question = get_question(tc)
            actual_raw = self.classifier.classify(question).query_type.value  # e.g. "statistical"
            actual_eval = CLASSIFIER_TO_EVAL.get(actual_raw, actual_raw)  # e.g. "sql_only"

            is_correct = actual_raw in expected_classifier_values
            cat = get_category(tc)

            if is_correct:
                self.results[dataset_name]["correct"] += 1
            else:
                self.results[dataset_name]["misclassified"].append({
                    "question": question,
                    "expected": list(expected_classifier_values)[0],
                    "actual": actual_raw,
                    "expected_eval": CLASSIFIER_TO_EVAL.get(list(expected_classifier_values)[0], "?"),
                    "actual_eval": actual_eval,
                    "category": cat,
                })

        total = self.results[dataset_name]["total"]
        correct = self.results[dataset_name]["correct"]
        accuracy = correct / total * 100 if total > 0 else 0
        print(f"{dataset_name.upper()} Dataset: {correct}/{total} ({accuracy:.1f}% accuracy)")

    def check_sql_dataset(self) -> None:
        """Check SQL test cases (expected: statistical → sql_only)."""
        self._check_dataset(
            "sql", SQL_TEST_CASES, SQL_ACCEPTABLE,
            get_question=lambda tc: tc.question,
            get_category=lambda tc: getattr(tc, "category", "unknown"),
        )

    def check_vector_dataset(self) -> None:
        """Check Vector test cases (expected: contextual → contextual_only)."""
        self._check_dataset(
            "vector", EVALUATION_TEST_CASES, VECTOR_ACCEPTABLE,
            get_question=lambda tc: tc.question,
            get_category=lambda tc: tc.category.value if hasattr(tc.category, "value") else str(tc.category),
        )

    def check_hybrid_dataset(self) -> None:
        """Check Hybrid test cases — respects per-case query_type field."""
        print(f"\n=== Checking HYBRID Test Cases ===")
        self.results["hybrid"]["total"] = len(HYBRID_TEST_CASES)

        for tc in HYBRID_TEST_CASES:
            question = tc.question
            actual_raw = self.classifier.classify(question).query_type.value  # e.g. "statistical"
            actual_eval = CLASSIFIER_TO_EVAL.get(actual_raw, actual_raw)

            # Use per-case query_type to determine expected classification
            # tc.query_type uses eval enum (sql_only/contextual_only/hybrid)
            # actual_raw uses classifier enum (statistical/contextual/hybrid)
            expected_eval_value = tc.query_type.value  # e.g. "sql_only", "hybrid"
            expected_raw = EVAL_TO_CLASSIFIER.get(expected_eval_value, expected_eval_value)
            is_correct = actual_raw == expected_raw
            cat = getattr(tc, "category", "unknown")

            if is_correct:
                self.results["hybrid"]["correct"] += 1
            else:
                self.results["hybrid"]["misclassified"].append({
                    "question": question,
                    "expected": expected_raw,
                    "actual": actual_raw,
                    "expected_eval": CLASSIFIER_TO_EVAL.get(expected_raw, "?"),
                    "actual_eval": actual_eval,
                    "category": cat,
                })

        accuracy = (
            self.results["hybrid"]["correct"] / self.results["hybrid"]["total"] * 100
        )
        print(
            f"Hybrid Dataset: {self.results['hybrid']['correct']}/{self.results['hybrid']['total']} "
            f"({accuracy:.1f}% accuracy)"
        )

    def analyze_misclassification_patterns(self) -> Dict[str, List[Dict]]:
        """Group misclassifications by routing pattern (e.g., sql→contextual)."""
        patterns = defaultdict(list)

        for dataset_name, dataset_results in self.results.items():
            for misclass in dataset_results["misclassified"]:
                pattern_key = f"{misclass['expected']}→{misclass['actual']}"
                patterns[pattern_key].append({
                    "dataset": dataset_name,
                    "question": misclass["question"],
                    "category": misclass["category"],
                })

        return dict(patterns)

    def generate_summary(self) -> Dict:
        """Generate overall summary statistics."""
        total_queries = sum(ds["total"] for ds in self.results.values())
        total_correct = sum(ds["correct"] for ds in self.results.values())
        total_misclassified = total_queries - total_correct
        overall_accuracy = (total_correct / total_queries * 100) if total_queries > 0 else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "total_queries": total_queries,
                "correct": total_correct,
                "misclassified": total_misclassified,
                "accuracy_percent": round(overall_accuracy, 2),
            },
            "per_dataset": {
                "sql": {
                    "total": self.results["sql"]["total"],
                    "correct": self.results["sql"]["correct"],
                    "misclassified": len(self.results["sql"]["misclassified"]),
                    "accuracy_percent": round(
                        (self.results["sql"]["correct"] / self.results["sql"]["total"] * 100)
                        if self.results["sql"]["total"] > 0 else 0,
                        2,
                    ),
                },
                "vector": {
                    "total": self.results["vector"]["total"],
                    "correct": self.results["vector"]["correct"],
                    "misclassified": len(self.results["vector"]["misclassified"]),
                    "accuracy_percent": round(
                        (self.results["vector"]["correct"] / self.results["vector"]["total"] * 100)
                        if self.results["vector"]["total"] > 0 else 0,
                        2,
                    ),
                },
                "hybrid": {
                    "total": self.results["hybrid"]["total"],
                    "correct": self.results["hybrid"]["correct"],
                    "misclassified": len(self.results["hybrid"]["misclassified"]),
                    "accuracy_percent": round(
                        (self.results["hybrid"]["correct"] / self.results["hybrid"]["total"] * 100)
                        if self.results["hybrid"]["total"] > 0 else 0,
                        2,
                    ),
                },
            },
            "misclassification_patterns": self.analyze_misclassification_patterns(),
            "all_misclassifications": {
                "sql": self.results["sql"]["misclassified"],
                "vector": self.results["vector"]["misclassified"],
                "hybrid": self.results["hybrid"]["misclassified"],
            },
        }

    def save_json_report(self, summary: Dict, output_path: Path) -> None:
        """Save full results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nJSON report saved: {output_path}")

    def save_markdown_report(self, summary: Dict, output_path: Path) -> None:
        """Save readable report to Markdown."""
        lines = [
            "# Query Classification Check Report",
            f"\n**Generated:** {summary['timestamp']}",
            "\n## Overall Summary",
            f"- **Total Queries:** {summary['overall']['total_queries']}",
            f"- **Correct Classifications:** {summary['overall']['correct']}",
            f"- **Misclassifications:** {summary['overall']['misclassified']}",
            f"- **Overall Accuracy:** {summary['overall']['accuracy_percent']:.2f}%",
            "\n## Per-Dataset Results",
        ]

        for dataset_name in ["sql", "vector", "hybrid"]:
            ds = summary["per_dataset"][dataset_name]
            lines.extend([
                f"\n### {dataset_name.upper()} Dataset",
                f"- Total: {ds['total']}",
                f"- Correct: {ds['correct']}",
                f"- Misclassified: {ds['misclassified']}",
                f"- Accuracy: {ds['accuracy_percent']:.2f}%",
            ])

        # Misclassification patterns
        patterns = summary["misclassification_patterns"]
        if patterns:
            lines.append("\n## Misclassification Patterns (Root Cause Analysis)")
            for pattern_key, cases in sorted(patterns.items(), key=lambda x: -len(x[1])):
                lines.extend([
                    f"\n### Pattern: `{pattern_key}` ({len(cases)} cases)",
                    "",
                ])
                for i, case in enumerate(cases, 1):
                    lines.append(
                        f"{i}. **[{case['dataset'].upper()}]** {case['question']}"
                    )
                    if case.get("category") and case["category"] != "unknown":
                        lines.append(f"   - Category: {case['category']}")

        # All misclassifications by dataset
        lines.append("\n## All Misclassifications by Dataset")
        for dataset_name in ["sql", "vector", "hybrid"]:
            misclass_list = summary["all_misclassifications"][dataset_name]
            if misclass_list:
                lines.append(f"\n### {dataset_name.upper()} Misclassifications ({len(misclass_list)})")
                for i, mc in enumerate(misclass_list, 1):
                    lines.extend([
                        f"\n{i}. **Question:** {mc['question']}",
                        f"   - **Expected:** `{mc['expected']}`",
                        f"   - **Actual:** `{mc['actual']}`",
                        f"   - **Category:** {mc.get('category', 'unknown')}",
                    ])
            else:
                lines.append(f"\n### {dataset_name.upper()} Misclassifications")
                lines.append("\nNo misclassifications! Perfect accuracy.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Markdown report saved: {output_path}")

    def run(self) -> None:
        """Run the full classification check."""
        print("=" * 80)
        print("QUERY CLASSIFICATION CHECK")
        print("=" * 80)
        print(f"\nDataset sizes:")
        print(f"  SQL Test Cases: {len(SQL_TEST_CASES)}")
        print(f"  Vector Test Cases: {len(EVALUATION_TEST_CASES)}")
        print(f"  Hybrid Test Cases: {len(HYBRID_TEST_CASES)}")
        print(f"  Total: {len(SQL_TEST_CASES) + len(EVALUATION_TEST_CASES) + len(HYBRID_TEST_CASES)}")

        # Run checks
        self.check_sql_dataset()
        self.check_vector_dataset()
        self.check_hybrid_dataset()

        # Generate summary
        summary = self.generate_summary()

        # Print overall summary
        print("\n" + "=" * 80)
        print("OVERALL SUMMARY")
        print("=" * 80)
        print(f"Total Queries: {summary['overall']['total_queries']}")
        print(f"Correct: {summary['overall']['correct']}")
        print(f"Misclassified: {summary['overall']['misclassified']}")
        print(f"Overall Accuracy: {summary['overall']['accuracy_percent']:.2f}%")

        # Print pattern summary
        patterns = summary["misclassification_patterns"]
        if patterns:
            print("\n" + "=" * 80)
            print("MISCLASSIFICATION PATTERNS")
            print("=" * 80)
            for pattern_key, cases in sorted(patterns.items(), key=lambda x: -len(x[1])):
                print(f"\n{pattern_key}: {len(cases)} cases")
                for case in cases[:3]:  # Show first 3 examples
                    print(f"  - [{case['dataset'].upper()}] {case['question'][:70]}...")
                if len(cases) > 3:
                    print(f"  ... and {len(cases) - 3} more")

        # Save reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("evaluation_results")
        json_path = results_dir / f"classification_check_{timestamp}.json"
        md_path = results_dir / f"classification_check_report_{timestamp}.md"

        self.save_json_report(summary, json_path)
        self.save_markdown_report(summary, md_path)

        print("\n" + "=" * 80)
        print("CLASSIFICATION CHECK COMPLETE")
        print("=" * 80)


if __name__ == "__main__":
    checker = ClassificationChecker()
    checker.run()
