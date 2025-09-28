import os
import sys
import httpx
import re
import asyncio
import json
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from duckduckgo_search import DDGS
import time
import logging

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastMCP 服务器
mcp = FastMCP("duckduckgo_search_and_cont")

# 设置默认 User-Agent
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

@mcp.tool()
async def duck_duck_go_search(query: str, max_results: int = 5) -> str:
    """
    在 DuckDuckGo 搜索引擎上根据查询内容自动检索相关信息，并将搜索结果以结构化格式返回

    Args:
        query: 要搜索的关键词或短语 (必填)
        max_results: 返回的最大结果数量，默认为5，范围1-10 (可选)

    Returns:
        包含搜索结果的字典列表，每个字典包含：
        - title: 搜索结果标题 (string)
        - link: 结果链接 (string)
        - snippet: 结果摘要文本 (string)
        - source: 来源网站域名 (string)

    Raises:
        ValueError: 如果查询为空或max_results超出范围
        RuntimeError: 如果搜索失败

    示例:
        duck_duck_go_search(query="Python编程", max_results=5)
    """
    # --- 健壮性与安全性: 严格的输入验证 ---
    if not query or not query.strip():
        raise ValueError("'query' 参数不能为空。")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results 必须在1到10之间")

    # --- 性能和健壮性: 添加重试逻辑 ---
    retries = 3
    delay = 2
    for attempt in range(retries):
        try:
            logger.info(f"执行搜索尝试 {attempt + 1} 次: {query}")
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r['title'],
                        "link": r['link'],
                        "snippet": r['snippet'],
                        "source": r['hostname']
                    })
            return json.dumps(results, ensure_ascii=False)

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            else:
                raise RuntimeError(f"DuckDuckGo搜索失败: {str(e)}")

@mcp.tool()
async def fetch_content(url: str, remove_ads: bool = True, timeout: int = 10) -> str:
    """
    根据提供的网页 URL 抓取并解析该网页的主要文本内容，去除无关元素后返回

    Args:
        url: 要抓取内容的网页 URL (必填)
        remove_ads: 是否尝试移除广告内容，默认为 True (可选)
        timeout: 请求超时时间（秒），默认为 10 (可选)

    Returns:
        包含网页内容的字典：
        - title: 网页标题 (string)
        - content: 清理后的正文内容 (string)
        - domain: 网站域名 (string)
        - status_code: HTTP 响应状态码 (int)
        - word_count: 内容字数统计 (int)

    Raises:
        ValueError: 如果URL无效
        httpx.HTTPStatusError: 如果HTTP请求失败

    示例:
        fetch_content(url="https://example.com", remove_ads=True, timeout=10)
    """
    # --- 健壮性: 输入验证 ---
    if not url or not url.strip():
        raise ValueError("'url' 参数不能为空")

    if not re.match(r"^https?://", url):
        raise ValueError("URL 必须以 http:// 或 https:// 开头")

    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": DEFAULT_USER_AGENT}) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # 移除script和style标签
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # 如果需要移除广告，尝试识别并删除常见的广告类div
            if remove_ads:
                for ad in soup.select('.ad, .advertisement, [id*="ad_"], [id*="sponsor"]'):
                    ad.decompose()

            title = soup.title.string if soup.title else "无标题"
            content = soup.get_text()
            word_count = len(content.split())

            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            result = {
                "title": title,
                "content": content,
                "domain": domain,
                "status_code": response.status_code,
                "word_count": word_count
            }

            return json.dumps(result, ensure_ascii=False)

        except httpx.HTTPStatusError as e:
            error_result = {
                "title": "",
                "content": f"HTTP请求失败: {str(e)}",
                "domain": "",
                "status_code": e.response.status_code,
                "word_count": 0
            }
            return json.dumps(error_result, ensure_ascii=False)
        except Exception as e:
            error_result = {
                "title": "",
                "content": f"内容抓取失败: {str(e)}",
                "domain": "",
                "status_code": 0,
                "word_count": 0
            }
            return json.dumps(error_result, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()