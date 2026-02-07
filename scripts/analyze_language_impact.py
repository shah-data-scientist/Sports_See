"""
FILE: analyze_language_impact.py
STATUS: Active
RESPONSIBILITY: Analyze language impact on RAGAS metrics (French vs English prompts)
LAST MAJOR UPDATE: 2026-02-07
MAINTAINER: Shahu
"""

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


def load_quick_test_results() -> dict[str, dict[str, Any]]:
    """Load all quick test results from quick_test_results directory.

    Returns:
        Dict mapping prompt_name to result data
    """
    results_dir = Path("quick_test_results")

    if not results_dir.exists():
        raise FileNotFoundError(
            f"Directory {results_dir} does not exist. "
            "Run 'poetry run python scripts/quick_prompt_test.py' first."
        )

    results = {}
    json_files = list(results_dir.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {results_dir}")

    for json_file in json_files:
        if json_file.name == "SUMMARY.json":
            continue

        logger.info(f"Loading {json_file.name}")
        with json_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            results[data.get("prompt_name", json_file.stem)] = data

    return results


def categorize_prompts(results: dict[str, dict]) -> dict[str, list[str]]:
    """Categorize prompts by language.

    Args:
        results: Dict of prompt results

    Returns:
        Dict with 'french' and 'english' keys containing prompt names
    """
    french_prompts = []
    english_prompts = []

    # Categorize based on prompt names
    for prompt_name in results.keys():
        if "french" in prompt_name.lower() or prompt_name == "phase4_current":
            french_prompts.append(prompt_name)
        elif "english" in prompt_name.lower():
            english_prompts.append(prompt_name)
        else:
            logger.warning(f"Unable to categorize prompt: {prompt_name}")

    return {
        "french": french_prompts,
        "english": english_prompts,
    }


def extract_metrics(results: dict[str, dict], prompt_names: list[str]) -> dict[str, list[float]]:
    """Extract metrics for a list of prompts.

    Args:
        results: Dict of prompt results
        prompt_names: List of prompt names to extract

    Returns:
        Dict with metric names as keys and lists of values
    """
    faithfulness_values = []
    answer_relevancy_values = []

    for prompt_name in prompt_names:
        if prompt_name not in results:
            logger.warning(f"Prompt {prompt_name} not found in results")
            continue

        data = results[prompt_name]

        # Extract metrics
        faith = data.get("faithfulness")
        rel = data.get("answer_relevancy")

        if faith is not None:
            faithfulness_values.append(faith)
        if rel is not None:
            answer_relevancy_values.append(rel)

    return {
        "faithfulness": faithfulness_values,
        "answer_relevancy": answer_relevancy_values,
    }


def calculate_statistics(french_metrics: dict, english_metrics: dict) -> dict[str, dict]:
    """Calculate statistical comparisons between French and English.

    Args:
        french_metrics: Dict with French metric values
        english_metrics: Dict with English metric values

    Returns:
        Dict with statistical analysis for each metric
    """
    statistics = {}

    for metric_name in ["faithfulness", "answer_relevancy"]:
        french_vals = french_metrics.get(metric_name, [])
        english_vals = english_metrics.get(metric_name, [])

        if not french_vals or not english_vals:
            statistics[metric_name] = {
                "french_mean": None,
                "english_mean": None,
                "difference": None,
                "percent_difference": None,
                "t_statistic": None,
                "p_value": None,
                "cohens_d": None,
                "interpretation": "Insufficient data",
            }
            continue

        # Calculate means
        french_mean = np.mean(french_vals)
        english_mean = np.mean(english_vals)
        difference = english_mean - french_mean
        percent_diff = (difference / french_mean * 100) if french_mean > 0 else 0

        # Calculate standard deviations
        french_std = np.std(french_vals, ddof=1) if len(french_vals) > 1 else 0
        english_std = np.std(english_vals, ddof=1) if len(english_vals) > 1 else 0

        # T-test (independent samples)
        if len(french_vals) > 1 and len(english_vals) > 1:
            t_stat, p_val = stats.ttest_ind(english_vals, french_vals)
        else:
            t_stat, p_val = None, None

        # Cohen's d (effect size)
        if french_std > 0 or english_std > 0:
            pooled_std = np.sqrt(((len(french_vals) - 1) * french_std**2 +
                                  (len(english_vals) - 1) * english_std**2) /
                                (len(french_vals) + len(english_vals) - 2))
            cohens_d = difference / pooled_std if pooled_std > 0 else 0
        else:
            cohens_d = 0

        # Interpret effect size
        if cohens_d is not None:
            abs_d = abs(cohens_d)
            if abs_d < 0.2:
                effect = "negligible"
            elif abs_d < 0.5:
                effect = "small"
            elif abs_d < 0.8:
                effect = "medium"
            else:
                effect = "large"
        else:
            effect = "unknown"

        # Interpret significance
        if p_val is not None:
            if p_val < 0.01:
                significance = "highly significant (p < 0.01)"
            elif p_val < 0.05:
                significance = "significant (p < 0.05)"
            elif p_val < 0.10:
                significance = "marginally significant (p < 0.10)"
            else:
                significance = "not significant (p ≥ 0.10)"
        else:
            significance = "unable to calculate"

        statistics[metric_name] = {
            "french_mean": french_mean,
            "french_std": french_std,
            "french_n": len(french_vals),
            "english_mean": english_mean,
            "english_std": english_std,
            "english_n": len(english_vals),
            "difference": difference,
            "percent_difference": percent_diff,
            "t_statistic": t_stat,
            "p_value": p_val,
            "cohens_d": cohens_d,
            "effect_size": effect,
            "significance": significance,
        }

    return statistics


def generate_report_content(
    results: dict[str, dict],
    categories: dict[str, list[str]],
    statistics: dict[str, dict],
) -> str:
    """Generate markdown report content.

    Args:
        results: All prompt results
        categories: Categorized prompt names
        statistics: Statistical analysis results

    Returns:
        Markdown report as string
    """
    lines = []

    # Header
    lines.append("# Language Impact Analysis: French vs English Prompts")
    lines.append("")
    lines.append("**Generated:** 2026-02-07")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")

    # Overall verdict
    faith_stats = statistics["faithfulness"]
    rel_stats = statistics["answer_relevancy"]

    faith_better = "English" if faith_stats["difference"] > 0 else "French"
    rel_better = "English" if rel_stats["difference"] > 0 else "French"

    faith_effect = faith_stats.get("effect_size", "unknown")
    rel_effect = rel_stats.get("effect_size", "unknown")

    lines.append(f"This analysis compares the performance of French prompts vs English prompts on the NBA RAG system using RAGAS metrics.")
    lines.append("")
    lines.append("**Key Findings:**")
    lines.append("")
    lines.append(f"- **Faithfulness:** {faith_better} prompts perform better by {abs(faith_stats['percent_difference']):.1f}% ({faith_effect} effect size)")
    lines.append(f"- **Answer Relevancy:** {rel_better} prompts perform better by {abs(rel_stats['percent_difference']):.1f}% ({rel_effect} effect size)")
    lines.append("")

    # Prompt inventory
    lines.append("## Prompt Inventory")
    lines.append("")
    lines.append("### French Prompts")
    lines.append("")
    for prompt in categories["french"]:
        lines.append(f"- `{prompt}`")
    lines.append("")

    lines.append("### English Prompts")
    lines.append("")
    for prompt in categories["english"]:
        lines.append(f"- `{prompt}`")
    lines.append("")

    # Metrics comparison table
    lines.append("## Metrics Comparison")
    lines.append("")
    lines.append("| Metric | French Mean | English Mean | Difference | % Difference | Effect Size |")
    lines.append("|--------|-------------|--------------|------------|--------------|-------------|")

    for metric_name in ["faithfulness", "answer_relevancy"]:
        stats_data = statistics[metric_name]
        metric_label = metric_name.replace("_", " ").title()

        if stats_data["french_mean"] is not None:
            lines.append(
                f"| {metric_label} | "
                f"{stats_data['french_mean']:.4f} | "
                f"{stats_data['english_mean']:.4f} | "
                f"{stats_data['difference']:+.4f} | "
                f"{stats_data['percent_difference']:+.1f}% | "
                f"{stats_data['effect_size']} |"
            )
        else:
            lines.append(f"| {metric_label} | N/A | N/A | N/A | N/A | N/A |")

    lines.append("")

    # Statistical significance
    lines.append("## Statistical Significance")
    lines.append("")

    for metric_name in ["faithfulness", "answer_relevancy"]:
        stats_data = statistics[metric_name]
        metric_label = metric_name.replace("_", " ").title()

        lines.append(f"### {metric_label}")
        lines.append("")

        if stats_data["p_value"] is not None:
            lines.append(f"- **T-statistic:** {stats_data['t_statistic']:.4f}")
            lines.append(f"- **P-value:** {stats_data['p_value']:.4f}")
            lines.append(f"- **Cohen's d:** {stats_data['cohens_d']:.4f}")
            lines.append(f"- **Effect size:** {stats_data['effect_size']}")
            lines.append(f"- **Interpretation:** {stats_data['significance']}")
            lines.append("")

            # Explain what this means
            if stats_data["p_value"] < 0.05:
                lines.append(f"The difference is **statistically significant**. This suggests that language choice has a measurable impact on {metric_label.lower()}.")
            else:
                lines.append(f"The difference is **not statistically significant**. The observed difference could be due to chance or small sample size.")
        else:
            lines.append("- **Insufficient data** for statistical testing (need n > 1 in each group)")

        lines.append("")

    # Detailed breakdown
    lines.append("## Detailed Breakdown by Prompt")
    lines.append("")
    lines.append("| Prompt Name | Language | Faithfulness | Answer Relevancy | Sample Count |")
    lines.append("|-------------|----------|--------------|------------------|--------------|")

    # Sort by language then by faithfulness
    all_prompts = [(p, "French") for p in categories["french"]] + \
                  [(p, "English") for p in categories["english"]]

    for prompt_name, lang in sorted(all_prompts, key=lambda x: (x[1], x[0])):
        data = results.get(prompt_name, {})
        faith = data.get("faithfulness")
        rel = data.get("answer_relevancy")
        count = data.get("sample_count", 0)

        faith_str = f"{faith:.4f}" if faith is not None else "N/A"
        rel_str = f"{rel:.4f}" if rel is not None else "N/A"

        lines.append(f"| {prompt_name} | {lang} | {faith_str} | {rel_str} | {count} |")

    lines.append("")

    # Effect size interpretation
    lines.append("## Effect Size Interpretation")
    lines.append("")
    lines.append("Cohen's d is a standardized measure of effect size:")
    lines.append("")
    lines.append("- **< 0.2:** Negligible effect")
    lines.append("- **0.2 - 0.5:** Small effect")
    lines.append("- **0.5 - 0.8:** Medium effect")
    lines.append("- **> 0.8:** Large effect")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")

    # Determine winner
    faith_better_en = faith_stats["difference"] > 0
    rel_better_en = rel_stats["difference"] > 0

    if faith_better_en and rel_better_en:
        lines.append("### Strong Recommendation: Use English Prompts")
        lines.append("")
        lines.append("English prompts outperform French prompts on both key metrics:")
        lines.append(f"- Faithfulness: {faith_stats['percent_difference']:+.1f}% improvement")
        lines.append(f"- Answer Relevancy: {rel_stats['percent_difference']:+.1f}% improvement")
        lines.append("")
        lines.append("**Action Items:**")
        lines.append("1. Switch production prompts to English")
        lines.append("2. Maintain French in the system prompt/UI for user-facing content")
        lines.append("3. Use English for internal retrieval and generation prompts")
    elif not faith_better_en and not rel_better_en:
        lines.append("### Strong Recommendation: Use French Prompts")
        lines.append("")
        lines.append("French prompts outperform English prompts on both key metrics:")
        lines.append(f"- Faithfulness: {abs(faith_stats['percent_difference']):.1f}% better")
        lines.append(f"- Answer Relevancy: {abs(rel_stats['percent_difference']):.1f}% better")
        lines.append("")
        lines.append("**Action Items:**")
        lines.append("1. Continue using French prompts in production")
        lines.append("2. Consider if language is being evaluated by a French-preferring model")
    else:
        lines.append("### Mixed Results: Language Choice Involves Trade-offs")
        lines.append("")
        lines.append("The results show trade-offs between metrics:")
        lines.append(f"- Faithfulness: {faith_better} performs better")
        lines.append(f"- Answer Relevancy: {rel_better} performs better")
        lines.append("")
        lines.append("**Action Items:**")
        lines.append("1. Prioritize the metric that matters most for your use case")
        lines.append("2. If faithfulness is critical (accuracy), choose the better language for that metric")
        lines.append("3. If relevancy is critical (user satisfaction), choose the better language for that metric")
        lines.append("4. Consider hybrid approach: different languages for different query types")

    lines.append("")

    # Limitations
    lines.append("## Limitations")
    lines.append("")
    lines.append("This analysis has several limitations:")
    lines.append("")
    lines.append(f"1. **Small sample size:** Only {faith_stats.get('french_n', 0)} French prompts and {faith_stats.get('english_n', 0)} English prompts tested")
    lines.append("2. **Single test set:** Results based on 12 samples from quick_prompt_test.py")
    lines.append("3. **Evaluator language bias:** RAGAS evaluator (Gemini/Mistral) may prefer one language")
    lines.append("4. **Prompt structure differences:** Not just language - instruction style also varies")
    lines.append("5. **No user satisfaction data:** Metrics don't capture actual user preferences")
    lines.append("")

    # Next steps
    lines.append("## Suggested Next Steps")
    lines.append("")
    lines.append("1. **Expand sample size:** Run full evaluation (47 samples) with French and English variants")
    lines.append("2. **Isolate language variable:** Create prompts that differ ONLY in language, not structure")
    lines.append("3. **Test evaluator bias:** Use French vs English evaluator models and compare results")
    lines.append("4. **A/B test in production:** Deploy both and measure real user engagement metrics")
    lines.append("5. **Qualitative analysis:** Manually review sample responses to understand quality differences")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("**Generated by:** `scripts/analyze_language_impact.py`")
    lines.append("")
    lines.append("**Data source:** `quick_test_results/`")
    lines.append("")

    return "\n".join(lines)


def save_report(content: str, output_path: Path) -> None:
    """Save report to markdown file.

    Args:
        content: Report content as markdown string
        output_path: Path to save the report
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Report saved to {output_path}")


def print_summary(statistics: dict[str, dict]) -> None:
    """Print summary to console.

    Args:
        statistics: Statistical analysis results
    """
    print("\n" + "=" * 80)
    print("  LANGUAGE IMPACT ANALYSIS SUMMARY")
    print("=" * 80)

    for metric_name in ["faithfulness", "answer_relevancy"]:
        stats_data = statistics[metric_name]
        metric_label = metric_name.replace("_", " ").title()

        print(f"\n  {metric_label.upper()}")
        print("  " + "-" * 76)

        if stats_data["french_mean"] is not None:
            print(f"    French:  {stats_data['french_mean']:.4f} (n={stats_data['french_n']})")
            print(f"    English: {stats_data['english_mean']:.4f} (n={stats_data['english_n']})")
            print(f"    Difference: {stats_data['difference']:+.4f} ({stats_data['percent_difference']:+.1f}%)")
            print(f"    Effect Size: {stats_data['effect_size']} (Cohen's d = {stats_data['cohens_d']:.3f})")

            if stats_data["p_value"] is not None:
                print(f"    Significance: {stats_data['significance']}")
        else:
            print("    Insufficient data for analysis")

    print("\n" + "=" * 80 + "\n")


def main() -> int:
    """Run language impact analysis.

    Returns:
        Exit code (0 for success)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    try:
        # Load results
        logger.info("Loading quick test results...")
        results = load_quick_test_results()
        logger.info(f"Loaded {len(results)} prompt variations")

        # Categorize by language
        categories = categorize_prompts(results)
        logger.info(f"French prompts: {len(categories['french'])}")
        logger.info(f"English prompts: {len(categories['english'])}")

        if len(categories["french"]) == 0 or len(categories["english"]) == 0:
            logger.error("Need both French and English prompts for comparison")
            return 1

        # Extract metrics
        french_metrics = extract_metrics(results, categories["french"])
        english_metrics = extract_metrics(results, categories["english"])

        # Calculate statistics
        logger.info("Calculating statistics...")
        statistics = calculate_statistics(french_metrics, english_metrics)

        # Print summary
        print_summary(statistics)

        # Generate and save report
        logger.info("Generating report...")
        report_content = generate_report_content(results, categories, statistics)

        output_path = Path("evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md")
        save_report(report_content, output_path)

        print(f"\nFull report saved to: {output_path.absolute()}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"Required files not found: {e}")
        logger.info("Run this command first: poetry run python scripts/quick_prompt_test.py")
        return 1

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
