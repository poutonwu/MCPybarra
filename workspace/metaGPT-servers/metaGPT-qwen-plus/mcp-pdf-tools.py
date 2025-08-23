import sys
import os
import re
import asyncio
from mcp.server.fastmcp import FastMCP
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
import fitz  # PyMuPDF

# 初始化 FastMCP 服务器
mcp = FastMCP("pdf_processor")


@mcp.tool()
def merge_pdfs(input_files: list[str], output_file: str) -> str:
    """
    将多个PDF文件合并为一个PDF文件。

    Args:
        input_files: 要合并的PDF文件路径列表。
        output_file: 合并后的输出文件路径。

    Returns:
        一个字符串，表示操作结果。

    Raises:
        ValueError: 如果输入文件列表为空或输出文件路径无效。
        FileNotFoundError: 如果任一输入文件不存在。
    """
    if not input_files or not output_file:
        raise ValueError("输入文件列表和输出文件路径都不能为空。")

    pdf_writer = PdfWriter()

    for file_path in input_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 '{file_path}' 不存在。")

        pdf_reader = PdfReader(file_path)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    with open(output_file, "wb") as output_stream:
        pdf_writer.write(output_stream)

    return f"成功合并 {len(input_files)} 个文件到 '{output_file}'。"


@mcp.tool()
def extract_pages(input_file: str, pages: list[int], output_file: str) -> str:
    """
    从PDF文件中提取特定页面并保存为新文件。

    Args:
        input_file: 输入PDF文件路径。
        pages: 要提取的页码列表（从1开始）。
        output_file: 提取后的输出文件路径。

    Returns:
        一个字符串，表示操作结果。

    Raises:
        ValueError: 如果输入文件或输出文件路径无效。
        FileNotFoundError: 如果输入文件不存在。
        IndexError: 如果页码超出范围。
    """
    if not input_file or not output_file:
        raise ValueError("输入文件和输出文件路径都不能为空。")

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"文件 '{input_file}' 不存在。")

    pdf_reader = PdfReader(input_file)
    total_pages = len(pdf_reader.pages)

    pdf_writer = PdfWriter()

    for page_num in pages:
        if page_num < 1 or page_num > total_pages:
            raise IndexError(f"页码 {page_num} 超出范围 (1-{total_pages})。")

        pdf_writer.add_page(pdf_reader.pages[page_num - 1])

    with open(output_file, "wb") as output_stream:
        pdf_writer.write(output_stream)

    return f"成功从 '{input_file}' 提取 {len(pages)} 页到 '{output_file}'。"


@mcp.tool()
def search_pdfs(directory: str, pattern: str) -> list[str]:
    """
    在指定目录中搜索匹配特定模式的PDF文件。

    Args:
        directory: 要搜索的目录路径。
        pattern: 正则表达式模式。

    Returns:
        匹配的PDF文件路径列表。

    Raises:
        ValueError: 如果目录或模式无效。
        NotADirectoryError: 如果指定的目录不是有效目录。
    """
    if not directory or not pattern:
        raise ValueError("目录和搜索模式都不能为空。")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"'{directory}' 不是有效的目录。")

    result = []
    pattern_re = re.compile(pattern)

    for root, _, files in os.walk(directory):
        for file in files:
            if pattern_re.search(file) and file.lower().endswith('.pdf'):
                result.append(os.path.join(root, file))

    return result


@mcp.tool()
def merge_pdfs_ordered(directory: str, pattern: str, output_file: str, fuzzy_match: bool = False) -> str:
    """
    按照指定的顺序模式合并PDF文件。

    Args:
        directory: 要搜索的目录路径。
        pattern: 文件名正则表达式模式。
        output_file: 合并后的输出文件路径。
        fuzzy_match: 是否使用模糊匹配（默认：False）。

    Returns:
        一个字符串，表示操作结果。

    Raises:
        ValueError: 如果目录或输出文件路径无效。
        NotADirectoryError: 如果指定的目录不是有效目录。
    """
    if not directory or not output_file:
        raise ValueError("目录和输出文件路径都不能为空。")

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"'{directory}' 不是有效的目录。")

    input_files = []
    pattern_re = re.compile(pattern)

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            if file.lower().endswith('.pdf'):
                if fuzzy_match and pattern_re.pattern in file:
                    input_files.append(file_path)
                elif not fuzzy_match and pattern_re.match(file):
                    input_files.append(file_path)

    # 对文件进行排序
    input_files.sort(
        key=lambda x: re.search(pattern, os.path.basename(x)).group() if re.search(pattern, os.path.basename(x)) else x)

    if not input_files:
        return f"在 '{directory}' 中未找到匹配模式 '{pattern}' 的PDF文件。"

    pdf_writer = PdfWriter()

    for file_path in input_files:
        pdf_reader = PdfReader(file_path)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)

    with open(output_file, "wb") as output_stream:
        pdf_writer.write(output_stream)

    return f"成功按模式 '{pattern}' 合并 {len(input_files)} 个文件到 '{output_file}'。"


@mcp.tool()
def find_related_pdfs(target_file: str, directory: str = None) -> list[str]:
    """
    根据目标PDF文件内容查找相关的PDF文件。

    Args:
        target_file: 目标PDF文件路径。
        directory: 要搜索的目录路径（默认：目标文件所在目录）。

    Returns:
        相关PDF文件路径列表。

    Raises:
        ValueError: 如果目标文件路径无效。
        FileNotFoundError: 如果目标文件不存在。
        NotADirectoryError: 如果指定的目录不是有效目录。
    """
    if not target_file:
        raise ValueError("目标文件路径不能为空。")

    if not os.path.exists(target_file):
        raise FileNotFoundError(f"文件 '{target_file}' 不存在。")

    if directory and not os.path.isdir(directory):
        raise NotADirectoryError(f"'{directory}' 不是有效的目录。")

    # 使用目标文件名生成搜索模式
    target_dir = directory if directory else os.path.dirname(target_file)
    target_basename = os.path.basename(target_file)
    target_name, _ = os.path.splitext(target_basename)

    # 创建基于文件名的正则表达式模式
    # 将文件名中的数字部分转换为通用模式以进行模糊匹配
    name_pattern = re.sub(r'\d+', r'\\d+', re.escape(target_name))
    pattern = fr"{name_pattern}.*\.pdf$"

    # 读取目标文件的内容
    target_text = ""
    with fitz.open(target_file) as doc:
        for page in doc:
            target_text += page.get_text()

    # 搜索相关文件
    related_files = []
    pattern_re = re.compile(pattern, re.IGNORECASE)

    for root, _, files in os.walk(target_dir):
        for file in files:
            file_path = os.path.join(root, file)

            if pattern_re.search(file) and file.lower().endswith('.pdf') and file_path != target_file:
                # 检查文件内容是否与目标文件相似
                try:
                    with fitz.open(file_path) as doc:
                        first_page_text = doc[0].get_text()
                        if any(word in first_page_text.lower() for word in target_name.lower().split()) or any(
                                word in target_text.lower() for word in first_page_text.lower().split()):
                            related_files.append(file_path)
                except Exception:
                    continue

    return related_files


async def main():
    """主函数，配置并运行服务器。"""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        await mcp.run_stdio_async()
    finally:
        print("PDF处理器服务器已关闭。")


if __name__ == "__main__":
    # 在Windows上, asyncio.run() 可能需要这个策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())