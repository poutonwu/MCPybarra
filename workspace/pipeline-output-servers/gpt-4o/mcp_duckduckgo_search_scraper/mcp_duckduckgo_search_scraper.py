import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("duckduckgo_search_scraper")
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
@mcp.tool()
def DuckDuckGo_search(query: str) -> str:
    """
    Fetches search results from DuckDuckGo based on a user-provided query string.

    Args:
        query (str): The search query string provided by the user.
            Example: "Python web scraping tutorial"

    Returns:
        str: A JSON string containing a list of structured search results, where each result contains:
            - title (str): The title of the search result.
            - url (str): The URL of the search result.
            - snippet (str): A brief snippet or summary of the result.

    Raises:
        ValueError: If the query is empty or invalid.
        Exception: If the DuckDuckGo API call fails.

    Example:
        DuckDuckGo_search(query="Python web scraping tutorial")
    """
    try:
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        # Perform search using DDGS
        ddgs = DDGS()
        results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=10)

        # Structure the results
        formatted_results = [
            {
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            }
            for result in results
        ]

        return json.dumps(formatted_results)

    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def fetch_content(url: str) -> str:
    """
    Extracts the main textual content from a webpage given its URL.

    Args:
        url (str): The URL of the webpage to scrape.
            Example: "https://example.com/article"

    Returns:
        str: A JSON string containing the main textual content of the webpage, stripped of irrelevant elements.

    Raises:
        ValueError: If the URL is invalid or empty.
        Exception: If the webpage content cannot be fetched or parsed.

    Example:
        fetch_content(url="https://example.com/article")
    """
    try:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        # Fetch webpage content
        response = requests.get(url, timeout=(3.05, 27))
        response.raise_for_status()

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)

        return json.dumps({"content": text_content})

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Request failed: {str(e)}"})

    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Ensure proper encoding for stdout
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()