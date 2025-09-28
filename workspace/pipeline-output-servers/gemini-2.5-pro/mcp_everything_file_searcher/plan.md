# MCP Server Implementation Plan: Everything File Search

## Server Overview

This document outlines the implementation plan for an MCP server designed for high-speed local file and folder searching on Windows. The server will leverage the "Everything" search engine by dynamically loading `everything.dll` using Python's `ctypes` library. It will provide a single, powerful tool that exposes Everything's rich search capabilities, including advanced syntax, result filtering, and sorting, to the MCP client.

## File to be Generated

-   `mcp_everything_server.py`

## Dependencies

-   `mcp`
-   The `everything.dll` file must be present on the system where the server is run. The plan will assume it's in a location accessible by the Python script (e.g., same directory or in the system's PATH).

## MCP Tools Plan

### Tool 1: `search_everything`

-   **Function Name**: `search_everything`
-   **Description**: Performs a high-speed search for files and folders using the Everything engine. It supports a wide range of search syntaxes like wildcards, regular expressions, paths, sizes, and dates. The tool allows for fine-grained control over the search with options for case sensitivity, matching, sorting, and result limits.
-   **Parameters**:
    -   `query` (str): The search string. This can be a simple keyword, or use Everything's advanced syntax (e.g., `"C:\Program Files\" *.exe size:>10mb dm:lastmonth`).
    -   `is_match_case` (bool, optional, default=False): If True, the search will be case-sensitive.
    -   `is_match_whole_word` (bool, optional, default=False): If True, the search will match whole words only.
    -   `is_regex` (bool, optional, default=False): If True, the `query` string will be interpreted as a regular expression.
    -   `max_results` (int, optional, default=100): The maximum number of results to return.
    -   `offset` (int, optional, default=0): The starting offset for the results, used for pagination.
    -   `sort_by` (str, optional, default="NAME_ASCENDING"): Specifies the sort order for the results. Valid values are:
        -   `"NAME_ASCENDING"`
        -   `"NAME_DESCENDING"`
        -   `"PATH_ASCENDING"`
        -   `"PATH_DESCENDING"`
        -   `"SIZE_ASCENDING"`
        -   `"SIZE_DESCENDING"`
        -   `"DATE_MODIFIED_ASCENDING"`
        -   `"DATE_MODIFIED_DESCENDING"`
        -   `"DATE_CREATED_ASCENDING"`
        -   `"DATE_CREATED_DESCENDING"`
-   **Return Value**:
    -   **Type**: `list[dict]`
    -   **Description**: A list of dictionaries, where each dictionary represents a found file or folder. If no results are found, an empty list is returned.
    -   **Dictionary Structure**:
        -   `type` (str): The type of the result, either `"FILE"` or `"FOLDER"`.
        -   `name` (str): The name of the file or folder.
        -   `path` (str): The full path to the file or folder.
        -   `size_bytes` (int): The size of the file in bytes (0 for folders).
        -   `date_modified` (str): The last modified timestamp in ISO 8601 format (e.g., `"2023-10-27T10:30:00Z"`).
        -   `date_created` (str): The creation timestamp in ISO 8601 format.