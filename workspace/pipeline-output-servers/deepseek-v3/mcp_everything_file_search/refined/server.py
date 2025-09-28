import sys
import ctypes
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_everything_file_search")

# Load everything.dll
EVERYTHING_DLL = r'D:\devEnvironment\Everything\dll\Everything64.dll'

def load_everything_dll():
    """
    Initializes and loads the everything.dll library using ctypes.
    Must be called before any search operations.

    Returns:
        bool: True if the DLL was loaded successfully, False otherwise.
    """
    try:
        global everything_dll
        everything_dll = ctypes.WinDLL(EVERYTHING_DLL)
        
        # Verify required functions are present
        required_functions = [
            'Everything_SetSearchW',
            'Everything_QueryW',
            'Everything_GetNumResults',
            'Everything_GetResultPathW',
            'Everything_GetLastError'
        ]
        
        for func in required_functions:
            if not hasattr(everything_dll, func):
                raise AttributeError(f"Missing required function {{func}} in {{EVERYTHING_DLL}}")
                
        return True
    except Exception as e:
        print(f"Failed to load {{EVERYTHING_DLL}}: {{e}}", file=sys.stderr)
        return False

@mcp.tool()
def search_files(
    query: str,
    limit: int = 100,
    case_sensitive: bool = False,
    full_word: bool = False,
    regex: bool = False,
    sort_by: str = None
) -> list:
    """
    Performs a high-speed search of files and folders on Windows using the everything.dll library.
    Supports multiple search syntaxes (wildcards, regex, path, size, time, attributes) and advanced features.

    Args:
        query (str): The search query string (e.g., `*.txt`, `size:>1MB`, `modified:today`).
        limit (int, optional): Maximum number of results to return (default: 100).
        case_sensitive (bool, optional): If True, performs case-sensitive matching (default: False).
        full_word (bool, optional): If True, matches only full words (default: False).
        regex (bool, optional): If True, treats the query as a regular expression (default: False).
        sort_by (str, optional): Specifies sorting criteria (e.g., "name", "size", "modified").

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - path (str): Full file/folder path.
            - size (int): File size in bytes.
            - modified (str): Last modified timestamp.
            - attributes (dict): File attributes (e.g., readonly, hidden).

    Raises:
        Exception: If the search operation fails.
    """
    try:
        if 'everything_dll' not in globals():
            raise Exception("everything.dll not loaded. Call load_everything_dll() first.")
        
        # Set search parameters
        everything_dll.Everything_SetSearchW(ctypes.c_wchar_p(query))
        everything_dll.Everything_SetMatchCase(1 if case_sensitive else 0)
        everything_dll.Everything_SetMatchWholeWord(1 if full_word else 0)
        everything_dll.Everything_SetRegex(1 if regex else 0)
        
        # Set sorting
        if sort_by:
            sort_mapping = {
                "name": 1,
                "size": 2,
                "modified": 3
            }
            everything_dll.Everything_SetSort(sort_mapping.get(sort_by.lower(), 0))

        # Execute search
        if not everything_dll.Everything_QueryW(1):
            error_code = everything_dll.Everything_GetLastError()
            raise Exception(f"Search query failed with error code {{error_code}}")

        # Get results
        results = []
        num_results = min(everything_dll.Everything_GetNumResults(), limit)
        
        for i in range(num_results):
            path = ctypes.create_unicode_buffer(32767)  # MAX_PATH is 32767
            if not everything_dll.Everything_GetResultPathW(i, path, 32767):
                continue
            
            size = everything_dll.Everything_GetResultSize(i)
            modified = everything_dll.Everything_GetResultDateModified(i)
            attributes = everything_dll.Everything_GetResultAttributes(i)

            results.append({
                "path": path.value,
                "size": size,
                "modified": modified,
                "attributes": {
                    "readonly": bool(attributes & 0x1),
                    "hidden": bool(attributes & 0x2),
                    "system": bool(attributes & 0x4),
                    "archive": bool(attributes & 0x20)
                }
            })

        return results
    except Exception as e:
        raise Exception(f"Search failed: {{e}}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    if load_everything_dll():
        mcp.run()
    else:
        print("Failed to initialize everything.dll. Exiting.", file=sys.stderr)
        sys.exit(1)