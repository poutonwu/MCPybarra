import sys
import paramiko
import uuid
import logging
import json
import os
import time
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("ssh_mcp_server")

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    session_id: str
    host: str
    username: str
    connected_at: float

# 存储活跃会话的字典
active_sessions: Dict[str, Dict[str, Any]] = {}

@mcp.tool()
def connect(host: str = "10.70.5.21", port: int = 26002, username: str = "pengbocheng", password: Optional[str] = None, 
                   key_path: Optional[str] = None, key_passphrase: Optional[str] = None) -> str:
    """
    建立与远程SSH服务器的安全连接，支持密码或密钥认证。

    Args:（默认为已经配好key_path的免密登录的主机）
        host: 目标SSH服务器的IP地址或主机名。（默认：10.70.5.21）
        port: SSH服务端口号，默认22。（默认：26002）
        username: 登录用户名。（默认：pengbocheng）
        password: 登录密码（如果使用密钥认证则不需要）。（默认：123456）
        key_path: 私钥文件路径（如果使用密码认证则不需要）。
        key_passphrase: 密钥文件的密码短语。

    Returns:
        包含会话ID的字符串，用于后续操作标识该连接。

    Raises:
        ValueError: 如果参数验证失败。
        paramiko.SSHException: 如果SSH连接失败。
    """
    try:
        # 参数验证
        if not host or not isinstance(host, str):
            raise ValueError("'host' 必须是有效的字符串。")
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError("'port' 必须是1到65535之间的有效整数。")
        if not username or not isinstance(username, str):
            raise ValueError("'username' 必须是有效的字符串。")
        
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 使用密码或密钥进行连接
        if password is not None:
            ssh.connect(hostname=host, port=port, username=username, password=password)
        elif key_path is not None:
            key = paramiko.RSAKey(filename=key_path, password=key_passphrase)
            ssh.connect(hostname=host, port=port, username=username, pkey=key)
        else:
            raise ValueError("必须提供密码或密钥路径进行认证。")
        
        # 生成唯一会话ID
        session_id = str(uuid.uuid4())
        
        # 存储会话信息和SSH连接对象
        active_sessions[session_id] = {
            'client': ssh,
            'host': host,
            'username': username,
            'connected_at': time.time()
        }
        
        logger.info(f"成功建立SSH连接到 {host}:{port} 作为 {username}")
        return session_id
    except Exception as e:
        logger.error(f"SSH连接失败: {str(e)}")
        raise

@mcp.tool()
def disconnect(session_id: str) -> str:
    """
    安全断开指定的SSH连接并释放相关资源。

    Args:
        session_id: 要断开的会话唯一标识符。

    Returns:
        包含操作结果状态的字符串（成功/失败）。

    Raises:
        ValueError: 如果会话ID无效。
    """
    try:
        # 参数验证
        if session_id not in active_sessions:
            raise ValueError(f"无效的会话ID: {session_id}")
        
        # 获取SSH客户端并关闭连接
        ssh_client = active_sessions[session_id]['client']
        ssh_client.close()
        
        # 从活跃会话中移除
        del active_sessions[session_id]
        
        logger.info(f"成功断开会话ID: {session_id}")
        return f"会话 {session_id} 已成功断开。"
    except Exception as e:
        logger.error(f"断开会话失败: {str(e)}")
        raise

@mcp.tool()
def list_sessions() -> str:
    """
    列出所有当前活跃的SSH会话信息。

    Args:
        无

    Returns:
        JSON格式字符串，包含活跃会话列表及详细信息。
    """
    try:
        # 构建活跃会话列表
        sessions = []
        for session_id, session_info in active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'host': session_info['host'],
                'username': session_info['username'],
                'connected_at': session_info['connected_at']
            })
        
        result = {
            'active_sessions': sessions,
            'total_sessions': len(sessions)
        }
        
        logger.info(f"列出 {len(sessions)} 个活跃会话")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"获取会话列表失败: {str(e)}")
        raise

