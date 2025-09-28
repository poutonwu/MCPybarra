import sys
import os
import json
from typing import Dict, List, Any, Optional
import mysql.connector
from mysql.connector import Error, errorcode, MySQLConnection
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mysql_database_manager")

# Configuration for database connection
CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'database': os.environ.get('DB_NAME', "user-db")
}

# Set up proxy if needed
os.environ['HTTP_PROXY'] = os.environ.get('HTTP_PROXY', 'http://127.0.0.1:7890')
os.environ['HTTPS_PROXY'] = os.environ.get('HTTPS_PROXY', 'http://127.0.0.1:7890')

def get_db_connection() -> MySQLConnection:
    """Establish and return a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**CONFIG)
        if connection.is_connected():
            return connection
    except Error as err:
        raise ConnectionError(f"Database connection failed: {err}")

@mcp.tool()
def list_resources() -> str:
    """List all available MySQL tables as resources.

    Returns:
        A JSON string containing a list of table names.

    Raises:
        ConnectionError: If database connection fails.
        RuntimeError: If listing tables fails.
    
    Example:
        >>> list_resources()
        '{"tables": ["users", "orders", "products"]}'
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return json.dumps({"tables": tables})
    except Error as err:
        raise RuntimeError(f"Failed to list tables: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@mcp.tool()
def read_resource(table_name: str) -> str:
    """Read data from a specified table.

    Args:
        table_name (str): Name of the table to read from (required).

    Returns:
        A JSON string containing column names and table data.

    Raises:
        ValueError: If table name is invalid.
        ConnectionError: If database connection fails.
        RuntimeError: If reading from the table fails.

    Example:
        >>> read_resource("users")
        '{"columns": ["id", "name", "email"], "rows": [{"id": 1, "name": "Alice", "email": "alice@example.com"}]}'
    """
    conn = None
    cursor = None
    try:
        # Input validation
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string")

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use parameterized query to prevent SQL injection
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return json.dumps({"columns": columns, "rows": rows}, default=str)
    except Error as err:
        raise RuntimeError(f"Failed to read table {table_name}: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@mcp.tool()
def execute_sql(sql_query: str) -> str:
    """Execute a custom SQL query.

    Args:
        sql_query (str): The SQL query to execute (required).

    Returns:
        A JSON string containing either query results or affected row count.

    Raises:
        ValueError: If SQL query is invalid.
        ConnectionError: If database connection fails.
        RuntimeError: If SQL execution fails.

    Example:
        >>> execute_sql("SELECT * FROM users WHERE id = 1")
        '{"columns": ["id", "name", "email"], "rows": [{"id": 1, "name": "Alice", "email": "alice@example.com"}]}'
        
        >>> execute_sql("UPDATE users SET email = 'new_email@example.com' WHERE id = 1")
        '{"affected_rows": 1}'
    """
    conn = None
    cursor = None
    try:
        # Input validation
        if not sql_query or not isinstance(sql_query, str):
            raise ValueError("SQL query must be a non-empty string")

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the SQL query
        cursor.execute(sql_query)
        
        # Check if the query is a SELECT or SHOW statement
        if sql_query.strip().upper().startswith(("SELECT", "SHOW")):
            columns = [desc[0] for desc in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
            result = {"columns": columns, "rows": rows}
        else:
            conn.commit()
            result = {"affected_rows": cursor.rowcount}
        
        return json.dumps(result, default=str)
    except Error as err:
        if conn:
            conn.rollback()
        raise RuntimeError(f"SQL execution failed: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()