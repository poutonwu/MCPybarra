# mcp_automated_data_explorer

## Overview
The `mcp_automated_data_explorer` is an MCP server that enables users to load, analyze, and explore datasets using Python-based tools. It provides functionality for loading CSV files into memory, executing custom scripts on loaded data, and generating comprehensive exploratory data analysis (EDA) reports.

This server is ideal for integrating data analysis capabilities into LLM workflows via the Model Context Protocol (MCP), allowing models to interact with real-world datasets programmatically.

## Installation
To install the required dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the MCP SDK:
   ```bash
   pip install mcp[cli]
   ```
3. Install the project dependencies from a `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

Your `requirements.txt` should include:
```
pandas
numpy
scipy
scikit-learn
statsmodels
ydata-profiling
mcp[cli]
```

## Running the Server
To start the server, run the Python script from the command line:
```bash
python mcp_automated_data_explorer.py
```

Ensure the script file is named accordingly and located in your working directory or provide the full path.

## Available Tools

### 1. `load_csv(dataset_name: str, file_path: str)`
Loads a dataset from a local CSV file into memory under a specified name. Returns metadata including number of rows and columns.

**Example Usage:**
```python
load_csv(dataset_name="titanic", file_path="data/titanic.csv")
```

### 2. `run_script(script_content: str)`
Executes a provided Python script string with access to pre-imported libraries and previously loaded datasets via the `DATASETS` dictionary. Captures and returns standard output and error messages.

**Example Usage:**
```python
run_script("df = DATASETS['titanic']; print(df.describe())")
```

### 3. `explore_data(dataset_name: str)`
Generates a detailed exploratory data analysis (EDA) report using the `ydata_profiling` library for a specified dataset already loaded into memory.

**Example Usage:**
```python
explore_data(dataset_name="titanic")
```