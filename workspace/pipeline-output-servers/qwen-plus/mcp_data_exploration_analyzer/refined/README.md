# mcp_data_exploration_analyzer

A Model Context Protocol (MCP) server for data exploration and analysis, enabling users to load datasets, execute custom scripts, generate exploration plans, and visualize data insights.

---

## Overview

The `mcp_data_exploration_analyzer` server provides a powerful interface for analyzing structured data using Python libraries such as pandas, NumPy, scikit-learn, statsmodels, and matplotlib. It supports the following core capabilities:

- Load CSV files into memory
- Run custom Python scripts on loaded datasets
- Automatically generate data exploration plans with statistical summaries and visualization suggestions
- Execute visualizations based on generated plans

This server is ideal for integrating into LLM workflows that require exploratory data analysis (EDA), preprocessing, or data visualization.

---

## Installation

1. Ensure you have Python 3.10+ installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
httpx
pandas
numpy
statsmodels
scikit-learn
matplotlib
```

---

## Running the Server

To start the MCP server, run the Python script from the command line:

```bash
python mcp_data_exploration_analyzer.py
```

By default, it uses the `stdio` transport protocol. You can change this by modifying the `mcp.run()` call in the script.

---

## Available Tools

Below are the available tools registered via `@mcp.tool()` along with their descriptions and usage:

### 1. `load_csv`

**Description:** Loads a CSV file into memory as a named dataset for further processing.

**Args:**
- `file_path`: Path to the CSV file (required).
- `dataset_name`: Optional name to assign to the dataset; defaults to the filename.

**Returns:** JSON status indicating success or error, including the dataset name.

**Example:**
```python
load_csv(file_path="data.csv", dataset_name="my_dataset")
```

---

### 2. `run_script`

**Description:** Executes a user-provided Python script using the currently loaded dataset. The script can use pandas, numpy, and other supported libraries. Optionally returns a new processed dataset.

**Args:**
- `script_code`: Python code string to execute (required).
- `dataset_name`: Name of the dataset to use (required).

**Returns:** JSON result containing output logs and optionally a new dataset name if a DataFrame was saved as `result_df`.

**Example:**
```python
run_script(script_code="df.describe()", dataset_name="my_dataset")
```

---

### 3. `generate_exploration_plan`

**Description:** Analyzes the current dataset and generates an exploration plan with statistical summaries and visualization suggestions.

**Args:**
- `dataset_name`: Name of the dataset to analyze (required).

**Returns:** JSON object containing detailed analysis and visualization suggestions.

**Example:**
```python
generate_exploration_plan(dataset_name="my_dataset")
```

---

### 4. `execute_visualization`

**Description:** Executes visualizations based on a previously generated exploration plan.

**Args:**
- `plan_id`: ID of the exploration plan to visualize (required).

**Returns:** JSON array of generated charts, each containing a Base64-encoded PNG image or an error message.

**Example:**
```python
execute_visualization(plan_id="exploration_plan_0001")
```

---