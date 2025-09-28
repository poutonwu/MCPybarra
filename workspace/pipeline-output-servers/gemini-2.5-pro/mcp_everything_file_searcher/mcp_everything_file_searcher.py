import sys
import ctypes
import os
from datetime import datetime, timedelta, timezone
from mcp.server.fastmcp import FastMCP
import json
from typing import List, Dict, Optional

# MCP Server Initialization
mcp = FastMCP("mcp_everything_server")

# --- Everything DLL Setup ---
DLL_LOADED = False
DLL_ERROR_MESSAGE = ""
try:
    # Load the Everything DLL
    # Ensure the DLL (32-bit or 64-bit) matches the Python interpreter's architecture.
    # This assumes the script is being run from a location where __file__ is defined.
    # In some execution contexts (like a frozen app or interactive session), __file__ might not be available.
    if hasattr(sys, 'frozen') and sys.frozen: # Handle PyInstaller case
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    dll_filename = "D:\devEnvironment\Everything\dll\Everything64.dll" if ctypes.sizeof(ctypes.c_voidp) == 8 else "D:\devEnvironment\Everything\dll\Everything32.dll"
    dll_path = os.path.join(script_dir, dll_filename)

    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"Everything DLL not found at {dll_path}. Please download it from voidtools.com and place it in the same directory as the script or executable.")
    everything_dll = ctypes.WinDLL(dll_path)

    # Define function prototypes from the Everything SDK
    everything_dll.Everything_GetResultDateCreated.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultDateModified.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_ulonglong)]
    everything_dll.Everything_GetResultSize.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_longlong)]
    everything_dll.Everything_GetResultFileNameW.argtypes = [ctypes.c_int]
    everything_dll.Everything_GetResultFileNameW.restype = ctypes.c_wchar_p
    everything_dll.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_int, ctypes.c_wchar_p, ctypes.c_uint]
    everything_dll.Everything_IsFileResult.argtypes = [ctypes.c_int]
    everything_dll.Everything_IsFileResult.restype = ctypes.c_bool
    everything_dll.Everything_GetNumResults.restype = ctypes.c_int
    everything_dll.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
    everything_dll.Everything_SetRequestFlags.argtypes = [ctypes.c_uint]
    everything_dll.Everything_SetMatchCase.argtypes = [ctypes.c_bool]
    everything_dll.Everything_SetMatchWholeWord.argtypes = [ctypes.c_bool]
    everything_dll.Everything_SetRegex.argtypes = [ctypes.c_bool]
    everything_dll.Everything_SetMax.argtypes = [ctypes.c_uint]
    everything_dll.Everything_SetOffset.argtypes = [ctypes.c_uint]
    everything_dll.Everything_SetSort.argtypes = [ctypes.c_uint]
    everything_dll.Everything_QueryW.argtypes = [ctypes.c_bool]
    everything_dll.Everything_QueryW.restype = ctypes.c_bool

    # Everything Constants
    EVERYTHING_REQUEST_FILE_NAME = 0x00000001
    EVERYTHING_REQUEST_PATH = 0x00000002
    EVERYTHING_REQUEST_SIZE = 0x00000010
    EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
    EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040

    SORT_MAP = {
        "NAME_ASCENDING": 1, "NAME_DESCENDING": 2,
        "PATH_ASCENDING": 3, "PATH_DESCENDING": 4,
        "SIZE_ASCENDING": 5, "SIZE_DESCENDING": 6,
        "DATE_MODIFIED_ASCENDING": 9, "DATE_MODIFIED_DESCENDING": 10,
        "DATE_CREATED_ASCENDING": 11, "DATE_CREATED_DESCENDING": 12,
    }
    DLL_LOADED = True
except (FileNotFoundError, OSError, AttributeError) as e:
    DLL_ERROR_MESSAGE = str(e)

def filetime_to_iso(filetime_val: int) -> str:
    """Converts a Windows FILETIME (in 100-nanosecond intervals since 1601-01-01) to an ISO 8601 string."""
    if filetime_val == 0:
        return ""
    # FILETIME epoch is 1601-01-01 UTC. Python's epoch is 1970-01-01 UTC.
    # The difference is 11644473600 seconds.
    try:
        # Add a timezone to the start date to make it aware
        dt = datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=filetime_val / 10)
        # Format to ISO 8601 with 'Z' for UTC
        return dt.isoformat().replace('+00:00', 'Z')
    except OverflowError:
        return "" # Handle cases where the timestamp is too large

