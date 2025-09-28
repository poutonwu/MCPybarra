import os
import mysql.connector
from mysql.connector import Error
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_mysql_database_manager")

@mcp.tool()
def list_resources() -> str:
    """
    Lists all available MySQL tables in the database and provides access to them as resources.

    Returns:
        A JSON string representing a list of strings, where each string represents the name of a table in the MySQL database.

    Example:
        list_resources()
        # Returns: ["table1", "table2", "table3"]
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', '123456'),
            database=os.environ.get('DB_NAME', 'user-db')
        )
        if not connection.is_connected():
            raise ConnectionError("Failed to establish a database connection.")
        
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return json.dumps(tables)
    except Error as e:
        return json.dumps({"error": str(e)})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def read_resource(table_name: str) -> str:
    """
    Reads the full data content of a specified table and returns it in rows and columns format.
    The result is limited to a maximum of 100 records.

    Args:
        table_name: The name of the MySQL table to read (e.g., 'users').

    Returns:
        A JSON string representing a list of dictionaries, where each dictionary represents a row in the table with column names as keys and row values as values.

    Example:
        read_resource(table_name="users")
        # Returns: [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    """
    connection = None
    try:
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Invalid table_name provided. Must be a non-empty string.")
        
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        if not connection.is_connected():
            raise ConnectionError("Failed to establish a database connection.")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        rows = cursor.fetchall()
        return json.dumps(rows)
    except Error as e:
        return json.dumps({"error": str(e)})
    except ValueError as ve:
        return json.dumps({"error": str(ve)})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def execute_sql(query: str) -> str:
    """
    Executes custom SQL queries on the MySQL database. Supports various SQL operations such as SELECT, SHOW, INSERT, UPDATE, etc., and returns structured results including affected rows or query result sets depending on the type of query executed.

    Args:
        query: The SQL query to execute (e.g., 'SELECT * FROM users WHERE id = 1').

    Returns:
        A JSON string representing the result set for SELECT and SHOW queries, or an integer indicating the number of affected rows for INSERT, UPDATE, DELETE queries.

    Example:
        execute_sql(query="SELECT * FROM users WHERE id = 1")
        # Returns: [{"id": 1, "name": "Alice"}]

        execute_sql(query="UPDATE users SET name = 'Bob' WHERE id = 1")
        # Returns: {"affected_rows": 1}
    """
    connection = None
    try:
        if not query or not isinstance(query, str):
            raise ValueError("Invalid query provided. Must be a non-empty string.")
        
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        if not connection.is_connected():
            raise ConnectionError("Failed to establish a database connection.")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        if query.strip().upper().startswith(('SELECT', 'SHOW')):
            rows = cursor.fetchall()
            return json.dumps(rows)
        else:
            connection.commit()
            return json.dumps({"affected_rows": cursor.rowcount})
    except Error as e:
        return json.dumps({"error": str(e)})
    except ValueError as ve:
        return json.dumps({"error": str(ve)})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    mcp.run()