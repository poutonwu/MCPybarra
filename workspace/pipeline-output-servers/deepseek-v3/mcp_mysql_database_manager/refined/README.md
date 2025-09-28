# mcp_mysql_database_manager

## Overview

The `mcp_mysql_database_manager` is a Model Context Protocol (MCP) server that provides a programmatic interface to interact with MySQL databases. It enables external tools and LLMs to list database tables, read table contents, and execute custom SQL queries.

## Installation

Before running the server, ensure you have the required dependencies installed:

```bash
pip install mcp[cli] mysql-connector-python
```

Make sure you have a MySQL database running and accessible with the credentials defined in the script (`root` / `123456` for the `user-db` database by default).

## Running the Server

To start the server, run the following command:

```bash
python mcp_mysql_database_manager.py
```

This will launch the MCP server using the default `stdio` transport protocol.

## Available Tools

The server provides the following MCP tools:

### `list_resources`

Lists all available tables in the connected MySQL database or a specified database.

**Parameters:**
- `database_name` (str, optional): Name of the database to inspect.

**Returns:**
- A list of dictionaries, each containing:
  - `table_name`: Name of the table.
  - `schema`: Schema name (if applicable).

### `read_resource`

Reads and returns the contents of a specified table (limited to 100 rows by default).

**Parameters:**
- `table_name` (str, required): Name of the table to read.
- `limit` (int, optional): Maximum number of rows to return (default: 100).

**Returns:**
- A dictionary with:
  - `columns`: List of column names.
  - `rows`: List of row data (each as a list of values).

### `execute_sql`

Executes a custom SQL query and returns structured results.

**Parameters:**
- `query` (str, required): SQL query to execute.

**Returns:**
- For `SELECT` or `SHOW` queries:
  - `columns`: List of column names.
  - `rows`: List of row data.
- For `INSERT`, `UPDATE`, or `DELETE` queries:
  - `affected_rows`: Number of rows modified.

This tool supports a wide range of SQL operations and is useful for both data retrieval and manipulation.