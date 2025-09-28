import os
import pandas as pd
import numpy as np
from mcp.server.fastmcp import FastMCP
from ydata_profiling import ProfileReport
import json

data_storage = {}

# Initialize the MCP server
mcp = FastMCP("mcp_automated_data_analysis")

@mcp.tool()
def load_csv(file_path: str, dataset_name: str) -> str:
    """
    Load a CSV file into memory and store it with a user-defined dataset name.

    Args:
        file_path (str): The path to the CSV file to be loaded.
        dataset_name (str): A unique name to associate with the dataset.

    Returns:
        str: JSON-formatted string indicating success or error.

    Example:
        load_csv("data/sales.csv", "sales_data")
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.lower().endswith((".csv", ".zip")):
            raise ValueError("Only .csv or .zip files are supported.")

        if file_path.lower().endswith(".zip"):
            try:
                # Explicitly specify compression for zip files
                data_storage[dataset_name] = pd.read_csv(file_path, compression='zip')
            except Exception as e:
                raise ValueError(f"Failed to extract CSV from zip: {e}")
        else:
            data_storage[dataset_name] = pd.read_csv(file_path)

        return json.dumps({
            "status": "success",
            "message": f"Dataset '{dataset_name}' loaded successfully.",
            "outputs": {
                "dataset_name": dataset_name
            }
        })
    except Exception as e:
        return json.dumps({
            "status": "error", 
            "message": str(e),
            "outputs": {}
        })

@mcp.tool()
def run_script(script_code: str, dataset_name: str) -> str:
    """
    Execute a Python script dynamically using a dataset loaded in memory.

    Args:
        script_code (str): The Python code to execute as a string.
        dataset_name (str): The name of the dataset to pass to the script.

    Returns:
        str: JSON-formatted string indicating success or error with execution output.

    Example:
        run_script("print(dataset.head())", "sales_data")
    """
    try:
        if dataset_name not in data_storage:
            raise ValueError(f"Dataset '{dataset_name}' not found.")

        dataset = data_storage[dataset_name]
        local_scope = {"dataset": dataset, "pd": pd, "np": np}
        exec(script_code, {}, local_scope)

        return json.dumps({
            "status": "success", 
            "output": "Script executed successfully.",
            "outputs": {
                "dataset_name": dataset_name
            }
        })
    except Exception as e:
        return json.dumps({
            "status": "error", 
            "message": str(e),
            "outputs": {}
        })

@mcp.tool()
def explore_data(dataset_name: str) -> str:
    """
    Generate an automated profile report for a dataset in memory.

    Args:
        dataset_name (str): The name of the dataset to explore.

    Returns:
        str: JSON-formatted string with summary insights and the path to the generated report.

    Example:
        explore_data("sales_data")
    """
    try:
        if dataset_name not in data_storage:
            raise ValueError(f"Dataset '{dataset_name}' not found.")

        dataset = data_storage[dataset_name]
        profile = ProfileReport(dataset, title=f"Profile Report for {dataset_name}", html={"style": {"full_width": True}})
        report_path = f"{dataset_name}_profile_report.html"
        profile.to_file(report_path)

        return json.dumps({
            "status": "success", 
            "summary": f"Profile report generated at {report_path}", 
            "report_path": report_path,
            "outputs": {
                "dataset_name": dataset_name
            }
        })
    except Exception as e:
        return json.dumps({
            "status": "error", 
            "message": str(e),
            "outputs": {}
        })

if __name__ == "__main__":
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    mcp.run()