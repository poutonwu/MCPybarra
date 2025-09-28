# mcp_ssh_remote_manager

## Overview
The `mcp_ssh_remote_manager` is an MCP (Model Context Protocol) server that provides a set of tools for managing remote servers via SSH. It allows LLMs to connect to remote hosts, execute commands, upload and download files, and manage active sessions.

This server enables secure and programmatic access to remote systems using either password-based or key-based authentication. It supports operations such as:
- Establishing and closing SSH connections
- Executing shell commands remotely
- Transferring files via SFTP
- Listing active sessions

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
paramiko
mcp[cli]
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_ssh_remote_manager.py
```

This will launch the MCP server using the default `stdio` transport protocol, allowing clients to communicate with it via standard input/output.

## Available Tools

### 1. **connect**
Establishes an SSH connection to a remote server.

**Args:**
- `hostname` (str): Remote hostname or IP address.
- `username` (str): Username for authentication.
- `password` (str, optional): Password for authentication.
- `private_key_path` (str, optional): Path to private key file for key-based authentication.
- `port` (int, optional): SSH port (default: 22).

**Returns:** A session ID for the established connection.

---

### 2. **disconnect**
Closes an active SSH session.

**Args:**
- `session_id` (str): The unique identifier of the session to terminate.

**Returns:** Confirmation that the session was closed successfully.

---

### 3. **list_sessions**
Lists all currently active SSH sessions.

**Returns:** A JSON list containing session IDs and associated hostnames.

---

### 4. **execute**
Runs a shell command on a connected remote server.

**Args:**
- `session_id` (str): Session ID of the active connection.
- `command` (str): Command to execute.
- `stdin` (str, optional): Data to pass to the command's standard input.
- `timeout` (int, optional): Maximum execution time in seconds.

**Returns:** Output, error messages, and exit code from the executed command.

---

### 5. **upload**
Uploads a local file to the remote server.

**Args:**
- `session_id` (str): Session ID of the active connection.
- `local_path` (str): Path to the local file.
- `remote_path` (str): Destination path on the remote server.

**Returns:** Confirmation that the file was uploaded successfully.

---

### 6. **download**
Downloads a file from the remote server to the local machine.

**Args:**
- `session_id` (str): Session ID of the active connection.
- `remote_path` (str): Path to the remote file.
- `local_path` (str): Destination path on the local machine.

**Returns:** Confirmation that the file was downloaded successfully.