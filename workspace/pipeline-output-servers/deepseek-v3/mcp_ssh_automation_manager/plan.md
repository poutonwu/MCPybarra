### **MCP Tools Plan**

#### **1. `connect` Tool**
- **Description**: Automatically establishes an SSH connection to a remote server, supporting either password or key-based authentication. Manages the session internally.
- **Parameters**:
  - `hostname` (str): The remote server's hostname or IP address.
  - `username` (str): The username for authentication.
  - `password` (str, optional): The password for authentication (required if `private_key` is not provided).
  - `private_key` (str, optional): The path to the private key file for authentication (required if `password` is not provided).
  - `port` (int, optional): The SSH port (default: 22).
- **Return Value**: 
  - `session_id` (str): A unique identifier for the active SSH session.

#### **2. `disconnect` Tool**
- **Description**: Automatically disconnects the specified SSH session and releases resources.
- **Parameters**:
  - `session_id` (str): The unique identifier of the SSH session to disconnect.
- **Return Value**: 
  - `status` (str): A success or failure message indicating the session termination.

#### **3. `list_sessions` Tool**
- **Description**: Lists all currently active SSH sessions, including their session IDs and connection details.
- **Parameters**: None.
- **Return Value**: 
  - `sessions` (list[dict]): A list of dictionaries, each containing `session_id`, `hostname`, `username`, and `status`.

#### **4. `execute` Tool**
- **Description**: Executes a command on the specified SSH session, supports optional standard input and timeout settings, and returns the output, error, and exit status.
- **Parameters**:
  - `session_id` (str): The unique identifier of the SSH session.
  - `command` (str): The command to execute.
  - `stdin` (str, optional): Standard input to pass to the command (default: `None`).
  - `timeout` (int, optional): Maximum execution time in seconds (default: `None` for no timeout).
- **Return Value**: 
  - `result` (dict): Contains `stdout` (str), `stderr` (str), and `exit_status` (int).

#### **5. `upload` Tool**
- **Description**: Uploads a local file to a specified path on the remote SSH server.
- **Parameters**:
  - `session_id` (str): The unique identifier of the SSH session.
  - `local_path` (str): The path to the local file.
  - `remote_path` (str): The destination path on the remote server.
- **Return Value**: 
  - `status` (str): A success or failure message.

#### **6. `download` Tool**
- **Description**: Downloads a file from the remote SSH server to a specified local path.
- **Parameters**:
  - `session_id` (str): The unique identifier of the SSH session.
  - `remote_path` (str): The path to the file on the remote server.
  - `local_path` (str): The destination path on the local machine.
- **Return Value**: 
  - `status` (str): A success or failure message.

---

### **Server Overview**
The MCP server will provide automated SSH remote management capabilities, including session establishment, command execution, and file transfer. It adheres to the JSON-RPC 2.0 protocol for seamless integration with LLMs or other clients.

---

### **File to be Generated**
- **Filename**: `mcp_ssh_server.py`

---

### **Dependencies**
- **Required Libraries**:
  - `mcp[cli]` (MCP SDK for server implementation)
  - `paramiko` (SSH library for Python)
  - `httpx` (Optional, for any additional HTTP-based features) 

The server will be self-contained in a single file (`mcp_ssh_server.py`) with all tools implemented as `@mcp.tool()`-decorated functions. No additional files or modules are required.