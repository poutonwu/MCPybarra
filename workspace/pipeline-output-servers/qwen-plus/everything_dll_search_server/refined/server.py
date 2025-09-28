import ctypes
import os
import sys
import json
from typing import List, Dict
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("everything_dll_search_server")

# Load everything.dll using ctypes
try:
    everything_dll_path = os.environ.get('EVERYTHING_DLL_PATH', r'D:/devEnvironment/Everything/dll/Everything64.dll')
    everything_dll = ctypes.CDLL(everything_dll_path)
except OSError as e:
    raise ImportError(f"Failed to load everything.dll: {e}")

# Define constants from EverythingSDK documentation
EVERYTHING_OK = 0
EVERYTHING_ERROR_INVALIDCALL = 1
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_SIZE = 0x00000004
EVERYTHING_SORT_NAME_ASCENDING = 1
EVERYTHING_SORT_PATH_ASCENDING = 2
EVERYTHING_SORT_SIZE_ASCENDING = 3
EVERYTHING_SORT_DATE_MODIFIED_ASCENDING = 4

# Map sort parameters to SDK constants
SORT_MAP = {
    "name": EVERYTHING_SORT_NAME_ASCENDING,
    "path": EVERYTHING_SORT_PATH_ASCENDING,
    "size": EVERYTHING_SORT_SIZE_ASCENDING,
    "date": EVERYTHING_SORT_DATE_MODIFIED_ASCENDING
}

def validate_search_parameters(query: str, sort_by: str, max_results: int):
    """
    Validate search parameters for the 'search_files' tool.

    Args:
        query: The search query string (non-empty).
        sort_by: Sorting criteria (must be one of ['name', 'path', 'size', 'date']).
        max_results: Maximum number of results to return (positive integer).

    Raises:
        ValueError: If any parameter is invalid.
    """
    if not query or not isinstance(query, str):
        raise ValueError("'query' must be a non-empty string.")
    if sort_by not in SORT_MAP:
        raise ValueError(f"Invalid 'sort_by' value '{sort_by}'. Must be one of {list(SORT_MAP.keys())}.")
    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("'max_results' must be a positive integer.")

@mcp.tool()
def search_files(
    query: str,
    sort_by: str = "name",
    max_results: int = 100,
    case_sensitive: bool = False,
    match_whole_word: bool = False,
    use_regex: bool = False
) -> str:
    """
    Executes a file search on the local Windows system using the loaded `everything.dll` with the specified query parameters.

    Args:
        query: The search query string (non-empty).
        sort_by: Sorting criteria ('name', 'path', 'size', 'date'). Defaults to 'name'.
        max_results: Maximum number of results to return (positive integer). Defaults to 100.
        case_sensitive: Whether the search should be case-sensitive. Defaults to False.
        match_whole_word: Whether to match whole words only. Defaults to False.
        use_regex: Whether to interpret the query as a regular expression. Defaults to False.

    Returns:
        A JSON-formatted string containing the search results or an error message.

    Example:
        >>> search_files(query="file.txt", sort_by="name", max_results=10)
        '[{"filename": "file.txt", "full_path": "D:\\tmp\\file.txt", "size": 1024}]'

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: If the Everything query fails.
    """
    try:
        # Validate search parameters
        validate_search_parameters(query, sort_by, max_results)

        # Set search parameters
        everything_dll.Everything_SetSearchW(query)
        request_flags = EVERYTHING_REQUEST_FILE_NAME | EVERYTHING_REQUEST_PATH | EVERYTHING_REQUEST_SIZE

        if case_sensitive:
            request_flags |= 0x00010000  # EVERYTHING_CASE_SENSITIVE
        if match_whole_word:
            request_flags |= 0x00020000  # EVERYTHING_MATCH_WHOLE_WORD
        if use_regex:
            request_flags |= 0x00040000  # EVERYTHING_MATCH_REGEX

        everything_dll.Everything_SetRequestFlags(request_flags)
        everything_dll.Everything_SetSort(SORT_MAP[sort_by])

        # Execute the query
        if not everything_dll.Everything_QueryW(True):
            error_code = everything_dll.Everything_GetLastError()
            raise RuntimeError(f"Everything Query failed with error code {error_code}.")

        # Retrieve results
        num_results = min(everything_dll.Everything_GetNumResults(), max_results)
        results = []

        for i in range(num_results):
            filename_buffer = ctypes.create_unicode_buffer(260)
            path_buffer = ctypes.create_unicode_buffer(260)

            everything_dll.Everything_GetResultFullPathNameW(i, path_buffer, 260)
            everything_dll.Everything_GetResultFileNameW(i, filename_buffer, 260)

            file_size = everything_dll.Everything_GetResultSize(i)

            result = {
                "filename": filename_buffer.value,
                "full_path": path_buffer.value,
                "size": file_size
            }
            results.append(result)

        return json.dumps(results, ensure_ascii=False)

    except Exception as e:
        # Ensure all exceptions are caught and returned as JSON strings
        error_message = f"An error occurred: {str(e)}"
        return json.dumps({"error": error_message}, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()