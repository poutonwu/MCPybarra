# mcp_data_explorer_analyzer

## Overview

The `mcp_data_explorer_analyzer` is an MCP (Model Context Protocol) server that enables seamless integration of data analysis tools with large language models (LLMs). It allows users to:

- Load CSV datasets into memory.
- Run custom Python scripts for data processing and transformation.
- Automatically explore datasets, generate statistical summaries, and create visualizations.

This server provides a flexible interface for performing in-memory data manipulation and exploratory data analysis via LLMs using the MCP protocol.

## Installation

To install the required dependencies, ensure you have Python 3.10+ installed and run:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
pandas
numpy
scipy
scikit-learn
matplotlib
seaborn
```

## Running the Server

To start the server, execute the Python script from the command line:

```bash
python mcp_data_explorer_analyzer.py
```

Ensure that your script file is named `mcp_data_explorer_analyzer.py` or adjust the command accordingly.

## Available Tools

The server provides the following MCP tools:

### 1. `load_csv`

**Description:**  
Loads a CSV file into memory as a pandas DataFrame and assigns it a unique identifier for future reference.

**Arguments:**
- `file_path` (str): Path to the CSV file.
- `dataset_id` (str): Unique identifier for the dataset.

**Returns:**  
A confirmation message indicating successful loading of the dataset.

**Example:**
```python
load_csv(file_path="data/sample.csv", dataset_id="dataset1")
```

---

### 2. `run_script`

**Description:**  
Executes a user-provided Python script using one or more preloaded datasets. The result is stored under a new dataset ID.

**Arguments:**
- `script_code` (str): Python code to execute.
- `input_datasets` (list of str): List of dataset IDs used in the script.
- `output_dataset_id` (str): Identifier for the resulting dataset.

**Returns:**  
A confirmation message indicating successful execution and storage of the output dataset.

**Example:**
```python
run_script(script_code="output = df['dataset1'].copy(); output['new_column'] = output.iloc[:, 0] * 2", 
           input_datasets=["dataset1"], output_dataset_id="processed_dataset")
```

---

### 3. `explore_data`

**Description:**  
Automatically analyzes the structure of one or more datasets, generates descriptive statistics, and creates visualizations (e.g., histograms).

**Arguments:**
- `dataset_ids` (list of str): List of dataset IDs to analyze.
- `exploration_id` (str): Identifier for storing the exploration results.

**Returns:**  
A summary of statistical insights and paths to generated visualization files.

**Example:**
```python
explore_data(dataset_ids=["dataset1", "dataset2"], exploration_id="exploration_results")
```

---