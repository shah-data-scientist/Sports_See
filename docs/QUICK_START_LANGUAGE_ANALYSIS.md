# Quick Start: Language Impact Analysis

## Goal

Quantify whether French prompts are hurting RAGAS metrics compared to English prompts.

## Two-Step Process

### 1. Generate Test Data (15-20 minutes)

```bash
poetry run python scripts/quick_prompt_test.py
```

This tests 5 prompt variations (3 French, 2 English) on 12 samples.

**Output:** `quick_test_results/*.json`

### 2. Analyze Language Impact (< 1 minute)

```bash
poetry run python scripts/analyze_language_impact.py
```

This performs statistical analysis comparing French vs English performance.

**Output:**
- Console: Summary statistics with significance tests
- File: `evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md` (detailed report)

## Example Results

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
```

## Key Questions Answered

1. **Is language a significant factor?**
   - Yes/No based on p-value (< 0.05 = significant)

2. **How big is the effect?**
   - Cohen's d: negligible/small/medium/large

3. **Which language performs better?**
   - Positive difference = English better
   - Negative difference = French better

4. **Should I switch languages?**
   - See recommendations in generated report

## What the Script Does

1. **Loads Results:** Reads all `*.json` files from `quick_test_results/`
2. **Categorizes:** Identifies French vs English prompts by name
3. **Extracts Metrics:** Pulls faithfulness and answer_relevancy scores
4. **Calculates Statistics:**
   - Means and standard deviations
   - T-test for significance (p-value)
   - Cohen's d for effect size
5. **Generates Report:** Creates markdown with tables, charts, and recommendations

## Files Created

| File | Purpose | Size |
|------|---------|------|
| `scripts/analyze_language_impact.py` | Analysis script | ~500 lines |
| `evaluation_results/LANGUAGE_IMPACT_ANALYSIS.md` | Detailed report | ~300 lines |
| `docs/LANGUAGE_IMPACT_ANALYSIS_GUIDE.md` | Usage guide | ~400 lines |
| `docs/LANGUAGE_IMPACT_EXAMPLE_OUTPUT.md` | Example output | ~300 lines |
| `docs/QUICK_START_LANGUAGE_ANALYSIS.md` | This file | ~100 lines |

## Script Features

- **5-field header:** Complies with project standards
- **Statistical rigor:** T-tests, Cohen's d, significance interpretation
- **Handles edge cases:** Missing data, None values, division by zero
- **UTF-8 encoding:** Properly handles French characters
- **Comprehensive reporting:** Tables, interpretation, recommendations
- **Error messages:** Clear instructions if prerequisites missing

## Dependencies

All required packages are already in the project:
- `numpy` (via pandas)
- `scipy` (via transitive dependencies)
- `pathlib`, `json`, `logging` (stdlib)

No additional installation needed!

## Troubleshooting

**Error:** "Directory quick_test_results does not exist"

**Fix:** Run step 1 first (`quick_prompt_test.py`)

---

**Need more details?** See `docs/LANGUAGE_IMPACT_ANALYSIS_GUIDE.md`

**Example output?** See `docs/LANGUAGE_IMPACT_EXAMPLE_OUTPUT.md`
