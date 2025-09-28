# 自动化文本文件处理MCP服务器实现计划

## MCP Tools Plan

### 1. get_text_file_contents
- **Description**: 读取多个文本文件的内容，支持按行范围读取并返回文件哈希值用于并发控制
- **Parameters**:
  - `file_paths`: List[str] - 需要读取的一个或多个文件的路径列表
  - `start_line`: Optional[int] - 起始行号（从0开始计数）
  - `end_line`: Optional[int] - 结束行号（包含该行）
- **Return Value**: Dict[str, Union[List[str], str]] - 返回一个字典，包含：
  - "contents": Dict[str, List[str]] - 每个文件指定范围内的内容行
  - "hashes": Dict[str, str] - 每个文件的SHA-256哈希值

### 2. create_text_file
- **Description**: 创建新的文本文件并写入内容
- **Parameters**:
  - `file_path`: str - 新建文件的路径
  - `content`: str - 需要写入文件的初始内容
- **Return Value**: Dict[str, Union[bool, str]] - 返回一个字典，包含：
  - "success": bool - 文件创建是否成功
  - "message": str - 操作结果的描述信息
  - "hash": Optional[str] - 新建文件的SHA-256哈希值（仅在成功时返回）

### 3. append_text_file_contents
- **Description**: 向现有文本文件追加内容
- **Parameters**:
  - `file_path`: str - 目标文件的路径
  - `content`: str - 需要追加的内容
- **Return Value**: Dict[str, Union[bool, str]] - 返回一个字典，包含：
  - "success": bool - 追加操作是否成功
  - "message": str - 操作结果的描述信息
  - "new_hash": Optional[str] - 修改后文件的SHA-256哈希值（仅在成功时返回）

### 4. delete_text_file_contents
- **Description**: 删除文本文件中特定范围的内容
- **Parameters**:
  - `file_path`: str - 需要修改的文件路径
  - `start_line`: int - 起始行号（从0开始计数）
  - `end_line`: int - 结束行号（包含该行）
  - `expected_hash`: Optional[str] - 文件当前预期的SHA-256哈希值（用于并发控制）
- **Return Value**: Dict[str, Union[bool, str]] - 返回一个字典，包含：
  - "success": bool - 删除操作是否成功
  - "message": str - 操作结果的描述信息
  - "new_hash": Optional[str] - 修改后文件的SHA-256哈希值（仅在成功时返回）

### 5. insert_text_file_contents
- **Description**: 在文本文件的指定位置插入内容
- **Parameters**:
  - `file_path`: str - 需要修改的文件路径
  - `insert_line`: int - 插入位置的行号（在该行之前插入）
  - `content`: str - 需要插入的内容
  - `expected_hash`: Optional[str] - 文件当前预期的SHA-256哈希值（用于并发控制）
- **Return Value**: Dict[str, Union[bool, str]] - 返回一个字典，包含：
  - "success": bool - 插入操作是否成功
  - "message": str - 操作结果的描述信息
  - "new_hash": Optional[str] - 修改后文件的SHA-256哈希值（仅在成功时返回）

### 6. patch_text_file_contents
- **Description**: 应用精确修改到文件，支持哈希值验证以避免冲突
- **Parameters**:
  - `file_path`: str - 需要修改的文件路径
  - `line_number`: int - 需要修改的行号
  - `old_content`: str - 原始行内容（用于验证）
  - `new_content`: str - 替换的新内容
  - `expected_hash`: Optional[str] - 文件当前预期的SHA-256哈希值（用于并发控制）
- **Return Value**: Dict[str, Union[bool, str]] - 返回一个字典，包含：
  - "success": bool - 修改操作是否成功
  - "message": str - 操作结果的描述信息
  - "new_hash": Optional[str] - 修改后文件的SHA-256哈希值（仅在成功时返回）

## Server Overview
本服务器提供一套完整的文本文件处理功能，允许客户端对服务器上的文本文件进行读取、创建、修改和删除操作。所有修改操作都支持基于文件哈希值的并发控制，确保多客户端访问时的数据一致性。

## File Structure
项目将采用单文件结构，所有功能实现在一个Python文件中：
- `text_file_processor_mcp_server.py`：包含所有工具函数定义和服务器初始化代码

## Dependencies
需要以下依赖：
- `mcp[cli]`：MCP协议核心库
- `fastmcp`：FastMCP服务器实现
- `typing_extensions`：用于更好的类型提示支持