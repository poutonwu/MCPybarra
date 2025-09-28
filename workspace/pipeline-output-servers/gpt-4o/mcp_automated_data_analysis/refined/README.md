# mcp_automated_data_analysis

## Overview

The `mcp_automated_data_analysis` server provides a set of tools for loading, analyzing, and exploring datasets using the Model Context Protocol (MCP). It allows users to load CSV or ZIP files into memory, run custom Python scripts on the data, and generate automated profiling reports.

## Installation

Before running the server, ensure you have Python 3.10+ installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt** should include:

```
mcp[cli]
pandas
numpy
ydata-profiling
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_automated_data_analysis.py
```

By default, the server uses standard I/O for communication. You can customize the transport method by modifying the `mcp.run()` call in the script if needed.

## Available Tools

The server exposes the following MCP tools:

### `load_csv`

**Description:** Loads a CSV file (or CSV inside a ZIP file) into memory under a user-defined dataset name.

**Arguments:**
- `file_path`: Path to the `.csv` or `.zip` file.
- `dataset_name`: A unique identifier name for the dataset in memory.

**Example:**
```python
load_csv("data/sales.csv", "sales_data")
```

---

### `run_script`

**Description:** Executes a Python script dynamically using a previously loaded dataset.

**Arguments:**
- `script_code`: The Python code as a string to execute.
- `dataset_name`: Name of the dataset already loaded in memory to use in the script.

**Example:**
```python
run_script("print(dataset.head())", "sales_data")
```

---

### `explore_data`

**Description:** Generates an automated profile report of the specified dataset using `ydata_profiling`.

**Arguments:**
- `dataset_name`: Name of the dataset to analyze.

**Output:**
- Saves a detailed HTML profile report named `{dataset_name}_profile_report.html`.

**Example:**
```python
explore_data("sales_data")
```