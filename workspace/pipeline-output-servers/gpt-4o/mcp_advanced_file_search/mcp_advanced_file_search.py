import os
import sys
import ctypes
import json
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("advanced_file_search")

# Load everything.dll dynamically using ctypes
try:
    everything_dll = ctypes.WinDLL(r"E:\Everything\dll\Everything64.dll")
except OSError:
    raise RuntimeError("Failed to load everything.dll. Ensure the DLL is in the system PATH or the current directory.")

# Define the tools
@mcp.tool()
def search_files(query: str, case_sensitive: bool = False, whole_word_match: bool = False,
                 regex: bool = False, sort_by: str = "name", limit: int = 100) -> str:
    """
    Searches for files and folders on the Windows system using the everything.dll library.

    Args:
        query (str): The search query string.
        case_sensitive (bool, optional): Whether the search should be case-sensitive. Defaults to False.
        whole_word_match (bool, optional): Whether to match whole words only. Defaults to False.
        regex (bool, optional): Whether to enable regular expression matching. Defaults to False.
        sort_by (str, optional): The sorting criterion for the results. Options include 'name', 'size',
                                 'date_created', 'date_modified'. Defaults to 'name'.
        limit (int, optional): The maximum number of results to return. Defaults to 100.

    Returns:
        str: A JSON string containing a list of dictionaries, where each dictionary represents a file or folder.

    Example:
        search_files(query="*.txt", case_sensitive=False, whole_word_match=False, regex=False, sort_by="name", limit=10)
    """
    try:
        # Placeholder for actual ctypes calls to everything.dll
        # Example: everything_dll.Everything_SetSearchW(query)
        # Ensure to use proper ctypes bindings for all DLL functions

        # Mock response for demonstration purposes
        results = [
            {
                "name": "example.txt",
                "path": "C:\\Path\\To\\example.txt",
                "size": 1024,
                "date_created": "2023-01-01",
                "date_modified": "2023-01-02",
                "attributes": ["readonly"]
            }
        ]

        # Return the results as a JSON string, limited to the specified number
        return json.dumps(results[:limit])
    except Exception as e:
        # Return an error message in JSON format if an exception occurs
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_file_details(file_path: str) -> str:
    """
    Retrieves detailed information about a specific file or folder.

    Args:
        file_path (str): The full path of the file or folder for which details are to be retrieved.

    Returns:
        str: A JSON string containing details of the file or folder.

    Example:
        get_file_details(file_path="C:\\Path\\To\\example.txt")
    """
    try:
        # Placeholder for actual ctypes calls to everything.dll
        # Example: everything_dll.Everything_GetResultFullPathNameW(index, buffer, buffer_size)
        # Ensure to use proper ctypes bindings for all DLL functions

        # Mock response for demonstration purposes
        file_details = {
            "name": "example.txt",
            "path": "C:\\Path\\To\\example.txt",
            "size": 1024,
            "date_created": "2023-01-01",
            "date_modified": "2023-01-02",
            "attributes": ["readonly"]
        }

        # Return the file details as a JSON string
        return json.dumps(file_details)
    except Exception as e:
        # Return an error message in JSON format if an exception occurs
        return json.dumps({"error": str(e)})

# Start the MCP server
if __name__ == "__main__":
    # Reconfigure stdout to handle UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8')
    # Run the MCP server
    mcp.run()