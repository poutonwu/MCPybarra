import sys
import os
import asyncio
import httpx
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("academic_paper_mcp")

# Global configuration for proxy support
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# AsyncClient instance for making HTTP requests
async_client = httpx.AsyncClient()

@mcp.tool()
async def search_papers(keywords: str, limit: int) -> str:
    """
    Searches for academic papers based on keywords and limits the number of results.

    Args:
        keywords (str): Search terms to query academic papers.
        limit (int): Maximum number of results to return.

    Returns:
        str: A JSON string containing a list of dictionaries, each with the following keys:
            - title (str): The title of the paper.
            - authors (list of str): A list of the authors' names.
            - year (int): The year of publication.
            - doi (str): The DOI of the paper.

    Example:
        search_papers(keywords="machine learning", limit=5)
    """
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={keywords}&limit={limit}"
        response = await async_client.get(url)
        response.raise_for_status()
        papers = response.json().get("data", [])

        formatted_papers = [
            {
                "title": paper["title"],
                "authors": [author["name"] for author in paper.get("authors", [])],
                "year": paper.get("year"),
                "doi": paper.get("doi")
            } for paper in papers
        ]

        return json.dumps(formatted_papers)

    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def fetch_paper_details(paper_id: str, source: str) -> str:
    """
    Fetches detailed information about a specific paper using its ID and specified source.

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
    try:
        if source.lower() == "semantic scholar":
            url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        elif source.lower() == "crossref":
            url = f"https://api.crossref.org/works/{paper_id}"
        else:
            raise ValueError("Invalid source specified. Use 'Semantic Scholar' or 'Crossref'.")

        response = await async_client.get(url)
        response.raise_for_status()
        data = response.json()

        paper_details = {
            "title": data.get("title"),
            "authors": [author["name"] for author in data.get("authors", [])],
            "abstract": data.get("abstract", ""),
            "venue": data.get("venue", "")
        }

        return json.dumps(paper_details)

    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def search_by_topic(topic: str, year_range: tuple = None, limit: int = 10) -> str:
    """
    Searches for papers related to a specific topic, with optional year range and result limit.

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
    try:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={topic}&limit={limit}"
        if year_range:
            url += f"&year_start={year_range[0]}&year_end={year_range[1]}"

        response = await async_client.get(url)
        response.raise_for_status()
        papers = response.json().get("data", [])

        formatted_papers = [
            {
                "title": paper["title"],
                "authors": [author["name"] for author in paper.get("authors", [])],
                "year": paper.get("year"),
                "doi": paper.get("doi")
            } for paper in papers
        ]

        return json.dumps(formatted_papers)

    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(async_client.aclose())
    mcp.run()