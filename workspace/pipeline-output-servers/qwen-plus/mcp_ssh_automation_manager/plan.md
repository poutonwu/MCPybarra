# SSH 远程管理 MCP 服务器实现计划

## MCP 工具计划

### 1. `connect` 工具
- **描述**: 建立与远程SSH服务器的安全连接，支持密码或密钥认证
- **参数**:
  - `host` (str): 目标SSH服务器的IP地址或主机名
  - `port` (int): SSH服务端口号，默认22
  - `username` (str): 登录用户名
  - `password` (str, optional): 登录密码（如果使用密钥认证则不需要）
  - `key_path` (str, optional): 私钥文件路径（如果使用密码认证则不需要）
  - `key_passphrase` (str, optional): 密钥文件的密码短语
- **返回值**: 包含会话ID的字符串，用于后续操作标识该连接

### 2. `disconnect` 工具
- **描述**: 安全断开指定的SSH连接并释放相关资源
- **参数**:
  - `session_id` (str): 要断开的会话唯一标识符
- **返回值**: 包含操作结果状态的字符串（成功/失败）

### 3. `list_sessions` 工具
- **描述**: 列出所有当前活跃的SSH会话信息
- **参数**: 无
- **返回值**: JSON格式字符串，包含以下字段：
  - `active_sessions`: 活跃会话列表，每个条目包含：
    - `session_id`: 会话唯一标识符
    - `host`: 连接的主机地址
    - `username`: 登录用户名
    - `connected_at`: 连接建立时间戳

### 4. `execute` 工具
- **描述**: 在指定的SSH会话中执行远程命令，支持标准输入和超时设置
- **参数**:
  - `session_id` (str): 要执行命令的会话ID
  - `command` (str): 要执行的远程命令
  - `timeout` (int, optional): 命令执行超时时间(秒)，默认60秒
  - `stdin_input` (str, optional): 传递给命令的标准输入内容
- **返回值**: JSON格式字符串，包含：
  - `stdout`: 命令的标准输出
  - `stderr`: 命令的错误输出
  - `exit_code`: 命令的退出状态码
  - `execution_time`: 实际执行时间(秒)

### 5. `upload` 工具
- **描述**: 将本地文件上传到远程SSH服务器的指定路径
- **参数**:
  - `session_id` (str): 使用的SSH会话ID
  - `local_path` (str): 本地文件的完整路径
  - `remote_path` (str): 远程服务器上的目标路径
- **返回值**: 包含传输结果状态的字符串（成功/失败）及传输统计信息

### 6. `download` 工具
- **描述**: 从远程SSH服务器下载文件到本地指定路径
- **参数**:
  - `session_id` (str): 使用的SSH会话ID
  - `remote_path` (str): 远程服务器上的文件路径
  - `local_path` (str): 本地保存文件的完整路径
- **返回值**: 包含传输结果状态的字符串（成功/失败）及传输统计信息

## 服务器概述
本MCP服务器实现旨在提供一个安全、高效的SSH远程管理解决方案。它允许通过标准化接口自动执行SSH连接管理、远程命令执行以及文件传输操作。服务器采用会话管理机制跟踪所有活跃连接，并为每个操作提供详细的输入验证和错误处理。

## 文件生成计划
- **文件名**: `ssh_mcp_server.py`
- **内容**: 单一Python文件将包含完整的MCP服务器实现，包括SSH连接管理、会话跟踪、远程命令执行和文件传输功能。代码将遵循MCP协议规范，利用FastMCP框架和Paramiko库实现SSH功能。

## 依赖项
- `mcp[cli]`: Model Context Protocol SDK
- `paramiko`: SSHv2协议库，用于安全连接管理
- `uuid`: 生成安全的非确定性会话ID
- `logging`: 记录服务器活动和错误信息
- `typing`: 类型提示支持
- `json`: 数据序列化/反序列化
- `dataclasses`: 简化数据模型定义