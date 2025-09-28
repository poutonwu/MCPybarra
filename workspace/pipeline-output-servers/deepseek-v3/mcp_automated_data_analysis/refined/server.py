import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mcp.server.fastmcp import FastMCP
from pathlib import Path
import io
import base64

# Initialize FastMCP server
mcp = FastMCP("mcp_automated_data_analysis")

# In-memory storage for datasets
datasets = {}

@mcp.tool()
def load_csv(file_path: str, dataset_name: str = None) -> dict:
    """
    Load a CSV file into memory for data analysis.

    Args:
        file_path (str): Path to the CSV file to be loaded.
        dataset_name (str, optional): Unique identifier for the dataset in memory. Defaults to the filename.

    Returns:
        dict: A status message indicating success or failure, along with the dataset name.
    """
    try:
        # Validate file path
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read CSV file
        df = pd.read_csv(file_path)
        
        # Determine dataset name
        if not dataset_name:
            dataset_name = Path(file_path).stem
        
        # Store dataset in memory
        datasets[dataset_name] = df
        
        return {"status": "success", "dataset_name": dataset_name}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def run_script(script: str, input_datasets: list, output_dataset: str = None) -> dict:
    """
    Execute a Python script for data analysis.

    Args:
        script (str): The Python script to execute.
        input_datasets (list): Names of the datasets in memory to be used as input.
        output_dataset (str, optional): Name to assign to the output dataset in memory.

    Returns:
        dict: The result of the script execution, including any computed metrics or processed data.
    """
    try:
        # Validate input datasets exist
        for name in input_datasets:
            if name not in datasets:
                raise KeyError(f"Dataset not found: {name}")
        
        # Prepare input data
        input_data = {name: datasets[name] for name in input_datasets}
        
        # Execute script with restricted globals
        local_vars = {
            "input_data": input_data,
            "pd": pd,
            "np": np,
            "plt": plt,
            "sns": sns
        }
        
        # Create a clean namespace for execution
        exec(script, {"__builtins__": None}, local_vars)
        
        # Store output if specified
        result = local_vars.get("result")
        if output_dataset and result is not None:
            if isinstance(result, pd.DataFrame):
                datasets[output_dataset] = result
                return {"status": "success", "result": "DataFrame stored", "output_dataset": output_dataset}
            return {"status": "error", "message": "Result must be a pandas DataFrame"}
        return {"result": result if result is not None else "No result returned"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def explore_data(dataset_name: str, visualization_type: str = "auto") -> dict:
    """
    Analyze the structure of a dataset and generate insights.

    Args:
        dataset_name (str): Name of the dataset in memory to explore.
        visualization_type (str, optional): Type of visualization to generate. Defaults to "auto".

    Returns:
        dict: A summary of data insights, including statistics and visualizations.
    """
    try:
        if dataset_name not in datasets:
            raise KeyError(f"Dataset not found: {dataset_name}")
            
        df = datasets[dataset_name]
        
        # Generate statistics
        stats = {
            "columns": list(df.columns),
            "shape": df.shape,
            "describe": df.describe().to_dict(),
            "null_values": df.isnull().sum().to_dict(),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
        
        # Generate visualizations
        visualizations = []
        if visualization_type == "auto":
            # Auto-generate visualizations based on data type
            for col in df.select_dtypes(include=['float64', 'int64']).columns:
                fig = plt.figure()
                sns.histplot(df[col])
                plt.title(f"Histogram of {col}")
                
                # Convert plot to base64 for JSON serialization
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                buf.seek(0)
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                visualizations.append({col: img_base64})
        
        return {"stats": stats, "visualizations": visualizations}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()