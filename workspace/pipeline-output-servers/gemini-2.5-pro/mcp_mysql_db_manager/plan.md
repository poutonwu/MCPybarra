# MCP Tools Plan

### 1. list_resources

*   **Function Name**: `list_resources`
*   **Description**: 列出当前数据库中所有可用的数据表。此工具不接受任何参数，并返回一个包含所有表名的列表。
*   **Parameters**: None
*   **Return Value**:
    *   **Type**: `dict`
    *   **Content**: 一个包含 `tables` 键的字典，其值为一个字符串列表，每个字符串代表一个数据表名称。
    *   **Example**: `{"tables": ["users", "products", "orders"]}`

### 2. read_resource

*   **Function Name**: `read_resource`
*   **Description**: 读取指定数据表的完整内容，以结构化的行列格式返回最多100条记录。
*   **Parameters**:
    *   `table_name` (str): 需要读取数据的目标数据表名称 (必填)。
*   **Return Value**:
    *   **Type**: `dict`
    *   **Content**: 一个包含 `columns` 和 `rows` 两个键的字典。`columns` 是一个包含列名的列表，`rows` 是一个包含数据行的列表的列表。
    *   **Example**:
        ```json
        {
          "columns": ["id", "name", "email"],
          "rows": [
            [1, "Alice", "alice@example.com"],
            [2, "Bob", "bob@example.com"]
          ]
        }
        ```

### 3. execute_sql

*   **Function Name**: `execute_sql`
*   **Description**: 在MySQL数据库上执行自定义的SQL查询语句。支持数据查询（如 `SELECT`, `SHOW`）和数据操作（如 `INSERT`, `UPDATE`, `DELETE`）。根据查询类型，返回查询结果集或受影响的行数。
*   **Parameters**:
    *   `query` (str): 要执行的SQL查询语句 (必填)。
*   **Return Value**:
    *   **Type**: `dict`
    *   **Content**:
        *   对于 `SELECT` 或 `SHOW` 等返回数据的查询，返回一个类似于 `read_resource` 的结构，包含 `columns` 和 `rows`。
        *   对于 `INSERT`, `UPDATE`, `DELETE` 等数据操作查询，返回一个包含 `affected_rows` 键的字典，其值为受影响的行数。
    *   **Example (SELECT Query)**:
        ```json
        {
          "columns": ["id", "name"],
          "rows": [[1, "Alice"]]
        }
        ```
    *   **Example (UPDATE Query)**:
        ```json
        {
          "affected_rows": 1
        }
        ```

# Server Overview

此MCP服务器旨在提供一个自动化的MySQL数据库管理接口。它允许客户端通过标准化的工具来发现可用的数据表、读取表内容以及执行任意的SQL命令，从而将数据库的底层操作能力安全、便捷地暴露给大语言模型或其他自动化系统。

# File to be Generated

*   `mcp_mysql_server.py`

# Dependencies

*   `mcp`
*   `aiomysql` (用于异步连接和操作MySQL数据库)