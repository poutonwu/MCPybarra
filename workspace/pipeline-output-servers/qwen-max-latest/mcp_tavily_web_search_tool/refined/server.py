import os
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Optional

# Initialize the FastMCP server with the name 'mcp_tavily_web_search_tool'
mcp = FastMCP("mcp_tavily_web_search_tool")

# Shared AsyncClient for performance optimization
client = httpx.AsyncClient(
    base_url="https://api.tavily.com",
    headers={"Authorization": f"Bearer {os.environ.get('TAVILY_API_KEY', 'REDACTED_SECRET')}"}
)

class SearchResult(BaseModel):
    title: str
    url: str
    content: str  # Changed from content_summary to content based on actual Tavily API response

class TavilyWebSearchToolInput(BaseModel):
    query: str
    search_depth: str = "basic"
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None
    max_results: int = 5

@mcp.tool()
async def tavily_web_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> List[SearchResult]:
    """
    Performs a comprehensive web search using the Tavily API.

    Args:
        query: The search query for technical information, APIs, or code examples.
        search_depth: Search depth: 'basic' for quick results, 'advanced' for more comprehensive analysis.
        include_domains: A list of domains to specifically include in the search results.
        exclude_domains: A list of domains to specifically exclude from the search results.
        max_results: Maximum number of search results to return.

    Returns:
        A list of search results, each containing the title, URL, and content.

    Example:
        Performing a basic search for Python libraries related to data science:
        tavily_web_search(query="Python data science libraries", search_depth="basic", max_results=3)
    """
    try:
        # Validate inputs
        if not query or not isinstance(query, str):
            raise ValueError("'query' must be a non-empty string.")
        if search_depth not in ["basic", "advanced"]:
            raise ValueError("'search_depth' must be either 'basic' or 'advanced'.")
        if max_results <= 0:
            raise ValueError("'max_results' must be a positive integer.")

        payload = {
            "query": query,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "max_results": max_results
        }

        response = await client.post("/search", json=payload)
        response.raise_for_status()

        results = response.json().get("results", [])
        return [
            SearchResult(title=r['title'], url=r['url'], content=r['content'])
            for r in results
        ]
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise RuntimeError(f"Request failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while performing the web search: {str(e)}")


class TavilyAnswerSearchToolInput(BaseModel):
    query: str
    max_results: int = 5

@mcp.tool()
async def tavily_answer_search(
    query: str,
    max_results: int = 5
) -> str:
    """
    Generates a direct answer based on the query content with supporting evidence using the Tavily API.

    Args:
        query: The search query for which an answer is needed.
        max_results: Maximum number of search results to return.

    Returns:
        A string containing the generated answer along with supporting evidence.

    Example:
        Generating an answer for a specific question about Python:
        tavily_answer_search(query="What is the difference between a list and a tuple in Python?", max_results=3)
    """
    try:
        # Validate inputs
        if not query or not isinstance(query, str):
            raise ValueError("'query' must be a non-empty string.")
        if max_results <= 0:
            raise ValueError("'max_results' must be a positive integer.")

        payload = {
            "query": query,
            "max_results": max_results,
            "include_answer": True  # Ensure answer is included in response
        }

        response = await client.post("/search", json=payload)  # Using /search endpoint instead of /answer
        response.raise_for_status()

        answer_data = response.json()
        return answer_data.get("answer", "No answer found.")
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise RuntimeError(f"Request failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while generating the answer: {str(e)}")


class TavilyNewsSearchToolInput(BaseModel):
    query: str
    days_back: int = 7
    include_sources: Optional[List[str]] = None
    exclude_sources: Optional[List[str]] = None
    max_results: int = 5

@mcp.tool()
async def tavily_news_search(
    query: str,
    days_back: int = 7,
    include_sources: Optional[List[str]] = None,
    exclude_sources: Optional[List[str]] = None,
    max_results: int = 5
) -> List[SearchResult]:
    """
    Searches recent news articles using the Tavily API.

    Args:
        query: The search query for news articles.
        days_back: Number of days back to search for news articles (maximum 365).
        include_sources: Specific news sources to include in the search results.
        exclude_sources: Specific news sources to exclude from the search results.
        max_results: Maximum number of search results to return.

    Returns:
        A list of recent news article results, each containing the title, URL, and content.

    Example:
        Searching for recent news about AI developments over the last 30 days:
        tavily_news_search(query="AI developments", days_back=30, max_results=3)
    """
    try:
        # Validate inputs
        if not query or not isinstance(query, str):
            raise ValueError("'query' must be a non-empty string.")
        if days_back <= 0 or days_back > 365:
            raise ValueError("'days_back' must be between 1 and 365.")
        if max_results <= 0:
            raise ValueError("'max_results' must be a positive integer.")

        payload = {
            "query": query,
            "days_back": days_back,
            "include_sources": include_sources,
            "exclude_sources": exclude_sources,
            "max_results": max_results,
            "topic": "news"  # Set topic to news for news searches
        }

        response = await client.post("/search", json=payload)  # Using /search endpoint instead of /news
        response.raise_for_status()

        results = response.json().get("results", [])
        return [
            SearchResult(title=r['title'], url=r['url'], content=r['content'])
            for r in results
        ]
    except httpx.HTTPStatusError as e:
        raise RuntimeError(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise RuntimeError(f"Request failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while searching for news articles: {str(e)}")

if __name__ == "__main__":
    mcp.run()