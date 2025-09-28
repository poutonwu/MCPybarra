### MCP Tools Plan

#### Tool 1: `list_resources`
- **Description**: Lists all available MySQL tables in the database and provides access to them as resources.
- **Parameters**:
  - None
- **Return Value**: 
  - A list of strings, where each string represents the name of a table in the MySQL database.

#### Tool 2: `read_resource`
- **Description**: Reads the full data content of a specified table and returns it in rows and columns format. The result is limited to a maximum of 100 records.
- **Parameters**:
  - `table_name` (str): The name of the MySQL table to read.
- **Return Value**: 
  - A list of dictionaries, where each dictionary represents a row in the table with column names as keys and row values as values. If the table has more than 100 records, only the first 100 will be returned.

#### Tool 3: `execute_sql`
- **Description**: Executes custom SQL queries on the MySQL database. Supports various SQL operations such as SELECT, SHOW, INSERT, UPDATE, etc., and returns structured results including affected rows or query result sets depending on the type of query executed.
- **Parameters**:
  - `query` (str): The SQL query to execute.
- **Return Value**: 
  - For SELECT and SHOW queries, returns a list of dictionaries representing the result set.
  - For INSERT, UPDATE, DELETE queries, returns an integer indicating the number of affected rows.

### Server Overview
The server is designed to automate MySQL database management by providing tools to list database resources, read specific table contents, and execute arbitrary SQL commands. It serves as an integration point for large language models to interact with MySQL databases through the Model Context Protocol (MCP).

### File to be Generated
- `mcp_mysql_server.py`: This single Python file will contain all the logic necessary to implement the described functionalities using the FastMCP framework.

### Dependencies
- `mysql-connector-python`: A third-party library required to connect to and interact with the MySQL database.
- `mcp[cli]`: The MCP SDK for building the MCP server.
- `httpx`: Although not directly required for this implementation, it's part of the initial setup example provided and might be useful if extending the server to include HTTP requests.