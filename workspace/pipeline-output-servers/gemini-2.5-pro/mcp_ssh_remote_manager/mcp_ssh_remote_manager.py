import sys
import json
import uuid
import os
from mcp.server.fastmcp import FastMCP
import paramiko

# Initialize FastMCP server
mcp = FastMCP("mcp_ssh_remote_manager")

# In-memory storage for SSH sessions
sessions = {}

@mcp.tool()
def connect(hostname: str = os.getenv('SSH_HOST'), port: int = os.getenv('SSH_PORT'), username: str = os.getenv('SSH_USERNAME'), password: str = "123456", key_filename: str = None) -> str:
    """Establishes an SSH connection to a remote server and manages the session.

    This tool creates a secure shell (SSH) connection to a specified host.
    Authentication can be performed using a password or a private key file.
    Upon successful connection, a unique session ID is generated and returned,
    which must be used for all subsequent operations with this connection
    (e.g., executing commands, transferring files). The session details are
    stored in-memory for the duration of the server's lifecycle.

    Args:
        hostname (str): The hostname or IP address of the SSH server.
        port (int): The port number of the SSH server (standard is 22).
        username (str): The username for authentication.
        password (str, optional): The password for password-based authentication.
            One of `password` or `key_filename` should be provided. Defaults to None.
        key_filename (str, optional): The local path to the private key for
            key-based authentication. Defaults to None.

    Returns:
        str: A JSON string containing the unique 'session_id' on success,
             or an 'error' message if the connection fails.

    Example:
        # Connect using a password
        connect(hostname="example.com", port=22, username="user", password="your_password")

        # Connect using a private key
        connect(hostname="192.168.1.100", port=22, username="admin", key_filename="/home/user/.ssh/id_rsa")
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password, key_filename=key_filename)
        session_id = str(uuid.uuid4())
        sessions[session_id] = client
        return json.dumps({"session_id": session_id})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def disconnect(session_id: str) -> str:
    """Disconnects an active SSH session.

    This tool closes a specific SSH connection identified by its session ID.
    It terminates the connection to the remote server and removes the session
    from the in-memory store, releasing associated resources.

    Args:
        session_id (str): The unique ID of the session to disconnect. This ID
                          is obtained from a successful `connect` call.

    Returns:
        str: A JSON string confirming the disconnection with a 'status' message,
             or an 'error' message if the session ID is not found or an issue
             occurs during disconnection.

    Example:
        disconnect(session_id="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    """
    try:
        if session_id in sessions:
            sessions[session_id].close()
            del sessions[session_id]
            return json.dumps({"status": "disconnected"})
        else:
            return json.dumps({"error": "Session not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def list_sessions() -> str:
    """Lists all active SSH sessions.

    This tool retrieves a list of all currently active SSH session IDs that
    are being managed by the server. This can be useful for tracking open
    connections.

    Returns:
        str: A JSON string containing a list of 'active_sessions' IDs.

    Example:
        list_sessions()
    """
    return json.dumps({"active_sessions": list(sessions.keys())})

@mcp.tool()
def execute(session_id: str, command: str, timeout: int = 60) -> str:
    """Executes a command on a remote SSH server.

    This tool runs a shell command on the remote server associated with the
    given session ID. It captures the standard output (stdout), standard
    error (stderr), and the exit code of the command.

    Args:
        session_id (str): The ID of the active SSH session.
        command (str): The shell command to execute on the remote server.
        timeout (int, optional): The maximum time in seconds to wait for the
                                 command to complete. Defaults to 60.

    Returns:
        str: A JSON string containing the 'stdout', 'stderr', and 'exit_code'
             from the command execution. Returns an 'error' message if the
             session is not found or an execution error occurs.

    Example:
        execute(session_id="a1b2c3d4-e5f6-7890-1234-567890abcdef", command="ls -l /home/user")
    """
    try:
        if session_id in sessions:
            client = sessions[session_id]
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            return json.dumps({
                "stdout": output,
                "stderr": error,
                "exit_code": exit_code
            })
        else:
            return json.dumps({"error": "Session not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> str:
    """Uploads a file to a remote SSH server using SFTP.

    This tool transfers a file from the local machine (where this server is
    running) to the remote server over an SFTP session. The destination path
    must be an absolute path or a path relative to the user's home directory
    on the remote server.

    Args:
        session_id (str): The ID of the active SSH session.
        local_path (str): The path to the file on the local filesystem to upload.
        remote_path (str): The destination path on the remote server.

    Returns:
        str: A JSON string indicating 'status' of the upload on success, or an
             'error' message if the session is not found or the upload fails.

    Example:
        upload(session_id="a1b2c3d4-e5f6-7890-1234-567890abcdef", local_path="/path/to/local/file.txt", remote_path="/home/user/remote/file.txt")
    """
    try:
        if session_id in sessions:
            client = sessions[session_id]
            sftp = client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return json.dumps({"status": "upload successful"})
        else:
            return json.dumps({"error": "Session not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> str:
    """Downloads a file from a remote SSH server using SFTP.

    This tool transfers a file from the remote server to the local machine
    (where this server is running) over an SFTP session. The local path
    specifies where the downloaded file will be saved.

    Args:
        session_id (str): The ID of the active SSH session.
        remote_path (str): The path to the file on the remote server to download.
        local_path (str): The destination path on the local filesystem.

    Returns:
        str: A JSON string indicating 'status' of the download on success, or an
             'error' message if the session is not found or the download fails.

    Example:
        download(session_id="a1b2c3d4-e5f6-7890-1234-567890abcdef", remote_path="/home/user/remote/file.txt", local_path="/path/to/local/downloaded_file.txt")
    """
    try:
        if session_id in sessions:
            client = sessions[session_id]
            sftp = client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return json.dumps({"status": "download successful"})
        else:
            return json.dumps({"error": "Session not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Reconfigure stdout to ensure UTF-8 encoding, preventing potential
    # UnicodeEncodeError when printing command outputs.
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()