import sys
import os
import httpx
import json
from typing import List, Optional, Dict, Any

# mcp SDK is required for this server
from mcp.server.fastmcp import FastMCP

# Ensure consistent output encoding
# This is good practice for applications that might run in varied environments.
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# --- Configuration Management ---
# For robust proxy support in enterprise environments, uncomment the following lines:
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize FastMCP Server
mcp = FastMCP("mcp_unsplash_search_photos")

# --- Constants and Global Client ---
UNSPLASH_API_BASE_URL = "https://api.unsplash.com"
# --- Performance: Use a shared AsyncClient ---
# Reusing the client improves performance by keeping connections alive across requests.
client = httpx.AsyncClient(
    base_url=UNSPLASH_API_BASE_URL,
    headers={"Accept-Version": "v1"}  # As per Unsplash API docs
)

@mcp.tool()
async def search_photos(
    query: str,
    page: Optional[int] = 1,
    per_page: Optional[int] = 10,
    order_by: Optional[str] = "relevant",
    color: Optional[str] = None,
    orientation: Optional[str] = None,
) -> str:
    """
    Searches for photos on Unsplash based on a query and optional filters.

    This function queries the Unsplash API to find photos matching the specified
    criteria. It requires an Unsplash API Access Key to be set as an
    environment variable `UNSPLASH_ACCESS_KEY`. The function returns a JSON
    string containing a list of photo objects, each with details like ID,
    description, and various image URLs.

    Args:
        query (str): The search keywords (e.g., "dogs", "office desk").
        page (int, optional): The page number to retrieve. Defaults to 1.
        per_page (int, optional): The number of items per page (max 30).
            Defaults to 10.
        order_by (str, optional): The sort order for the results. Valid
            options are "latest" or "relevant". Defaults to "relevant".
        color (str, optional): A color filter for the search. Valid options
            include "black_and_white", "black", "white", "yellow", "orange",
            "red", "purple", "magenta", "green", "teal", "blue".
            Defaults to None.
        orientation (str, optional): A filter for the photo orientation.
            Valid options are "landscape", "portrait", or "squarish".
            Defaults to None.

    Returns:
        str: A JSON formatted string representing a list of photo objects.
             If no photos are found, it returns a JSON string of an empty list.

    Raises:
        ValueError: If the `UNSPLASH_ACCESS_KEY` environment variable is not
            set or if any of the provided arguments are invalid (e.g.,
            `per_page` out of range, invalid `order_by` value).
        httpx.HTTPStatusError: If the Unsplash API returns an HTTP error
            (e.g., 4xx or 5xx status code).
        RuntimeError: For any other unexpected errors during execution.

    Example:
        >>> # Assuming UNSPLASH_ACCESS_KEY is set in the environment
        >>> # import asyncio
        >>> # asyncio.run(search_photos(query="cats", per_page=1, orientation="squarish"))
        '[
          {
            "id": "some_photo_id",
            "description": "a cat sitting on a window sill",
            "width": 4000,
            "height": 4000,
            "urls": {
              "raw": "...",
              "full": "...",
              "regular": "...",
              "small": "...",
              "thumb": "..."
            }
          }
        ]'
    """
    # --- Security: Retrieve API Key from environment variables ---
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise ValueError("UNSPLASH_ACCESS_KEY environment variable not set.")

    headers = {"Authorization": f"Client-ID {access_key}"}
    params: Dict[str, Any] = {
        "query": query,
        "page": page,
        "per_page": per_page,
        "order_by": order_by,
    }

    # --- Robustness: Input Validation ---
    if per_page and not 1 <= per_page <= 30:
        raise ValueError("per_page must be between 1 and 30.")
    if order_by and order_by not in ["latest", "relevant"]:
        raise ValueError("order_by must be 'latest' or 'relevant'.")
    valid_colors = ["black_and_white", "black", "white", "yellow", "orange", "red", "purple", "magenta", "green", "teal", "blue"]
    if color and color not in valid_colors:
        raise ValueError(f"Invalid color. Must be one of: {', '.join(valid_colors)}")
    valid_orientations = ["landscape", "portrait", "squarish"]
    if orientation and orientation not in valid_orientations:
        raise ValueError(f"Invalid orientation. Must be one of: {', '.join(valid_orientations)}")

    # Add optional parameters if they are provided
    if color:
        params["color"] = color
    if orientation:
        params["orientation"] = orientation

    try:
        # --- Functionality & Performance: Asynchronous API Call ---
        response = await client.get("/search/photos", headers=headers, params=params)
        # --- Robustness: Check for HTTP errors ---
        response.raise_for_status()
        data = response.json()

        # --- Functionality: Process and structure the results ---
        results = [
            {
                "id": photo.get("id"),
                "description": photo.get("description") or photo.get("alt_description"),
                "width": photo.get("width"),
                "height": photo.get("height"),
                "urls": photo.get("urls"),
            }
            for photo in data.get("results", [])
        ]

        # --- Data Serialization: Return a well-formed JSON string ---
        return json.dumps(results, indent=2)

    except httpx.HTTPStatusError as e:
        # --- Transparency: Propagate clear error messages ---
        error_message = f"API request failed with status {e.response.status_code}: {e.response.text}"
        raise httpx.HTTPStatusError(error_message, request=e.request, response=e.response) from e
    except Exception as e:
        # Catch any other unexpected errors and wrap them
        raise RuntimeError(f"An unexpected error occurred: {e}") from e

if __name__ == "__main__":
    # To run this server, you need to set the UNSPLASH_ACCESS_KEY environment variable:
    # export UNSPLASH_ACCESS_KEY='your_unsplash_api_key'
    # Then run the script:
    # python <filename>.py
    mcp.run()