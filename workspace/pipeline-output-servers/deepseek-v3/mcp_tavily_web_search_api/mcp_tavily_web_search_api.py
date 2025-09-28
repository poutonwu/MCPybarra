import sys
import httpx
import os
from mcp.server.fastmcp import FastMCP
from typing import Optional, List

# Initialize FastMCP server
mcp = FastMCP("mcp_tavily_web_search_api")
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

TAVILY_API_KEY="REDACTED_SECRET"

httpx_client = httpx.AsyncClient()

@mcp.tool()
async def tavily_web_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> str:
    """
    Perform a comprehensive web search using the Tavily API.

    Args:
        query: The search query for technical information, APIs, or code examples.
        search_depth: Search depth; 'basic' for quick results, 'advanced' for more comprehensive analysis. Defaults to 'basic'.
        include_domains: A list of domains to specifically include in the search results.
        exclude_domains: A list of domains to specifically exclude from the search results.
        max_results: Maximum number of search results to return. Defaults to 5, maximum 10.

    Returns:
        A JSON string containing a list of search results, each with 'title', 'url', and 'summary'.

    Raises:
        ValueError: If the query is empty or invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty or contain only whitespace.")
    
    if max_results > 10:
        max_results = 10
    
    params = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results
    }
    
    if include_domains:
        params["include_domains"] = include_domains
    if exclude_domains:
        params["exclude_domains"] = exclude_domains
    
    try:
        response = await httpx_client.get("https://api.tavily.com/search", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(f"API request failed with status {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        raise httpx.RequestError(f"API request failed: {str(e)}")

@mcp.tool()
async def tavily_answer_search(query: str, max_results: int = 5) -> str:
    """
    Generate direct answers to queries using the Tavily API, including supporting evidence.

    Args:
        query: The query for which a direct answer is needed.
        max_results: Maximum number of supporting evidence items to return. Defaults to 5, maximum 10.

    Returns:
        A JSON string containing 'answer' and 'evidence' (a list of dictionaries with 'title', 'url', and 'summary').

    Raises:
        ValueError: If the query is empty or invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty or contain only whitespace.")
    
    if max_results > 10:
        max_results = 10
    
    params = {
        "query": query,
        "max_results": max_results
    }
    
    try:
        response = await httpx_client.get("https://api.tavily.com/answer", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(f"API request failed with status {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        raise httpx.RequestError(f"API request failed: {str(e)}")

@mcp.tool()
async def tavily_news_search(
    query: str,
    time_limit_days: int = 30,
    include_sources: Optional[List[str]] = None,
    exclude_sources: Optional[List[str]] = None,
    max_results: int = 5
) -> str:
    """
    Search for recent news articles using the Tavily API.

    Args:
        query: The search query for news articles.
        time_limit_days: Maximum age of news articles in days. Defaults to 30, maximum 365.
        include_sources: A list of news sources to specifically include in the search results.
        exclude_sources: A list of news sources to specifically exclude from the search results.
        max_results: Maximum number of news articles to return. Defaults to 5, maximum 10.

    Returns:
        A JSON string containing a list of news articles, each with 'title', 'url', 'summary', and 'published_date'.

    Raises:
        ValueError: If the query is empty or invalid.
        httpx.HTTPStatusError: If the API request fails.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty or contain only whitespace.")
    
    if time_limit_days > 365:
        time_limit_days = 365
    if max_results > 10:
        max_results = 10
    
    params = {
        "query": query,
        "time_limit_days": time_limit_days,
        "max_results": max_results
    }
    
    if include_sources:
        params["include_sources"] = include_sources
    if exclude_sources:
        params["exclude_sources"] = exclude_sources
    
    try:
        response = await httpx_client.get("https://api.tavily.com/news", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(f"API request failed with status {e.response.status_code}: {e.response.text}")
    except httpx.RequestError as e:
        raise httpx.RequestError(f"API request failed: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()