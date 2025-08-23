import sys
import asyncio
from typing import Optional, Dict, List, Tuple
from mcp.server.fastmcp import FastMCP
from paramiko import SSHClient, AutoAddPolicy, SFTPClient
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import SSHException, AuthenticationException

# 初始化 FastMCP 服务器
mcp = FastMCP("ssh_manager")

class SSHSession:
    """封装SSH会话，支持密码或密钥认证"""
    
    def __init__(self, session_id: str, hostname: str, port: int, username: str):
        self.session_id = session_id
        self.hostname = hostname
        self.port = port
        self.username = username
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.connected = False

    async def connect(self, password: Optional[str] = None, key_file: Optional[str] = None) -> None:
        """建立SSH连接，支持密码或密钥认证"""
        loop = asyncio.get_event_loop()
        try:
            if key_file:
                pkey = await loop.run_in_executor(None, RSAKey.from_private_key_file, key_file)
                await loop.run_in_executor(None, self.client.connect,
                                           self.hostname, self.port, self.username, None, pkey)
            else:
                await loop.run_in_executor(None, self.client.connect,
                                           self.hostname, self.port, self.username, password)
            self.connected = True
        except AuthenticationException as e:
            raise ValueError(f"SSH认证失败: {str(e)}")
        except SSHException as e:
            raise ValueError(f"SSH连接失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"意外错误: {str(e)}")

    def disconnect(self) -> None:
        """断开SSH连接"""
        if self.connected:
            self.client.close()
            self.connected = False

    def execute(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        """在远程主机上执行命令"""
        if not self.connected:
            raise ValueError("SSH连接未建立")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
            stdout_str = ''.join(stdout.readlines())
            stderr_str = ''.join(stderr.readlines())
            exit_status = stdout.channel.recv_exit_status()
            return stdout_str, stderr_str, exit_status
        except SSHException as e:
            raise ValueError(f"执行命令失败: {str(e)}")

    def upload(self, local_path: str, remote_path: str) -> None:
        """上传文件到远程主机"""
        if not self.connected:
            raise ValueError("SSH连接未建立")
        
        try:
            sftp: SFTPClient = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
        except SSHException as e:
            raise ValueError(f"文件上传失败: {str(e)}")

    def download(self, remote_path: str, local_path: str) -> None:
        """从远程主机下载文件"""
        if not self.connected:
            raise ValueError("SSH连接未建立")
        
        try:
            sftp: SFTPClient = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
        except SSHException as e:
            raise ValueError(f"文件下载失败: {str(e)}")


class SSHManager:
    """管理所有SSH会话"""
    
    def __init__(self):
        self.sessions: Dict[str, SSHSession] = {}

    def generate_session_id(self, hostname: str, username: str) -> str:
        """生成唯一的会话ID"""
        base_id = f"{username}@{hostname}"
        counter = 1
        session_id = base_id
        
        while session_id in self.sessions:
            session_id = f"{base_id}_{counter}"
            counter += 1
            
        return session_id

    async def connect(self, 
                     hostname: str, 
                     username: str, 
                     password: Optional[str] = None, 
                     port: int = 22, 
                     key_file: Optional[str] = None) -> str:
        """创建并连接一个新的SSH会话"""
        session_id = self.generate_session_id(hostname, username)
        session = SSHSession(session_id, hostname, port, username)
        
        await session.connect(password=password, key_file=key_file)
        self.sessions[session_id] = session
        
        return session_id

    def disconnect(self, session_id: str) -> None:
        """断开指定的SSH会话"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
            
        session.disconnect()
        del self.sessions[session_id]

    def list_sessions(self) -> List[Dict]:
        """列出所有活跃的SSH会话"""
        return [
            {
                "session_id": session.session_id,
                "hostname": session.hostname,
                "port": session.port,
                "username": session.username,
                "connected": session.connected
            }
            for session in self.sessions.values()
        ]

    def get_session(self, session_id: str) -> SSHSession:
        """获取指定的SSH会话"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")
            
        return session


# 创建全局SSH管理器实例
ssh_manager = SSHManager()


@mcp.tool()
async def connect(hostname: str = '10.70.5.21', username: str = 'pengbocheng', password: Optional[str] = '123456', 
                 port: int = 26002, key_file: Optional[str] = None) -> str:
    """
    建立SSH连接。
    Args:
        hostname: 远程主机名或IP地址  (默认:10.70.5.21)
        username: 登录用户名 (默认:pengbocheng)
        password: 登录密码 (可选， 默认:123456)
        port: SSH端口号，默认为26002 (可选)。
        key_file: 私钥文件路径 (可选，如果使用密码认证则不需要)。

    Returns:
        一个字符串，表示成功建立的会话ID。
        
    示例:
        connect(hostname="192.168.1.100", username="admin", password="secret")
        connect(hostname="192.168.1.100", username="admin", key_file="/path/to/private_key")
    """
    # 输入验证
    if not hostname or not hostname.strip():
        raise ValueError("'hostname' 不能为空。")
    if not username or not username.strip():
        raise ValueError("'username' 不能为空。")
    if password is None and key_file is None:
        raise ValueError("必须提供密码或密钥文件。")
    if password is not None and key_file is not None:
        raise ValueError("只能提供密码或密钥文件中的一种认证方式。")
        
    return await ssh_manager.connect(hostname, username, password, port, key_file)


@mcp.tool()
def disconnect(session_id: str) -> str:
    """
    断开指定的SSH会话。
    
    Args:
        session_id: 要断开的会话ID (必填)。

    Returns:
        一个字符串，表示操作结果（成功或失败）。
        
    示例:
        disconnect(session_id="admin@192.168.1.100")
    """
    # 输入验证
    if not session_id or not session_id.strip():
        raise ValueError("'session_id' 不能为空。")
        
    try:
        ssh_manager.disconnect(session_id)
        return f"会话 {session_id} 已成功断开。"
    except ValueError as e:
        return f"断开会话失败: {str(e)}"


@mcp.tool()
def list_sessions() -> List[Dict]:
    """
    列出所有当前活跃的SSH会话信息。
    
    Returns:
        一个包含会话信息的列表，每个元素是一个字典，包含会话ID、主机名、端口、用户名和连接状态。
        
    示例:
        list_sessions()
    """
    return ssh_manager.list_sessions()


@mcp.tool()
def execute(session_id: str, command: str, timeout: Optional[int] = None) -> Dict:
    """
    在指定的SSH会话中执行命令。
    
    Args:
        session_id: 要执行命令的会话ID (必填)。
        command: 要执行的远程命令 (必填)。
        timeout: 命令执行超时时间(秒)，默认为None (可选)。

    Returns:
        一个字典，包含标准输出、标准错误和退出状态码。
        
    示例:
        execute(session_id="admin@192.168.1.100", command="ls -l", timeout=30)
    """
    # 输入验证
    if not session_id or not session_id.strip():
        raise ValueError("'session_id' 不能为空。")
    if not command or not command.strip():
        raise ValueError("'command' 不能为空。")
        
    session = ssh_manager.get_session(session_id)
    stdout, stderr, exit_code = session.execute(command, timeout)
    
    return {
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code
    }


@mcp.tool()
def upload(session_id: str, local_path: str, remote_path: str) -> str:
    """
    将本地文件上传到远程主机。
    
    Args:
        session_id: 要使用的SSH会话ID (必填)。
        local_path: 本地文件路径 (必填)。
        remote_path: 远程目标路径 (必填)。

    Returns:
        一个字符串，表示上传结果（成功或失败）。
        
    示例:
        upload(session_id="admin@192.168.1.100", local_path="/local/file.txt", remote_path="/remote/file.txt")
    """
    # 输入验证
    if not session_id or not session_id.strip():
        raise ValueError("'session_id' 不能为空。")
    if not local_path or not local_path.strip():
        raise ValueError("'local_path' 不能为空。")
    if not remote_path or not remote_path.strip():
        raise ValueError("'remote_path' 不能为空。")
        
    session = ssh_manager.get_session(session_id)
    session.upload(local_path, remote_path)
    
    return f"文件 {local_path} 成功上传到 {remote_path}"


@mcp.tool()
def download(session_id: str, remote_path: str, local_path: str) -> str:
    """
    从远程主机下载文件到本地。
    
    Args:
        session_id: 要使用的SSH会话ID (必填)。
        remote_path: 远程文件路径 (必填)。
        local_path: 本地目标路径 (必填)。

    Returns:
        一个字符串，表示下载结果（成功或失败）。
        
    示例:
        download(session_id="admin@192.168.1.100", remote_path="/remote/file.txt", local_path="/local/file.txt")
    """
    # 输入验证
    if not session_id or not session_id.strip():
        raise ValueError("'session_id' 不能为空。")
    if not remote_path or not remote_path.strip():
        raise ValueError("'remote_path' 不能为空。")
    if not local_path or not local_path.strip():
        raise ValueError("'local_path' 不能为空。")
        
    session = ssh_manager.get_session(session_id)
    session.download(remote_path, local_path)
    
    return f"文件 {remote_path} 成功下载到 {local_path}"




if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()