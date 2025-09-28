import sys
import os
import paramiko
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("mcp_ssh_manager")

# Active sessions storage
active_sessions = {}

@mcp.tool()
def connect(host: str = '10.70.5.21', port: int = 26002, username: str = "pengbocheng", password: str = '123456', key_path: str = None) -> str:
    """
    Establishes an SSH connection to a remote server using either password or key-based authentication.
    Automatically manages the session.

    Args:
        host (str): The hostname or IP address of the remote server.
        port (int, optional): The port number for the SSH connection (default is 22).
        username (str): The username for authentication.
        password (str, optional): The password for password-based authentication.
        key_path (str, optional): The path to the private key file for key-based authentication.

    Returns:
        A unique session identifier (str) representing the established SSH session.

    Raises:
        ValueError: If neither password nor key_path is provided.
        paramiko.AuthenticationException: If authentication fails.
        paramiko.SSHException: If there is an issue establishing the SSH connection.

    Example:
        connect(host="192.168.1.10", port=22, username="admin", password="password123")
    """
    if not password and not key_path:
        raise ValueError("Either password or key_path must be provided.")

    try:
        # Create SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect using password or key
        if password:
            ssh_client.connect(hostname=host, port=port, username=username, password=password)
        elif key_path:
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            ssh_client.connect(hostname=host, port=port, username=username, pkey=private_key)

        # Generate unique session ID
        session_id = f"session_{len(active_sessions) + 1}"
        active_sessions[session_id] = {
            "client": ssh_client,
            "host": host,
            "port": port,
            "username": username
        }
        return session_id

    except paramiko.AuthenticationException as e:
        raise paramiko.AuthenticationException(f"Authentication failed: {e}")
    except paramiko.SSHException as e:
        raise paramiko.SSHException(f"SSH connection error: {e}")

@mcp.tool()
def disconnect(session_id: str) -> bool:
    """
    Disconnects a specified SSH session and releases associated resources.

    Args:
        session_id (str): The unique identifier of the SSH session to disconnect.

    Returns:
        A boolean indicating whether the disconnection was successful.

    Raises:
        ValueError: If the session_id does not exist.

    Example:
        disconnect(session_id="session_1")
    """
    if session_id not in active_sessions:
        raise ValueError(f"No active session found with ID: {session_id}")

    try:
        ssh_client = active_sessions[session_id]["client"]
        ssh_client.close()
        del active_sessions[session_id]
        return True
    except Exception as e:
        raise Exception(f"Error while disconnecting session: {e}")

@mcp.tool()
def list_sessions() -> list:
    """
    Lists all currently active SSH sessions managed by the server.

    Returns:
        A list of dictionaries, each containing details about an active session such as `session_id`, `host`, `port`, `username`.

    Example:
        list_sessions()
    """
    return [
        {"session_id": sid, **details} for sid, details in active_sessions.items()
    ]

@mcp.tool()
def execute(session_id: str, command: str, stdin: str = None, timeout: int = None) -> dict:
    """
    Executes a command on a specified SSH session with options for standard input and timeout settings.
    Returns standard output, error output, and exit status.

    Args:
        session_id (str): The unique identifier of the SSH session.
        command (str): The command to execute on the remote server.
        stdin (str, optional): Standard input to pass to the command.
        timeout (int, optional): Timeout in seconds for the command execution.

    Returns:
        A dictionary containing `stdout` (str), `stderr` (str), and `exit_status` (int).

    Raises:
        ValueError: If the session_id does not exist.
        paramiko.SSHException: If there is an issue executing the command.

    Example:
        execute(session_id="session_1", command="ls -la", timeout=10)
    """
    if session_id not in active_sessions:
        raise ValueError(f"No active session found with ID: {session_id}")

    try:
        ssh_client = active_sessions[session_id]["client"]
        stdin_stream, stdout_stream, stderr_stream = ssh_client.exec_command(command, timeout=timeout)
        
        if stdin:
            stdin_stream.write(stdin)
            stdin_stream.close()

        exit_status = stdout_stream.channel.recv_exit_status()
        stdout = stdout_stream.read().decode('utf-8')
        stderr = stderr_stream.read().decode('utf-8')

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exit_status": exit_status
        }

    except paramiko.SSHException as e:
        raise paramiko.SSHException(f"Command execution failed: {e}")

@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> bool:
    """
    Uploads a local file to a specified path on the remote SSH server.

    Args:
        session_id (str): The unique identifier of the SSH session.
        local_path (str): The path to the local file to upload.
        remote_path (str): The destination path on the remote server.

    Returns:
        A boolean indicating whether the upload was successful.

    Raises:
        ValueError: If the session_id does not exist.
        FileNotFoundError: If the local file does not exist.
        paramiko.SSHException: If there is an issue during file transfer.

    Example:
        upload(session_id="session_1", local_path="/local/file.txt", remote_path="/remote/file.txt")
    """
    if session_id not in active_sessions:
        raise ValueError(f"No active session found with ID: {session_id}")
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")

    try:
        ssh_client = active_sessions[session_id]["client"]
        sftp = ssh_client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return True
    except paramiko.SSHException as e:
        raise paramiko.SSHException(f"File upload failed: {e}")

@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> bool:
    """
    Downloads a file from the remote SSH server to a specified local path.

    Args:
        session_id (str): The unique identifier of the SSH session.
        remote_path (str): The path to the file on the remote server.
        local_path (str): The destination path on the local machine.

    Returns:
        A boolean indicating whether the download was successful.

    Raises:
        ValueError: If the session_id does not exist.
        FileNotFoundError: If the remote file does not exist.
        paramiko.SSHException: If there is an issue during file transfer.

    Example:
        download(session_id="session_1", remote_path="/remote/file.txt", local_path="/local/file.txt")
    """
    if session_id not in active_sessions:
        raise ValueError(f"No active session found with ID: {session_id}")

    try:
        ssh_client = active_sessions[session_id]["client"]
        sftp = ssh_client.open_sftp()

        # Check if the remote file exists
        try:
            sftp.stat(remote_path)
        except IOError:
            raise FileNotFoundError(f"Remote file not found: {remote_path}")

        sftp.get(remote_path, local_path)
        sftp.close()
        return True
    except paramiko.SSHException as e:
        raise paramiko.SSHException(f"File download failed: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()