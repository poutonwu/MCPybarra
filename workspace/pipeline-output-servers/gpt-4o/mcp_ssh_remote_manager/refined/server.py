import os
import json
import sys
from paramiko import SSHClient, AutoAddPolicy, SSHException, AuthenticationException
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_ssh_remote_manager")

# Dictionary to store active sessions
active_sessions = {}

@mcp.tool()
def connect(hostname: str = "10.70.5.21", username: str = 'pengbocheng', password: str = "123456", private_key_path: str = None, port: int = 26002) -> str:
    """
    Establishes an SSH connection to a remote server.

    Args:
        hostname (str): The remote server's hostname or IP address.Defaults to 10.70.5.21.
        username (str): The username for authentication.Defaults to pengbocheng.
        password (str, optional): The password for authentication (used if private_key_path is not provided).
        private_key_path (str, optional): The file path to the private key for key-based authentication.
        port (int, optional): The port number for the SSH connection. Defaults to 26002.

    Returns:
        str: A unique identifier for the established SSH session in JSON format.

    Raises:
        AuthenticationException: If authentication fails.
        SSHException: If the connection fails.
    """
    try:
        # Input validation
        if not hostname:
            return json.dumps({"error": "Invalid hostname", "details": "Hostname cannot be empty"})
        
        if not username:
            return json.dumps({"error": "Invalid username", "details": "Username cannot be empty"})
        
        if password is None and private_key_path is None:
            return json.dumps({"error": "Authentication failed", 
                              "details": "Either password or private key must be provided"})

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())

        try:
            if private_key_path:
                ssh.connect(hostname, port=port, username=username, key_filename=private_key_path, timeout=10)
            else:
                ssh.connect(hostname, port=port, username=username, password=password, timeout=10)
        except SSHException as e:
            # Handle specific SSH connection errors
            if "No route to host" in str(e):
                return json.dumps({"error": "Network unreachable", 
                                 "details": f"Cannot reach {hostname}:{port} - No route to host"})
            elif "Connection refused" in str(e):
                return json.dumps({"error": "Connection refused", 
                                 "details": f"The SSH service on {hostname}:{port} is not available"})
            elif "not found" in str(e):  # Private key not found
                return json.dumps({"error": "Private key not found", 
                                 "details": f"The private key at {private_key_path} could not be loaded"})
            else:
                return json.dumps({"error": "SSH connection failed", 
                                 "details": f"Failed to establish SSH connection: {str(e)}"})

        session_id = f"session_{len(active_sessions) + 1}"
        active_sessions[session_id] = ssh

        return json.dumps({"session_id": session_id})

    except AuthenticationException as e:
        return json.dumps({"error": "Authentication failed", "details": str(e)})
    except Exception as e:
        return json.dumps({"error": "Unexpected error", "details": f"An unexpected error occurred: {str(e)}"})


@mcp.tool()
def disconnect(session_id: str) -> str:
    """
    Closes an active SSH session and releases its resources.

    Args:
        session_id (str): The unique identifier of the SSH session to be terminated.

    Returns:
        str: A confirmation message indicating the session was successfully terminated in JSON format.

    Raises:
        ValueError: If the session ID is invalid.
    """
    try:
        if session_id in active_sessions:
            active_sessions[session_id].close()
            del active_sessions[session_id]
            return json.dumps({"status": "Session terminated successfully"})
        else:
            raise ValueError("Invalid session ID")
    except ValueError as e:
        return json.dumps({"error": "Invalid session ID", "details": str(e)})


@mcp.tool()
def list_sessions() -> str:
    """
    Lists all currently active SSH sessions.

    Returns:
        str: A JSON string containing all active sessions.
    """
    sessions = [{"session_id": session_id, "hostname": ssh.get_transport().getpeername()[0]} for session_id, ssh in active_sessions.items()]
    return json.dumps({"sessions": sessions})


@mcp.tool()
def execute(session_id: str, command: str, stdin: str = None, timeout: int = None) -> str:
    """
    Executes a command on a specified SSH session.

    Args:
        session_id (str): The unique identifier of the SSH session.
        command (str): The command to be executed on the remote server.
        stdin (str, optional): Data to be passed to the command's standard input.
        timeout (int, optional): The maximum time (in seconds) to wait for the command's execution.

    Returns:
        str: A JSON string containing the command's output, error, and exit code.

    Raises:
        ValueError: If the session ID is invalid.
    """
    try:
        if session_id not in active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}. No active session found.")
            
        transport = active_sessions[session_id].get_transport()
        if not transport.is_active():
            raise ValueError(f"Session {session_id} exists but the underlying SSH connection is no longer active.")
            
        channel = transport.open_session()
        if timeout:
            channel.settimeout(timeout)

        channel.exec_command(command)
        if stdin:
            channel.sendall(stdin.encode())

        stdout = channel.recv(1024).decode()
        stderr = channel.recv_stderr(1024).decode()
        exit_code = channel.recv_exit_status()

        return json.dumps({"stdout": stdout, "stderr": stderr, "exit_code": exit_code})
        
    except ValueError as e:
        return json.dumps({"error": "Session error", "details": str(e)})
    except SSHException as e:
        return json.dumps({"error": "SSH error", "details": f"SSH operation failed: {str(e)}"})


@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> str:
    """
    Uploads a local file to a specified path on the remote server.

    Args:
        session_id (str): The unique identifier of the SSH session.
        local_path (str): The file path of the local file to be uploaded.
        remote_path (str): The destination file path on the remote server.

    Returns:
        str: A confirmation message indicating the file was successfully uploaded in JSON format.

    Raises:
        ValueError: If the session ID is invalid.
    """
    try:
        if session_id not in active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}. No active session found.")
            
        sftp = active_sessions[session_id].open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        return json.dumps({"status": "File uploaded successfully"})
        
    except ValueError as e:
        return json.dumps({"error": "Session error", "details": str(e)})
    except FileNotFoundError as e:
        return json.dumps({"error": "File not found", "details": f"Local file not found: {str(e)}"})
    except PermissionError as e:
        return json.dumps({"error": "Permission denied", "details": f"Permission denied accessing file: {str(e)}"})
    except SSHException as e:
        return json.dumps({"error": "SSH error", "details": f"SSH operation failed: {str(e)}"})


@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> str:
    """
    Downloads a file from the remote server to a specified local path.

    Args:
        session_id (str): The unique identifier of the SSH session.
        remote_path (str): The file path on the remote server to be downloaded.
        local_path (str): The destination file path on the local machine.

    Returns:
        str: A confirmation message indicating the file was successfully downloaded in JSON format.

    Raises:
        ValueError: If the session ID is invalid.
    """
    try:
        if session_id not in active_sessions:
            raise ValueError(f"Invalid session ID: {session_id}. No active session found.")
            
        sftp = active_sessions[session_id].open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()
        return json.dumps({"status": "File downloaded successfully"})
        
    except ValueError as e:
        return json.dumps({"error": "Session error", "details": str(e)})
    except FileNotFoundError as e:
        return json.dumps({"error": "File not found", "details": f"Remote file not found: {str(e)}"})
    except PermissionError as e:
        return json.dumps({"error": "Permission denied", "details": f"Permission denied accessing file: {str(e)}"})
    except SSHException as e:
        return json.dumps({"error": "SSH error", "details": f"SSH operation failed: {str(e)}"})


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()