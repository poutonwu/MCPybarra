import sys
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_duckduckgo_search_and_fetch")

# Shared HTTP client for async requests
async def get_async_client():
    return httpx.AsyncClient(timeout=30)

@mcp.tool()
async def duckduckgo_search(query: str, max_results: int = 5) -> dict:
    """
    Perform a search on DuckDuckGo and return structured results.

    Args:
        query: The search term or phrase to query on DuckDuckGo (required).
        max_results: Maximum number of search results to return (default: 5).

    Returns:
        A dictionary containing search results with 'title', 'url', and 'snippet' under 'results' key.

    Raises:
        ValueError: If the query is empty or max_results is invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")
    if max_results <= 0 or max_results > 10:
        raise ValueError("max_results must be between 1 and 10.")

    try:
        # Use lowercase query to avoid case sensitivity issues
        url = f"https://api.duckduckgo.com/?q={query.lower()}&format=json&no_html=1&no_redirect=1"
        async with await get_async_client() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        results = []
        # Fallback to "Results" if "RelatedTopics" is empty
        search_results = data.get("RelatedTopics", []) or data.get("Results", [])
        
        for item in search_results[:max_results]:
            title = item.get("Text", "")
            first_url = item.get("FirstURL", "")
            snippet = item.get("Result", "") or item.get("Text", "")
            if title and first_url:
                results.append({
                    "title": title,
                    "url": first_url,
                    "snippet": snippet
                })
        
        if not results:
            # Fallback response if no results found
            return {
                "results": [],
                "warning": "No results found. This may be due to API limitations or query restrictions."
            }
        
        return {"results": results}
    except httpx.RequestError as e:
        raise httpx.HTTPStatusError(f"Request failed: {str(e)}", request=e.request)

@mcp.tool()
async def fetch_content(url: str) -> str:
    """
    Fetch and parse the main text content of a webpage.

    Args:
        url: The URL of the webpage to scrape (required).

    Returns:
        A string containing the cleaned, main text content of the webpage.

    Raises:
        ValueError: If the URL is invalid or empty.
        httpx.HTTPStatusError: If the request fails.
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty.")

    try:
        async with await get_async_client() as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

        # Remove unwanted elements (scripts, styles, etc.)
        for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            element.decompose()

        # Extract meaningful content
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
            
        # Ensure we have some usable content
        if not text.strip():
            return "Warning: Unable to extract meaningful content from this page."
            
        return text
    except httpx.RequestError as e:
        raise httpx.HTTPStatusError(f"Request failed: {str(e)}", request=e.request)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()