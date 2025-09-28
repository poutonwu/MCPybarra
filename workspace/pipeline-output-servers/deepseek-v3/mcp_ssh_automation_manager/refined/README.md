# mcp_ssh_automation_manager

## Overview

`mcp_ssh_automation_manager` 是一个基于 Model Context Protocol (MCP) 的 SSH 自动化管理服务器，允许通过 MCP 客户端建立、管理和操作远程 SSH 会话。该服务器支持连接远程主机、执行命令、上传/下载文件、列出当前会话以及断开连接等操作。

## Installation

确保已安装 Python 3.10 或更高版本，然后使用 pip 安装依赖：

```bash
pip install -r requirements.txt
```

`requirements.txt` 应包含以下内容（或根据实际环境调整）：

```
mcp[cli]
paramiko
```

## Running the Server

运行服务器的命令如下：

```bash
python mcp_ssh_automation_manager.py
```

默认情况下，服务器将连接到 IP 地址为 `10.70.5.21` 的远程主机，使用端口 `26002` 和用户名 `pengbocheng`。

## Available Tools

以下是 `mcp_ssh_automation_manager` 提供的可用工具及其功能描述：

### `connect`

建立到远程服务器的 SSH 连接。支持密码或私钥认证。

**Parameters:**
- `hostname`: 主机名或 IP 地址（默认：`10.70.5.21`）
- `username`: 登录用户名（默认：`pengbocheng`）
- `password`: 登录密码（可选）
- `private_key`: 私钥路径（可选）
- `port`: SSH 端口（默认：`26002`）

**Returns:** 会话 ID 字符串。

### `disconnect`

断开指定的 SSH 会话并释放资源。

**Parameters:**
- `session_id`: 要断开的会话 ID。

**Returns:** 断开状态信息。

### `list_sessions`

列出所有当前活动的 SSH 会话。

**Returns:** 会话列表，每个会话包含 `session_id`, `hostname`, `username`, 和 `status`。

### `execute`

在指定的 SSH 会话中执行命令。

**Parameters:**
- `session_id`: 会话 ID。
- `command`: 要执行的命令。
- `stdin`: 传递给命令的标准输入（可选）。
- `timeout`: 命令执行超时时间（秒，可选）。

**Returns:** 包含 `stdout`, `stderr`, 和 `exit_status` 的字典。

### `upload`

将本地文件上传到远程服务器。

**Parameters:**
- `session_id`: 会话 ID。
- `local_path`: 本地文件路径。
- `remote_path`: 远程目标路径。

**Returns:** 上传结果状态信息。

### `download`

从远程服务器下载文件到本地。

**Parameters:**
- `session_id`: 会话 ID。
- `remote_path`: 远程文件路径。
- `local_path`: 本地目标路径。

**Returns:** 下载结果状态信息。