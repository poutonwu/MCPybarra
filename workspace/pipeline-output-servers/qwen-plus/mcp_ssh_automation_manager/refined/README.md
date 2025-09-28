# mcp_ssh_automation_manager

## Overview

`mcp_ssh_automation_manager` 是一个基于 Model Context Protocol (MCP) 的 SSH 自动化管理服务器，提供通过编程方式与远程服务器建立安全连接、执行命令、上传/下载文件等功能。它适用于需要自动化操作远程系统的场景，如部署脚本、系统监控和批量任务处理。

该服务支持密码或密钥认证的SSH连接，并提供会话管理功能，可列出、建立和断开多个SSH连接。

---

## Installation

在运行服务器之前，请确保安装了以下依赖：

```bash
pip install -r requirements.txt
```

**requirements.txt 示例内容（根据实际项目调整）：**

```
paramiko>=2.11.0
mcp[cli]>=0.1.0
```

---

## Running the Server

要启动 `mcp_ssh_automation_manager` 服务器，请使用以下命令：

```bash
python mcp_ssh_automation_manager.py
```

默认情况下，服务器将通过标准输入/输出（stdio）运行，适用于本地测试和集成环境。

---

## Available Tools

以下是 `mcp_ssh_automation_manager` 提供的可用工具列表及其简要说明：

### 1. `connect`

**描述**: 建立与远程SSH服务器的安全连接，支持密码或密钥认证。

**参数**:
- `host`: 目标SSH服务器的IP地址或主机名（默认：`10.70.4.146`）
- `port`: SSH服务端口号（默认：`26002`）
- `username`: 登录用户名（默认：`pengbocheng`）
- `password`: 登录密码（如果使用密钥认证则不需要）
- `key_path`: 私钥文件路径（如果使用密码认证则不需要）
- `key_passphrase`: 私钥文件的密码短语

**返回值**: 包含会话ID的字符串，用于后续操作标识该连接。

---

### 2. `disconnect`

**描述**: 安全断开指定的SSH连接并释放相关资源。

**参数**:
- `session_id`: 要断开的会话唯一标识符

**返回值**: 包含操作结果状态的字符串（成功/失败）。

---

### 3. `list_sessions`

**描述**: 列出所有当前活跃的SSH会话信息。

**参数**: 无

**返回值**: JSON格式字符串，包含活跃会话列表及详细信息（如会话ID、主机、用户名、连接时间等）。

---

### 4. `execute`

**描述**: 在指定的SSH会话中执行远程命令，支持标准输入和超时设置。

**参数**:
- `session_id`: 要执行命令的会话ID
- `command`: 要执行的远程命令
- `timeout`: 命令执行超时时间（秒），默认60秒
- `stdin_input`: 传递给命令的标准输入内容（可选）

**返回值**: JSON格式字符串，包含命令的标准输出、错误输出、退出状态码和执行时间。

---

### 5. `upload`

**描述**: 将本地文件上传到远程SSH服务器的指定路径。

**参数**:
- `session_id`: 使用的SSH会话ID
- `local_path`: 本地文件的完整路径
- `remote_path`: 远程服务器上的目标路径

**返回值**: 包含传输结果状态的字符串（成功/失败）及传输统计信息（如传输字节数）。

---

### 6. `download`

**描述**: 从远程SSH服务器下载文件到本地指定路径。

**参数**:
- `session_id`: 使用的SSH会话ID
- `remote_path`: 远程服务器上的文件路径
- `local_path`: 本地保存文件的完整路径

**返回值**: 包含传输结果状态的字符串（成功/失败）及传输统计信息（如传输字节数）。