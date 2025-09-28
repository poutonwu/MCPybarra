# mcp_ssh_remote_manager

## Overview

`mcp_ssh_remote_manager` is an MCP (Model Context Protocol) server that provides a set of tools for managing SSH connections to remote servers. It allows you to connect, execute commands, upload and download files, and manage sessions—all through a structured JSON-based interface designed for integration with large language models.

This server enables automation of remote operations such as executing shell commands, transferring files via SFTP, and managing multiple SSH sessions in memory.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

If you don't already have a `requirements.txt`, it should include:

```
mcp[cli]
paramiko
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_ssh_remote_manager.py
```

The server will initialize and begin listening for MCP client requests over standard input/output.

---

## Available Tools

Below is a list of available tools provided by the `mcp_ssh_remote_manager` server:

### `connect`

**Description:** Establishes an SSH connection to a remote server using either password or key-based authentication.

**Arguments:**
- `hostname` (str): Hostname or IP address of the SSH server.
- `port` (int): Port number of the SSH server (default: 26002).
- `username` (str): Username for authentication.
- `password` (str, optional): Password for login.
- `key_filename` (str, optional): Path to private key file for key-based authentication.

**Returns:** A JSON string containing a unique `session_id`.

---

### `disconnect`

**Description:** Closes an active SSH session identified by its session ID.

**Arguments:**
- `session_id` (str): The session ID obtained from a previous `connect` call.

**Returns:** A JSON confirmation of disconnection or an error message.

---

### `list_sessions`

**Description:** Lists all currently active SSH session IDs.

**Returns:** A JSON list of active session IDs.

---

### `execute`

**Description:** Executes a shell command on a remote server using an established SSH session.

**Arguments:**
- `session_id` (str): Session ID of the active SSH connection.
- `command` (str): Shell command to execute on the remote server.
- `timeout` (int, optional): Command execution timeout in seconds (default: 60).

**Returns:** A JSON object containing `stdout`, `stderr`, and `exit_code` of the executed command.

---

### `upload`

**Description:** Uploads a local file to a remote server using SFTP over an active SSH session.

**Arguments:**
- `session_id` (str): Session ID of the active SSH connection.
- `local_path` (str): Path to the local file to upload.
- `remote_path` (str): Destination path on the remote server.

**Returns:** A JSON status indicating success or failure.

---

### `download`

**Description:** Downloads a file from a remote server to the local machine using SFTP over an active SSH session.

**Arguments:**
- `session_id` (str): Session ID of the active SSH connection.
- `remote_path` (str): Path to the remote file to download.
- `local_path` (str): Local destination path for the downloaded file.

**Returns:** A JSON status indicating success or failure.