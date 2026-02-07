# Evaluation Results & Visualizations

This directory contains RAGAS evaluation results and visualizations comparing the performance of the NBA RAG chatbot across different development phases.

## Directory Structure

```
evaluation_results/
├── ragas_baseline.json           # Baseline evaluation (Phase 1)
├── ragas_phase2.json              # Phase 2 evaluation (SQL integration)
├── ragas_phase4.json              # Phase 4 evaluation (Prompt engineering + classification)
├── ragas_phase5_extended.json     # Phase 5 evaluation (Extended test cases) [pending]
├── PHASE_COMPARISON_REPORT.md     # Generated comparison report with charts
└── charts/                        # Generated visualization charts
    ├── 01_metric_evolution.png
    ├── 02_category_performance.png
    ├── 03_radar_comparison.png
    ├── 04_heatmap_*.png
    └── 05_improvement_from_baseline.png
```

## Generating Visualizations

### Prerequisites

The visualization script requires matplotlib, seaborn, and numpy:

```bash
poetry add matplotlib seaborn numpy
```

These libraries are already installed if you ran the script previously.

### Usage

Run the visualization script from the project root:

```bash
poetry run python scripts/visualize_phases.py
```

This will:
1. Load all available evaluation results (baseline, phase2, phase4, phase5)
2. Generate comprehensive charts comparing metrics across phases
3. Create a markdown report with embedded visualizations
4. Save all outputs to `evaluation_results/`

### Graceful Degradation

- **Missing phases**: The script gracefully handles missing evaluation files (e.g., phase5). Missing phases are marked as "Pending" in the report.
- **Missing libraries**: If matplotlib/seaborn are not installed, the script will generate the markdown report without charts and display installation instructions.

## Visualization Types

### 1. Line Chart: Metric Evolution
Shows how each RAGAS metric (faithfulness, answer relevancy, context precision, context recall) evolves from baseline through all phases.

### 2. Bar Chart: Category Performance
Grouped bar chart comparing performance across query categories (simple, complex, noisy, conversational) for each phase.

### 3. Radar Chart: Overall Metrics
Provides a holistic view of all metrics across phases, making it easy to see strengths and weaknesses at a glance.

### 4. Heatmaps: Metric x Phase x Category
Individual heatmaps for each metric showing the intersection of phases and query categories. Helps identify which improvements worked for which query types.

### 5. Improvement Chart
Bar chart showing percentage changes from baseline, making it easy to quantify the impact of each development phase.

## Report Contents

The generated `PHASE_COMPARISON_REPORT.md` includes:

- **Executive Summary**: Overview of available phases and their configurations
- **Overall Scores Table**: Side-by-side comparison of all metrics
- **Visualizations**: Embedded charts with descriptions
- **Key Findings**: Phase-specific improvements with percentage changes
- **Recommendations**: Prioritized improvement suggestions

## Metrics Explained

### Faithfulness
Measures whether the generated answer is factually consistent with the provided context. Higher is better. Target: 0.80+

### Answer Relevancy
Measures how relevant the answer is to the question asked. Higher is better. Target: 0.75+

### Context Precision
Measures whether the retrieved context is relevant to the question. Higher is better. Target: 0.75+

### Context Recall
Measures whether all necessary information to answer the question was retrieved. Higher is better. Target: 0.80+

## Interpreting Results

### Good Signs
- ✅ Context Precision/Recall > 0.70: Retrieval is working well
- ✅ Faithfulness > 0.75: Minimal hallucination
- ✅ Answer Relevancy > 0.70: Responses are focused and concise

### Warning Signs
- ⚠️ Answer Relevancy < 0.30: Responses are verbose or off-topic
- ⚠️ Faithfulness < 0.60: High risk of hallucination
- ⚠️ Context Recall < 0.50: Missing critical information

### Critical Issues
- 🚨 Any metric < 0.20: Major system failure requiring immediate attention
- 🚨 Complex category = 0.00: Complete failure on analytical questions

## Adding New Phases

To add a new phase evaluation:

1. Run your evaluation script (e.g., `scripts/evaluate_phase5.py`)
2. Ensure the output JSON is saved to `evaluation_results/ragas_phase*.json`
3. Re-run `scripts/visualize_phases.py` to regenerate charts and report

The script automatically detects and includes any new phase files.

## Troubleshooting

### Charts not generating
```bash
# Install visualization libraries
poetry add matplotlib seaborn numpy
```

### "File not found" error
Ensure baseline evaluation exists:
```bash
ls evaluation_results/ragas_baseline.json
```

### Outdated visualizations
Simply re-run the script - it regenerates everything from scratch:
```bash
poetry run python scripts/visualize_phases.py
```

## Technical Details

- **Chart Resolution**: 300 DPI (publication quality)
- **Color Scheme**: Seaborn "husl" palette for accessibility
- **Encoding**: UTF-8 (supports Unicode characters like "Jokić")
- **Backend**: matplotlib 'Agg' (non-interactive, server-safe)

---

*Generated by Sports_See evaluation pipeline*
