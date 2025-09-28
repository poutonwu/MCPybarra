import os
import re
import json
import sys
from typing import List, Dict
from mcp.server.fastmcp import FastMCP
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import requests

os.environ.get('HTTP_PROXY', 'http://127.0.0.1:7890')
os.environ.get('HTTPS_PROXY', 'http://127.0.0.1:7890')
# Initialize the MCP server
mcp = FastMCP("duckduckgo_search_and_fetch")

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
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string.")
    if not isinstance(num_results, int) or num_results <= 0:
        raise ValueError("num_results must be a positive integer.")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
    except Exception as e:
        raise RuntimeError(f"Error occurred during DuckDuckGo search: {e}")

    if not results:
        return []

    processed_results = []
    for result in results:
        url = result.get("href")
        title = result.get("title")
        if not url or not title:
            continue

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator="\n")
            cleaned_text = clean_text(text)
            processed_results.append({"title": title, "url": url, "content": cleaned_text})
        except requests.RequestException as e:
            print(f"Failed to fetch content from {url}: {e}", file=sys.stderr)

    return processed_results


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