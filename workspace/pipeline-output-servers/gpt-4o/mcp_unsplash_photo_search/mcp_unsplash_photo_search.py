import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List, Dict

# Load environment variables
load_dotenv()
UNSPLASH_API_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
if not UNSPLASH_API_KEY:
    raise EnvironmentError("Missing UNSPLASH_API_KEY in environment variables.")

# Initialize MCP server
mcp = FastMCP("mcp_unsplash_photo_search")

@mcp.tool()
async def search_photos(
    query: str,
    page: int = 1,
    per_page: int = 10,
    order_by: str = "relevant",
    color: str = None,
    orientation: str = None
) -> List[Dict]:
    """
    Searches for photos on the Unsplash platform based on specified parameters.

    Args:
        query (str): The search keyword for photos (e.g., "nature"). Required.
        page (int): The page number for pagination. Defaults to 1.
        per_page (int): Number of photos to return per page. Defaults to 10.
        order_by (str): Sorting order for results. Possible values: "relevant", "latest". Defaults to "relevant".
        color (str): Filter for photos matching a specific color (e.g., "black_and_white", "blue"). Optional.
        orientation (str): Filter by photo orientation. Possible values: "landscape", "portrait", "squarish". Optional.

    Returns:
        List[Dict]: A list of dictionaries containing photo details.

    Raises:
        ValueError: If the query parameter is empty.
        RuntimeError: If there is a network issue or the Unsplash API returns a non-2xx response.

    Example:
        search_photos(query="nature", page=1, per_page=10, order_by="latest")
    """
    if not query:
        raise ValueError("The 'query' parameter cannot be empty.")

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "order_by": order_by,
    }
    if color:
        params["color"] = color
    if orientation:
        params["orientation"] = orientation

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            photos = []
            for photo in data.get("results", []):
                photos.append({
                    "id": photo.get("id"),
                    "description": photo.get("description"),
                    "urls": photo.get("urls"),
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                })

            return photos
        except httpx.RequestError as exc:
            raise RuntimeError(f"An error occurred while making the request: {exc}")
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"Error response {exc.response.status_code} while requesting {exc.request.url}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    mcp.run()