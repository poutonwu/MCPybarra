# Performance vs. Cost Analysis Report

This report provides a multi-dimensional evaluation of models based on their performance scores, project costs, and token consumption.

## Data Summary

| Model          |   Average Score |   Average Cost (USD) |   Average Tokens |
|:---------------|----------------:|---------------------:|-----------------:|
| deepseek-v3    |           78.95 |               0.018  |            83686 |
| gemini-2.5-pro |           84.29 |               0.133  |           119095 |
| gpt-4o         |           78.23 |               0.1404 |           133968 |
| qwen-max       |           79.66 |               0.0312 |           141956 |
| qwen-plus      |           79.46 |               0.0231 |           165582 |

## Chart Interpretation

The following bubble chart visualizes the analysis, where:
- **X-axis**: Average Project Cost (USD) - Further to the left is better.
- **Y-axis**: Average Performance Score - Higher is better.
- **Bubble Size**: Average Token Consumption - Smaller is better.

![Performance vs. Cost Analysis](performance_cost_analysis.png)

### Quadrant Analysis

- **Top-Left (Star Zone)**: High performance at a low cost. This is the ideal quadrant.
- **Top-Right (Performance Zone)**: High performance at a high cost. Models are effective but expensive.
- **Bottom-Left (Economic Zone)**: Low performance at a low cost. Suitable for budget-sensitive applications where performance is not critical.
- **Bottom-Right (Warning Zone)**: Low performance at a high cost. This is the least desirable quadrant.
