import sys
import mysql.connector
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any, Union

class MySQLMCP:
    """
    MySQL MCP 服务器实现，提供数据库管理工具。
    
    功能：
    1. 列出所有可用的MySQL数据表（list_resources）
    2. 读取指定表的完整数据内容（read_resource）
    3. 执行自定义SQL查询语句（execute_sql）
    """
    
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        初始化MySQL MCP服务器。
        
        Args:
            host: MySQL服务器地址
            user: 数据库用户名
            password: 数据库密码
            database: 要连接的数据库名称
        """
        self.mcp = FastMCP("mysql_db")
        self.db_config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.conn = None
        self._connect()
        self._register_tools()

    def _connect(self):
        """
        建立数据库连接。
        
        Raises:
            mysql.connector.Error: 如果数据库连接失败。
        """
        try:
            self.conn = mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            raise ValueError(f"数据库连接失败: {err}") from err

    def _register_tools(self):
        """
        注册MCP工具。
        """
        @self.mcp.tool()
        def list_resources() -> Dict[str, Any]:
            """
            列出数据库中所有可用的数据表。

            Returns:
                包含数据表列表的字典。

            示例:
                >>> list_resources()
                {'tables': ['users', 'orders', 'products']}
            """
            return {'tables': self.list_tables()}

        @self.mcp.tool()
        def read_resource(table_name: str) -> Dict[str, Any]:
            """
            读取指定表的完整数据内容。

            Args:
                table_name: 要读取数据的表名。

            Returns:
                包含表结构和数据的字典。

            示例:
                >>> read_resource(table_name='users')
                {
                    'columns': ['id', 'name', 'email'],
                    'data': [
                        [1, 'Alice', 'alice@example.com'],
                        [2, 'Bob', 'bob@example.com']
                    ]
                }
            """
            return self.read_table_data(table_name)

        @self.mcp.tool()
        def execute_sql(sql: str) -> Dict[str, Any]:
            """
            执行自定义SQL查询语句。

            Args:
                sql: 要执行的SQL语句。

            Returns:
                包含执行结果的字典。对于SELECT查询，返回查询结果；
                对于其他操作，返回受影响的行数。

            示例:
                >>> execute_sql(sql="SELECT * FROM users WHERE id = 1")
                {
                    'columns': ['id', 'name', 'email'],
                    'data': [[1, 'Alice', 'alice@example.com']]
                }
                
                >>> execute_sql(sql="UPDATE users SET name = 'New Name' WHERE id = 1")
                {'affected_rows': 1}
            """
            return self.execute_custom_sql(sql)

    def list_tables(self) -> List[str]:
        """
        获取数据库中所有表的列表。

        Returns:
            表名列表。
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute("SHOW TABLES")
            result = cursor.fetchall()
            return [row[0] for row in result]
        finally:
            cursor.close()

    def read_table_data(self, table_name: str) -> Dict[str, Any]:
        """
        读取指定表的全部数据。

        Args:
            table_name: 要读取数据的表名。

        Returns:
            包含表结构和数据的字典。

        Raises:
            ValueError: 如果表不存在。
        """
        # 验证表是否存在
        if table_name not in self.list_tables():
            raise ValueError(f"表 '{table_name}' 不存在")

        cursor = self.conn.cursor()
        try:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return {'columns': columns, 'data': data}
        finally:
            cursor.close()

    def execute_custom_sql(self, sql: str) -> Dict[str, Any]:
        """
        执行自定义SQL查询。

        Args:
            sql: 要执行的SQL语句。

        Returns:
            包含执行结果的字典。

        Raises:
            ValueError: 如果SQL语句无效。
            mysql.connector.Error: 如果数据库操作失败。
        """
        cursor = self.conn.cursor()
        try:
            # 检查SQL语句类型
            sql_lower = sql.strip().lower()
            if not sql_lower.startswith(("select", "show", "insert", "update", "delete", "create", "alter", "drop")):
                raise ValueError(f"不支持的SQL语句类型: {sql[:30]}...")

            cursor.execute(sql)
            
            # 处理查询结果
            if sql_lower.startswith(("select", "show")):
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                return {'columns': columns, 'data': data}
            else:
                self.conn.commit()
                return {'affected_rows': cursor.rowcount}
        except mysql.connector.Error as err:
            self.conn.rollback()
            raise err
        finally:
            cursor.close()

    def run(self, transport: str = "stdio") -> None:
        """
        启动MCP服务器。
        
        Args:
            transport: 传输协议 ("stdio", "sse", 或 "http")。
        """
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            self.mcp.run(transport)
        finally:
            if self.conn and self.conn.is_connected():
                self.conn.close()
                print("数据库连接已关闭")

if __name__ == "__main__":
    # 示例用法（需要替换为实际的数据库信息）
    server = MySQLMCP(host="localhost", user="root", password="123456", database="user-db")
    server.run()