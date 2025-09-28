# mcp_everything_file_search

A high-performance file search MCP server for Windows, leveraging the Everything64.dll library to enable lightning-fast file and folder searches with support for advanced query syntax.

## Overview

This server provides an MCP interface to perform fast file system searches on Windows using the Everything64.dll library. It supports a wide range of search operations including wildcards, regular expressions, size filters, modification time constraints, and more.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure `Everything64.dll` is available at the specified path (`D:\devEnvironment\Everything\dll\Everything64.dll`) or update the `EVERYTHING_DLL` constant in the code to reflect the correct location.

## Running the Server

To start the server, run the following command from your terminal:

```bash
python mcp_everything_file_search.py
```

Ensure that `Everything64.dll` is accessible at the configured path before starting the server.

## Available Tools

### `search_files`

Performs a high-speed search of files and folders on Windows using the everything.dll library. Supports multiple search syntaxes (wildcards, regex, path, size, time, attributes) and advanced features.

#### Parameters:
- `query` (str): The search query string (e.g., `*.txt`, `size:>1MB`, `modified:today`).
- `limit` (int, optional): Maximum number of results to return (default: 100).
- `case_sensitive` (bool, optional): If True, performs case-sensitive matching (default: False).
- `full_word` (bool, optional): If True, matches only full words (default: False).
- `regex` (bool, optional): If True, treats the query as a regular expression (default: False).
- `sort_by` (str, optional): Specifies sorting criteria (e.g., "name", "size", "modified").

#### Returns:
A list of dictionaries containing:
- `path` (str): Full file/folder path.
- `size` (int): File size in bytes.
- `modified` (str): Last modified timestamp.
- `attributes` (dict): File attributes (readonly, hidden, system, archive).

#### Raises:
- Exception if the search operation fails or the DLL is not loaded.