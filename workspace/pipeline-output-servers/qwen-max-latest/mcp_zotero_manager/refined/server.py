import os
import sys
import requests
from mcp.server.fastmcp import FastMCP
import json

# Initialize the MCP server
mcp = FastMCP("mcp_zotero_manager")

# Zotero API base URL and constants
ZOTERO_API_BASE = "https://api.zotero.org"
USER_AGENT = "mcp-zotero-manager/1.0 (contact@example.com)"
# Zotero 库的 ID
ZOTERO_LIBRARY_ID = "16026771"
ZOTERO_LIBRARY_TYPE = "user"
ZOTERO_API_KEY = "goIOXCQJi4LP4WIZbJlpb4Ve"

# Set up proxies if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

@mcp.tool()
def get_item_metadata(item_key: str) -> str:
    """
    Fetches the detailed metadata of a specified Zotero item using its unique item key.

    Args:
        item_key: The unique identifier for the Zotero item whose metadata is to be fetched.

    Returns:
        A JSON string containing the detailed metadata of the specified Zotero item.

    Raises:
        ValueError: If the `item_key` is not provided or is invalid.
        requests.exceptions.HTTPError: If the request to the Zotero API fails.

    Example:
        get_item_metadata(item_key="ABC123XYZ")
    """
    if not item_key or not isinstance(item_key, str):
        raise ValueError("'item_key' must be a non-empty string.")

    try:
        url = f"{ZOTERO_API_BASE}/{ZOTERO_LIBRARY_TYPE}/{ZOTERO_LIBRARY_ID}/items/{item_key}"
        headers = {"User-Agent": USER_AGENT, "Authorization": f"Bearer {ZOTERO_API_KEY}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTP errors

        return json.dumps(response.json())

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.HTTPError(f"Request failed: {e}") from e

@mcp.tool()
def get_item_fulltext(item_key: str) -> str:
    """
    Extracts the full text content of a specified Zotero item using its unique item key.

    Args:
        item_key: The unique identifier for the Zotero item whose full text content is to be extracted.

    Returns:
        A JSON string containing the full text content of the specified Zotero item.

    Raises:
        ValueError: If the `item_key` is not provided or is invalid.
        requests.exceptions.HTTPError: If the request to the Zotero API fails.

    Example:
        get_item_fulltext(item_key="ABC123XYZ")
    """
    if not item_key or not isinstance(item_key, str):
        raise ValueError("'item_key' must be a non-empty string.")

    try:
        url = f"{ZOTERO_API_BASE}/{ZOTERO_LIBRARY_TYPE}/{ZOTERO_LIBRARY_ID}/items/{item_key}/fulltext"
        headers = {"User-Agent": USER_AGENT, "Authorization": f"Bearer {ZOTERO_API_KEY}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTP errors

        return json.dumps(response.json())

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.HTTPError(f"Request failed: {e}") from e

@mcp.tool()
def search_items(query: str, search_by_title: bool = True, search_by_creator: bool = True, search_by_year: bool = False, search_by_fulltext: bool = False) -> str:
    """
    Searches the Zotero library flexibly based on title, creator, year, or full text and returns a formatted list of search results.

    Args:
        query: The search query text.
        search_by_title: Whether to include titles in the search. Defaults to True.
        search_by_creator: Whether to include creators in the search. Defaults to True.
        search_by_year: Whether to include publication years in the search. Defaults to False.
        search_by_fulltext: Whether to include full text in the search. Defaults to False.

    Returns:
        A JSON string containing a list of dictionaries where each dictionary contains the metadata of an item that matches the search criteria.

    Raises:
        ValueError: If the `query` is not provided or is invalid.
        requests.exceptions.HTTPError: If the request to the Zotero API fails.

    Example:
        search_items(query="Machine Learning", search_by_title=True, search_by_creator=True, search_by_year=False, search_by_fulltext=False)
    """
    if not query or not isinstance(query, str):
        raise ValueError("'query' must be a non-empty string.")

    try:
        url = f"{ZOTERO_API_BASE}/{ZOTERO_LIBRARY_TYPE}/{ZOTERO_LIBRARY_ID}/items"
        headers = {"User-Agent": USER_AGENT, "Authorization": f"Bearer {ZOTERO_API_KEY}"}
        params = {
            "q": query,
            "qmode": "everything" if search_by_fulltext else "titleCreatorYear",
            "include": "data"
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTP errors

        items = response.json()
        result = []

        for item in items:
            data = item.get("data", {})
            if (
                (search_by_title and query.lower() in data.get("title", "").lower()) or
                (search_by_creator and any(query.lower() in creator.get("name", "").lower() for creator in data.get("creators", []))) or
                (search_by_year and str(data.get("year", "")) == query) or
                (search_by_fulltext and query.lower() in data.get("fulltext", "").lower())
            ):
                result.append(data)

        return json.dumps(result)

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.HTTPError(f"Request failed: {e}") from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run(transport="stdio")