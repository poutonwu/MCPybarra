import sys
import os
import json
import asyncio
import aiomysql
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any, Union

# --- Server Initialization ---
mcp = FastMCP("mcp_mysql_db_manager")

# --- Configuration Management ---
# Retrieve database credentials from environment variables.
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "123456"),
    "db": os.environ.get("DB_NAME", "user-db"),
}

if not all([DB_CONFIG["user"], DB_CONFIG["password"], DB_CONFIG["db"]]):
    print("Error: DB_USER, DB_PASSWORD, and DB_NAME environment variables must be set.", file=sys.stderr)
    sys.exit(1)

# Global connection pool
POOL = None

async def get_pool() -> aiomysql.Pool:
    """
    Initializes and returns a global aiomysql connection pool.
    If the pool already exists, it returns the existing one.
    """
    global POOL
    if POOL is None:
        try:
            POOL = await aiomysql.create_pool(
                **DB_CONFIG,
                autocommit=False, # Set autocommit to False for better transaction control
                loop=asyncio.get_event_loop()
            )
        except Exception as e:
            print(f"Failed to create database connection pool: {e}", file=sys.stderr)
            raise
    return POOL

@mcp.tool()
async def list_resources() -> Dict[str, List[str]]:
    """
    Lists all available tables in the current database.

    This tool takes no parameters and returns a list of all table names.

    Returns:
        Dict[str, List[str]]: A dictionary with a 'tables' key,
        the value of which is a list of strings, where each string
        is a table name.
        Example: `{"tables": ["users", "products", "orders"]}`
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SHOW TABLES")
                tables = [row[0] for row in await cur.fetchall()]
                return {"tables": tables}
    except Exception as e:
        # Transparency: Provide a clear error message.
        raise RuntimeError(f"An error occurred while listing resources: {e}")

@mcp.tool()
async def read_resource(table_name: str) -> Dict[str, Union[List[str], List[List[Any]]]]:
    """
    Reads the full content of a specified table, returning up to 100 records
    in a structured row-column format.

    Args:
        table_name (str): The name of the target table to read data from (required).

    Returns:
        Dict[str, Union[List[str], List[List[Any]]]]: A dictionary containing
        'columns' and 'rows' keys. 'columns' is a list of column names, and
        'rows' is a list of lists, where each inner list represents a data row.
        Example:
        ```json
        {
          "columns": ["id", "name", "email"],
          "rows": [
            [1, "Alice", "alice@example.com"],
            [2, "Bob", "bob@example.com"]
          ]
        }
        ```
    """
    # Robustness: Validate input parameter.
    if not table_name or not isinstance(table_name, str):
        raise ValueError("Parameter 'table_name' must be a non-empty string.")

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Security: Verify table_name exists to prevent SQL injection.
                await cur.execute("SHOW TABLES")
                valid_tables = [row[0] for row in await cur.fetchall()]
                if table_name not in valid_tables:
                    raise ValueError(f"Table '{table_name}' not found in the database.")

                # Functionality: Safely execute the query.
                await cur.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
                columns = [desc[0] for desc in cur.description]
                rows = await cur.fetchall()
                return {"columns": columns, "rows": rows}
    except ValueError as ve:
        # Re-raise validation errors to provide clear feedback.
        raise ve
    except Exception as e:
        # Transparency: Provide a clear error message for other errors.
        raise RuntimeError(f"An error occurred while reading the resource '{table_name}': {e}")

@mcp.tool()
async def execute_sql(query: str) -> Dict[str, Any]:
    """
    Executes a custom SQL query on the MySQL database.
    Supports data query (e.g., `SELECT`, `SHOW`) and data manipulation
    (e.g., `INSERT`, `UPDATE`, `DELETE`).

    Args:
        query (str): The SQL query string to be executed (required).

    Returns:
        Dict[str, Any]: For queries that return data like `SELECT` or `SHOW`,
        returns a dictionary with 'columns' and 'rows'. For data manipulation
        queries like `INSERT`, `UPDATE`, `DELETE`, returns a dictionary with
        an 'affected_rows' key.
        Example (SELECT): `{"columns": ["id", "name"], "rows": [[1, "Alice"]]}`
        Example (UPDATE): `{"affected_rows": 1}`
    """
    # Robustness: Validate input parameter.
    if not query or not isinstance(query, str) or not query.strip():
        raise ValueError("Parameter 'query' must be a non-empty SQL string.")

    # Security: Basic check for potentially dangerous commands. More advanced checks may be needed.
    trimmed_query = query.strip().lower()
    if trimmed_query.startswith("drop") or trimmed_query.startswith("truncate"):
        raise SecurityWarning("DROP and TRUNCATE statements are not allowed for safety reasons.")

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                # Check if the query is a data manipulation or data query statement.
                if trimmed_query.startswith(('select', 'show', 'describe', 'explain')):
                    if cur.description:
                        columns = [desc[0] for desc in cur.description]
                        rows = await cur.fetchall()
                        return {"columns": columns, "rows": rows}
                    else:
                        return {"result": "Query executed, but no data was returned."}
                else:
                    # For INSERT, UPDATE, DELETE, etc.
                    affected_rows = cur.rowcount
                    await conn.commit() # Commit the transaction for DML statements.
                    return {"affected_rows": affected_rows}
    except Exception as e:
        # Transparency: Provide a clear, detailed error message.
        raise RuntimeError(f"An error occurred while executing the SQL query: {e}")

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout.
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    # Set up and run the server.
    # The server will handle incoming MCP requests and dispatch them to the decorated tools.
    print("Starting MCP MySQL DB Manager Server...")
    print(f"Reading DB config for user '{DB_CONFIG['user']}' on host '{DB_CONFIG['host']}:{DB_CONFIG['port']}'")
    mcp.run()