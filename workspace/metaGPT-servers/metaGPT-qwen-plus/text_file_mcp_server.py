import sys
import os
import hashlib
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("text_file_processor")

@mcp.tool()
def get_text_file_contents(file_paths: list, start_line: int = None, end_line: int = None) -> dict:
    """
    读取多个文本文件内容，支持按行范围读取并返回文件哈希值。

    Args:
        file_paths: 要读取的文件路径列表。
        start_line: 开始行号（可选）。如果指定，则必须同时指定 end_line。
        end_line: 结束行号（可选）。如果指定，则必须同时指定 start_line。

    Returns:
        一个包含文件内容和哈希值的字典。

    Raises:
        ValueError: 如果文件不存在或行号范围无效。
        RuntimeError: 如果读取文件时发生错误。
    """
    try:
        results = {}
        for file_path in file_paths:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise ValueError(f"文件 {file_path} 不存在")

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 验证行号范围
            if start_line is not None and end_line is not None:
                if start_line < 1 or end_line > len(lines):
                    raise ValueError(f"文件 {file_path} 的行号范围无效")
                content = ''.join(lines[start_line-1:end_line])
            else:
                content = ''.join(lines)

            # 计算文件哈希值
            file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

            # 将结果添加到结果字典中
            results[file_path] = {
                "content": content,
                "hash": file_hash
            }

        return results
    except Exception as e:
        raise RuntimeError(f"读取文件时发生错误: {str(e)}")

@mcp.tool()
def create_text_file(file_path: str, content: str) -> dict:
    """
    创建新文本文件并写入内容。

    Args:
        file_path: 要创建的文件路径。
        content: 要写入的内容。

    Returns:
        一个包含操作结果和文件哈希值的字典。

    Raises:
        ValueError: 如果文件已经存在。
        RuntimeError: 如果创建文件时发生错误。
    """
    try:
        # 检查文件是否已经存在
        if os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 已经存在")

        # 写入内容到新文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # 计算文件哈希值
        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        return {
            "message": f"文件 {file_path} 创建成功",
            "hash": file_hash
        }
    except Exception as e:
        raise RuntimeError(f"创建文件时发生错误: {str(e)}")

@mcp.tool()
def append_text_file_contents(file_path: str, content: str, expected_hash: str = None) -> dict:
    """
    向现有文本文件追加内容。

    Args:
        file_path: 要追加内容的文件路径。
        content: 要追加的内容。
        expected_hash: 文件的预期哈希值（可选）。如果提供，将验证文件内容与哈希值匹配。

    Returns:
        一个包含操作结果和新文件哈希值的字典。

    Raises:
        ValueError: 如果文件不存在或哈希验证失败。
        RuntimeError: 如果追加内容时发生错误。
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # 哈希验证
        if expected_hash is not None:
            current_hash = hashlib.sha256(current_content.encode('utf-8')).hexdigest()
            if current_hash != expected_hash:
                raise ValueError(f"哈希验证失败。当前文件哈希: {current_hash}, 预期哈希: {expected_hash}")

        # 追加内容到文件
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

        # 计算新文件哈希值
        new_hash = hashlib.sha256((current_content + content).encode('utf-8')).hexdigest()

        return {
            "message": f"内容已成功追加到文件 {file_path}",
            "hash": new_hash
        }
    except Exception as e:
        raise RuntimeError(f"追加内容到文件时发生错误: {str(e)}")

@mcp.tool()
def delete_text_file_contents(file_path: str, start_line: int, end_line: int, expected_hash: str = None) -> dict:
    """
    删除文本文件中特定范围的内容。

    Args:
        file_path: 要修改的文件路径。
        start_line: 开始行号（包括）。
        end_line: 结束行号（包括）。
        expected_hash: 文件的预期哈希值（可选）。如果提供，将验证文件内容与哈希值匹配。

    Returns:
        一个包含操作结果和新文件哈希值的字典。

    Raises:
        ValueError: 如果文件不存在、行号范围无效或哈希验证失败。
        RuntimeError: 如果删除内容时发生错误。
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 验证行号范围
        if start_line < 1 or end_line > len(lines):
            raise ValueError(f"文件 {file_path} 的行号范围无效")

        # 读取文件的当前内容以进行哈希验证
        current_content = ''.join(lines)

        # 哈希验证
        if expected_hash is not None:
            current_hash = hashlib.sha256(current_content.encode('utf-8')).hexdigest()
            if current_hash != expected_hash:
                raise ValueError(f"哈希验证失败。当前文件哈希: {current_hash}, 预期哈希: {expected_hash}")

        # 删除指定范围的内容
        modified_lines = lines[:start_line-1] + lines[end_line:]

        # 写回修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)

        # 计算新文件哈希值
        new_content = ''.join(modified_lines)
        new_hash = hashlib.sha256(new_content.encode('utf-8')).hexdigest()

        return {
            "message": f"文件 {file_path} 的内容删除成功",
            "hash": new_hash
        }
    except Exception as e:
        raise RuntimeError(f"删除文件内容时发生错误: {str(e)}")

