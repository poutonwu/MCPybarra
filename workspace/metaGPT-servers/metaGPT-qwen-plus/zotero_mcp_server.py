import sys
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("zotero")

# Zotero API 基础URL (示例链接，请替换为实际的API)
ZOTERO_API_BASE = "https://api.zotero.org"
USER_AGENT = "zotero-mcp-server/1.0 (contact@example.com)"

@mcp.tool()
def get_item_metadata(item_key: str) -> str:
    """
    获取指定 Zotero 条目的元数据。

    Args:
        item_key (str): 要查询的条目键值。

    Returns:
        str: 条目的元数据信息。
    """
    url = f"{ZOTERO_API_BASE}/items/{item_key}?format=json"
    headers = {"User-Agent": USER_AGENT}
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.text

@mcp.tool()
def get_item_fulltext(item_key: str) -> str:
    """
    提取指定 Zotero 条目的全文内容。

    Args:
        item_key (str): 要查询的条目键值。

    Returns:
        str: 条目的全文内容。
    """
    url = f"{ZOTERO_API_BASE}/items/{item_key}?format=tei&style=apa"
    headers = {"User-Agent": USER_AGENT}
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.text

@mcp.tool()
def search_items(query: str, search_field: str = "title") -> str:
    """
    在 Zotero 库中执行灵活搜索，支持按标题、创建者、年份或全文搜索。

    Args:
        query (str): 搜索关键词。
        search_field (str): 搜索字段（title, creator, date, 或 fulltext）。

    Returns:
        str: 格式化的搜索结果列表。
    """
    if search_field == "fulltext":
        url = f"{ZOTERO_API_BASE}/items?format=tei&style=apa&q={query}"
    else:
        url = f"{ZOTERO_API_BASE}/items?format=json&q={search_field}:{query}"
    headers = {"User-Agent": USER_AGENT}
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.text

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()