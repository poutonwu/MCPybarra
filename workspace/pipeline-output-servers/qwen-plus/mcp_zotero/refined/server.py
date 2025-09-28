import sys
import httpx
import os
from urllib.parse import urlencode
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_zotero")

# Set up Zotero API base URL and headers
ZOTERO_API_BASE = "https://api.zotero.org"
USER_AGENT = "mcp_zotero_server/1.0 (contact@example.com)"

# Get Zotero credentials from environment variables
ZOTERO_LIBRARY_ID = os.getenv('ZOTERO_LIBRARY_ID')
ZOTERO_API_KEY = os.getenv('ZOTERO_API_KEY')
ZOTERO_LIBRARY_TYPE = os.getenv('ZOTERO_LIBRARY_TYPE')  # 'user' or 'group'

# Configure proxy if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Create a shared async client for better performance
client = httpx.AsyncClient(
    base_url=ZOTERO_API_BASE,
    headers={
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {ZOTERO_API_KEY}"
    }
)

@mcp.tool()
async def get_item_metadata(item_key: str) -> dict:
    """
    获取指定 Zotero 条目的详细元数据。

    Args:
        item_key: 要获取元数据的 Zotero 条目键值，必须是字符串类型且非空。

    Returns:
        返回包含条目详细元数据的 JSON 字典，包括标题、作者、出版年份等信息。

    Raises:
        ValueError: 如果 item_key 无效或格式不正确。
    """
    # 验证输入参数
    if not item_key or not isinstance(item_key, str):
        return {
            "error": "Invalid input",
            "message": "item_key 必须是非空字符串",
            "code": 400
        }

    # 构建API请求URL
    url = f"/{ZOTERO_LIBRARY_TYPE}s/{ZOTERO_LIBRARY_ID}/items/{item_key}?format=json"
    
    try:
        # 发送GET请求获取元数据
        response = await client.get(url)
        
        if response.status_code == 404:
            return {
                "error": "Item not found",
                "message": f"未找到 item_key 为 '{item_key}' 的 Zotero 条目",
                "code": 404
            }
        
        response.raise_for_status()
        
        # 解析响应数据
        item_data = response.json()
        
        # 提取并结构化元数据
        metadata = {
            "title": item_data.get("data", {}).get("title", "无标题"),
            "creators": [
                {"name": creator.get("name", "无创作者")}
                for creator in item_data.get("data", {}).get("creators", [])
            ],
            "year": item_data.get("data", {}).get("date", "未知年份"),
            "item_type": item_data.get("data", {}).get("itemType", "未知类型"),
            "tags": item_data.get("data", {}).get("tags", []),
            "collections": item_data.get("data", {}).get("collections", []),
            "abstract": item_data.get("data", {}).get("abstractNote", ""),
            "publication_title": item_data.get("data", {}).get("publicationTitle", ""),
            "volume": item_data.get("data", {}).get("volume", ""),
            "issue": item_data.get("data", {}).get("issue", ""),
            "pages": item_data.get("data", {}).get("pages", ""),
            "doi": item_data.get("data", {}).get("DOI", ""),
            "isbn": item_data.get("data", {}).get("ISBN", "")
        }
        
        return {
            "metadata": metadata,
            "status": "success",
            "code": 200
        }
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "error": "Item not found",
                "message": f"未找到 item_key 为 '{item_key}' 的 Zotero 条目",
                "code": 404
            }
        else:
            return {
                "error": "Server error",
                "message": f"获取 Zotero 元数据时发生错误: {str(e)}",
                "code": e.response.status_code
            }

