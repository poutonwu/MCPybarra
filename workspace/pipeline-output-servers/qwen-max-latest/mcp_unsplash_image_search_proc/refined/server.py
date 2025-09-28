import sys
import os
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server with a name
mcp = FastMCP("unsplash_image_search")

# Define a function to create an AsyncClient instance
async def create_client():
    return httpx.AsyncClient(
        base_url="https://api.unsplash.com",
        headers={"Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"}
    )

@mcp.tool()
async def search_photos(
    query: str,
    page: int = 1,
    per_page: int = 10,
    order_by: str = "relevant",
    color: str = None,
    orientation: str = None
) -> str:
    """
    Searches for photos on the Unsplash platform based on specified criteria such as keywords, pagination, sorting order, color, and image orientation.

    Args:
        query (str): The keyword(s) to search for in photos. (Required)
        page (int): The page number of the results to retrieve (default is 1). (Optional)
        per_page (int): The number of photos per page (default is 10). (Optional)
        order_by (str): The sort order for the photos (`\"latest\"`, `\"relevant\"`, or `\"popular\"`). (Optional)
        color (str): Filter results by color (`\"black_and_white\"`, `\"black\"`, `\"white\"`, `\"yellow\"`, `\"orange\"`, `\"red\"`, `\"purple\"`, `\"magenta\"`, `\"green\"`, `\"teal\"`, `\"blue\"`). (Optional)
        orientation (str): Filter by photo orientation (`\"landscape\"`, `\"portrait\"`, `\"squarish\"`). (Optional)

    Returns:
        A JSON string containing a list of dictionaries, where each dictionary contains the following keys:
        - `id` (str): Unique identifier for the photo.
        - `description` (str): Description of the photo (if available).
        - `urls` (dict): Dictionary containing URLs for different photo sizes (`\"raw\"`, `\"full\"`, `\"regular\"`, `\"small\"`, `\"thumb\"`).
        - `width` (int): The width of the photo in pixels.
        - `height` (int): The height of the photo in pixels.

    Example:
        search_photos(query=\"mountains\", page=1, per_page=10, order_by=\"relevant\", color=\"green\", orientation=\"landscape\")
    """
    try:
        # Input validation for required parameter
        if not query or not isinstance(query, str):
            raise ValueError("'query' must be a non-empty string.")

        # Validate optional parameters
        if page < 1:
            raise ValueError("'page' must be greater than or equal to 1.")

        if per_page < 1 or per_page > 100:
            raise ValueError("'per_page' must be between 1 and 100.")

        valid_order_by = ["latest", "relevant", "popular"]
        if order_by not in valid_order_by:
            raise ValueError(f"Invalid 'order_by'. Must be one of {valid_order_by}.")

        valid_colors = [
            "black_and_white", "black", "white", "yellow", "orange",
            "red", "purple", "magenta", "green", "teal", "blue"
        ]
        if color and color not in valid_colors:
            raise ValueError(f"Invalid 'color'. Must be one of {valid_colors}.")

        valid_orientations = ["landscape", "portrait", "squarish"]
        if orientation and orientation not in valid_orientations:
            raise ValueError(f"Invalid 'orientation'. Must be one of {valid_orientations}.")

        # Construct query parameters
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

        # Create a new client for each request
        async with await create_client() as client:
            # Make the API request
            response = await client.get("/search/photos", params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the response
            data = response.json()

            # Format the output
            results = []
            for photo in data.get("results", []):
                results.append({
                    "id": photo.get("id"),
                    "description": photo.get("description", "No description available"),
                    "urls": photo.get("urls", {}),
                    "width": photo.get("width"),
                    "height": photo.get("height")
                })

            return json.dumps(results)

    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except ValueError as ve:
        raise Exception(f"Value error: {ve}")
    except Exception as ex:
        raise Exception(f"An unexpected error occurred: {ex}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()