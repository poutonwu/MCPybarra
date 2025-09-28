# mcp_everything_file_searcher

A MCP server that provides file search capabilities using the Everything engine.

## Overview

The `mcp_everything_file_searcher` server enables fast and flexible file and folder searches across the system using the Everything search engine. It supports advanced queries including wildcards, regular expressions, path filters, size constraints, and date-based filtering. Results include metadata such as name, full path, size, and timestamps.

## Installation

1. Ensure Python 3.10 or higher is installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure the Everything SDK DLL (Everything32.dll or Everything64.dll) is placed in the same directory as the script or executable, matching your Python interpreter architecture.

## Running the Server

To run the server directly for testing:

```bash
python mcp_everything_server.py
```

Ensure the Everything service is running on the host machine for successful query execution.

## Available Tools

### `search_everything`

Performs a high-speed search for files and folders using the Everything engine.

#### Description

This tool allows for fine-grained control over file and folder searches with support for case sensitivity, whole-word matching, regular expressions, sorting, and pagination. The query syntax supports wildcards, paths, size ranges, and date filters.

#### Parameters

- `query` (str): The search string. Can be a simple keyword or use Everything's advanced syntax (e.g., `"C:\\Program Files\\" *.exe size:>10mb dm:lastmonth`).
- `is_match_case` (bool, optional): If True, the search will be case-sensitive. Defaults to False.
- `is_match_whole_word` (bool, optional): If True, the search will match whole words only. Defaults to False.
- `is_regex` (bool, optional): If True, the query string will be interpreted as a regular expression. Defaults to False.
- `max_results` (int, optional): The maximum number of results to return. Defaults to 100.
- `offset` (int, optional): The starting offset for the results, used for pagination. Defaults to 0.
- `sort_by` (str, optional): Specifies the sort order. Valid values are:
  - "NAME_ASCENDING"
  - "NAME_DESCENDING"
  - "PATH_ASCENDING"
  - "PATH_DESCENDING"
  - "SIZE_ASCENDING"
  - "SIZE_DESCENDING"
  - "DATE_MODIFIED_ASCENDING"
  - "DATE_MODIFIED_DESCENDING"
  - "DATE_CREATED_ASCENDING"
  - "DATE_CREATED_DESCENDING"

Defaults to "NAME_ASCENDING".

#### Returns

A JSON-formatted string representing a list of dictionaries, where each dictionary contains:

- `type` (str): "FILE" or "FOLDER".
- `name` (str): The name of the file or folder.
- `path` (str): The full path to the file or folder.
- `size_bytes` (int): The size of the file in bytes (0 for folders).
- `date_created` (str): The creation timestamp in ISO 8601 format.
- `date_modified` (str): The last modified timestamp in ISO 8601 format.

Returns an empty list if no results are found.

#### Raises

- `ConnectionError`: If the Everything.dll cannot be loaded or the Everything service is not running.
- `ValueError`: If an invalid value for `sort_by` or an empty `query` is provided.