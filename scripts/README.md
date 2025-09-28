# Analysis & Reporting Scripts

This directory contains Python scripts used to process raw experimental data and generate the final charts, tables, and reports used in the paper.

## Execution

Most scripts can be run directly from the command line, assuming you are in the `scripts/` directory:

```bash
python <script_name>.py
```

**Dependencies:**
- Scripts read input data primarily from `../data/raw_run_data/` and `../data/summary_data/`.
- Final charts and markdown reports are saved to `../results/`.
- Intermediate processed data files (CSVs) are saved to `../data/summary_data/`.

---

## Key Visualization Scripts

These three scripts are the most critical as they produce the main figures presented in the paper.

- **`generate_composite_plots.py`**
  - **Purpose:** Generates the two main composite figures for multi-dimensional analysis.
  - **Key Outputs:**
    - `dimensional_analysis_composite.png`: A composite plot featuring a radar chart for overall dimensional performance and heatmaps showing score improvements by category.
    - `functionality_usability_composite.png`: A set of stacked bar charts breaking down the functionality usability of different models across server categories.

- **`generate_overall_performance_chart.py`**
  - **Purpose:** Compares the best performance of MCPybarra against the MetaGPT and human-written public baselines for each task.
  - **Key Outputs:**
    - `overall_performance_comparison.png`: A horizontal bar chart showing the final scores for each task.
    - `overall_performance_report.md`: A markdown report with summary statistics like success rate and average improvement.

- **`generate_performance_cost_analysis.py`**
  - **Purpose:** Creates the performance vs. cost analysis visualization.
  - **Key Outputs:**
    - `performance_cost_analysis.png`: A bubble chart where the X-axis is cost, the Y-axis is performance score, and the bubble size represents token consumption.
    - `performance_cost_analysis_report.md`: A markdown report summarizing the data and interpreting the chart.

---

## Data Processing & Utility Scripts

These scripts are primarily used for data aggregation, consolidation, and preliminary analysis. They generate the CSV files that are used as inputs for the key visualization scripts.

- **`consolidate_scores.py`**: Gathers raw total scores from all experimental run logs in `data/raw_run_data/` and consolidates them into `raw_scores_collection.csv`.
- **`generate_dimensional_report.py`**: Gathers detailed dimensional scores (Functionality, Robustness, etc.) from all runs and consolidates them into `dimensional_scores_collection.csv`.
- **`calculate_token_consumption.py`**: Parses detailed agent logs to calculate the average token and cost consumption per model, producing `average_usage_report.md` as its data output.
- **`token_consume_old_version.py`**: A specialized script to parse logs from an older framework version to calculate its token/cost usage.
- **`calculate_consolidated_costs.py`**: Consolidates cost data from multiple sources into `average_costs.csv`.
- **`analyze_dimensional_improvements.py`**: Calculates the performance improvement of each model over the baseline for each quality dimension and outputs `dimensional_improvements.csv`.
- **`analyze_pipeline_runs.py`**: Analyzes a specific subset of five pipeline runs to generate a consolidated report on their mean scores, duration, and token usage.
- **`generate_pipeline_category_comparison.py`**: Generates heatmap plots that compare model performance improvements across different server categories.
- **`generate_cost_performance_report.py`**: A simpler script that generates a basic cost vs. performance scatter plot.