@mcp.tool()
def execute(session_id: str, command: str, timeout: int = 60, stdin_input: Optional[str] = None) -> str:
    """
    在指定的SSH会话中执行远程命令，支持标准输入和超时设置。

    Args:
        session_id: 要执行命令的会话ID。
        command: 要执行的远程命令。
        timeout: 命令执行超时时间(秒)，默认60秒。
        stdin_input: 传递给命令的标准输入内容。

    Returns:
        JSON格式字符串，包含命令的标准输出、错误输出、退出状态码和执行时间。

    Raises:
        ValueError: 如果参数验证失败。
    """
    try:
        # 参数验证
        if session_id not in active_sessions:
            raise ValueError(f"无效的会话ID: {session_id}")
        if not command or not isinstance(command, str):
            raise ValueError("'command' 必须是非空字符串。")
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("'timeout' 必须是大于0的有效整数。")
        
        # 获取SSH客户端
        ssh_client = active_sessions[session_id]['client']
        
        # 执行命令
        start_time = time.time()
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        
        # 处理标准输入
        if stdin_input is not None:
            stdin.write(stdin_input)
            stdin.flush()
        
        # 获取输出和错误信息
        stdout_data = stdout.read().decode('utf-8')
        stderr_data = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()
        execution_time = time.time() - start_time
        
        result = {
            'stdout': stdout_data,
            'stderr': stderr_data,
            'exit_code': exit_code,
            'execution_time': execution_time
        }
        
        logger.info(f"在会话 {session_id} 执行命令完成，退出码: {exit_code}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"执行命令失败: {str(e)}")
        raise

@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> str:
    """
    将本地文件上传到远程SSH服务器的指定路径。

    Args:
        session_id: 使用的SSH会话ID。
        local_path: 本地文件的完整路径。
        remote_path: 远程服务器上的目标路径。

    Returns:
        包含传输结果状态的字符串（成功/失败）及传输统计信息。

    Raises:
        ValueError: 如果参数验证失败。
    """
    try:
        # 参数验证
        if session_id not in active_sessions:
            raise ValueError(f"无效的会话ID: {session_id}")
        if not local_path or not isinstance(local_path, str):
            raise ValueError("'local_path' 必须是非空字符串。")
        if not remote_path or not isinstance(remote_path, str):
            raise ValueError("'remote_path' 必须是非空字符串。")
        
        # 获取SFTP客户端
        sftp = active_sessions[session_id]['client'].open_sftp()
        
        # 上传文件
        sftp.put(local_path, remote_path)
        
        # 获取文件大小
        local_size = os.path.getsize(local_path)
        
        result = {
            'status': 'success',
            'message': f"文件 {local_path} 成功上传到 {remote_path}",
            'transferred_bytes': local_size
        }
        
        logger.info(f"文件上传成功: {local_path} -> {remote_path}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise

@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> str:
    """
    从远程SSH服务器下载文件到本地指定路径。

    Args:
        session_id: 使用的SSH会话ID。
        remote_path: 远程服务器上的文件路径。
        local_path: 本地保存文件的完整路径。

    Returns:
        包含传输结果状态的字符串（成功/失败）及传输统计信息。

    Raises:
        ValueError: 如果参数验证失败。
    """
    try:
        # 参数验证
        if session_id not in active_sessions:
            raise ValueError(f"无效的会话ID: {session_id}")
        if not remote_path or not isinstance(remote_path, str):
            raise ValueError("'remote_path' 必须是非空字符串。")
        if not local_path or not isinstance(local_path, str):
            raise ValueError("'local_path' 必须是非空字符串。")
        
        # 获取SFTP客户端
        sftp = active_sessions[session_id]['client'].open_sftp()
        
        # 下载文件
        sftp.get(remote_path, local_path)
        
        # 获取文件大小
        remote_size = sftp.stat(remote_path).st_size
        
        result = {
            'status': 'success',
            'message': f"文件 {remote_path} 成功下载到 {local_path}",
            'transferred_bytes': remote_size
        }
        
        logger.info(f"文件下载成功: {remote_path} -> {local_path}")
        return json.dumps(result)
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        raise

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()