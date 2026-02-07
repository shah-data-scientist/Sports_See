# Language Impact Analysis Guide

## Overview

This guide explains how to use the language impact analysis tools to quantify whether French prompts are hurting RAGAS metrics compared to English prompts.

## Workflow

### Step 1: Run Quick Prompt Test

First, generate test results for multiple prompt variations (both French and English):

```bash
poetry run python scripts/quick_prompt_test.py
```

This will:
- Test 5 prompt variations on 12 carefully selected samples (3 per category)
- Generate answers using Gemini 2.0 Flash Lite
- Evaluate with RAGAS (Faithfulness and Answer Relevancy)
- Save results to `quick_test_results/`

**Expected output structure:**
```
quick_test_results/
  ├── phase4_current.json          # French - current production prompt
  ├── balanced_french.json         # French - balanced style
  ├── concise_french.json          # French - minimal style
  ├── english_detailed.json        # English - detailed instructions
  ├── english_concise.json         # English - minimal style
  └── SUMMARY.json                 # Aggregate results
```

**Runtime:** ~15-20 minutes (with rate limiting and API cooldowns)

### Step 2: Run Language Impact Analysis

Once quick test results exist, analyze the language impact:

```bash
poetry run python scripts/analyze_language_impact.py
```

This will:
- Load all prompt test results
- Categorize prompts by language (French vs English)
- Extract metrics (faithfulness, answer_relevancy)
- Calculate statistical comparisons:
  - Mean values for each language
  - Standard deviations
  - T-tests for significance
  - Cohen's d for effect size
- Generate comprehensive markdown report
- Save to `evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md`

**Expected console output:**
```
================================================================================
  LANGUAGE IMPACT ANALYSIS SUMMARY
================================================================================

  FAITHFULNESS
  ----------------------------------------------------------------------------
    French:  0.4753 (n=3)
    English: 0.5214 (n=2)
    Difference: +0.0461 (+9.7%)
    Effect Size: small (Cohen's d = 0.328)
    Significance: not significant (p ≥ 0.10)

  ANSWER RELEVANCY
  ----------------------------------------------------------------------------
    French:  0.0818 (n=3)
    English: 0.1523 (n=2)
    Difference: +0.0705 (+86.2%)
    Effect Size: large (Cohen's d = 1.142)
    Significance: significant (p < 0.05)

================================================================================

Full report saved to: evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md
```

### Step 3: Review the Report

Open the generated report at `evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md`.

The report includes:

1. **Executive Summary** - High-level findings and verdict
2. **Prompt Inventory** - List of French and English prompts tested
3. **Metrics Comparison Table** - Side-by-side numerical comparison
4. **Statistical Significance** - T-tests, p-values, effect sizes
5. **Detailed Breakdown** - Per-prompt performance
6. **Recommendations** - Actionable next steps based on findings
7. **Limitations** - Known biases and constraints
8. **Suggested Next Steps** - How to expand the analysis

## Understanding the Results

### Metrics Explained

**Faithfulness (0.0 - 1.0):**
- Measures whether the answer is factually consistent with retrieved context
- Higher is better
- Critical for accuracy and avoiding hallucinations

**Answer Relevancy (0.0 - 1.0):**
- Measures how directly the answer addresses the user's question
- Higher is better
- Critical for user satisfaction

### Statistical Measures

**Cohen's d (Effect Size):**
- < 0.2: Negligible effect
- 0.2 - 0.5: Small effect
- 0.5 - 0.8: Medium effect
- \> 0.8: Large effect

**P-value (Significance):**
- < 0.01: Highly significant (very unlikely due to chance)
- < 0.05: Significant (standard threshold)
- < 0.10: Marginally significant
- ≥ 0.10: Not significant (could be chance)

### Interpretation Example

If the report shows:
- English faithfulness: 0.521 (+9.7% vs French)
- English relevancy: 0.152 (+86.2% vs French)
- Effect sizes: small and large respectively
- P-values: 0.15 and 0.03

