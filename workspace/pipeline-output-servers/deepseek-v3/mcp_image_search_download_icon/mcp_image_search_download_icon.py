import sys
import httpx
import os
import json
from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageDraw
import io

# Initialize FastMCP server
mcp = FastMCP("mcp_image_search_download_icon")
# Unsplash API 访问密钥
UNSPLASH_ACCESS_KEY="xxx"

# ---------------- Unsplash MCP Server ----------------
# Unsplash API 访问密钥
PIXABAY_API_KEY="xxx"

# ---------------- Unsplash MCP Server ----------------
# Unsplash API 访问密钥
PEXELS_API_KEY="xxx"
# Constants
UNSPLASH_API_KEY = os.environ.get('UNSPLASH_API_KEY', UNSPLASH_ACCESS_KEY)
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', PEXELS_API_KEY)
PIXABAY_API_KEY = os.environ.get('PIXABAY_API_KEY', PIXABAY_API_KEY)

# Shared HTTP client
client = httpx.AsyncClient()

@mcp.tool()
async def search_images(keywords: str, source: str = None, max_results: int = 5) -> str:
    """
    Searches for images based on user-provided keywords across popular image sources.

    Args:
        keywords: The search query for images.
        source: Specify the image source (e.g., "unsplash", "pexels", "pixabay"). Defaults to searching all sources.
        max_results: Maximum number of results to return. Defaults to 5.

    Returns:
        A JSON string containing a list of dictionaries with image details.

    Raises:
        ValueError: If no API keys are configured for the specified source.
        httpx.HTTPStatusError: If the API request fails.
    """
    results = []
    
    async def search_unsplash():
        if not UNSPLASH_API_KEY:
            raise ValueError("Unsplash API key not configured.")
        url = f"https://api.unsplash.com/search/photos?query={keywords}&per_page={max_results}"
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        for item in response.json()["results"]:
            results.append({
                "url": item["urls"]["regular"],
                "author": item["user"]["name"],
                "source": "unsplash",
                "license": item["user"]["links"]["html"]
            })
    
    async def search_pexels():
        if not PEXELS_API_KEY:
            raise ValueError("Pexels API key not configured.")
        url = f"https://api.pexels.com/v1/search?query={keywords}&per_page={max_results}"
        headers = {"Authorization": PEXELS_API_KEY}
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        for item in response.json()["photos"]:
            results.append({
                "url": item["src"]["original"],
                "author": item["photographer"],
                "source": "pexels",
                "license": item["url"]
            })
    
    async def search_pixabay():
        if not PIXABAY_API_KEY:
            raise ValueError("Pixabay API key not configured.")
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={keywords}&per_page={max_results}"
        response = await client.get(url)
        response.raise_for_status()
        for item in response.json()["hits"]:
            results.append({
                "url": item["webformatURL"],
                "author": item["user"],
                "source": "pixabay",
                "license": "https://pixabay.com/service/license/"
            })
    
    try:
        if source == "unsplash" or not source:
            await search_unsplash()
        if source == "pexels" or not source:
            await search_pexels()
        if source == "pixabay" or not source:
            await search_pixabay()
        return json.dumps(results)
    except Exception as e:
        raise e

@mcp.tool()
async def download_image(image_url: str, filename: str, save_dir: str = "./downloads") -> str:
    """
    Downloads an image from a given URL and saves it to a specified directory.

    Args:
        image_url: URL of the image to download.
        filename: Name to save the file as (excluding extension).
        save_dir: Directory path to save the image. Defaults to "./downloads".

    Returns:
        A JSON string containing the save status and path information.

    Raises:
        httpx.HTTPStatusError: If the download request fails.
        IOError: If the file cannot be saved.
    """
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        response = await client.get(image_url)
        response.raise_for_status()
        
        # Determine file extension
        content_type = response.headers.get('content-type')
        if content_type == 'image/jpeg':
            ext = '.jpg'
        elif content_type == 'image/png':
            ext = '.png'
        elif content_type == 'image/gif':
            ext = '.gif'
        else:
            ext = '.jpg'  # Default
        
        file_path = os.path.join(save_dir, f"{filename}{ext}")
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return json.dumps({"status": "success", "path": file_path})
    except Exception as e:
        raise e

@mcp.tool()
async def generate_icon(description: str, size: str = "32x32", save_dir: str = "./icons") -> str:
    """
    Generates an icon based on a user-provided description and saves it to a specified directory.

    Args:
        description: Text description of the desired icon.
        size: Dimensions of the icon (e.g., "64x64"). Defaults to "32x32".
        save_dir: Directory path to save the icon. Defaults to "./icons".

    Returns:
        A JSON string containing the save status and path information.

    Raises:
        IOError: If the file cannot be saved.
    """
    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        width, height = map(int, size.split('x'))
        
        img = Image.new('RGB', (width, height), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), description[:3], fill=(255, 255, 0))
        
        sanitized_desc = "".join(c for c in description if c.isalnum() or c in (' ', '_')).rstrip()
        file_path = os.path.join(save_dir, f"icon_{sanitized_desc.replace(' ', '_')}.png")
        img.save(file_path)
        
        return json.dumps({"status": "success", "path": file_path})
    except Exception as e:
        raise e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()