import sys
import os
import httpx
import json
import time
from mcp.server.fastmcp import FastMCP
import asyncio

# Initialize FastMCP server
mcp = FastMCP("academic_paper_mcp")

# Global configuration for proxy support
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

def handle_api_errors(func):
    """Decorator to handle API errors consistently"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                return json.dumps({"error": "API rate limit exceeded. Please try again later."})
            elif e.response.status_code == 404:
                return json.dumps({"error": "Paper not found in specified source"})
            else:
                return json.dumps({"error": f"API error: {str(e)}"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    return wrapper

async def exponential_backoff(max_retries=3, base_delay=1):
    """Implement exponential backoff for API requests"""
    for attempt in range(max_retries):
        yield attempt
        if attempt < max_retries - 1:
            await asyncio.sleep(base_delay * (2 ** attempt))

@mcp.tool()
@handle_api_errors
async def search_papers(keywords: str, limit: int) -> str:
    """    Searches for academic papers based on keywords and limits the number of results.

    Args:
        keywords (str): Search terms to query academic papers. Must not be empty.
        limit (int): Maximum number of results to return. Must be positive.

    Returns:
        str: A JSON string containing a list of dictionaries, each with the following keys:
            - title (str): The title of the paper.
            - authors (list of str): A list of the authors' names.
            - year (int): The year of publication.
            - doi (str): The DOI of the paper.

    Example:
        search_papers(keywords="machine learning", limit=5)
    """
    # Input validation
    if not keywords or not keywords.strip():
        return json.dumps({"error": "Keywords cannot be empty"})
    if limit <= 0:
        return json.dumps({"error": "Limit must be a positive integer"})

    async with httpx.AsyncClient() as async_client:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={keywords}&limit={limit}"
        
        # Implement rate limit handling with exponential backoff
        async for attempt in exponential_backoff():
            try:
                response = await async_client.get(url)
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < 3:
                    continue  # Retry if rate limited
                raise

        papers = response.json().get("data", [])

        if not papers:
            return json.dumps({"error": "No papers found matching the criteria"})

        formatted_papers = []
        for paper in papers:
            # Add validation to ensure we have required fields
            if not paper.get("title"):
                continue  # Skip papers without titles
                
            formatted_papers.append({
                "title": paper["title"],
                "authors": [author["name"] for author in paper.get("authors", []) if author and author.get("name")],
                "year": paper.get("year") if paper.get("year") else None,
                "doi": paper.get("doi") if paper.get("doi") else None
            })

        if not formatted_papers:
            return json.dumps({"error": "Found papers but they were missing required information (title, authors, year, or DOI)"})

        return json.dumps(formatted_papers)

@mcp.tool()
@handle_api_errors
async def fetch_paper_details(paper_id: str, source: str) -> str:
    """    Fetches detailed information about a specific paper using its ID and specified source.

    Args:
        paper_id (str): The identifier of the paper (e.g., DOI or Semantic Scholar ID).
        source (str): The source to fetch details from ("Semantic Scholar" or "Crossref").

    Returns:
        str: A JSON string containing a dictionary with the following keys:
            - title (str): The title of the paper.
            - authors (list of str): A list of the authors' names.
            - abstract (str): The abstract of the paper.
            - venue (str): The venue or publication source.

    Example:
        fetch_paper_details(paper_id="10.1145/3368089.3417052", source="Semantic Scholar")
    """
    if not paper_id:
        return json.dumps({"error": "Paper ID cannot be empty or null. This typically happens when a previous search step failed to return valid paper information."})

    try:
        if source.lower() == "semantic scholar":
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        elif source.lower() == "crossref":
            url = f"https://api.crossref.org/works/{paper_id}"
        else:
            raise ValueError("Invalid source specified. Use 'Semantic Scholar' or 'Crossref'.")

        async with httpx.AsyncClient() as async_client:
            # Implement rate limit handling with exponential backoff
            async for attempt in exponential_backoff():
                try:
                    response = await async_client.get(url)
                    response.raise_for_status()
                    break
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429 and attempt < 3:
                        continue  # Retry if rate limited
                    raise

            data = response.json()

            # Improve data extraction with fallbacks
            paper_details = {
                "title": data.get("title") or "Untitled Paper",
                "authors": [author["name"] for author in data.get("authors", []) if author and author.get("name")],
                "abstract": data.get("abstract", "No abstract available"),
                "venue": data.get("venue", "Unknown venue")
            }

            # If we're missing critical information, return an error
            if not paper_details["title"] and not paper_details["abstract"]:
                return json.dumps({"error": "Failed to retrieve essential paper details (title and abstract are missing). The paper might not exist in this source."})

            return json.dumps(paper_details)

    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
@handle_api_errors
async def search_by_topic(topic: str, year_range: tuple = None, limit: int = 10) -> str:
    """    Searches for papers related to a specific topic, with optional year range and result limit.

    Args:
        topic (str): The topic keyword(s) to search for.
        year_range (tuple of int, optional): A tuple specifying the start and end years for filtering results.
        limit (int): Maximum number of results to return.

    Returns:
        str: A JSON string containing a list of dictionaries, each with the following keys:
            - title (str): The title of the paper.
            - authors (list of str): A list of the authors' names.
            - year (int): The year of publication.
            - doi (str): The DOI of the paper.

    Example:
        search_by_topic(topic="artificial intelligence", year_range=(2015, 2020), limit=5)
    """
    # Input validation
    if not topic or not topic.strip():
        return json.dumps({"error": "Topic cannot be empty"})
    if limit <= 0:
        return json.dumps({"error": "Limit must be a positive integer"})
    if year_range and (len(year_range) != 2 or year_range[0] > year_range[1]):
        return json.dumps({"error": "Invalid year range format. Use (start_year, end_year)"})

    async with httpx.AsyncClient() as async_client:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={topic}&limit={limit}"
        if year_range:
            url += f"&year_start={year_range[0]}&year_end={year_range[1]}"

        # Implement rate limit handling with exponential backoff
        async for attempt in exponential_backoff():
            try:
                response = await async_client.get(url)
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < 3:
                    continue  # Retry if rate limited
                raise

        papers = response.json().get("data", [])

        if not papers:
            return json.dumps({"error": "No papers found matching the criteria"})

        formatted_papers = []
        for paper in papers:
            # Add validation to ensure we have required fields
            if not paper.get("title"):
                continue  # Skip papers without titles

            formatted_papers.append({
                "title": paper["title"],
                "authors": [author["name"] for author in paper.get("authors", []) if author and author.get("name")],
                "year": paper.get("year") if paper.get("year") else None,
                "doi": paper.get("doi") if paper.get("doi") else None
            })

        if not formatted_papers:
            return json.dumps({"error": "Found papers but they were missing required information (title, authors, year, or DOI)"})

        return json.dumps(formatted_papers)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()