**Interpretation:**
- English prompts show improvement in both metrics
- Answer relevancy improvement is statistically significant and large
- Faithfulness improvement is not statistically significant (small sample)
- **Recommendation:** Consider switching to English prompts, but validate with larger sample

## Troubleshooting

### Error: "Directory quick_test_results does not exist"

**Solution:** Run `quick_prompt_test.py` first:
```bash
poetry run python scripts/quick_prompt_test.py
```

### Error: "No JSON files found in quick_test_results"

**Cause:** The quick test didn't complete successfully or files were deleted.

**Solution:** Re-run the quick test and ensure it completes without errors.

### Error: "Need both French and English prompts for comparison"

**Cause:** Only one language type was found in the results.

**Solution:** Ensure `quick_prompt_test.py` includes both French and English prompt variations in the `PROMPT_VARIATIONS` dict.

### Warning: "not significant (p ≥ 0.10)"

**Interpretation:** The observed difference could be due to chance. This is common with small sample sizes (n=2-3 per language).

**Solution:** Run a full evaluation (47 samples) instead of quick test (12 samples) for more statistical power.

## Extending the Analysis

### Testing More Prompt Variations

Edit `scripts/quick_prompt_test.py` and add new entries to `PROMPT_VARIATIONS`:

```python
PROMPT_VARIATIONS = {
    # ... existing prompts ...

    "your_new_prompt": """Your prompt template here with {context} and {question} placeholders""",
}
```

Then re-run the quick test.

### Full Evaluation (47 samples)

For more robust results, create a full evaluation version:

```bash
# Create evaluation_phase6.py based on quick_prompt_test.py
# Use all 47 EVALUATION_TEST_CASES instead of SUBSET_INDICES
poetry run python scripts/evaluation_phase6.py
```

This will take 2-3 hours but provide much stronger statistical power.

### Testing Different Evaluator Models

The RAGAS evaluator model might have language bias. Test with different evaluators:

1. Edit `quick_prompt_test.py` → `_build_evaluator_llm()`
2. Change from Gemini to Mistral or vice versa
3. Re-run quick test
4. Compare results

If English prompts only win with an English-preferring evaluator, the improvement may be biased.

## Files Reference

| File | Purpose |
|------|---------|
| `scripts/quick_prompt_test.py` | Generate test data for prompt variations |
| `scripts/analyze_language_impact.py` | Analyze and compare French vs English performance |
| `quick_test_results/*.json` | Raw test results (generated) |
| `evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md` | Final analysis report (generated) |

## Best Practices

1. **Always run quick test first** - Don't analyze without fresh data
2. **Use consistent sample size** - Rerun both languages with same samples
3. **Check evaluator bias** - Test with multiple evaluator models
4. **Validate in production** - A/B test before full rollout
5. **Consider context** - Language choice affects more than just metrics (user experience, maintainability)

## Frequently Asked Questions

**Q: Why only 12 samples in quick test?**

A: To balance speed vs accuracy. 12 samples (3 per category) is enough to detect large effects quickly. For publication-quality results, use full 47-sample evaluation.

**Q: Can I add more languages (e.g., Spanish)?**

A: Yes! Add Spanish prompts to `PROMPT_VARIATIONS` and the analysis script will automatically categorize them (update `categorize_prompts()` function if needed).

**Q: What if results are mixed (one metric better in French, one in English)?**

A: Prioritize based on your use case. If accuracy is critical, optimize for faithfulness. If user engagement matters most, optimize for relevancy. You can also use different prompts for different query types.

**Q: How do I know if the evaluator is biased?**

A: Run the same test with different evaluator models (Gemini, Mistral, GPT-4). If language preference flips, there's evaluator bias. Also manually review sample responses for quality.

## Support

For issues or questions:
1. Check `PROJECT_MEMORY.md` for known issues
2. Review `CHANGELOG.md` for recent changes
3. Examine test logs in console output
4. Open an issue with full error trace

---

**Last Updated:** 2026-02-07
**Maintainer:** Shahu
