import sys
import paramiko
from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Optional
import os

# Initialize the MCP server
mcp = FastMCP("mcp_ssh_automation_manager")

# Global dictionary to manage active SSH sessions
active_sessions: Dict[str, paramiko.SSHClient] = {}
SSH_HOST=os.getenv("SSH_HOST")
SSH_USERNAME=os.getenv("SSH_USERNAME")
SSH_PORT=os.getenv("SSH_PORT")

@mcp.tool()
def connect(hostname: str = SSH_HOST, username: str = SSH_USERNAME, password: Optional[str] = '123456', private_key: Optional[str] = None, port: int = SSH_PORT) -> str:
    """
    Establishes an SSH connection to a remote server.

    Args:
        hostname: The remote server's hostname or IP address.
        username: The username for authentication.
        password: The password for authentication (required if private_key is not provided).
        private_key: The path to the private key file for authentication (required if password is not provided).
        port: The SSH port (default: 22).

    Returns:
        A unique session_id for the active SSH session.

    Raises:
        ValueError: If neither password nor private_key is provided.
        paramiko.SSHException: If the SSH connection fails.
    """
    if not password and not private_key:
        raise ValueError("Either password or private_key must be provided.")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if private_key:
            if not os.path.exists(private_key):
                raise FileNotFoundError(f"Private key file not found: {private_key}")
            key = paramiko.RSAKey.from_private_key_file(private_key)
            client.connect(hostname, port=port, username=username, pkey=key)
        else:
            client.connect(hostname, port=port, username=username, password=password)

        session_id = f"session_{len(active_sessions) + 1}"
        active_sessions[session_id] = client
        return session_id
    except Exception as e:
        client.close()
        raise paramiko.SSHException(f"SSH connection failed: {str(e)}")

@mcp.tool()
def disconnect(session_id: str) -> str:
    """
    Disconnects the specified SSH session and releases resources.

    Args:
        session_id: The unique identifier of the SSH session to disconnect.

    Returns:
        A status message indicating the session termination.

    Raises:
        KeyError: If the session_id does not exist.
    """
    if session_id not in active_sessions:
        raise KeyError(f"Session {session_id} not found.")

    client = active_sessions.pop(session_id)
    client.close()
    return f"Session {session_id} disconnected successfully."

@mcp.tool()
def list_sessions() -> List[Dict[str, str]]:
    """
    Lists all currently active SSH sessions.

    Returns:
        A list of dictionaries, each containing session_id, hostname, username, and status.
    """
    sessions = []
    for session_id, client in active_sessions.items():
        transport = client.get_transport() if client else None
        status = "active" if transport and transport.is_active() else "inactive"
        sessions.append({
            "session_id": session_id,
            "hostname": transport.getpeername()[0] if transport else "unknown",
            "username": transport.get_username() if transport else "unknown",
            "status": status
        })
    return sessions

@mcp.tool()
def execute(session_id: str, command: str, stdin: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, str]:
    """
    Executes a command on the specified SSH session.

    Args:
        session_id: The unique identifier of the SSH session.
        command: The command to execute.
        stdin: Standard input to pass to the command (default: None).
        timeout: Maximum execution time in seconds (default: None for no timeout).

    Returns:
        A dictionary containing stdout, stderr, and exit_status.

    Raises:
        KeyError: If the session_id does not exist.
        paramiko.SSHException: If the command execution fails.
    """
    if session_id not in active_sessions:
        raise KeyError(f"Session {session_id} not found.")

    client = active_sessions[session_id]
    try:
        stdin_stream = stdin.encode('utf-8') if stdin else None
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        
        if stdin_stream:
            stdin_channel = stdout.channel
            stdin_channel.send(stdin_stream)
            stdin_channel.shutdown_write()

        stdout_str = stdout.read().decode('utf-8').strip()
        stderr_str = stderr.read().decode('utf-8').strip()
        exit_status = stdout.channel.recv_exit_status()

        return {
            "stdout": stdout_str,
            "stderr": stderr_str,
            "exit_status": exit_status
        }
    except Exception as e:
        raise paramiko.SSHException(f"Command execution failed: {str(e)}")

@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> str:
    """
    Uploads a local file to a specified path on the remote SSH server.

    Args:
        session_id: The unique identifier of the SSH session.
        local_path: The path to the local file.
        remote_path: The destination path on the remote server.

    Returns:
        A status message indicating the upload result.

    Raises:
        KeyError: If the session_id does not exist.
        FileNotFoundError: If the local file doesn't exist.
        paramiko.SSHException: If the file upload fails.
    """
    if session_id not in active_sessions:
        raise KeyError(f"Session {session_id} not found.")
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local file not found: {local_path}")

    client = active_sessions[session_id]
    sftp = client.open_sftp()
    try:
        sftp.put(local_path, remote_path)
        return f"File {local_path} uploaded to {remote_path} successfully."
    except Exception as e:
        raise paramiko.SSHException(f"File upload failed: {str(e)}")
    finally:
        sftp.close()

@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> str:
    """
    Downloads a file from the remote SSH server to a specified local path.

    Args:
        session_id: The unique identifier of the SSH session.
        remote_path: The path to the file on the remote server.
        local_path: The destination path on the local machine.

    Returns:
        A status message indicating the download result.

    Raises:
        KeyError: If the session_id does not exist.
        paramiko.SSHException: If the file download fails.
    """
    if session_id not in active_sessions:
        raise KeyError(f"Session {session_id} not found.")

    client = active_sessions[session_id]
    sftp = client.open_sftp()
    try:
        sftp.get(remote_path, local_path)
        return f"File {remote_path} downloaded to {local_path} successfully."
    except Exception as e:
        raise paramiko.SSHException(f"File download failed: {str(e)}")
    finally:
        sftp.close()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()