@mcp.tool()
def search_everything(
    query: str,
    is_match_case: bool = False,
    is_match_whole_word: bool = False,
    is_regex: bool = False,
    max_results: int = 100,
    offset: int = 0,
    sort_by: str = "NAME_ASCENDING"
) -> str:
    """
    Performs a high-speed search for files and folders using the Everything engine.
    Supports a wide range of search syntaxes like wildcards, regular expressions, paths, sizes, and dates.
    The tool allows for fine-grained control over the search with options for case sensitivity, matching, sorting, and result limits.

    Args:
        query (str): The search string. Can be a simple keyword or use Everything's advanced syntax (e.g., `"C:\\Program Files\\" *.exe size:>10mb dm:lastmonth`).
        is_match_case (bool, optional): If True, the search will be case-sensitive. Defaults to False.
        is_match_whole_word (bool, optional): If True, the search will match whole words only. Defaults to False.
        is_regex (bool, optional): If True, the query string will be interpreted as a regular expression. Defaults to False.
        max_results (int, optional): The maximum number of results to return. Defaults to 100.
        offset (int, optional): The starting offset for the results, used for pagination. Defaults to 0.
        sort_by (str, optional): Specifies the sort order. Valid values are "NAME_ASCENDING", "NAME_DESCENDING", "PATH_ASCENDING", "PATH_DESCENDING", "SIZE_ASCENDING", "SIZE_DESCENDING", "DATE_MODIFIED_ASCENDING", "DATE_MODIFIED_DESCENDING", "DATE_CREATED_ASCENDING", "DATE_CREATED_DESCENDING". Defaults to "NAME_ASCENDING".

    Returns:
        str: A JSON formatted string representing a list of dictionaries, where each dictionary is a found file or folder.
             Returns a JSON string of an empty list '[]' if no results are found.
             Dictionary Structure:
                 - type (str): "FILE" or "FOLDER".
                 - name (str): The name of the file or folder.
                 - path (str): The full path to the file or folder.
                 - size_bytes (int): The size of the file in bytes (0 for folders).
                 - date_modified (str): The last modified timestamp in ISO 8601 format.
                 - date_created (str): The creation timestamp in ISO 8601 format.

    Raises:
        ConnectionError: If the Everything.dll cannot be loaded or found.
        ValueError: If an invalid value for 'sort_by' or an empty 'query' is provided.
    """
    if not DLL_LOADED:
        raise ConnectionError(f"Everything service is not available. Error: {DLL_ERROR_MESSAGE}")

    if not query or not query.strip():
        raise ValueError("'query' cannot be empty.")

    if sort_by not in SORT_MAP:
        raise ValueError(f"Invalid 'sort_by' value: {sort_by}. Must be one of {list(SORT_MAP.keys())}")

    try:
        # --- Configure Search ---
        everything_dll.Everything_SetMatchCase(is_match_case)
        everything_dll.Everything_SetMatchWholeWord(is_match_whole_word)
        everything_dll.Everything_SetRegex(is_regex)
        everything_dll.Everything_SetSearchW(query)
        everything_dll.Everything_SetSort(SORT_MAP[sort_by])
        everything_dll.Everything_SetMax(max_results)
        everything_dll.Everything_SetOffset(offset)

        # Request the necessary fields for the output
        request_flags = (
            EVERYTHING_REQUEST_FILE_NAME |
            EVERYTHING_REQUEST_PATH |
            EVERYTHING_REQUEST_SIZE |
            EVERYTHING_REQUEST_DATE_CREATED |
            EVERYTHING_REQUEST_DATE_MODIFIED
        )
        everything_dll.Everything_SetRequestFlags(request_flags)

        # --- Execute Query ---
        if not everything_dll.Everything_QueryW(True):
            # This can happen if the Everything service is not running
            raise ConnectionError("Failed to execute Everything query. Ensure the Everything service is running.")

        # --- Process Results ---
        num_results = everything_dll.Everything_GetNumResults()
        results = []

        # Buffers for retrieving data
        path_buffer = ctypes.create_unicode_buffer(2048)
        size_ptr = ctypes.c_longlong()
        created_ptr = ctypes.c_ulonglong()
        modified_ptr = ctypes.c_ulonglong()

        for i in range(num_results):
            # Get basic info
            is_file = everything_dll.Everything_IsFileResult(i)
            file_name = everything_dll.Everything_GetResultFileNameW(i)

            # Get full path
            everything_dll.Everything_GetResultFullPathNameW(i, path_buffer, 2048)
            full_path = path_buffer.value

            # Get size
            everything_dll.Everything_GetResultSize(i, ctypes.byref(size_ptr))

            # Get dates
            everything_dll.Everything_GetResultDateCreated(i, ctypes.byref(created_ptr))
            everything_dll.Everything_GetResultDateModified(i, ctypes.byref(modified_ptr))

            results.append({
                "type": "FILE" if is_file else "FOLDER",
                "name": file_name,
                "path": full_path,
                "size_bytes": size_ptr.value if is_file else 0,
                "date_created": filetime_to_iso(created_ptr.value),
                "date_modified": filetime_to_iso(modified_ptr.value),
            })

        return json.dumps(results, indent=4)

    except Exception as e:
        # Catch any other ctypes or logic errors and report them
        raise RuntimeError(f"An unexpected error occurred while searching: {e}")


if __name__ == "__main__":
    # This allows the server to be run directly for testing.
    # The MCP CLI will typically manage the server's lifecycle.
    if not DLL_LOADED:
        print(f"Error: {DLL_ERROR_MESSAGE}", file=sys.stderr)
        sys.exit(1)

    # Ensure stdout can handle UTF-8 characters, common in file paths
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    mcp.run()