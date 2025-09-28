import os
import json
import mysql.connector
from mysql.connector import Error
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("mcp_mysql_db_manager")

def get_mysql_connection():
    """
    Establish and return a connection to the MySQL database.

    Returns:
        mysql.connector.connection.MySQLConnection: The MySQL database connection object.

    Raises:
        mysql.connector.Error: If the connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", "123456"),
            database=os.environ.get("MYSQL_DATABASE", "user-db")
        )
        return connection
    except Error as e:
        raise Error(f"Error connecting to MySQL: {e}")

@mcp.tool()
def list_resources() -> list:
    """
    Lists all available MySQL tables in the connected database.

    Returns:
        list: A list of table names as strings.

    Example:
        >>> list_resources()
        ['users', 'orders', 'products']

    Raises:
        mysql.connector.Error: If the database query fails.
    """
    connection = None
    cursor = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        return {"error": f"Failed to list tables: {e}"}
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()

@mcp.tool()
def read_resource(table_name: str) -> list:
    """
    Reads the first 100 rows from the specified MySQL table.

    Args:
        table_name (str): The name of the table to read data from.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row in the table.

    Example:
        >>> read_resource("users")
        [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Doe"}]

    Raises:
        ValueError: If the table_name is invalid.
        mysql.connector.Error: If the database query fails.
    """
    if not table_name or not isinstance(table_name, str):
        raise ValueError("Invalid table_name. It must be a non-empty string.")

    connection = None
    cursor = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        return {"error": f"Failed to read table {table_name}: {e}"}
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()

@mcp.tool()
def execute_sql(query: str) -> dict:
    """
    Executes a custom SQL query on the connected MySQL database.

    Args:
        query (str): The SQL query to execute.

    Returns:
        dict: For SELECT or SHOW queries, a list of dictionaries representing the result set.
              For INSERT, UPDATE, DELETE, or other queries, a dictionary with the number of affected rows.

    Example:
        >>> execute_sql("SELECT * FROM users")
        [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Doe"}]

        >>> execute_sql("INSERT INTO users (name) VALUES ('Alice')")
        {"affected_rows": 1}

    Raises:
        ValueError: If the query is invalid.
        mysql.connector.Error: If the database query fails.
    """
    if not query or not isinstance(query, str):
        raise ValueError("Invalid query. It must be a non-empty string.")

    connection = None
    cursor = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query)
        if query.strip().lower().startswith("select") or query.strip().lower().startswith("show"):
            results = cursor.fetchall()
            return results
        else:
            connection.commit()
            return {"affected_rows": cursor.rowcount}
    except Error as e:
        return {"error": f"Failed to execute query: {e}"}
    finally:
        if connection and connection.is_connected():
            if cursor:
                cursor.close()
            connection.close()

if __name__ == "__main__":
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
    mcp.run()