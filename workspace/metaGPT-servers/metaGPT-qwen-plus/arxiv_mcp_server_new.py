import sys
import asyncio
import re
import os
import aiohttp
import arxiv
from mcp.server.fastmcp import FastMCP
import json

# 初始化 FastMCP 服务器
mcp = FastMCP("arxiv_paper_server")

# 论文存储目录
PAPERS_DIR = "downloaded_papers"

# 确保论文存储目录存在
os.makedirs(PAPERS_DIR, exist_ok=True)

@mcp.tool()
async def search_papers(query: str, max_results: int = 5) -> str:
    """
    根据用户输入的查询条件搜索arXiv论文。

    Args:
        query: 搜索关键词或表达式。
        max_results: 返回的最大结果数，默认为5，范围1-20。

    Returns:
        JSON格式字符串，包含匹配的论文列表，每个论文包含id、标题、摘要、发表日期和链接。

    Raises:
        ValueError: 如果查询为空或max_results超出范围。
    """
    # 输入验证
    if not query or not query.strip():
        raise ValueError("查询不能为空")

    if max_results < 1 or max_results > 20:
        raise ValueError(f"max_results必须在1-20之间，当前值: {max_results}")

    try:
        # 创建搜索客户端
        client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)

        # 执行搜索
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        results = client.results(search)

        # 收集结果
        papers = []
        for paper in results:
            papers.append({
                "id": paper.get_short_id(),
                "title": paper.title,
                "summary": paper.summary,
                "published": paper.published.isoformat(),
                "url": paper.entry_id
            })

        return json.dumps(papers, ensure_ascii=False)

    except Exception as e:
        raise ValueError(f"搜索论文时发生错误: {str(e)}") from e

@mcp.tool()
async def download_paper(paper_id: str) -> str:
    """
    下载指定arXiv论文的PDF文件并存储至本地。

    Args:
        paper_id: 论文的arXiv ID（如1607.08567）。

    Returns:
        下载文件的存储路径。

    Raises:
        ValueError: 如果paper_id格式无效。
        FileNotFoundError: 如果无法找到指定的论文。
    """
    # 验证论文ID格式
    if not re.match(r"^\d{4}\.\d{5}$", paper_id) and not re.match(r"^[a-zA-Z]+(-\d+)+$", paper_id):
        raise ValueError(f"无效的论文ID格式: '{paper_id}'. 正确格式示例: '1607.08567' 或 'cs.LG-2403.02645'")

    try:
        # 获取论文信息
        client = arxiv.Client()
        search = arxiv.Search(query=paper_id, max_results=1)
        result = list(client.results(search))

        if not result:
            raise FileNotFoundError(f"未找到ID为'{paper_id}'的论文")

        paper = result[0]

        # 构建文件名
        safe_title = re.sub(r"[^a-zA-Z0-9]", "_", paper.title[:50])
        filename = f"{safe_title}_{paper_id}.pdf"
        filepath = os.path.join(PAPERS_DIR, filename)

        # 下载论文
        async with aiohttp.ClientSession() as session:
            async with session.get(paper.pdf_url) as response:
                if response.status == 200:
                    with open(filepath, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                else:
                    raise ValueError(f"下载失败，HTTP状态码: {response.status}")

        return filepath

    except Exception as e:
        raise ValueError(f"下载论文时发生错误: {str(e)}") from e

@mcp.tool()
def list_papers() -> str:
    """
    列出本地存储的所有论文。

    Returns:
        JSON格式字符串，包含本地存储的论文列表，每个论文包含文件名和大小。

    Raises:
        ValueError: 如果论文目录不存在。
    """
    if not os.path.exists(PAPERS_DIR):
        raise ValueError(f"论文存储目录不存在: {PAPERS_DIR}")

    # 获取文件列表
    papers = []
    for filename in os.listdir(PAPERS_DIR):
        if filename.endswith('.pdf'):
            filepath = os.path.join(PAPERS_DIR, filename)
            size = os.path.getsize(filepath)
            papers.append({
                "filename": filename,
                "size_kb": round(size / 1024, 2)
            })

    return json.dumps(papers, ensure_ascii=False)

@mcp.tool()
async def read_paper(filename: str) -> str:
    """
    读取指定论文的内容。

    Args:
        filename: 要读取的论文文件名（需存在于论文存储目录中）。

    Returns:
        文件内容的文本字符串。

    Raises:
        ValueError: 如果文件名无效或文件不存在。
        IOError: 如果读取文件时发生错误。
    """
    # 验证文件名格式
    if not filename or not filename.endswith('.pdf'):
        raise ValueError("必须提供有效的PDF文件名")

    filepath = os.path.join(PAPERS_DIR, filename)

    if not os.path.exists(filepath):
        raise ValueError(f"文件不存在: {filepath}")

    try:
        # 使用asyncio执行文件操作以避免阻塞
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, _read_file_sync, filepath)
        return content
    except Exception as e:
        raise IOError(f"读取论文时发生错误: {str(e)}") from e

def _read_file_sync(filepath: str) -> str:
    """同步读取文件的辅助函数"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

async def main():
    """主函数，配置并运行服务器。"""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        print("Starting arXiv Paper Server...")
        await mcp.run_stdio_async()
    except Exception as e:
        print(f"服务器启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    # 在Windows上, asyncio.run() 可能需要这个策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 使用anyio.run()代替asyncio.run()，因为FastMCP已经使用了异步框架
    import anyio
    anyio.run(main)