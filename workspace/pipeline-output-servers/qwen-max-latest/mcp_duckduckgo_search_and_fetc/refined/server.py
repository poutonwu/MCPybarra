import os
import re
import sys
import time
import random
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import requests
from urllib3.util import Retry
from requests import Session
from requests.adapters import HTTPAdapter
from duckduckgo_search.exceptions import RatelimitException

# Set up proxy from environment if available
os.environ.get('HTTP_PROXY', 'http://127.0.0.1:7890')
os.environ.get('HTTPS_PROXY', 'http://127.0.0.1:7890')

# Initialize the MCP server
mcp = FastMCP("duckduckgo_search_and_fetch")

def configure_session_with_retries() -> Session:
    """Configure a requests Session with retry strategy to handle transient failures."""
    s = Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504, 429],
        allowed_methods=('GET', 'POST')
    )
    s.mount('https://', HTTPAdapter(max_retries=retries))
    s.mount('http://', HTTPAdapter(max_retries=retries))
    return s

@mcp.tool()
def search_and_fetch(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Perform a DuckDuckGo search for the given query and fetch the content of the top results.

    Args:
        query (str): The search query.
        num_results (int): The number of top results to fetch. Defaults to 5.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the title, URL, and cleaned text of each result.
    """
    # Validate inputs immediately before any external calls
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must be a non-empty string.")
    
    if not isinstance(num_results, int) or num_results <= 0:
        raise ValueError("num_results must be a positive integer.")

    try:
        # Handle rate limiting by adding exponential backoff
        for attempt in range(3):
            try:
                # Use DDGS context manager for search
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=num_results))
                break
            except RatelimitException:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Retrying in {wait_time:.2f} seconds...", file=sys.stderr)
                time.sleep(wait_time)
        else:
            # If all attempts fail, raise an error
            raise RuntimeError("Search failed due to rate limiting. Consider reducing request frequency or using an API key if available.")

        # If no results found, return empty list
        if not results:
            return []

        # Configure session with retry strategy
        session = configure_session_with_retries()
        
        processed_results = []
        for result in results:
            url = result.get("href")
            title = result.get("title")
            
            if not url or not title:
                continue

            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                text = soup.get_text(separator="\n")
                cleaned_text = clean_text(text)
                processed_results.append({"title": title, "url": url, "content": cleaned_text})
            except requests.RequestException as e:
                print(f"Failed to fetch content from {url}: {e}", file=sys.stderr)
                continue
                
        return processed_results
        
    except Exception as e:
        # Handle specific rate limiting cases
        if "Ratelimit" in str(e):
            raise RuntimeError("Search failed due to rate limiting. Consider using an API key for unrestricted access.") from e
        else:
            raise RuntimeError(f"Error occurred during DuckDuckGo search: {e}") from e

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing excessive whitespace, special characters, and other noise.

    Args:
        text (str): The raw text to clean.

    Returns:
        str: The cleaned and normalized text.
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")

    # Remove HTML tags and excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove special characters except basic punctuation
    text = re.sub(r"[^a-zA-Z0-9\s.,!?;:'\"-]", "", text)
    return text

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()