@mcp.tool()
async def get_item_fulltext(item_key: str) -> dict:
    """
    提取指定 Zotero 条目的全文内容。

    Args:
        item_key: 要提取全文的 Zotero 条目键值，必须是字符串类型且非空。

    Returns:
        返回包含条目全文内容的字典，如果条目没有全文内容则返回空字符串。
    """
    # 验证输入参数
    if not item_key or not isinstance(item_key, str):
        return {
            "error": "Invalid input",
            "message": "item_key 必须是非空字符串",
            "code": 400
        }

    # 构建API请求URL
    url = f"/{ZOTERO_LIBRARY_TYPE}s/{ZOTERO_LIBRARY_ID}/items/{item_key}/fulltext?format=text"
    
    try:
        # 发送GET请求获取全文内容
        response = await client.get(url)
        
        if response.status_code == 404:
            # 如果返回404，表示该条目没有全文内容
            return {
                "fulltext": "",
                "message": "该条目没有可用的全文内容",
                "code": 200
            }
        
        response.raise_for_status()
        
        # 返回全文内容
        return {
            "fulltext": response.text,
            "status": "success",
            "code": 200
        }
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "error": "Item not found",
                "message": f"未找到 item_key 为 '{item_key}' 的 Zotero 条目",
                "code": 404
            }
        elif e.response.status_code == 500:
            return {
                "error": "Server internal error",
                "message": "服务器内部错误：可能是无效的附件路径或服务器问题导致无法获取全文。请确认条目是否包含附件，并稍后重试。",
                "code": 500
            }
        else:
            return {
                "error": "Server error",
                "message": f"获取 Zotero 全文内容时发生错误: {str(e)}",
                "code": e.response.status_code
            }

@mcp.tool()
async def search_items(query: str, search_type: str = "title", page: int = 1, items_per_page: int = 20) -> dict:
    """
    在 Zotero 库中执行灵活搜索，支持按标题、创建者、年份或全文搜索。

    Args:
        query: 搜索查询字符串，必须是字符串类型且非空。
        search_type: 搜索类型，可选值为 "title", "creator", "year", "fulltext"，默认为 "title"。
        page: 当前页码，必须是正整数，默认为1。
        items_per_page: 每页结果数量，必须是正整数，默认为20。

    Returns:
        返回格式化的搜索结果列表，每个结果包含条目键值、标题和匹配度评分。
    """
    # 验证查询参数
    if not query or not isinstance(query, str):
        return {
            "error": "Invalid input",
            "message": "query 必须是非空字符串",
            "code": 400
        }

    # 验证分页参数
    if not isinstance(page, int) or page < 1:
        return {
            "error": "Invalid parameter",
            "message": "page 必须是大于等于1的正整数",
            "code": 400
        }

    if not isinstance(items_per_page, int) or items_per_page < 1:
        return {
            "error": "Invalid parameter",
            "message": "items_per_page 必须是大于等于1的正整数",
            "code": 400
        }

    # 验证搜索类型
    valid_search_types = ["title", "creator", "year", "fulltext"]
    if search_type not in valid_search_types:
        return {
            "error": "Invalid parameter",
            "message": f"search_type 必须是以下之一：{', '.join(valid_search_types)}",
            "code": 400
        }

    try:
        # 根据搜索类型构建不同的查询参数
        params = {}
        
        if search_type == "title":
            # 按标题搜索使用基本搜索
            params["q"] = query
            params["index"] = "title"
        elif search_type == "creator":
            # 按创建者搜索需要指定creator字段
            params["q"] = f"creator:{query}"
        elif search_type == "year":
            # 按年份搜索需要使用date字段
            params["q"] = f"date:{query}"
        elif search_type == "fulltext":
            # 全文搜索需要特殊处理
            params["fulltext"] = query
            params["fulltextField"] = "text"
        
        # 添加分页参数
        params["start"] = (page - 1) * items_per_page
        params["limit"] = items_per_page
        
        # 构建API请求URL
        url = f"/{ZOTERO_LIBRARY_TYPE}s/{ZOTERO_LIBRARY_ID}/items?{urlencode(params, doseq=True)}"
        
        # 发送GET请求执行搜索
        response = await client.get(url)
        response.raise_for_status()
        
        # 解析响应数据
        search_results = response.json()
        
        # 处理搜索结果
        results = []
        for item in search_results:
            result = {
                "item_key": item.get("key", "无键值"),
                "title": item.get("data", {}).get("title", "无标题"),
                "score": item.get("score", 0)
            }
            results.append(result)
        
        return {
            "results": results,
            "total": len(results),
            "search_type": search_type,
            "query": query,
            "page": page,
            "items_per_page": items_per_page,
            "status": "success",
            "code": 200
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": "Server error",
            "message": f"执行 Zotero 搜索时发生错误: {str(e)}",
            "code": e.response.status_code
        }

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()