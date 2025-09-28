import sys
import mysql.connector
from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Union, Optional

# Initialize FastMCP server
mcp = FastMCP("mysql_database_manager")

# Database connection configuration (retrieve from environment variables)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "user-db"
}

@mcp.tool()
def list_resources(database_name: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Lists all available MySQL database tables as accessible resources.

    Args:
        database_name (str, optional): Name of the MySQL database. If omitted, lists tables from the default connected database.

    Returns:
        A list of dictionaries, where each dictionary represents a table with keys:
            - `table_name` (str): Name of the table.
            - `schema` (str, optional): Schema name if applicable.

    Raises:
        mysql.connector.Error: If there is an error connecting to the database or executing the query.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        if database_name:
            cursor.execute(f"USE {database_name}")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        result = [{"table_name": table[0]} for table in tables]
        return result

    except mysql.connector.Error as e:
        raise mysql.connector.Error(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def read_resource(table_name: str, limit: int = 100) -> Dict[str, Union[List[str], List[List[str]]]]:
    """
    Reads the full data content of a specified MySQL table (limited to 100 rows).

    Args:
        table_name (str, required): Name of the table to read.
        limit (int, optional): Maximum number of rows to return (default: 100).

    Returns:
        A dictionary with:
            - `columns` (list of str): Column names.
            - `rows` (list of lists): Row data, where each inner list represents a row.

    Raises:
        mysql.connector.Error: If there is an error connecting to the database or executing the query.
        ValueError: If table_name is empty or limit is negative.
    """
    if not table_name:
        raise ValueError("table_name cannot be empty")
    if limit < 0:
        raise ValueError("limit must be non-negative")

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        return {"columns": columns, "rows": rows}

    except mysql.connector.Error as e:
        raise mysql.connector.Error(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def execute_sql(query: str) -> Dict[str, Union[List[str], List[List[str]], int]]:
    """
    Executes a custom SQL query (SELECT, SHOW, INSERT, UPDATE, etc.) and returns structured results.

    Args:
        query (str, required): The SQL query to execute.

    Returns:
        For SELECT/SHOW: A dictionary with `columns` (list of str) and `rows` (list of lists).
        For INSERT/UPDATE/DELETE: A dictionary with `affected_rows` (int) indicating the number of rows modified.

    Raises:
        mysql.connector.Error: If there is an error connecting to the database or executing the query.
        ValueError: If query is empty.
    """
    if not query.strip():
        raise ValueError("query cannot be empty")

    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute(query)

        if query.strip().upper().startswith(("SELECT", "SHOW")):
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            return {"columns": columns, "rows": rows}
        else:
            connection.commit()
            return {"affected_rows": cursor.rowcount}

    except mysql.connector.Error as e:
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
        raise mysql.connector.Error(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()