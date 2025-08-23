import sys
import httpx
import os
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("image_search")

# 定义常量
UNSPLASH_API_BASE = "https://api.unsplash.com/search/photos"
PEXELS_API_BASE = "https://api.pexels.com/v1/search"
PIXABAY_API_BASE = "https://pixabay.com/api/"
USER_AGENT = "image-search-app/1.0 (contact@example.com)"
IMAGE_DIR = "./images"

@mcp.tool()
async def search_images(keyword: str, source: str = "unsplash") -> str:
    """
    根据关键词在指定图片源中检索图片。

    Args:
        keyword: 搜索关键词。
        source: 图片源（unsplash, pexels, pixabay）。

    Returns:
        包含图片链接、作者等信息的JSON字符串。

    Raises:
        ValueError: 如果图片源无效。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    if source not in ["unsplash", "pexels", "pixabay"]:
        raise ValueError(f"无效的图片源: {source}")

    headers = {"User-Agent": USER_AGENT}
    params = {"query": keyword, "per_page": 5}

    async with httpx.AsyncClient() as client:
        if source == "unsplash":
            headers["Authorization"] = "xxx"
            response = await client.get(UNSPLASH_API_BASE, params=params, headers=headers)
        elif source == "pexels":
            headers["Authorization"] = "xxx"
            response = await client.get(PEXELS_API_BASE, params=params, headers=headers)
        else:  # pixabay
            params["key"] = "xxx"
            params["image_type"] = "photo"
            response = await client.get(PIXABAY_API_BASE, params=params)

    response.raise_for_status()
    return response.text

@mcp.tool()
async def download_image(url: str, filename: str) -> str:
    """
    下载并保存指定URL的图片。

    Args:
        url: 图片URL。
        filename: 保存的文件名。

    Returns:
        包含保存状态和路径的JSON字符串。

    Raises:
        httpx.HTTPStatusError: 如果图片下载失败。
    """
    os.makedirs(IMAGE_DIR, exist_ok=True)
    file_path = os.path.join(IMAGE_DIR, filename)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(response.content)

    return f"{{\"status\": \"success\", \"path\": \"{file_path}\"}}"

@mcp.tool()
async def generate_icon(description: str, size: int = 64) -> str:
    """
    根据描述生成指定尺寸的图标。

    Args:
        description: 图标描述。
        size: 图标尺寸，默认为64。

    Returns:
        包含保存状态和路径的JSON字符串。

    Raises:
        ValueError: 如果尺寸小于16或大于256。
    """
    if size < 16 or size > 256:
        raise ValueError(f"尺寸超出范围: {size}. 有效范围是16到256。")

    os.makedirs(IMAGE_DIR, exist_ok=True)
    file_name = f"icon_{description.lower().replace(' ', '_')}_{size}x{size}.png"
    file_path = os.path.join(IMAGE_DIR, file_name)

    # 这里只是一个模拟实现
    # 实际应用中可以使用图像生成库如Pillow或调用外部服务
    with open(file_path, 'w') as f:
        f.write(f"This is a simulated icon of {description}, size {size}x{size} pixels.")

    return f"{{\"status\": \"success\", \"path\": \"{file_path}\"}}"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()