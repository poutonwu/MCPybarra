import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP
from duckduckgo_search.exceptions import RatelimitException, DuckDuckGoSearchException

# Initialize FastMCP server
mcp = FastMCP("duckduckgo_search_scraper")

# Set up proxy if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

def retry_with_backoff(retries=3, backoff_factor=0.5):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except RatelimitException as e:
                    wait_time = backoff_factor * (2 ** attempt)
                    print(f"Rate limit exceeded: {e}. Retrying in {wait_time}s (attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                    attempt += 1
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break
            return json.dumps({"error": "Failed after maximum retries due to rate limiting."})
        return wrapper
    return decorator

@mcp.tool()
@retry_with_backoff()
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
        RatelimitException: If rate limits are exceeded after max retries.

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

    except DuckDuckGoSearchException as e:
        return json.dumps({"error": f"DuckDuckGo search failed: {str(e)}"})
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