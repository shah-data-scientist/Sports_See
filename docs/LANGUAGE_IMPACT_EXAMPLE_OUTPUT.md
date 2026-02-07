# Example Output: Language Impact Analysis

This document shows example output from running the language impact analysis script.

## Console Output Example

```
2026-02-07 19:30:45 - INFO - __main__ - Loading quick test results...
2026-02-07 19:30:45 - INFO - __main__ - Loaded 5 prompt variations
2026-02-07 19:30:45 - INFO - __main__ - French prompts: 3
2026-02-07 19:30:45 - INFO - __main__ - English prompts: 2
2026-02-07 19:30:45 - INFO - __main__ - Calculating statistics...

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

2026-02-07 19:30:46 - INFO - __main__ - Generating report...
2026-02-07 19:30:46 - INFO - __main__ - Report saved to evaluation_results\LANGUAGE_IMPACT_ANALYSIS.md

Full report saved to: C:\Users\shahu\...\LANGUAGE_IMPACT_ANALYSIS.md
```

## Generated Report Example

The following is an example of what `LANGUAGE_IMPACT_ANALYSIS.md` might contain:

---

# Language Impact Analysis: French vs English Prompts

**Generated:** 2026-02-07

## Executive Summary

This analysis compares the performance of French prompts vs English prompts on the NBA RAG system using RAGAS metrics.

**Key Findings:**

- **Faithfulness:** English prompts perform better by 9.7% (small effect size)
- **Answer Relevancy:** English prompts perform better by 86.2% (large effect size)

## Prompt Inventory

### French Prompts

- `phase4_current`
- `balanced_french`
- `concise_french`

### English Prompts

- `english_detailed`
- `english_concise`

## Metrics Comparison

| Metric | French Mean | English Mean | Difference | % Difference | Effect Size |
|--------|-------------|--------------|------------|--------------|-------------|
| Faithfulness | 0.4753 | 0.5214 | +0.0461 | +9.7% | small |
| Answer Relevancy | 0.0818 | 0.1523 | +0.0705 | +86.2% | large |

## Statistical Significance

### Faithfulness

- **T-statistic:** 0.8542
- **P-value:** 0.1523
- **Cohen's d:** 0.3280
- **Effect size:** small
- **Interpretation:** not significant (p ≥ 0.10)

The difference is **not statistically significant**. The observed difference could be due to chance or small sample size.

### Answer Relevancy

- **T-statistic:** 2.3451
- **P-value:** 0.0432
- **Cohen's d:** 1.1420
- **Effect size:** large
- **Interpretation:** significant (p < 0.05)

The difference is **statistically significant**. This suggests that language choice has a measurable impact on answer relevancy.

## Detailed Breakdown by Prompt

| Prompt Name | Language | Faithfulness | Answer Relevancy | Sample Count |
|-------------|----------|--------------|------------------|--------------|
| balanced_french | French | 0.4521 | 0.0942 | 12 |
| concise_french | French | 0.4312 | 0.0651 | 12 |
| phase4_current | French | 0.5426 | 0.0861 | 12 |
| english_concise | English | 0.4987 | 0.1324 | 12 |
| english_detailed | English | 0.5441 | 0.1722 | 12 |

## Effect Size Interpretation

Cohen's d is a standardized measure of effect size:

- **< 0.2:** Negligible effect
- **0.2 - 0.5:** Small effect
- **0.5 - 0.8:** Medium effect
- **> 0.8:** Large effect

## Recommendations

### Strong Recommendation: Use English Prompts

English prompts outperform French prompts on both key metrics:
- Faithfulness: +9.7% improvement
- Answer Relevancy: +86.2% improvement

**Action Items:**
1. Switch production prompts to English
2. Maintain French in the system prompt/UI for user-facing content
3. Use English for internal retrieval and generation prompts

## Limitations

This analysis has several limitations:

1. **Small sample size:** Only 3 French prompts and 2 English prompts tested
2. **Single test set:** Results based on 12 samples from quick_prompt_test.py
3. **Evaluator language bias:** RAGAS evaluator (Gemini/Mistral) may prefer one language
4. **Prompt structure differences:** Not just language - instruction style also varies
5. **No user satisfaction data:** Metrics don't capture actual user preferences

## Suggested Next Steps

1. **Expand sample size:** Run full evaluation (47 samples) with French and English variants
2. **Isolate language variable:** Create prompts that differ ONLY in language, not structure
3. **Test evaluator bias:** Use French vs English evaluator models and compare results
4. **A/B test in production:** Deploy both and measure real user engagement metrics
5. **Qualitative analysis:** Manually review sample responses to understand quality differences

---

**Generated by:** `scripts/analyze_language_impact.py`

**Data source:** `quick_test_results/`

---

## Interpretation Guide

### Scenario 1: Both metrics favor English (like above)

**Strong signal** that English prompts are better. The 86% improvement in answer relevancy with p=0.04 is statistically significant despite small sample size.

**Recommendation:** Switch to English prompts but validate with A/B test.

### Scenario 2: Mixed results

Example:
- Faithfulness: French +15% (medium effect, p=0.03)
- Answer Relevancy: English +20% (medium effect, p=0.04)

**Trade-off situation.** Need to prioritize:
- If accuracy critical → Use French
- If user engagement critical → Use English

### Scenario 3: No significant difference

Example:
- Faithfulness: English +3% (negligible effect, p=0.45)
- Answer Relevancy: English +5% (negligible effect, p=0.38)

**Language doesn't matter.** Choose based on:
- Development team language preference
- Ease of prompt maintenance
- User base language

### Scenario 4: Evaluator bias suspected

Example:
- With Gemini evaluator: English wins
- With Mistral evaluator: French wins

**Evaluator bias detected.** The model doing the evaluation has language preferences that don't reflect actual quality. Consider:
- Using a neutral third model (GPT-4)
- Collecting human ratings
- Using language-agnostic metrics (BLEU, ROUGE)

## Real-World Considerations

Beyond the statistical analysis, consider:

1. **Team capabilities:** Is your team fluent in English for prompt engineering?
2. **Maintainability:** Which language is easier to iterate on prompts?
3. **User base:** Do users care about seeing French vs English in responses?
4. **Model training:** Are the LLMs (Gemini, Mistral) trained more on English or French data?
5. **Context retrieval:** Is the vector store better at English or French semantic search?

The statistics tell you **what** performs better. Context tells you **why** and **whether it matters**.
