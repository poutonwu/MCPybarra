### **MCP Tools Plan**  

#### 1. **Tool: `list_resources`**  
- **Description**: Lists all available MySQL database tables as accessible resources.  
- **Parameters**:  
  - `database_name` (str, optional): Name of the MySQL database. If omitted, lists tables from the default connected database.  
- **Return Value**:  
  - A list of dictionaries, where each dictionary represents a table with keys:  
    - `table_name` (str): Name of the table.  
    - `schema` (str, optional): Schema name if applicable.  

#### 2. **Tool: `read_resource`**  
- **Description**: Reads the full data content of a specified MySQL table (limited to 100 rows).  
- **Parameters**:  
  - `table_name` (str, required): Name of the table to read.  
  - `limit` (int, optional): Maximum number of rows to return (default: 100).  
- **Return Value**:  
  - A dictionary with:  
    - `columns` (list of str): Column names.  
    - `rows` (list of lists): Row data, where each inner list represents a row.  

#### 3. **Tool: `execute_sql`**  
- **Description**: Executes a custom SQL query (SELECT, SHOW, INSERT, UPDATE, etc.) and returns structured results.  
- **Parameters**:  
  - `query` (str, required): The SQL query to execute.  
- **Return Value**:  
  - For **SELECT/SHOW**: A dictionary with `columns` (list of str) and `rows` (list of lists).  
  - For **INSERT/UPDATE/DELETE**: A dictionary with `affected_rows` (int) indicating the number of rows modified.  

---

### **Server Overview**  
The MCP server automates MySQL database management, providing:  
1. Table listing (`list_resources`).  
2. Table data retrieval (`read_resource`).  
3. Custom SQL execution (`execute_sql`).  

---

### **File to be Generated**  
- **Filename**: `mcp_mysql_server.py`  

---

### **Dependencies**  
1. **`mcp[cli]`**: MCP SDK for server implementation.  
2. **`mysql-connector-python`**: Library for MySQL database interactions.  
3. **`pydantic`** (optional): For input validation if needed.  

---

This plan strictly adheres to the user's request without introducing additional functionalities. The implementation will focus on the three core tools with clear input/output specifications.