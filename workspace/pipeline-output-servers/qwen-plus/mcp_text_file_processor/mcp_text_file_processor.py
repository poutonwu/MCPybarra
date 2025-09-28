import sys
import os
import hashlib
import json
from typing import Dict, List, Optional, Union, Any
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("text_file_processor")

# ----------------------------- 工具函数定义 -----------------------------

def calculate_file_hash(file_path: str) -> str:
    """计算文件的SHA-256哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否安全，防止路径穿越攻击"""
    # 获取当前工作目录的绝对路径
    base_dir = os.path.abspath(os.getcwd())
    
    try:
        # 获取文件的绝对路径
        file_dir = os.path.abspath(file_path)
        
        # 检查文件路径是否在当前工作目录内
        return file_dir.startswith(base_dir)
    except Exception:
        return False

# ----------------------------- 工具实现 -----------------------------

@mcp.tool()
def get_text_file_contents(file_paths: List[str], start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    读取多个文本文件的内容，支持按行范围读取并返回文件哈希值用于并发控制

    Args:
        file_paths: 需要读取的一个或多个文件的路径列表
        start_line: 起始行号（从0开始计数），可选参数
        end_line: 结束行号（包含该行），可选参数

    Returns:
        返回一个JSON字符串，包含：
        - "contents": 每个文件指定范围内的内容行
        - "hashes": 每个文件的SHA-256哈希值

    示例:
        get_text_file_contents(file_paths=["example.txt"], start_line=0, end_line=5)
    """
    try:
        result = {
            "contents": {},
            "hashes": {}
        }

        # 验证参数
        if not isinstance(file_paths, list) or len(file_paths) == 0:
            raise ValueError("file_paths 必须是一个非空列表")
        
        if start_line is not None and end_line is not None and start_line > end_line:
            raise ValueError("start_line 不能大于 end_line")

        for file_path in file_paths:
            # 验证文件路径安全性
            if not validate_file_path(file_path):
                raise ValueError(f"非法的文件路径: {file_path}. 文件路径必须位于当前工作目录内.")

            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                    
                    # 计算实际的起始和结束行
                    actual_start = max(0, start_line) if start_line is not None else 0
                    actual_end = min(len(lines) - 1, end_line) if end_line is not None else len(lines) - 1
                    
                    # 确保实际范围有效
                    if actual_start > actual_end:
                        result["contents"][file_path] = []
                    else:
                        result["contents"][file_path] = lines[actual_start:actual_end + 1]
                    
                    # 计算文件哈希
                    result["hashes"][file_path] = calculate_file_hash(file_path)
            except FileNotFoundError:
                raise ValueError(f"文件未找到: {file_path}")
            except Exception as e:
                raise ValueError(f"读取文件 {file_path} 时发生错误: {str(e)}")

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        # 捕获所有异常并返回错误信息
        error_result = {
            "error": str(e)
        }
        return json.dumps(error_result, ensure_ascii=False)

@mcp.tool()
def create_text_file(file_path: str, content: str) -> str:
    """
    创建新的文本文件并写入内容

    Args:
        file_path: 新建文件的路径
        content: 需要写入文件的初始内容

    Returns:
        返回一个JSON字符串，包含：
        - "success": 布尔值，表示文件创建是否成功
        - "message": 描述操作结果的信息
        - "hash": 如果成功，包含新建文件的SHA-256哈希值

    示例:
        create_text_file(file_path="new_file.txt", content="这是文件内容")
    """
    try:
        # 验证参数
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path 必须是非空字符串")
        
        if not isinstance(content, str):
            raise ValueError("content 必须是字符串类型")
        
        # 验证文件路径安全性
        if not validate_file_path(file_path):
            raise ValueError(f"非法的文件路径: {file_path}. 文件路径必须位于当前工作目录内.")

        # 创建文件所在目录（如果不存在）
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 计算文件哈希
        file_hash = calculate_file_hash(file_path)

        result = {
            "success": True,
            "message": f"文件 {file_path} 创建成功",
            "hash": file_hash
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"创建文件失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False)

@mcp.tool()
def append_text_file_contents(file_path: str, content: str) -> str:
    """
    向现有文本文件追加内容

    Args:
        file_path: 目标文件的路径
        content: 需要追加的内容

    Returns:
        返回一个JSON字符串，包含：
        - "success": 布尔值，表示追加操作是否成功
        - "message": 描述操作结果的信息
        - "new_hash": 如果成功，包含修改后文件的SHA-256哈希值

    示例:
        append_text_file_contents(file_path="existing_file.txt", content="\n这是追加的内容")
    """
    try:
        # 验证参数
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path 必须是非空字符串")
        
        if not isinstance(content, str):
            raise ValueError("content 必须是字符串类型")
        
        # 验证文件路径安全性
        if not validate_file_path(file_path):
            raise ValueError(f"非法的文件路径: {file_path}. 文件路径必须位于当前工作目录内.")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 追加内容到文件
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

        # 计算新哈希
        new_hash = calculate_file_hash(file_path)

        result = {
            "success": True,
            "message": f"成功向文件 {file_path} 追加内容",
            "new_hash": new_hash
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"追加内容失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False)

@mcp.tool()
def delete_text_file_contents(file_path: str, start_line: int, end_line: int, expected_hash: Optional[str] = None) -> str:
    """
    删除文本文件中特定范围的内容

    Args:
        file_path: 需要修改的文件路径
        start_line: 起始行号（从0开始计数）
        end_line: 结束行号（包含该行）
        expected_hash: 文件当前预期的SHA-256哈希值（用于并发控制，可选）

    Returns:
        返回一个JSON字符串，包含：
        - "success": 布尔值，表示删除操作是否成功
        - "message": 描述操作结果的信息
        - "new_hash": 如果成功，包含修改后文件的SHA-256哈希值

    示例:
        delete_text_file_contents(file_path="example.txt", start_line=2, end_line=5)
    """
    try:
        # 验证参数
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path 必须是非空字符串")
        
        if not isinstance(start_line, int):
            raise ValueError("start_line 必须是整数")
        
        if not isinstance(end_line, int):
            raise ValueError("end_line 必须是整数")
        
        # 验证文件路径安全性
        if not validate_file_path(file_path):
            raise ValueError(f"非法的文件路径: {file_path}. 文件路径必须位于当前工作目录内.")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 验证并发控制哈希值
        if expected_hash is not None:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                raise ValueError("文件已被其他进程修改，请刷新后再试")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # 验证行号范围
        if start_line < 0 or end_line >= len(lines):
            raise ValueError(f"行号范围无效。文件共有 {len(lines)} 行，但请求删除的行号范围为 {start_line}-{end_line}")
        
        if start_line > end_line:
            raise ValueError("start_line 不能大于 end_line")

        # 删除指定范围的内容
        del lines[start_line:end_line+1]

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # 计算新哈希
        new_hash = calculate_file_hash(file_path)

        result = {
            "success": True,
            "message": f"已成功从文件 {file_path} 中删除第 {start_line} 到 {end_line} 行 的内容",
            "new_hash": new_hash
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"删除内容失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False)

@mcp.tool()
def insert_text_file_contents(file_path: str, insert_line: int, content: str, expected_hash: Optional[str] = None) -> str:
    """
    在文本文件的指定位置插入内容

    Args:
        file_path: 需要修改的文件路径
        insert_line: 插入位置的行号（在该行之前插入）
        content: 需要插入的内容
        expected_hash: 文件当前预期的SHA-256哈希值（用于并发控制，可选）

    Returns:
        返回一个JSON字符串，包含：
        - "success": 布尔值，表示插入操作是否成功
        - "message": 描述操作结果的信息
        - "new_hash": 如果成功，包含修改后文件的SHA-256哈希值

    示例:
        insert_text_file_contents(file_path="example.txt", insert_line=3, content="这是插入的新内容\n")
    """
    try:
        # 验证参数
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path 必须是非空字符串")
        
        if not isinstance(insert_line, int):
            raise ValueError("insert_line 必须是整数")
        
        if not isinstance(content, str):
            raise ValueError("content 必须是字符串类型")
        
        # 验证文件路径安全性
        if not validate_file_path(file_path):
            raise ValueError(f"非法的文件路径: {file_path}. 文件路径必须位于当前工作目录内.")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 验证并发控制哈希值
        if expected_hash is not None:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                raise ValueError("文件已被其他进程修改，请刷新后再试")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # 验证插入位置
        if insert_line < 0 or insert_line > len(lines):
            raise ValueError(f"插入位置无效。文件共有 {len(lines)} 行，但请求插入的位置为 {insert_line}")

        # 将内容拆分为多行
        content_lines = content.split('\n')
        if content and content[-1] != '\n':  # 如果内容不是以换行符结尾，则添加一个
            content_lines.append('')
        
        # 插入内容
        inserted_lines = [line + '\n' for line in content_lines[:-1]]
        if content_lines[-1]:
            inserted_lines.append(content_lines[-1])
        lines[insert_line:insert_line] = inserted_lines

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # 计算新哈希
        new_hash = calculate_file_hash(file_path)

        result = {
            "success": True,
            "message": f"已成功在文件 {file_path} 的第 {insert_line} 行前插入内容",
            "new_hash": new_hash
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"插入内容失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False)

@mcp.tool()
def patch_text_file_contents(file_path: str, line_number: int, old_content: str, new_content: str, expected_hash: Optional[str] = None) -> str:
    """
    应用精确修改到文件，支持哈希值验证以避免冲突

    Args:
        file_path: 需要修改的文件路径
        line_number: 需要修改的行号
        old_content: 原始行内容（用于验证）
        new_content: 替换的新内容
        expected_hash: 文件当前预期的SHA-256哈希值（用于并发控制，可选）

    Returns:
        返回一个JSON字符串，包含：
        - "success": 布尔值，表示修改操作是否成功
        - "message": 描述操作结果的信息
        - "new_hash": 如果成功，包含修改后文件的SHA-256哈希值

    示例:
        patch_text_file_contents(file_path="example.txt", line_number=4, old_content="旧内容", new_content="新内容")
    """
    try:
        # 验证参数
        if not isinstance(file_path, str) or not file_path.strip():
            raise ValueError("file_path 必须是非空字符串")
        
        if not isinstance(line_number, int):
            raise ValueError("line_number 必须是整数")
        
        if not isinstance(old_content, str):
            raise ValueError("old_content 必须是字符串类型")
        
        if not isinstance(new_content, str):
            raise ValueError("new_content 必须是字符串类型")
        
        # 验证文件路径安全性
        if not validate_file_path(file_path):
            raise ValueError(f"非法的文件路径: {file_path}. 文件路径必须位于当前工作目录内.")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 验证并发控制哈希值
        if expected_hash is not None:
            actual_hash = calculate_file_hash(file_path)
            if actual_hash != expected_hash:
                raise ValueError("文件已被其他进程修改，请刷新后再试")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # 验证行号
        if line_number < 0 or line_number >= len(lines):
            raise ValueError(f"行号无效。文件共有 {len(lines)} 行，但请求修改的行号为 {line_number}")

        # 验证当前行内容
        if lines[line_number].rstrip('\n') != old_content.rstrip('\n'):
            raise ValueError(f"文件内容与预期不符。期望内容: '{old_content}'，实际内容: '{lines[line_number].rstrip('\n')}'")

        # 替换内容
        lines[line_number] = new_content + ('' if lines[line_number].endswith('\n') else '\n')

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # 计算新哈希
        new_hash = calculate_file_hash(file_path)

        result = {
            "success": True,
            "message": f"已成功将文件 {file_path} 的第 {line_number} 行内容替换为 '{new_content}'",
            "new_hash": new_hash
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_result = {
            "success": False,
            "message": f"应用修改失败: {str(e)}"
        }
        return json.dumps(error_result, ensure_ascii=False)

# ----------------------------- 主程序入口 -----------------------------
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()