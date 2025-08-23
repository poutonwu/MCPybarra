import os
import sys
import json
import httpx
import asyncio
import re
from typing import List, Optional, Tuple
from mcp.server.fastmcp import FastMCP
from PIL import Image, ImageDraw, ImageFont

# Set up proxy if available
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize FastMCP server
mcp = FastMCP("image_mcp_server")

# Shared HTTPX async client for performance
client = httpx.AsyncClient()

# --- Helper Functions ---

async def search_unsplash(query: str, api_key: str, per_page: int) -> List[dict]:
    """Helper to search images on Unsplash."""
    if not api_key:
        return []
    headers = {"Authorization": f"Client-ID {api_key}"}
    params = {"query": query, "per_page": per_page}
    try:
        response = await client.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [{
            "source": "unsplash",
            "id": img["id"],
            "url": img["urls"]["regular"],
            "photographer": img["user"]["name"],
            "description": img.get("description") or img.get("alt_description") or "No description",
        } for img in data.get("results", [])]
    except httpx.HTTPStatusError as e:
        print(f"Unsplash API error: {e}")
        return []

async def search_pexels(query: str, api_key: str, per_page: int) -> List[dict]:
    """Helper to search images on Pexels."""
    if not api_key:
        return []
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": per_page}
    try:
        response = await client.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [{
            "source": "pexels",
            "id": str(img["id"]),
            "url": img["src"]["original"],
            "photographer": img["photographer"],
            "description": img.get("alt") or "No description",
        } for img in data.get("photos", [])]
    except httpx.HTTPStatusError as e:
        print(f"Pexels API error: {e}")
        return []

async def search_pixabay(query: str, api_key: str, per_page: int) -> List[dict]:
    """Helper to search images on Pixabay."""
    if not api_key:
        return []
    params = {"key": api_key, "q": query, "per_page": per_page, "image_type": "photo"}
    try:
        response = await client.get("https://pixabay.com/api/", params=params)
        response.raise_for_status()
        data = response.json()
        return [{
            "source": "pixabay",
            "id": str(img["id"]),
            "url": img["webformatURL"],
            "photographer": img["user"],
            "description": img.get("tags") or "No description",
        } for img in data.get("hits", [])]
    except httpx.HTTPStatusError as e:
        print(f"Pixabay API error: {e}")
        return []

# --- MCP Tools ---

@mcp.tool()
async def search_images(
    query: str,
    sources: Optional[List[str]] = None,
    per_page: int = 10
) -> str:
    """
    Searches for images based on a keyword from multiple online sources.

    This tool queries APIs from Unsplash, Pexels, and Pixabay to find
    images matching the given query. It requires API keys for these
    services to be configured as environment variables:
    - UNSPLASH_API_KEY
    - PEXELS_API_KEY
    - PIXABAY_API_KEY

    Args:
        query (str): The search keyword for images (e.g., "cats", "sunset"). Must not be empty.
        sources (Optional[List[str]]): A list of sources to search from.
            Valid options are 'unsplash', 'pexels', 'pixabay'.
            If None, it defaults to searching all three sources.
        per_page (int): The number of results to request from each source.
            Defaults to 10.

    Returns:
        str: A JSON string containing a list of image results. Each result is a
             dictionary with details like source, id, url, photographer, and
             description. Returns an empty list if no results are found or if
             API keys are missing.
    """
    # Validate input
    if not query or not query.strip():
        return json.dumps({
            "status": "error",
            "message": "Query cannot be empty or whitespace only. Please provide a valid search term.",
            "results": []
        })

    if sources is None:
        sources = ['unsplash', 'pexels', 'pixabay']

    # Improved API key handling - prioritize environment variables, use defaults if not found
    api_keys = {
        "unsplash": os.environ.get("UNSPLASH_API_KEY", "xxx"),
        "pexels": os.environ.get("PEXELS_API_KEY", "xxx"),
        "pixabay": os.environ.get("PIXABAY_API_KEY", "xxx"),
    }

    search_tasks = []
    for source in sources:
        api_key = api_keys.get(source)
        if not api_key:
            print(f"API key for {source} not found. Skipping.")
            continue
        if source == "unsplash":
            search_tasks.append(search_unsplash(query, api_key, per_page))
        elif source == "pexels":
            search_tasks.append(search_pexels(query, api_key, per_page))
        elif source == "pixabay":
            search_tasks.append(search_pixabay(query, api_key, per_page))

    try:
        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Filter out any exceptions that occurred during the search tasks
        valid_results = []
        for result in all_results:
            if isinstance(result, Exception):
                print(f"Error during search task: {result}")
                continue
            valid_results.extend(result)
            
        return json.dumps({"results": valid_results})
    except Exception as e:
        # Provide detailed error information
        return json.dumps({
            "status": "error",
            "message": f"Search failed due to an unexpected error: {str(e)}",
            "results": []
        })

