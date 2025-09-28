import sys
import httpx
from mcp.server.fastmcp import FastMCP
from pyzotero import zotero
from typing import Any, Dict, List, Union

# Initialize FastMCP server
mcp = FastMCP("mcp_zotero_library_manager")

# Zotero API configuration
ZOTERO_API_KEY = "goIOXCQJi4LP4WIZbJlpb4Ve"
ZOTERO_LIBRARY_ID = "16026771"
ZOTERO_LIBRARY_TYPE = "user"  # or "group"

# Initialize Zotero client
zot = zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, ZOTERO_API_KEY)

@mcp.tool()
def get_item_metadata(item_key: str) -> Dict[str, Any]:
    """
    Retrieves detailed metadata for a specified Zotero entry using its unique item key.

    Args:
        item_key: The unique identifier for the Zotero entry.

    Returns:
        A dictionary containing the entry's metadata (e.g., title, authors, publication year, DOI, etc.).

    Raises:
        ValueError: If the item_key is not provided or is invalid.
        Exception: If there is an error fetching the metadata from Zotero.
    """
    if not item_key or not isinstance(item_key, str):
        raise ValueError("Valid item key must be provided.")
    try:
        item = zot.item(item_key)
        if not item:
            raise ValueError(f"No item found with key: {item_key}")
        return item
    except httpx.HTTPError as e:
        raise Exception(f"HTTP error occurred while fetching metadata for item {item_key}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to fetch metadata for item {item_key}: {str(e)}")

@mcp.tool()
def get_item_fulltext(item_key: str) -> Union[str, bytes]:
    """
    Extracts the full-text content of a Zotero entry (e.g., PDF, HTML, or plain text).

    Args:
        item_key: The unique identifier for the Zotero entry.

    Returns:
        A string or binary data representing the full-text content (if available).

    Raises:
        ValueError: If the item_key is not provided or is invalid.
        Exception: If there is an error fetching the full-text content from Zotero.
    """
    if not item_key or not isinstance(item_key, str):
        raise ValueError("Valid item key must be provided.")
    try:
        fulltext = zot.fulltext(item_key)
        if not fulltext:
            raise ValueError(f"No fulltext content found for item: {item_key}")
        return fulltext
    except httpx.HTTPError as e:
        raise Exception(f"HTTP error occurred while fetching fulltext for item {item_key}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to fetch fulltext for item {item_key}: {str(e)}")

@mcp.tool()
def search_items(query: str, search_type: str = "title") -> List[Dict[str, Any]]:
    """
    Performs a flexible search in the Zotero library, supporting queries by title, creator, year, or full-text content.

    Args:
        query: The search term (e.g., title, author name, year, or keyword).
        search_type: Specifies the search scope (`title`, `creator`, `year`, `fulltext`). Default: `title`.

    Returns:
        A list of dictionaries containing metadata for matching entries.

    Raises:
        ValueError: If the query is not provided or search_type is invalid.
        Exception: If there is an error performing the search in Zotero.
    """
    if not query or not isinstance(query, str):
        raise ValueError("Valid search query must be provided.")
    valid_search_types = ["title", "creator", "year", "fulltext"]
    if search_type not in valid_search_types:
        raise ValueError(f"Invalid search_type: {search_type}. Must be one of {valid_search_types}.")
    try:
        if search_type == "title":
            results = zot.items(q=query, qmode="title")
        elif search_type == "creator":
            results = zot.items(q=query, qmode="creator")
        elif search_type == "year":
            results = zot.items(q=query, qmode="year")
        else:  # fulltext
            results = zot.items(q=query, qmode="fulltext")
        if not results:
            return []
        return results
    except httpx.HTTPError as e:
        raise Exception(f"HTTP error occurred while performing search: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to perform search: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()