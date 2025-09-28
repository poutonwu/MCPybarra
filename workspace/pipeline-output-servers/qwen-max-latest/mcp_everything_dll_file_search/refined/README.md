# mcp_everything_dll_file_search

## Overview

This MCP server provides advanced file search capabilities on Windows systems using the Everything API. It allows searching for files and folders with complex filters including size, modification date, attributes, and regular expressions.

The server exposes a single tool for performing comprehensive file system searches with detailed filtering options, making it ideal for applications that need to quickly locate files based on multiple criteria.

## Installation

1. Install Python 3.10 or later
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Ensure the `requirements.txt` file includes:
```
mcp[cli]
```

## Running the Server

To run the server, use the following command:
```bash
python everything_search_server.py
```

Before running, make sure to set the `EVERYTHING_DLL_PATH` environment variable to point to the location of `everything.dll`:
```bash
set EVERYTHING_DLL_PATH=D:\devEnvironment\Everything\dll\Everything64.dll
```

## Available Tools

### `perform_everything_search`

Performs an advanced file search on Windows using the Everything API with various filtering options.

**Description:**  
Searches the file system for files and folders matching the specified criteria. Supports filtering by name, path, size, modification date, and file attributes.

**Parameters:**
- `query` (str): The search query including keywords, wildcards, or regex patterns.
- `path` (str, optional): The root directory path to start the search from.
- `size_min` (int, optional): Minimum file size in bytes.
- `size_max` (int, optional): Maximum file size in bytes.
- `date_modified_start` (str, optional): Start date for filtering by modification time (YYYY-MM-DD).
- `date_modified_end` (str, optional): End date for filtering by modification time (YYYY-MM-DD).
- `attributes` (list of str, optional): List of file attributes to filter by (e.g., 'readonly', 'hidden').
- `sort_by` (str, optional): Sorting criteria ('name', 'size', 'date').
- `case_sensitive` (bool, optional): If True, the search is case-sensitive.
- `whole_word` (bool, optional): If True, only whole word matches are returned.
- `regex` (bool, optional): If True, the query is treated as a regular expression.

**Returns:**  
A JSON string containing a list of dictionaries, where each dictionary contains detailed information about a found file or folder.

**Example:**
```python
perform_everything_search(
    query="*.txt",
    path="C:\\Users\\Public",
    size_min=1048576,
    date_modified_start="2023-01-01"
)
```