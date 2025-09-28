import ctypes
import os
from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime

class EverythingAPI:
    def __init__(self, dll_path):
        """
        Initialize the EverythingAPI class by loading the everything.dll using ctypes.

        Args:
            dll_path (str): The path to the everything.dll file.
        """
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"DLL file not found at path: {dll_path}")

        try:
            self.everything_dll = ctypes.WinDLL(dll_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load DLL: {e}")

        # Set up function prototypes and argument types for use in the search
        self.everything_dll.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
        self.everything_dll.Everything_QueryW.argtypes = [ctypes.c_bool]
        self.everything_dll.Everything_GetNumResults.restype = ctypes.c_ulong
        self.everything_dll.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_ulong, ctypes.c_wchar_p, ctypes.c_ulong]

        # Assign function existence flags
        self.has_size_min = hasattr(self.everything_dll, 'Everything_SetSizeMin')
        self.has_size_max = hasattr(self.everything_dll, 'Everything_SetSizeMax')
        self.has_date_modified_start = hasattr(self.everything_dll, 'Everything_SetDateModifiedStart')
        self.has_date_modified_end = hasattr(self.everything_dll, 'Everything_SetDateModifiedEnd')
        self.has_attribute_flags = hasattr(self.everything_dll, 'Everything_SetAttributeFlags')

    def search(self, query, path=None, size_min=None, size_max=None, date_modified_start=None,
               date_modified_end=None, attributes=None, sort_by=None, case_sensitive=False, whole_word=False, regex=False):
        """
        Perform a search using the Everything API with various filtering options.

        Args:
            query (str): The search query including keywords, wildcards, or regex patterns.
            path (str, optional): The root directory path to start the search from. Defaults to the entire system.
            size_min (int, optional): Minimum file size in bytes.
            size_max (int, optional): Maximum file size in bytes.
            date_modified_start (str, optional): Start date for filtering by modification time (YYYY-MM-DD).
            date_modified_end (str, optional): End date for filtering by modification time (YYYY-MM-DD).
            attributes (list of str, optional): List of file attributes to filter by (e.g., 'readonly', 'hidden').
            sort_by (str, optional): Sorting criteria ('name', 'size', 'date').
            case_sensitive (bool, optional): If True, the search is case-sensitive.
            whole_word (bool, optional): If True, only whole word matches are returned.
            regex (bool, optional): If True, the query is treated as a regular expression.

        Returns:
            A JSON string containing a list of dictionaries, where each dictionary contains detailed information about a found file or folder.
        """
        try:
            # Reset previous search settings
            self.everything_dll.Everything_Reset()

            # Set the search query
            full_query = f"{path}\\{query}" if path else query
            self.everything_dll.Everything_SetSearchW(full_query)

            # Apply additional filters
            if size_min is not None:
                if not isinstance(size_min, int) or size_min < 0:
                    raise ValueError("size_min must be a non-negative integer")
                if self.has_size_min:
                    self.everything_dll.Everything_SetSizeMin(size_min)
                else:
                    raise NotImplementedError("The DLL does not support size filtering (Everything_SetSizeMin)")

            if size_max is not None:
                if not isinstance(size_max, int) or size_max < 0:
                    raise ValueError("size_max must be a non-negative integer")
                if self.has_size_max:
                    self.everything_dll.Everything_SetSizeMax(size_max)
                else:
                    raise NotImplementedError("The DLL does not support size filtering (Everything_SetSizeMax)")

            if date_modified_start:
                try:
                    datetime.strptime(date_modified_start, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("date_modified_start must be in YYYY-MM-DD format")
                if self.has_date_modified_start:
                    self.everything_dll.Everything_SetDateModifiedStart(date_modified_start)
                else:
                    raise NotImplementedError("The DLL does not support date filtering (Everything_SetDateModifiedStart)")

            if date_modified_end:
                try:
                    datetime.strptime(date_modified_end, "%Y-%m-%d")
                except ValueError:
                    raise ValueError("date_modified_end must be in YYYY-MM-DD format")
                if self.has_date_modified_end:
                    self.everything_dll.Everything_SetDateModifiedEnd(date_modified_end)
                else:
                    raise NotImplementedError("The DLL does not support date filtering (Everything_SetDateModifiedEnd)")

            if attributes:
                if not isinstance(attributes, list):
                    raise ValueError("attributes must be a list of strings")
                attribute_flags = self._convert_attributes(attributes)
                if self.has_attribute_flags:
                    self.everything_dll.Everything_SetAttributeFlags(attribute_flags)
                else:
                    raise NotImplementedError("The DLL does not support attribute filtering (Everything_SetAttributeFlags)")

            if sort_by:
                sort_flags = {
                    'name': 1,
                    'size': 2,
                    'date': 3
                }
                if sort_by.lower() not in sort_flags:
                    raise ValueError("sort_by must be one of 'name', 'size', 'date'")
                self.everything_dll.Everything_SetSort(sort_flags.get(sort_by.lower(), 0))

            self.everything_dll.Everything_SetMatchCase(case_sensitive)
            self.everything_dll.Everything_SetMatchWholeWord(whole_word)
            self.everything_dll.Everything_SetRegex(regex)

            # Execute the query with timeout handling
            try:
                result = self.everything_dll.Everything_QueryW(True)
                if not result:
                    error_code = ctypes.windll.kernel32.GetLastError()
                    raise RuntimeError(f"Query failed with error code: {error_code}")
            except ctypes.WinDLL.WindowsError as e:
                raise TimeoutError(f"Search operation timed out or was interrupted: {e}")

            # Retrieve results
            num_results = self.everything_dll.Everything_GetNumResults()
            results = []

            for i in range(num_results):
                buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                self.everything_dll.Everything_GetResultFullPathNameW(i, buf, ctypes.wintypes.MAX_PATH)
                results.append({"file_path": buf.value})

            return json.dumps(results, ensure_ascii=False)

        except Exception as e:
            raise RuntimeError(f"Error during search: {e}")

    @staticmethod
    def _convert_attributes(attributes):
        """
        Convert a list of attribute strings into a bitmask for use with Everything_SetAttributeFlags.

        Args:
            attributes (list of str): List of attribute names.

        Returns:
            An integer bitmask representing the combined attributes.
        """
        attribute_map = {
            'readonly': 0x00000001,
            'hidden': 0x00000002,
            'system': 0x00000004,
            'directory': 0x00000010,
            'archive': 0x00000020,
            'normal': 0x00000080
        }

        flag = 0
        for attr in attributes:
            if attr.lower() not in attribute_map:
                raise ValueError(f"Invalid attribute: {attr}")
            flag |= attribute_map.get(attr.lower(), 0)

        return flag

# Initialize FastMCP server
mcp = FastMCP("everything_search")

@mcp.tool()
def perform_everything_search(query: str, path: str = None, size_min: int = None, size_max: int = None,
                              date_modified_start: str = None, date_modified_end: str = None,
                              attributes: list = None, sort_by: str = None, case_sensitive: bool = False,
                              whole_word: bool = False, regex: bool = False) -> str:
    """
    Perform an advanced file search on Windows using the Everything API via ctypes.

    Args:
        query (str): The search query including keywords, wildcards, or regex patterns.
        path (str, optional): The root directory path to start the search from. Defaults to the entire system.
        size_min (int, optional): Minimum file size in bytes.
        size_max (int, optional): Maximum file size in bytes.
        date_modified_start (str, optional): Start date for filtering by modification time (YYYY-MM-DD).
        date_modified_end (str, optional): End date for filtering by modification time (YYYY-MM-DD).
        attributes (list of str, optional): List of file attributes to filter by (e.g., 'readonly', 'hidden').
        sort_by (str, optional): Sorting criteria ('name', 'size', 'date').
        case_sensitive (bool, optional): If True, the search is case-sensitive.
        whole_word (bool, optional): If True, only whole word matches are returned.
        regex (bool, optional): If True, the query is treated as a regular expression.

    Returns:
        A JSON string containing a list of dictionaries, where each dictionary contains detailed information about a found file or folder.

    Example:
        To search for all .txt files in C:\\Users\\Public that are larger than 1MB and modified after 2023-01-01:
        perform_everything_search(
            query="*.txt",
            path="C:\\Users\\Public",
            size_min=1048576,
            date_modified_start="2023-01-01"
        )
    """
    dll_path = os.environ.get('EVERYTHING_DLL_PATH', r'D:\\devEnvironment\\Everything\\dll\\Everything64.dll')
    if not dll_path:
        raise ValueError("Environment variable EVERYTHING_DLL_PATH must be set to the path of everything.dll")

    api = EverythingAPI(dll_path)
    return api.search(
        query=query,
        path=path,
        size_min=size_min,
        size_max=size_max,
        date_modified_start=date_modified_start,
        date_modified_end=date_modified_end,
        attributes=attributes,
        sort_by=sort_by,
        case_sensitive=case_sensitive,
        whole_word=whole_word,
        regex=regex
    )

if __name__ == "__main__":
    mcp.run()