import sys
import os
import httpx
import json
from mcp.server.fastmcp import FastMCP
import asyncio

# 初始化 FastMCP 服务器
mcp = FastMCP("mcp_unsplash_photo_searcher")

# 设置代理（如需要）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 从环境变量获取 Unsplash Access Key
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')
if not UNSPLASH_ACCESS_KEY:
    raise ValueError("UNSPLASH_ACCESS_KEY 环境变量未设置")

# 创建异步 HTTP 客户端
client = httpx.AsyncClient(
    base_url="https://api.unsplash.com",
    headers={
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
        "User-Agent": "unsplash-photo-searcher/1.0"
    },
    timeout=10.0,
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)

@mcp.tool()
async def search_photos(query: str, page: int = 1, per_page: int = 10,
                        order_by: str = "relevant", color: str = None,
                        orientation: str = None) -> dict:
    """
    在 Unsplash 平台根据关键词、分页、排序、颜色和图片方向等条件搜索图片。

    Args:
        query (str): 搜索关键词（必填）
        page (int): 分页编号，默认为 1
        per_page (int): 每页结果数量，默认为 10，最大不超过 30
        order_by (str): 排序方式：latest, oldest, relevant，默认为 relevant
        color (str): 图片颜色过滤，如 red, blue, black 等（可选）
        orientation (str): 图片方向：landscape, portrait, squarish（可选）

    Returns:
        dict: 包含以下字段的字典：
            - results: 包含图片信息的列表，每项包括：
                - id: 图片ID
                - description: 图片描述
                - urls: 包含不同尺寸URL的对象（raw, full, regular, small, thumb）
                - width: 图片宽度
                - height: 图片高度
            - total: 总结果数
            - page: 当前页码
            - per_page: 每页结果数

    Raises:
        ValueError: 如果必填参数缺失或参数值无效
        httpx.HTTPStatusError: 如果API请求失败
    """
    try:
        # 参数验证
        if not query or not query.strip():
            raise ValueError("搜索关键词不能为空")
        
        if page < 1:
            raise ValueError("页码必须大于等于1")
        
        if per_page < 1 or per_page > 30:
            raise ValueError("每页结果数量必须在1到30之间")
        
        valid_order_by = ["latest", "oldest", "relevant"]
        if order_by not in valid_order_by:
            raise ValueError(f"排序方式必须是 {', '.join(valid_order_by)} 中的一个")
        
        valid_orientation = ["landscape", "portrait", "squarish"]
        if orientation and orientation not in valid_orientation:
            raise ValueError(f"图片方向必须是 {', '.join(valid_orientation)} 中的一个或None")

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

        # 发起API请求，添加重试逻辑以处理限流
        retries = 3
        for attempt in range(retries):
            response = await client.get("/search/photos", params=params)
            if response.status_code == 429:  # Too Many Requests
                if attempt < retries - 1:
                    wait_time = 2 ** attempt
                    print(f"收到限流响应，等待 {wait_time} 秒后重试...")
                    await asyncio.sleep(wait_time)
                    continue
            break
        
        response.raise_for_status()
        
        # 解析响应数据
        data = response.json()
        
        # 构造返回结果
        result = {
            "results": [],
            "total": data.get("total", 0),
            "page": page,
            "per_page": per_page
        }
        
        for item in data.get("results", []):
            photo = {
                "id": item.get("id"),
                "description": item.get("description") or item.get("alt_description", "无描述"),
                "urls": item.get("urls", {}),
                "width": item.get("width"),
                "height": item.get("height")
            }
            result["results"].append(photo)
        
        return result
    
    except httpx.HTTPStatusError as e:
        # 处理HTTP错误
        error_msg = f"Unsplash API 请求失败: {e.response.status_code} - {e.response.text}"
        raise ValueError(error_msg) from e
    
    except Exception as e:
        # 处理其他异常
        raise ValueError(f"搜索图片时发生错误: {str(e)}") from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()