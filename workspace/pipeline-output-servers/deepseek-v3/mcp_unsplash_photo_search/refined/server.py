import sys
import httpx
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_unsplash_photo_search")

# Unsplash API configuration
UNSPLASH_API_BASE = "https://api.unsplash.com"
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
if not UNSPLASH_ACCESS_KEY:
    raise ValueError("Unsplash API access key not found in environment variables.")

@mcp.tool()
def search_photos(
    query: str,
    page: int = 1,
    per_page: int = 10,
    order_by: str = "popular",
    color: str = None,
    orientation: str = None
) -> list:
    """
    Searches for photos on Unsplash based on keywords, pagination, sorting, color, and orientation filters.
    Returns a list of photo details including ID, description, URLs for multiple sizes, width, and height.

    Args:
        query (str, required): The search keyword(s) for photos.
        page (int, optional): The page number for paginated results. Defaults to 1.
        per_page (int, optional): The number of results per page. Defaults to 10.
        order_by (str, optional): The sorting order for results (e.g., 'latest', 'popular'). Defaults to 'popular'.
        color (str, optional): Filter photos by a specific color (e.g., 'red', 'blue'). Optional.
        orientation (str, optional): Filter photos by orientation ('landscape', 'portrait', 'squarish'). Optional.

    Returns:
        A list of dictionaries, each containing:
            - 'id' (str): Unique identifier for the photo.
            - 'description' (str): Description or alt text of the photo.
            - 'urls' (dict): URLs for different sizes ('raw', 'full', 'regular', 'small', 'thumb').
            - 'width' (int): Width of the photo in pixels.
            - 'height' (int): Height of the photo in pixels.

    Raises:
        httpx.HTTPStatusError: If the API request fails.
        ValueError: If required parameters are missing or invalid.
    """
    # Validate required parameters
    if not query or not isinstance(query, str):
        raise ValueError("The 'query' parameter is required and must be a non-empty string.")
    if not isinstance(page, int) or page < 1:
        raise ValueError("The 'page' parameter must be a positive integer.")
    if not isinstance(per_page, int) or per_page < 1 or per_page > 30:
        raise ValueError("The 'per_page' parameter must be an integer between 1 and 30.")
    if order_by not in ["latest", "popular", "relevant"]:
        raise ValueError("The 'order_by' parameter must be one of: 'latest', 'popular', 'relevant'")
    if color and not isinstance(color, str):
        raise ValueError("The 'color' parameter must be a string if provided.")
    if orientation and orientation not in ["landscape", "portrait", "squarish"]:
        raise ValueError("The 'orientation' parameter must be one of: 'landscape', 'portrait', 'squarish'")

    # Construct API request URL
    url = f"{UNSPLASH_API_BASE}/search/photos"
    params = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "order_by": order_by,
        "client_id": UNSPLASH_ACCESS_KEY
    }
    
    # Add optional filters
    if color:
        params["color"] = color
    if orientation:
        params["orientation"] = orientation

    # Make the API request
    try:
        response = httpx.get(url, params=params)
        response.raise_for_status()
        photos = response.json()["results"]
        
        # Format the response
        formatted_photos = []
        for photo in photos:
            formatted_photos.append({
                "id": photo["id"],
                "description": photo.get("alt_description", ""),
                "urls": photo["urls"],
                "width": photo["width"],
                "height": photo["height"]
            })
        
        return formatted_photos
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(f"Unsplash API request failed: {e}")
    except KeyError as e:
        raise KeyError(f"Unexpected response format from Unsplash API: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()