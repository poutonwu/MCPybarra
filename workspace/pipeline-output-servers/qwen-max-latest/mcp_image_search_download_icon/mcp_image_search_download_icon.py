import os
import sys
import httpx
import json
from PIL import Image, ImageDraw
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("image_search_download_icon")

# Shared HTTP client for performance optimization
client = httpx.AsyncClient(
    headers={"Authorization": f"Bearer {os.environ.get('IMAGE_API_KEY', 'xxx')}"}
)

@mcp.tool()
async def search_images(keywords: str) -> str:
    """
    Searches for images based on user-provided keywords from popular image sources such as Unsplash or Pexels.

    Args:
        keywords: A string of keywords separated by spaces to search for relevant images.

    Returns:
        A JSON-formatted string containing a list of dictionaries. Each dictionary contains:
            - image_url (str): The URL of the image.
            - author (str): The name of the author/photographer.

    Raises:
        ValueError: If keywords are empty or invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not keywords.strip():
        raise ValueError("Keywords cannot be empty or contain only whitespace.")

    # Example using Unsplash API
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": keywords,
        "per_page": 10  # Limit results to 10 images
    }

    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "image_url": item["urls"]["regular"],
                "author": item["user"]["name"]
            })

        return json.dumps(results)

    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"API request failed with status code {e.response.status_code}: {e.response.text}")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch images: {e}")


@mcp.tool()
async def download_image(image_url: str, file_name: str, save_directory: str) -> str:
    """
    Downloads an image from a provided URL and saves it to a specified directory.

    Args:
        image_url: The URL of the image to download.
        file_name: The desired file name for the downloaded image.
        save_directory: The directory where the image should be saved.

    Returns:
        A JSON-formatted string containing:
            - status (str): Indicates success or failure of the operation (e.g., "success" or "failure").
            - file_path (str): The full path to the saved image if successful.

    Raises:
        ValueError: If any parameter is empty or invalid.
        httpx.HTTPStatusError: If the image download fails.
    """
    if not image_url.strip() or not file_name.strip() or not save_directory.strip():
        raise ValueError("All parameters must be non-empty strings.")

    if not os.path.isdir(save_directory):
        raise ValueError(f"Invalid directory: '{save_directory}'")

    try:
        async with httpx.AsyncClient() as temp_client:
            response = await temp_client.get(image_url)
            response.raise_for_status()

            file_path = os.path.join(save_directory, file_name)
            with open(file_path, 'wb') as f:
                f.write(response.content)

        return json.dumps({
            "status": "success",
            "file_path": file_path
        })

    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "failure",
            "error_message": f"Image download failed with status code {e.response.status_code}: {e.response.text}"
        })
    except Exception as e:
        return json.dumps({
            "status": "failure",
            "error_message": str(e)
        })


@mcp.tool()
async def generate_icon(description: str, icon_size: int, save_directory: str) -> str:
    """
    Generates an icon of a specified size based on a description provided by the user.

    Args:
        description: A textual description of the desired icon.
        icon_size: The desired size in pixels (e.g., 64 for a 64x64 icon).
        save_directory: The directory where the generated icon will be saved.

    Returns:
        A JSON-formatted string containing:
            - status (str): Indicates success or failure of the operation (e.g., "success" or "failure").
            - file_path (str): The full path to the generated icon if successful.

    Raises:
        ValueError: If any parameter is invalid.
    """
    if not description.strip() or icon_size <= 0:
        raise ValueError("Description must be non-empty and icon size must be positive.")

    if not os.path.isdir(save_directory):
        raise ValueError(f"Invalid directory: '{save_directory}'")

    try:
        # Simulate icon generation using a blank square image
        file_name = f"icon_{icon_size}x{icon_size}.png"
        file_path = os.path.join(save_directory, file_name)

        img = Image.new("RGB", (icon_size, icon_size), color="blue")
        draw = ImageDraw.Draw(img)
        text = description[:20]
        text_size = draw.textsize(text)
        text_position = ((icon_size - text_size[0]) // 2, (icon_size - text_size[1]) // 2)
        draw.text(text_position, text, fill="white")  # Add short description text centered

        img.save(file_path, format="PNG")

        return json.dumps({
            "status": "success",
            "file_path": file_path
        })

    except Exception as e:
        return json.dumps({
            "status": "failure",
            "error_message": str(e)
        })


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()