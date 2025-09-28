import sys
import httpx
import re
import asyncio
import json  # 缺失的json导入
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("duckduckgo_search_and_cont")

# --- 性能: 使用共享的 AsyncClient ---
# 通过复用连接，提高多次API调用的性能
client = httpx.AsyncClient()

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
        httpx.HTTPStatusError: 如果API请求失败

    示例:
        duck_duck_go_search(query="Python编程", max_results=5)
    """
    # --- 健壮性与安全性: 严格的输入验证 ---
    # 验证输入格式，防止无效或恶意的输入。
    if not query or not query.strip():
        # --- 透明性: 提供清晰的错误信息 ---
        # 错误信息清晰地说明了问题和期望的格式。
        raise ValueError("'query' 参数不能为空。")

    if not 1 <= max_results <= 10:
        raise ValueError("max_results 必须在1到10之间")

    try:
        # --- 功能性: 正确执行核心逻辑 ---
        # 使用ddg包进行搜索
        from duckduckgo_search import DDGS
        
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r['title'],
                    "link": r['link'],
                    "snippet": r['snippet'],
                    "source": r['hostname']
                })

        # 返回JSON字符串结果
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        # --- 透明性: 提供清晰的错误信息 ---
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

    try:
        # --- 功能性: 执行HTTP请求 ---
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()

        # --- 功能性: 解析HTML内容 ---
        soup = BeautifulSoup(response.text, 'lxml')

        # 移除script和style标签
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # 如果需要移除广告，尝试识别并删除常见的广告类div
        if remove_ads:
            for ad in soup.select('.ad, .advertisement, [id*="ad_"], [id*="sponsor"]'):
                ad.decompose()

        # 获取页面标题
        title = soup.title.string if soup.title else "无标题"

        # 获取正文内容
        content = soup.get_text()
        
        # 统计字数
        word_count = len(content.split())

        # 提取域名
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # 构建结果字典
        result = {
            "title": title,
            "content": content,
            "domain": domain,
            "status_code": response.status_code,
            "word_count": word_count
        }

        # 返回JSON字符串结果
        return json.dumps(result, ensure_ascii=False)
    except httpx.HTTPStatusError as e:
        # --- 透明性: 提供清晰的错误信息 ---
        error_result = {
            "title": "",
            "content": f"HTTP请求失败: {str(e)}",
            "domain": "",
            "status_code": e.response.status_code,
            "word_count": 0
        }
        return json.dumps(error_result, ensure_ascii=False)
    except Exception as e:
        # --- 透明性: 提供清晰的错误信息 ---
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