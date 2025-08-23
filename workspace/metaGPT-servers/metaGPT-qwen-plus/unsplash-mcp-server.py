import sys
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("unsplash_photo_search")

# Unsplash API配置
UNSPLASH_API_BASE = "https://api.unsplash.com"
ACCESS_KEY = "xxx"  # 需要替换为实际的Unsplash访问密钥
USER_AGENT = "photo-search-server/1.0 (contact@example.com)"

# 存储搜索结果缓存（简单实现）
search_cache = {}

# 定义可用的颜色选项
COLOR_OPTIONS = [
    "black", "white", "red", "orange", "yellow", 
    "green", "turquoise", "blue", "purple", "magenta",
    "brown", "black_and_white"
]

# 定义图片方向选项
ORIENTATION_OPTIONS = ["landscape", "portrait", "squarish"]

# 定义排序选项
ORDER_BY_OPTIONS = ["relevant", "latest", "popular"]

@mcp.tool()
async def search_photos(
    query: str,
    page: int = 1,
    per_page: int = 10,
    order_by: str = "relevant",
    color: Optional[str] = None,
    orientation: Optional[str] = None
) -> Dict[str, Any]:
    """
    在Unsplash平台根据关键词、分页、排序、颜色和图片方向等条件搜索图片。
    
    Args:
        query: 搜索关键词 (必填)。
        page: 当前页码，从1开始计数 (可选，默认: 1)。
        per_page: 每页返回的结果数量 (可选，默认: 10，最大: 30)。
        order_by: 排序方式 (可选，默认: relevant，可选值: relevant/latest/popular)。
        color: 过滤颜色 (可选，可选值: black/white/red/orange/yellow/green/turquoise/blue/purple/magenta/brown/black_and_white)。
        orientation: 图片方向 (可选，可选值: landscape/portrait/squarish)。
            
    Returns:
        包含图片搜索结果的字典，包含以下字段：
        - total: 总结果数
        - total_pages: 总页数
        - current_page: 当前页码
        - results: 图片结果列表，每个元素包含：
            * id: 图片唯一标识符
            * description: 图片描述
            * urls: 包含不同尺寸URL的对象，包含：raw/regular/small/thumb
            * width: 原始图片宽度
            * height: 原始图片高度
            * color: 图片主色调
            * orientation: 图片方向
            
    Raises:
        ValueError: 如果参数验证失败
        httpx.HTTPStatusError: 如果API请求失败
    
    示例:
        search_photos(query="nature", page=1, per_page=5, order_by="popular", color="green", orientation="landscape")
    """
    # 参数验证
    if not query or not query.strip():
        raise ValueError("'query' 参数不能为空")
    
    if page < 1:
        raise ValueError("'page' 参数必须大于等于1")
    
    if per_page < 1 or per_page > 30:
        raise ValueError("'per_page' 参数必须在1到30之间")
    
    if order_by not in ORDER_BY_OPTIONS:
        raise ValueError(f"'order_by' 参数必须是 {', '.join(ORDER_BY_OPTIONS)} 中的一个")
    
    if color is not None and color not in COLOR_OPTIONS:
        raise ValueError(f"'color' 参数必须是 {', '.join(COLOR_OPTIONS)} 中的一个")
    
    if orientation is not None and orientation not in ORIENTATION_OPTIONS:
        raise ValueError(f"'orientation' 参数必须是 {', '.join(ORIENTATION_OPTIONS)} 中的一个")
    
    # 检查缓存
    cache_key = f"{query}_{page}_{per_page}_{order_by}_{color}_{orientation}"
    if cache_key in search_cache:
        return search_cache[cache_key]
    
    # 构建查询参数
    params = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "order_by": order_by
    }
    
    if color:
        params["color"] = color
    
    if orientation:
        params["orientation"] = orientation
    
    # 发起API请求
    headers = {
        "Authorization": f"Client-ID {ACCESS_KEY}",
        "User-Agent": USER_AGENT
    }
    
    async with httpx.AsyncClient(base_url=UNSPLASH_API_BASE, headers=headers) as client:
        response = await client.get("/search/photos", params=params)
        
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        # 添加更详细的错误信息
        error_msg = f"Unsplash API 请求失败: {str(e)}"
        if response.text:
            error_msg += f"\n响应内容: {response.text[:200]}..."  # 只显示前200字符
        raise httpx.HTTPStatusError(error_msg, request=e.request, response=e.response)
    
    # 处理响应数据
    data = response.json()
    
    # 提取需要的字段
    processed_results = []
    for item in data["results"]:
        processed_item = {
            "id": item["id"],
            "description": item["description"] or item["alt_description"] or "No description",
            "urls": item["urls"],
            "width": item["width"],
            "height": item["height"],
            "color": item["color"],
            "orientation": item["orientation"]
        }
        processed_results.append(processed_item)
    
    # 构建最终结果
    result = {
        "total": data["total"],
        "total_pages": data["total_pages"],
        "current_page": data["page"],
        "results": processed_results
    }
    
    # 缓存结果（5分钟）
    search_cache[cache_key] = result
    
    return result

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()