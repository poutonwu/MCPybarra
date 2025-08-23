import sys
import httpx
from mcp.server.fastmcp import FastMCP
from bs4 import BeautifulSoup

# 初始化 FastMCP 服务器
mcp = FastMCP("duckduckgo")

# 定义常量
USER_AGENT = "duckduckgo-app/1.0 (contact@example.com)"

@mcp.tool()
async def duckduckgo_search(query: str) -> str:
    """
    在 DuckDuckGo 搜索引擎上检索相关信息。

    Args:
        query: 用户输入的查询内容 (字符串类型，必填)。

    Returns:
        一个包含搜索结果的 JSON 格式字符串。

    Raises:
        ValueError: 如果查询为空或仅包含空白字符。
        httpx.HTTPStatusError: 如果 API 请求失败。
    """
    if not query or not query.strip():
        raise ValueError("'query' 不能为空。")

    search_url = "https://api.duckduckgo.com/search"
    params = {"q": query, "format": "json"}
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient() as client:
        response = await client.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def fetch_content(url: str) -> str:
    """
    根据用户提供的网页 URL 抓取并解析主要文本内容。

    Args:
        url: 用户输入的网页 URL (字符串类型，必填)。

    Returns:
        一个包含清理后的网页主要内容的字符串。

    Raises:
        ValueError: 如果 URL 无效。
        httpx.HTTPStatusError: 如果 网页请求失败。
    """
    if not url or not url.strip():
        raise ValueError("'url' 不能为空。")

    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

        # 使用 BeautifulSoup 解析 HTML 并提取文本
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        content = '\n'.join([p.get_text(strip=True) for p in paragraphs])
        return content

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()