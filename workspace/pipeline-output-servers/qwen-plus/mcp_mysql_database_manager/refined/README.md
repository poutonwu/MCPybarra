# mcp_mysql_database_manager

## Overview
A Model Context Protocol (MCP) server that provides database management capabilities for interacting with MySQL databases. It allows LLMs to:
- List available database tables
- Read table contents
- Execute custom SQL queries

## Installation
1. Install Python 3.10+
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

The `requirements.txt` should include:
```
mcp[cli]
mysql-connector-python
```

## Running the Server
Set up database connection environment variables first:
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=user-db
```

Then run the server:
```bash
python mcp_mysql_database_manager.py
```

## Available Tools

### list_resources()
Lists all available tables in the connected MySQL database.

**Returns:**  
JSON string containing a list of table names

**Example Response:**
```json
{"tables": ["users", "orders", "products"]}
```

### read_resource(table_name: str)
Reads data from a specified database table.

**Parameters:**
- `table_name` (str): Name of the table to read from

**Returns:**  
JSON string containing column names and table rows (limited to 100 records)

**Example Response:**
```json
{
  "columns": ["id", "name", "email"],
  "rows": [{"id": 1, "name": "Alice", "email": "alice@example.com"}]
}
```

### execute_sql(sql_query: str)
Executes a custom SQL query on the database.

**Parameters:**
- `sql_query` (str): The SQL query to execute

**Returns:**  
For SELECT/SHOW queries: JSON string with columns and matching rows  
For other operations: JSON string indicating number of affected rows

**Example Responses:**
```json
{
  "columns": ["id", "name", "email"],
  "rows": [{"id": 1, "name": "Alice", "email": "alice@example.com"}]
}
```
or
```json
{"affected_rows": 1}
```