import os
import httpx
from PIL import Image
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("image_mcp_server")

@mcp.tool()
def search_images(keyword: str, source: str) -> str:
    """
    Search for images based on user-provided keywords using APIs from Unsplash, Pexels, or Pixabay.

    Args:
        keyword (str): The search term used to find relevant images. Example: "sunset"
        source (str): The image source to query ('unsplash', 'pexels', or 'pixabay'). Example: "unsplash"

    Returns:
        str: A JSON string representing a list of dictionaries, where each dictionary contains:
            image_url (str): URL of the image.
            author (str): Name of the image creator.
            metadata (dict): Additional metadata, such as image dimensions and license information.

    Example:
        search_images(keyword="beach", source="unsplash")
    """
    try:
        base_urls = {
            "unsplash": "https://api.unsplash.com/search/photos",
            "pexels": "https://api.pexels.com/v1/search",
            "pixabay": "https://pixabay.com/api/"
        }

        if source not in base_urls:
            raise ValueError(f"Invalid source '{source}'. Must be one of: {', '.join(base_urls.keys())}")

        headers = {
            "Authorization": os.environ.get(f"{source.upper()}_API_KEY", "")
        }

        if not headers["Authorization"]:
            raise ValueError(f"Missing API key for source '{source}'. Ensure the environment variable '{source.upper()}_API_KEY' is set.")

        params = {"query": keyword, "per_page": 10}

        response = httpx.get(base_urls[source], headers=headers, params=params)
        response.raise_for_status()

        images = response.json()
        result = []

        for item in images.get("results", []):
            result.append({
                "image_url": item.get("urls", {}).get("regular", ""),
                "author": item.get("user", {}).get("name", "Unknown"),
                "metadata": {
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "license": item.get("license", "Unknown")
                }
            })

        return {"status": "success", "data": result}

    except Exception as e:
        return {"status": "failure", "error": str(e)}

@mcp.tool()
def download_image(image_url: str, file_name: str, directory: str) -> str:
    """
    Download an image from a given URL and save it to a specified file path with a custom filename.

    Args:
        image_url (str): The URL of the image to be downloaded. Example: "https://example.com/image.jpg"
        file_name (str): The desired name for the saved image file, including the extension. Example: "image.jpg"
        directory (str): The directory path where the image will be saved. Example: "./images"

    Returns:
        str: A JSON string containing:
            status (str): The result of the operation ('success' or 'failure').
            file_path (str): The full path to the saved image file.

    Example:
        download_image(image_url="https://example.com/image.jpg", file_name="image.jpg", directory="./images")
    """
    try:
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, file_name)

        response = httpx.get(image_url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        return {"status": "success", "file_path": file_path}

    except Exception as e:
        return {"status": "failure", "error": str(e)}

@mcp.tool()
def generate_icon(description: str, size: tuple[int, int], directory: str) -> str:
    """
    Generate an icon based on a textual description. If a cloud-based generation service is unavailable, 
    it uses a local sample image for simulation.

    Args:
        description (str): A textual description of the desired icon. Example: "sun and clouds"
        size (tuple[int, int]): Dimensions of the icon (width, height). Example: (128, 128)
        directory (str): The directory path where the icon will be saved. Example: "./icons"

    Returns:
        str: A JSON string containing:
            status (str): The result of the operation ('success' or 'failure').
            file_path (str): The full path to the generated icon file.

    Example:
        generate_icon(description="sun and clouds", size=(128, 128), directory="./icons")
    """
    try:
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"icon_{description.replace(' ', '_')}.png")

        # Simulate icon generation
        with Image.new("RGB", size, color=(255, 255, 255)) as im:
            im.save(file_path)

        return {"status": "success", "file_path": file_path}

    except Exception as e:
        return {"status": "failure", "error": str(e)}

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()