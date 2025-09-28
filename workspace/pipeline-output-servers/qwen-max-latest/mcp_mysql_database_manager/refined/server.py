import os
import mysql.connector
from mysql.connector import Error
import json
from mcp.server.fastmcp import FastMCP
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("mcp_mysql_database_manager")

def get_db_connection():
    """Establish and return a database connection with error handling."""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', '123456'),
            database=os.environ.get('DB_NAME', 'user-db'),
            connect_timeout=10,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        if not connection.is_connected():
            raise ConnectionError("Failed to establish a database connection.")
        return connection
    except Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

@mcp.tool()
def list_resources() -> str:
    """Lists all available MySQL tables in the database and provides access to them as resources.\n\nReturns:\n    A JSON string representing a list of strings, where each string represents the name of a table in the MySQL database.\n\nExample:\n    list_resources()\n    # Returns: [\"table1\", \"table2\", \"table3\"]\n    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return json.dumps(tables)
    except (Error, ConnectionError) as e:
        return json.dumps({"error": f"Database connection failed: {str(e)}"})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def read_resource(table_name: str) -> str:
    """Reads the full data content of a specified table and returns it in rows and columns format.\n    The result is limited to a maximum of 100 records.\n\nArgs:\n    table_name: The name of the MySQL table to read (e.g., 'users').\n\nReturns:\n    A JSON string representing a list of dictionaries, where each dictionary represents a row in the table with column names as keys and row values as values.\n\nExample:\n    read_resource(table_name=\"users\")\n    # Returns: [{\"id\": 1, \"name\": \"Alice\"}, {\"id\": 2, \"name\": \"Bob\"}]
    """
    connection = None
    try:
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Invalid table_name provided. Must be a non-empty string.")
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 100")
        rows = cursor.fetchall()
        return json.dumps(rows)
    except ValueError as ve:
        return json.dumps({"error": str(ve)})
    except (Error, ConnectionError) as e:
        return json.dumps({"error": f"Database connection failed: {str(e)}"})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@mcp.tool()
def execute_sql(query: str) -> str:
    """Executes custom SQL queries on the MySQL database. Supports various SQL operations such as SELECT, SHOW, INSERT, UPDATE, etc., and returns structured results including affected rows or query result sets depending on the type of query executed.\n\nArgs:\n    query: The SQL query to execute (e.g., 'SELECT * FROM users WHERE id = 1').\n\nReturns:\n    A JSON string representing the result set for SELECT and SHOW queries, or an integer indicating the number of affected rows for INSERT, UPDATE, DELETE queries.\n\nExample:\n    execute_sql(query=\"SELECT * FROM users WHERE id = 1\")\n    # Returns: [{\"id\": 1, \"name\": \"Alice\"}]\n\n    execute_sql(query=\"UPDATE users SET name = 'Bob' WHERE id = 1\")\n    # Returns: {\"affected_rows\": 1}"
    """
    connection = None
    try:
        if not query or not isinstance(query, str):
            raise ValueError("Invalid query provided. Must be a non-empty string.")
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        
        if query.strip().upper().startswith(('SELECT', 'SHOW')):
            rows = cursor.fetchall()
            return json.dumps(rows)
        else:
            connection.commit()
            return json.dumps({"affected_rows": cursor.rowcount})
    except ValueError as ve:
        return json.dumps({"error": str(ve)})
    except (Error, ConnectionError) as e:
        return json.dumps({"error": f"Database connection failed: {str(e)}"})
    except mysql.connector.ProgrammingError as pe:
        return json.dumps({"error": f"SQL syntax error: {str(pe)}"})
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # Reconfigure stdout for UTF-8 encoding
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_USER', 'root')
    os.environ.setdefault('DB_PASSWORD', '123456')
    os.environ.setdefault('DB_NAME', 'user-db')
    
    # Reconfigure stdout for UTF-8 encoding
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    mcp.run()