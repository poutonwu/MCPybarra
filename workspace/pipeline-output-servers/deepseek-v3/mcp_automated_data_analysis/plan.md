### **MCP Tools Plan**

#### **1. `load_csv` Tool**
- **Description**: Loads a CSV file into memory for data analysis. Supports multiple datasets simultaneously.
- **Parameters**:
  - `file_path` (str): Path to the CSV file to be loaded.
  - `dataset_name` (str, optional): Unique identifier for the dataset in memory. If not provided, defaults to the filename.
- **Return Value**:
  - `dict`: A status message indicating success or failure, along with the dataset name for reference (e.g., `{"status": "success", "dataset_name": "data1"}`).

#### **2. `run_script` Tool**
- **Description**: Executes a Python script for data analysis, supporting libraries like `pandas`, `numpy`, `scipy`, `sklearn`, and `statsmodels`. Results can be saved in memory for further operations.
- **Parameters**:
  - `script` (str): The Python script to execute.
  - `input_datasets` (list of str): Names of the datasets in memory to be used as input.
  - `output_dataset` (str, optional): Name to assign to the output dataset in memory. If not provided, results are not saved.
- **Return Value**:
  - `dict`: The result of the script execution, including any computed metrics or processed data (e.g., `{"result": <script_output>, "output_dataset": "processed_data"}`).

#### **3. `explore_data` Tool**
- **Description**: Automatically analyzes the structure of a dataset, generates a data exploration plan, and performs insightful visualizations.
- **Parameters**:
  - `dataset_name` (str): Name of the dataset in memory to explore.
  - `visualization_type` (str, optional): Type of visualization to generate (e.g., "histogram", "scatterplot"). Defaults to "auto" for automatic selection.
- **Return Value**:
  - `dict`: A summary of data insights, including statistics, visualization paths (if saved), and recommendations (e.g., `{"stats": {...}, "visualizations": ["plot1.png"], "recommendations": [...]}`).

---

### **Server Overview**
The MCP server will provide an automated data exploration and analysis platform, enabling users to:
1. Load and manage multiple CSV datasets in memory.
2. Execute custom Python scripts for advanced data manipulation and statistical analysis.
3. Automatically explore datasets, generate insights, and visualize data for deeper understanding.

---

### **File to be Generated**
- **Filename**: `mcp_data_server.py`

---

### **Dependencies**
- Required Libraries:
  - `pandas` (for data manipulation)
  - `numpy` (for numerical operations)
  - `scipy` (for scientific computing)
  - `scikit-learn` (for machine learning)
  - `statsmodels` (for statistical modeling)
  - `matplotlib` (for data visualization)
  - `seaborn` (for enhanced visualizations)
  - `fastapi` (for the MCP server framework, if HTTP transport is used)
  - `mcp[cli]` (for MCP protocol support)