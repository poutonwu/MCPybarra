### **MCP Tools Plan**

#### **1. Function Name: `search_files`**
- **Description**: Performs a high-speed search of files and folders on Windows using the `everything.dll` library. Supports multiple search syntaxes (wildcards, regex, path, size, time, attributes) and advanced features (sorting, size limits, case sensitivity, full-word matching, regex matching).
- **Parameters**:
  - `query` (str): The search query string (e.g., `*.txt`, `size:>1MB`, `modified:today`).
  - `limit` (int, optional): Maximum number of results to return (default: `100`).
  - `case_sensitive` (bool, optional): If `True`, performs case-sensitive matching (default: `False`).
  - `full_word` (bool, optional): If `True`, matches only full words (default: `False`).
  - `regex` (bool, optional): If `True`, treats the query as a regular expression (default: `False`).
  - `sort_by` (str, optional): Specifies sorting criteria (e.g., `"name"`, `"size"`, `"modified"`).
- **Return Value**:  
  A list of dictionaries, where each dictionary contains:
  - `path` (str): Full file/folder path.
  - `size` (int): File size in bytes.
  - `modified` (str): Last modified timestamp.
  - `attributes` (dict): File attributes (e.g., `readonly`, `hidden`).

#### **2. Function Name: `load_everything_dll`**  
- **Description**: Initializes and loads the `everything.dll` library using `ctypes`. Must be called before any search operations.
- **Parameters**: None.
- **Return Value**:  
  - `bool`: `True` if the DLL was loaded successfully, `False` otherwise.

---

### **Server Overview**  
The MCP server enables **high-speed Windows file and folder searches** by leveraging the `everything.dll` library. It supports advanced search features such as wildcards, regex, size/time filters, and result sorting. The server is designed for efficiency and ease of integration with LLM-based workflows.

---

### **File to be Generated**  
`mcp_file_search_server.py`  
(All server logic will be contained in this single file.)

---

### **Dependencies**  
- `ctypes` (Python built-in)  
- `everything.dll` (Must be accessible in the system PATH or specified location)  

--- 

This plan adheres strictly to the user's request, focusing on **core functionalities without unnecessary additions**. The implementation will prioritize **performance, robustness, and clarity** in error handling.