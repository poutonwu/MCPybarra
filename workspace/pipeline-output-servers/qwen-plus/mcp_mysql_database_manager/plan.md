# MCP MySQL 数据库管理服务器实现计划

## MCP Tools Plan

### 1. `list_resources` 工具
- **Function Name**: `list_resources`
- **Description**: 列出所有可用的MySQL数据表，作为资源提供访问。
- **Parameters**:
  - 无参数
- **Return Value**:
  - 返回一个包含所有数据表名称的列表，格式为：`{"tables": ["table1", "table2", ...]}`

---

### 2. `read_resource` 工具
- **Function Name**: `read_resource`
- **Description**: 读取指定表的完整数据内容，以行和列的格式返回表中的最多100条记录。
- **Parameters**:
  - `table_name`: 字符串类型，表示要读取的数据表名称（必填）
- **Return Value**:
  - 返回一个包含查询结果的字典，格式为：
    ```json
    {
      "columns": ["column1", "column2", ...],
      "rows": [
        {"column1": "value1", "column2": "value2", ...},
        ...
      ]
    }
    ```

---

### 3. `execute_sql` 工具
- **Function Name**: `execute_sql`
- **Description**: 执行自定义SQL查询语句，支持各种SQL操作（如SELECT、SHOW、INSERT、UPDATE等），并根据查询类型返回结构化的结果。
- **Parameters**:
  - `sql_query`: 字符串类型，表示要执行的SQL查询语句（必填）
- **Return Value**:
  - 如果是查询操作（如SELECT）：
    ```json
    {
      "columns": ["column1", "column2", ...],
      "rows": [
        {"column1": "value1", "column2": "value2", ...},
        ...
      ]
    }
    ```
  - 如果是非查询操作（如INSERT、UPDATE、DELETE）：
    ```json
    {
      "affected_rows": 5
    }
    ```

---

## Server Overview
该MCP服务器旨在提供对MySQL数据库的自动化管理功能。用户可以通过以下三个工具与MySQL数据库进行交互：
- `list_resources`: 获取所有可用的数据表名称。
- `read_resource`: 读取指定数据表的内容（最多100条记录）。
- `execute_sql`: 执行自定义SQL查询语句，并返回结构化结果。

---

## File to be Generated
- **File Name**: `mysql_mcp_server.py`
- **Content Description**: 该文件将包含完整的MCP服务器逻辑，包括MySQL数据库连接、工具函数实现以及FastMCP服务器的初始化和运行。

---

## Dependencies
- `mcp[cli]`: 用于构建和运行MCP协议服务器。
- `mysql-connector-python`: 用于连接和操作MySQL数据库。
- `httpx`: 用于处理HTTP请求（如果需要）。