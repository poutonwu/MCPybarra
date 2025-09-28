# mcp_mysql_database_manager

## Overview

The `mcp_mysql_database_manager` is an MCP (Model Context Protocol) server that provides a set of tools for interacting with a MySQL database. It allows large language models (LLMs) to access and manipulate database resources through structured function calls.

This server supports the following key operations:

- Listing all available tables in the connected database.
- Reading data from a specific table (up to 100 rows).
- Executing custom SQL queries, including SELECT, INSERT, UPDATE, DELETE, and SHOW commands.

It uses environment variables for database configuration and ensures robust error handling and logging.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed and then install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following:

```
mcp[cli]
mysql-connector-python
```

---

## Running the Server

You can run the server using the following command:

```bash
python mcp_mysql_database_manager.py
```

By default, the server will use these environment values to connect to the database:

- Host: `localhost`
- User: `root`
- Password: `123456`
- Database: `user-db`

To customize the connection, set the appropriate environment variables before running the server:

```bash
export DB_HOST="your_host"
export DB_USER="your_user"
export DB_PASSWORD="your_password"
export DB_NAME="your_database"
python mcp_mysql_database_manager.py
```

---

## Available Tools

### `list_resources()`

**Description:** Lists all available tables in the current database.

**Returns:** A JSON array containing the names of all tables in the database.

**Example Response:**
```json
["users", "orders", "products"]
```

---

### `read_resource(table_name: str)`

**Description:** Reads and returns the first 100 rows from the specified table.

**Arguments:**
- `table_name` (string): The name of the table to read from.

**Returns:** A JSON array of dictionaries, where each dictionary represents a row in the table.

**Example Response:**
```json
[
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"}
]
```

---

### `execute_sql(query: str)`

**Description:** Executes a custom SQL query on the database.

**Arguments:**
- `query` (string): The SQL statement to execute.

**Returns:**
- For SELECT or SHOW queries: A JSON array of result rows.
- For INSERT, UPDATE, or DELETE queries: A JSON object indicating the number of affected rows.

**Example Responses:**

For SELECT:
```json
[
  {"id": 1, "name": "Alice"}
]
```

For UPDATE:
```json
{"affected_rows": 1}
```

---