@mcp.tool()
async def download_image(
    image_url: str,
    filename: str,
    save_dir: str = './downloads'
) -> str:
    """
    Downloads an image from a given URL and saves it to a local directory.

    This function performs security checks to validate the URL scheme (HTTP/HTTPS)
    and to prevent path traversal attacks in the filename.

    Args:
        image_url (str): The direct URL of the image to download OR a local file path.
        filename (str): The name for the saved file, including the extension
                        (e.g., 'my_image.jpg').
        save_dir (str): The local directory where the image will be saved.
                        It will be created if it doesn't exist.
                        Defaults to './downloads'.

    Returns:
        str: A JSON string indicating the outcome. On success, it includes the
             status, the absolute path to the saved file, and a confirmation
             message. On failure, it provides an error status and message.
    """
    try:
        # Security: Prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise ValueError("Invalid filename. It cannot contain path traversal elements.")

        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        # Handle local file paths
        if re.match(r'^file://', image_url) or os.path.exists(image_url):
            # Local file path - copy instead of downloading
            if image_url.startswith('file://'):
                image_url = image_url[7:]  # Remove file:// prefix
            
            # Use OS-specific file copying to handle different OS paths
            import shutil
            shutil.copy2(image_url, file_path)
        else:
            # Security: Basic URL validation
            if not re.match(r'^https?://', image_url):
                raise ValueError("Invalid URL scheme. Only HTTP, HTTPS, and local file paths are allowed.")

            async with httpx.AsyncClient() as download_client:
                response = await download_client.get(image_url, follow_redirects=True)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(response.content)

        return json.dumps({
            "status": "success",
            "file_path": os.path.abspath(file_path),
            "message": f"Image saved to {os.path.abspath(file_path)}"
        })
    except (ValueError, httpx.HTTPError, IOError, Exception) as e:
        return json.dumps({
            "status": "error",
            "file_path": None,
            "message": str(e)
        })

@mcp.tool()
async def generate_icon(
    description: str,
    size: Tuple[int, int] = (128, 128),
    filename: Optional[str] = None,
    save_dir: str = './icons'
) -> str:
    """
    Generates a simple placeholder icon with a solid color background and text.

    This is useful for creating quick, programmatic visual assets. It creates
    an image, draws the provided text in the center, and saves it as a PNG file.
    A default font is used if 'arial.ttf' is not available.

    Args:
        description (str): The text to display on the icon (e.g., "App").
        size (Tuple[int, int]): The dimensions (width, height) of the icon in
                                pixels. Defaults to (128, 128).
        filename (Optional[str]): The desired filename for the icon (e.g.,
                                  'app_icon.png'). If None, a filename is
                                  auto-generated from the description.
        save_dir (str): The directory where the generated icon will be saved.
                        It will be created if it doesn't exist.
                        Defaults to './icons'.

    Returns:
        str: A JSON string indicating the outcome. On success, it includes the
             status, the absolute path to the saved file, and a confirmation
             message. On failure, it provides an error status and message.
    """
    try:
        # Validate size parameters
        if not isinstance(size, tuple) and not isinstance(size, list):
            raise ValueError("Size must be a tuple or list of two integers")
        
        if len(size) != 2:
            raise ValueError("Size must be a tuple or list of exactly two integers")
        
        width, height = size
        
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError("Size values must be integers")
        
        if width <= 0 or height <= 0:
            raise ValueError("Icon dimensions must be positive integers")

        if filename is None:
            safe_desc = re.sub(r'[\W_]+', '_', description).lower()
            filename = f"{safe_desc}_icon.png"

        # Security: Prevent path traversal in filename
        if ".." in filename or "/" in filename or "\\" in filename:
             raise ValueError("Invalid filename. It cannot contain path traversal elements.")

        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)

        img = Image.new('RGB', size, color = (73, 109, 137))
        d = ImageDraw.Draw(img)

        # Use a default font if a specific one isn't found
        try:
            font = ImageFont.truetype("arial.ttf", 15)
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text position to center it
        bbox = d.textbbox((0, 0), description, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (size[0] - text_width) / 2
        text_y = (size[1] - text_height) / 2
        
        d.text((text_x, text_y), description, font=font, fill=(255, 255, 255))
        
        img.save(file_path)

        return json.dumps({
            "status": "success",
            "file_path": os.path.abspath(file_path),
            "message": f"Icon saved to {os.path.abspath(file_path)}"
        })
    except (ValueError, IOError, Exception) as e:
        return json.dumps({
            "status": "error",
            "file_path": None,
            "message": str(e)
        })


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()