import sys
import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ValidationError, validator
import os
import json

# Initialize FastMCP Server
mcp = FastMCP("mcp_tavily_web_tools")

# Setup Proxy (optional)
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Load Tavily API Key from environment variables
TAVILY_API_KEY="REDACTED_SECRET"
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is not set.")

# Base Model for Validation
class TavilyRequest(BaseModel):
    query: str
    search_depth: str = "basic"
    include_domains: list[str] = []
    exclude_domains: list[str] = []
    max_results: int = 5
    time_range: int = None
    include_sources: list[str] = []
    exclude_sources: list[str] = []

    @validator('search_depth')
    def validate_search_depth(cls, v):
        if v not in ["basic", "advanced"]:
            raise ValueError("search_depth must be either 'basic' or 'advanced'")
        return v

    @validator('time_range')
    def validate_time_range(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("time_range cannot be negative")
            if v > 365:
                raise ValueError("time_range cannot exceed 365 days")
        return v

    @validator('max_results')
    def validate_max_results(cls, v):
        if v <= 0:
            raise ValueError("max_results must be a positive integer")
        if v > 10:
            raise ValueError("max_results cannot exceed 10")
        return v

@mcp.tool()
async def tavily_web_search(query: str, search_depth: str = "basic", include_domains: list[str] = [], exclude_domains: list[str] = [], max_results: int = 5) -> str:
    """
    Conduct a comprehensive web search using the Tavily API.

    Args:
        query (str): The search query for retrieving information.
        search_depth (str, optional): The depth of the search, either 'basic' or 'advanced'. Defaults to 'basic'.
        include_domains (list of str, optional): Domains to include in the search results.
        exclude_domains (list of str, optional): Domains to exclude from the search results.
        max_results (int, optional): Maximum number of search results to return. Defaults to 5.

    Returns:
        str: A JSON string containing the search results.

    Raises:
        ValidationError: If input parameters are invalid.
        httpx.HTTPStatusError: If the API request fails.

    Example:
        tavily_web_search(query="Python documentation", search_depth="basic", max_results=3)
    """
    try:
        # Validate input
        validated_data = TavilyRequest(
            query=query,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            max_results=max_results
        )

        headers = {
            "Authorization": f"Bearer {TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "query": validated_data.query,
                    "search_depth": validated_data.search_depth,
                    "include_domains": validated_data.include_domains,
                    "exclude_domains": validated_data.exclude_domains,
                    "max_results": validated_data.max_results
                },
                headers=headers
            )
            response.raise_for_status()
            return json.dumps(response.json())

    except ValidationError as e:
        return json.dumps({"error": "Validation Error", "details": str(e)})

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": "HTTP Request Failed", "details": str(e)})

@mcp.tool()
async def tavily_answer_search(query: str, search_depth: str = "advanced", max_results: int = 5) -> str:
    """
    Retrieve a direct answer to a query using the Tavily API.

    Args:
        query (str): The question or query to be answered.
        search_depth (str, optional): The depth of the search, either 'basic' or 'advanced'. Defaults to 'advanced'.
        max_results (int, optional): Maximum number of results to return. Defaults to 5.

    Returns:
        str: A JSON string containing the answer and supporting evidence.

    Raises:
        ValidationError: If input parameters are invalid.
        httpx.HTTPStatusError: If the API request fails.

    Example:
        tavily_answer_search(query="What is Python?", max_results=2)
    """
    try:
        # Validate input
        validated_data = TavilyRequest(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )

        headers = {
            "Authorization": f"Bearer {TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "query": validated_data.query,
                    "search_depth": validated_data.search_depth,
                    "max_results": validated_data.max_results
                },
                headers=headers
            )
            response.raise_for_status()
            return json.dumps(response.json())

    except ValidationError as e:
        return json.dumps({"error": "Validation Error", "details": str(e)})

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": "HTTP Request Failed", "details": str(e)})

@mcp.tool()
async def tavily_news_search(query: str, time_range: int = 30, include_sources: list[str] = [], exclude_sources: list[str] = [], max_results: int = 5) -> str:
    """
    Search for recent news articles using the Tavily API.

    Args:
        query (str): The search query for retrieving news.
        time_range (int, optional): The number of days to look back for news articles (maximum 365 days). Defaults to 30.
        include_sources (list of str, optional): News sources to include in the search results.
        exclude_sources (list of str, optional): News sources to exclude from the search results.
        max_results (int, optional): Maximum number of news articles to return. Defaults to 5.

    Returns:
        str: A JSON string containing the news articles.

    Raises:
        ValidationError: If input parameters are invalid.
        httpx.HTTPStatusError: If the API request fails.

    Example:
        tavily_news_search(query="AI advancements", time_range=7, max_results=3)
    """
    try:
        # Validate input
        validated_data = TavilyRequest(
            query=query,
            time_range=time_range,
            include_sources=include_sources,
            exclude_sources=exclude_sources,
            max_results=max_results
        )

        headers = {
            "Authorization": f"Bearer {TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "query": validated_data.query,
                    "time_range": validated_data.time_range,
                    "include_sources": validated_data.include_sources,
                    "exclude_sources": validated_data.exclude_sources,
                    "max_results": validated_data.max_results
                },
                headers=headers
            )
            response.raise_for_status()
            return json.dumps(response.json())

    except ValidationError as e:
        return json.dumps({"error": "Validation Error", "details": str(e)})

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": "HTTP Request Failed", "details": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()