@mcp.tool()
def insert_text_file_contents(file_path: str, line_number: int, content: str, expected_hash: str = None) -> dict:
    """
    在文本文件的指定位置插入内容。

    Args:
        file_path: 要修改的文件路径。
        line_number: 插入位置的行号（从1开始计数）。
        content: 要插入的内容。
        expected_hash: 文件的预期哈希值（可选）。如果提供，将验证文件内容与哈希值匹配。

    Returns:
        一个包含操作结果和新文件哈希值的字典。

    Raises:
        ValueError: 如果文件不存在、行号无效或哈希验证失败。
        RuntimeError: 如果插入内容时发生错误。
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 验证行号
        if line_number < 1 or line_number > len(lines) + 1:
            raise ValueError(f"文件 {file_path} 的行号无效")

        # 读取文件的当前内容以进行哈希验证
        current_content = ''.join(lines)

        # 哈希验证
        if expected_hash is not None:
            current_hash = hashlib.sha256(current_content.encode('utf-8')).hexdigest()
            if current_hash != expected_hash:
                raise ValueError(f"哈希验证失败。当前文件哈希: {current_hash}, 预期哈希: {expected_hash}")

        # 插入内容
        lines.insert(line_number - 1, content + '\n')

        # 写回修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        # 计算新文件哈希值
        new_content = ''.join(lines)
        new_hash = hashlib.sha256(new_content.encode('utf-8')).hexdigest()

        return {
            "message": f"内容已成功插入到文件 {file_path}",
            "hash": new_hash
        }
    except Exception as e:
        raise RuntimeError(f"插入内容到文件时发生错误: {str(e)}")

@mcp.tool()
def patch_text_file_contents(file_path: str, old_content: str, new_content: str, expected_hash: str = None) -> dict:
    """
    应用精确修改到文本文件，并支持哈希验证。

    Args:
        file_path: 要修改的文件路径。
        old_content: 需要被替换的旧内容。
        new_content: 替换的新内容。
        expected_hash: 文件的预期哈希值（可选）。如果提供，将验证文件内容与哈希值匹配。

    Returns:
        一个包含操作结果和新文件哈希值的字典。

    Raises:
        ValueError: 如果文件不存在、旧内容不匹配或哈希验证失败。
        RuntimeError: 如果修改文件时发生错误。
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise ValueError(f"文件 {file_path} 不存在")

        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # 哈希验证
        if expected_hash is not None:
            current_hash = hashlib.sha256(current_content.encode('utf-8')).hexdigest()
            if current_hash != expected_hash:
                raise ValueError(f"哈希验证失败。当前文件哈希: {current_hash}, 预期哈希: {expected_hash}")

        # 检查旧内容是否存在
        if old_content not in current_content:
            raise ValueError(f"未找到需要替换的旧内容: {old_content}")

        # 替换内容
        modified_content = current_content.replace(old_content, new_content, 1)

        # 写回修改后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        # 计算新文件哈希值
        new_hash = hashlib.sha256(modified_content.encode('utf-8')).hexdigest()

        return {
            "message": f"文件 {file_path} 内容修改成功",
            "hash": new_hash
        }
    except Exception as e:
        raise RuntimeError(f"修改文件内容时发生错误: {str(e)}")

# 所有功能方法已实现，现在运行服务器

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()