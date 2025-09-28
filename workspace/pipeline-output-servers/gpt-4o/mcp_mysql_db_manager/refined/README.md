# mcp_mysql_db_manager

## Overview

`mcp_mysql_db_manager` is an MCP (Model Context Protocol) server that provides a set of tools for interacting with a MySQL database. It allows language models to list tables, read data from tables, and execute custom SQL queries.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following packages:

```
mcp[cli]
mysql-connector-python
```

## Running the Server

To run the server, use the following command:

```bash
python mcp_mysql_db_manager.py
```

Ensure that the required environment variables are set before running the server:

- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

Default values will be used if the environment variables are not set:

- Host: `localhost`
- User: `root`
- Password: `123456`
- Database: `user-db`

## Available Tools

The server provides the following tools via the MCP interface:

### `list_resources`

Lists all available tables in the connected MySQL database.

**Returns:**  
A list of table names as strings.

### `read_resource`

Reads the first 100 rows from a specified MySQL table.

**Parameters:**  
- `table_name` (str): The name of the table to read from.

**Returns:**  
A list of dictionaries, where each dictionary represents a row in the table.

### `execute_sql`

Executes a custom SQL query on the connected MySQL database.

**Parameters:**  
- `query` (str): The SQL query to execute.

**Returns:**  
- For SELECT or SHOW queries: A list of dictionaries representing the result set.
- For INSERT, UPDATE, DELETE, or other queries: A dictionary with the number of affected rows.