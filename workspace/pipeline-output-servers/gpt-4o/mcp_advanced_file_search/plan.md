```markdown
# MCP Server Implementation Plan

## MCP Tools Plan

### Tool 1: `search_files`
- **Function Name**: `search_files`
- **Description**: Searches for files and folders on the Windows system using the `everything.dll` library. Supports advanced search syntax such as wildcards, regular expressions, file paths, size, time, and attributes.
- **Parameters**:
  1. `query` (str): The search query string. Can include advanced syntax like:
     - Wildcards (`*`, `?`)
     - Regular expressions (e.g., `regex:.*\.txt$`)
     - File paths (e.g., `C:\Users\*`)
     - Size filters (e.g., `size:>10MB`)
     - Time filters (e.g., `date:>=01/01/2023`)
     - Attributes (e.g., `attribute:readonly`).
  2. `case_sensitive` (bool): Whether the search should be case-sensitive. Default is `False`.
  3. `whole_word_match` (bool): Whether to match whole words only. Default is `False`.
  4. `regex` (bool): Whether to enable regular expression matching. Default is `False`.
  5. `sort_by` (str): The sorting criterion for the results. Options include `name`, `size`, `date_created`, `date_modified`. Default is `name`.
  6. `limit` (int): The maximum number of results to return. Default is `100`.
- **Return Value**:
  - A list of dictionaries where each dictionary represents a file or folder with details:
    - `name` (str): The name of the file or folder.
    - `path` (str): The full path to the file or folder.
    - `size` (int): The size of the file in bytes.
    - `date_created` (str): The creation date of the file.
    - `date_modified` (str): The last modified date of the file.
    - `attributes` (list of str): A list of attributes (e.g., `readonly`, `hidden`).

### Tool 2: `get_file_details`
- **Function Name**: `get_file_details`
- **Description**: Retrieves detailed information about a specific file or folder.
- **Parameters**:
  1. `file_path` (str): The full path of the file or folder for which details are to be retrieved.
- **Return Value**:
  - A dictionary containing:
    - `name` (str): The name of the file or folder.
    - `path` (str): The full path.
    - `size` (int): The size in bytes.
    - `date_created` (str): The creation date.
    - `date_modified` (str): The last modified date.
    - `attributes` (list of str): A list of attributes (e.g., `readonly`, `hidden`).

---

## Server Overview

The MCP server will provide automation for high-speed file and folder searches on Windows systems using the `everything.dll` library. It supports advanced query capabilities such as wildcards, regular expressions, and attribute filtering. The server will allow users to retrieve detailed file information based on their query criteria and enable sorting, size limits, case sensitivity, and whole word matching.

---

## File to be Generated

The code will be implemented in a single Python file:
- **File Name**: `mcp_file_search_server.py`

---

## Dependencies

The server will require the following Python libraries:
1. **`mcp[cli]`**: For MCP server functionality.
2. **`ctypes`**: To load and interact with the `everything.dll` library.
3. **`os`**: For file path manipulations and environment checks.
4. **`typing`**: For type annotations to ensure robust and maintainable code.

---
```