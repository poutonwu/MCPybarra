# mcp_ssh_manager

## Overview

`mcp_ssh_manager` 是一个基于 Model Context Protocol (MCP) 的 SSH 管理服务器，提供远程连接、命令执行和文件传输功能。它允许通过 MCP 协议与远程主机进行安全交互，包括建立连接、运行命令、上传/下载文件以及管理多个会话。

## Installation

确保已安装 Python 3.10 或更高版本，并使用以下命令安装依赖项：

```bash
pip install -r requirements.txt
```

所需依赖项应包含：
- `paramiko`
- `mcp[cli]`

## Running the Server

要启动服务器，请运行以下命令：

```bash
python mcp_ssh_manager.py
```

该命令将启动 MCP 服务器并监听标准输入输出（stdio），以便与其他支持 MCP 的客户端通信。

## Available Tools

以下是 `mcp_ssh_manager` 提供的可用工具及其简要说明：

### `connect`

**用途**: 建立与远程主机的 SSH 连接。  
**参数**:  
- `host`: 主机名或 IP 地址  
- `port`: SSH 端口（默认为 26002）  
- `username`: 登录用户名  
- `password`: 登录密码（可选）  
- `key_path`: 私钥路径（用于密钥认证）  

返回唯一会话 ID，用于后续操作。

---

### `disconnect`

**用途**: 断开指定的 SSH 会话。  
**参数**:  
- `session_id`: 要断开的会话 ID  

成功则返回 `True`。

---

### `list_sessions`

**用途**: 列出当前所有活动的 SSH 会话。  
**返回值**: 包含会话信息（ID、主机、端口、用户名等）的字典列表。

---

### `execute`

**用途**: 在指定会话中执行远程命令。  
**参数**:  
- `session_id`: 有效会话 ID  
- `command`: 要执行的命令  
- `stdin`: 标准输入内容（可选）  
- `timeout`: 执行超时时间（秒）  

返回包含 `stdout`, `stderr`, 和 `exit_status` 的字典。

---

### `upload`

**用途**: 将本地文件上传到远程主机。  
**参数**:  
- `session_id`: 有效会话 ID  
- `local_path`: 本地文件路径  
- `remote_path`: 远程目标路径  

成功则返回 `True`。

---

### `download`

**用途**: 从远程主机下载文件到本地。  
**参数**:  
- `session_id`: 有效会话 ID  
- `remote_path`: 远程文件路径  
- `local_path`: 本地目标路径  

成功则返回 `True`。