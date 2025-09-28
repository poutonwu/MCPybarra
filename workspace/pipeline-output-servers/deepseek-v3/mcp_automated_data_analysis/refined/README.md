# mcp_automated_data_analysis

## Overview
The `mcp_automated_data_analysis` server provides an interface for automated data analysis using the Model Context Protocol (MCP). It allows users to load datasets, execute custom Python scripts for analysis, and explore data through descriptive statistics and visualizations.

## Installation
To install the required dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the MCP SDK and other dependencies:
   ```bash
   pip install mcp[cli] pandas numpy matplotlib seaborn
   ```

Make sure your project includes a `requirements.txt` file listing all necessary packages.

## Running the Server
To run the server, use the following command:
```bash
python path/to/your/server_script.py
```

Replace `path/to/your/server_script.py` with the actual path to the Python script containing this MCP server implementation.

## Available Tools

### `load_csv`
**Description:** Loads a CSV file into memory for data analysis.

**Arguments:**
- `file_path`: Path to the CSV file to be loaded (required).
- `dataset_name`: Optional unique identifier for the dataset in memory. Defaults to the filename stem.

**Returns:**
- A status message indicating success or failure, along with the dataset name if successful.

---

### `run_script`
**Description:** Executes a Python script for data analysis using one or more input datasets. Optionally stores the result as a new dataset.

**Arguments:**
- `script`: The Python script to execute (as a string) (required).
- `input_datasets`: List of dataset names already loaded in memory to be used as input (required).
- `output_dataset`: Optional name to assign to the output dataset if the script returns a DataFrame.

**Returns:**
- The result of the script execution, including any computed metrics or processed data.
- If an output dataset is specified and the result is a DataFrame, it will be stored in memory.

---

### `explore_data`
**Description:** Analyzes the structure of a dataset and generates basic insights, including descriptive statistics and histograms for numeric columns.

**Arguments:**
- `dataset_name`: Name of the dataset in memory to explore (required).
- `visualization_type`: Type of visualization to generate. Currently only supports `"auto"` which generates histograms for numeric columns (optional).

**Returns:**
- A dictionary containing:
  - **Statistics**: Column names, shape, descriptive statistics, null value counts, and data types.
  - **Visualizations**: Base64-encoded PNG images of histograms for numeric columns (if enabled).