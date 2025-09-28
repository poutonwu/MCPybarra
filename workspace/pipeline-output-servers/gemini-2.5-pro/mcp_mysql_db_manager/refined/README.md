# mcp_mysql_db_manager

## Overview
The `mcp_mysql_db_manager` is a Model Context Protocol (MCP) server that provides tools for interacting with a MySQL database. It allows external systems to list available tables, read table contents, and execute custom SQL queries—all while ensuring robustness, security, and transparency.

This server connects to a MySQL database using credentials provided via environment variables and exposes three core tools:
- List all available tables in the connected database.
- Read data from a specific table (up to 100 records).
- Execute arbitrary SQL queries with support for both read and write operations.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed and then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following:

```
mcp[cli]
aiomysql
```

---

## Running the Server

To run the server, set the required environment variables and execute the script:

```bash
export DB_HOST="127.0.0.1"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="123456"
export DB_NAME="user-db"

python mcp_mysql_db_manager.py
```

Replace the values above with those matching your MySQL database configuration.

---

## Available Tools

### 1. `list_resources()`
**Description:** Lists all available tables in the current database.

**Returns:**
```json
{
  "tables": ["users", "products", "orders"]
}
```

---

### 2. `read_resource(table_name: str)`
**Description:** Reads up to 100 rows from the specified table and returns column names along with the data.

**Parameters:**
- `table_name` (str): The name of the table to read from.

**Returns:**
```json
{
  "columns": ["id", "name", "email"],
  "rows": [
    [1, "Alice", "alice@example.com"],
    [2, "Bob", "bob@example.com"]
  ]
}
```

---

### 3. `execute_sql(query: str)`
**Description:** Executes a custom SQL query on the database. Supports both data manipulation (e.g., INSERT, UPDATE, DELETE) and data query (e.g., SELECT, SHOW).

**Parameters:**
- `query` (str): A valid SQL query string.

**Returns:**
- For `SELECT`, `SHOW`, etc.:
```json
{
  "columns": ["id", "name"],
  "rows": [[1, "Alice"]]
}
```
- For `INSERT`, `UPDATE`, `DELETE`:
```json
{
  "affected_rows": 1
}
```

> ⚠️ **Note:** This tool blocks potentially destructive commands like `DROP` and `TRUNCATE` for safety reasons.