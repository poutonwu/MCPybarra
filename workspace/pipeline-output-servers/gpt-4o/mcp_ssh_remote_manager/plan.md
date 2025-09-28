```markdown
# MCP Server Implementation Plan

## MCP Tools Plan

### 1. **Tool: `connect`**
   - **Description**: Establishes an SSH connection to a remote server using password or private key authentication. Automatically manages the session.
   - **Parameters**:
     - `hostname` (str): The remote server's hostname or IP address.
     - `port` (int, optional): The port number for the SSH connection. Defaults to 22.
     - `username` (str): The username for authentication.
     - `password` (str, optional): The password for authentication (used if `private_key_path` is not provided).
     - `private_key_path` (str, optional): The file path to the private key for key-based authentication.
   - **Return Value**:
     - `session_id` (str): A unique identifier for the established SSH session.

---

### 2. **Tool: `disconnect`**
   - **Description**: Closes an active SSH session and releases its resources.
   - **Parameters**:
     - `session_id` (str): The unique identifier of the SSH session to be terminated.
   - **Return Value**:
     - `status` (str): A confirmation message indicating the session was successfully terminated.

---

### 3. **Tool: `list_sessions`**
   - **Description**: Lists all currently active SSH sessions.
   - **Parameters**: None.
   - **Return Value**:
     - `sessions` (list): A list of dictionaries, where each dictionary contains:
       - `session_id` (str): Unique identifier for the session.
       - `hostname` (str): The remote server's hostname or IP address.
       - `username` (str): The username associated with the session.

---

### 4. **Tool: `execute`**
   - **Description**: Executes a command on a specified SSH session and supports standard input and timeout settings.
   - **Parameters**:
     - `session_id` (str): The unique identifier of the SSH session.
     - `command` (str): The command to be executed on the remote server.
     - `stdin` (str, optional): Data to be passed to the command's standard input.
     - `timeout` (int, optional): The maximum time (in seconds) to wait for the command's execution.
   - **Return Value**:
     - `result` (dict): A dictionary containing:
       - `stdout` (str): The standard output from the command.
       - `stderr` (str): The standard error output from the command.
       - `exit_code` (int): The command's exit status.

---

### 5. **Tool: `upload`**
   - **Description**: Uploads a local file to a specified path on the remote server.
   - **Parameters**:
     - `session_id` (str): The unique identifier of the SSH session.
     - `local_path` (str): The file path of the local file to be uploaded.
     - `remote_path` (str): The destination file path on the remote server.
   - **Return Value**:
     - `status` (str): A confirmation message indicating the file was successfully uploaded.

---

### 6. **Tool: `download`**
   - **Description**: Downloads a file from the remote server to a specified local path.
   - **Parameters**:
     - `session_id` (str): The unique identifier of the SSH session.
     - `remote_path` (str): The file path on the remote server to be downloaded.
     - `local_path` (str): The destination file path on the local machine.
   - **Return Value**:
     - `status` (str): A confirmation message indicating the file was successfully downloaded.

---

## Server Overview
The server is an MCP-based implementation for automated SSH remote management. It provides tools for managing SSH sessions, executing remote commands, and transferring files between the local and remote systems. These tools include the ability to establish and disconnect SSH sessions, list active sessions, execute commands with support for standard input and timeouts, and upload/download files.

---

## File to be Generated
- **File Name**: `ssh_mcp_server.py`
- All functionalities will be implemented in this single Python file.

---

## Dependencies
- **Paramiko**: For SSH connection management, including session handling, command execution, and file transfer.
  - Installation: `pip install paramiko`
- **MCP SDK**: For building the MCP server.
  - Installation: `pip install mcp[cli]`
- **Optional**: `python-dotenv` for managing sensitive configuration like usernames, passwords, or private key paths.
```