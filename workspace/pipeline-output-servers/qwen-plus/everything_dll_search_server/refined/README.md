# Everything DLL Search Server

## Overview

The Everything DLL Search Server is a powerful tool designed to provide fast and efficient file searching capabilities on Windows systems. It leverages the `everything.dll` from [Everything](https://www.voidtools.com/) to perform searches with advanced filtering options such as case sensitivity, regex matching, and whole word matching.

This server is built using the FastMCP framework and exposes an API endpoint for executing file searches based on user-provided query parameters.

## Installation

### Prerequisites
- **Python 3.x**
- **FastMCP** (`pip install fastmcp`)
- **`everything.dll`**: Download and install [Everything by Voidtools](https://www.voidtools.com/). Ensure that the DLL path is correctly set in your environment variables or specify it manually.

### Steps
1. Clone this repository or download the source code.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set the environment variable `EVERYTHING_DLL_PATH` to point to your `Everything64.dll` location (or modify the path in the code directly).
   Example:
   ```bash
   set EVERYTHING_DLL_PATH=D:\devEnvironment\Everything\dll\Everything64.dll
   ```
4. Run the server (details below).

## Usage

To start the server, execute the following command:
```bash
python everything_dll_search_server.py
```

Once running, you can send HTTP requests to the server's endpoint to perform file searches.

## Available Tools

### `search_files`

The main functionality of this server is exposed through the `search_files` tool. This function allows users to search for files using various filters and return results in JSON format.

#### Parameters
- `query` (str): The search string (required, non-empty).
- `sort_by` (str): Sorting criteria ('name', 'path', 'size', 'date'). Defaults to 'name'.
- `max_results` (int): Maximum number of results to return. Defaults to 100.
- `case_sensitive` (bool): Whether the search should be case-sensitive. Defaults to False.
- `match_whole_word` (bool): Whether to match whole words only. Defaults to False.
- `use_regex` (bool): Whether to interpret the query as a regular expression. Defaults to False.

#### Returns
A JSON-formatted string containing the search results or an error message.

#### Example Request
```json
POST /execute/search_files
Content-Type: application/json

{
    "query": "file.txt",
    "sort_by": "name",
    "max_results": 10,
    "case_sensitive": false,
    "match_whole_word": true,
    "use_regex": false
}
```

#### Example Response
```json
[
    {
        "filename": "file.txt",
        "full_path": "D:\\tmp\\file.txt",
        "size": 1024
    }
]
```

## Example Requests

### Basic Search
Search for files named `file.txt`, sorted by name:
```json
POST /execute/search_files
Content-Type: application/json

{
    "query": "file.txt",
    "sort_by": "name"
}
```

### Advanced Search
Perform a case-insensitive regex search for files containing `log` in their names, limited to 50 results:
```json
POST /execute/search_files
Content-Type: application/json

{
    "query": "log",
    "sort_by": "date",
    "max_results": 50,
    "case_sensitive": false,
    "use_regex": true
}
```

## Error Handling

If invalid parameters are provided or if the search fails, the server will return a JSON object with an `error` key describing the issue.

Example:
```json
{
    "error": "An error occurred: Invalid 'sort_by' value 'invalid_value'. Must be one of ['name', 'path', 'size', 'date']."
}
```

---

For any issues, questions, or feature requests, please open an issue in the repository.