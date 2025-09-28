import sys
import httpx
import json
import asyncio
from mcp.server.fastmcp import FastMCP
from semanticscholar import SemanticScholar
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# Initialize FastMCP server
mcp = FastMCP("mcp_academic_paper_search_engine")

# Initialize Semantic Scholar client
semantic_scholar = SemanticScholar()

# Shared HTTPX AsyncClient for performance
client = httpx.AsyncClient(
    headers={"User-Agent": "mcp-academic-paper-search/1.0 (contact@example.com)"}
)

@mcp.tool()
async def search_papers(keywords: str, limit: int = 10) -> str:
    """
    Search for academic papers based on keywords and a result limit.

    Args:
        keywords: The search query for academic papers.
        limit: Maximum number of results to return. Defaults to 10.

    Returns:
        A JSON string containing a list of papers with title, authors, year, and DOI.

    Raises:
        ValueError: If keywords are empty or limit is not a positive integer.
        httpx.HTTPStatusError: If API requests fail.
    """
    if not keywords or not keywords.strip():
        raise ValueError("Keywords cannot be empty.")
    if limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    try:
        # Search Semantic Scholar
        results = semantic_scholar.search_paper(keywords, limit=limit)
        papers = [
            {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "year": paper.year,
                "doi": paper.paperId,
                "source": "semantic_scholar"
            }
            for paper in results
        ]

        # Fallback to Crossref if needed
        if len(papers) < limit:
            crossref_url = f"https://api.crossref.org/works?query={keywords}&rows={limit - len(papers)}"
            response = await client.get(crossref_url)
            response.raise_for_status()
            crossref_data = response.json()
            for item in crossref_data["message"]["items"]:
                papers.append({
                    "title": item.get("title", [""])[0],
                    "authors": [creator.get("name", "") for creator in item.get("author", [])],
                    "year": item.get("created", {}).get("date-parts", [[None]])[0][0],
                    "doi": item.get("DOI", ""),
                    "source": "crossref"
                })

        return json.dumps(papers[:limit])
    except Exception as e:
        raise httpx.HTTPStatusError(f"Failed to search papers: {str(e)}")

@mcp.tool()
async def fetch_paper_details(paper_id: str, source: str) -> str:
    """
    Fetch detailed information for a paper using its ID and source.

    Args:
        paper_id: The paper's DOI or Semantic Scholar ID.
        source: The source to fetch from ('semantic_scholar' or 'crossref').

    Returns:
        A JSON string containing detailed paper information.

    Raises:
        ValueError: If source is invalid or paper_id is empty.
        httpx.HTTPStatusError: If API requests fail.
    """
    if not paper_id or not paper_id.strip():
        raise ValueError("Paper ID cannot be empty.")
    if source not in ["semantic_scholar", "crossref"]:
        raise ValueError("Source must be 'semantic_scholar' or 'crossref'.")

    try:
        if source == "semantic_scholar":
            paper = semantic_scholar.get_paper(paper_id)
            details = {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "abstract": paper.abstract,
                "publication_venue": paper.venue,
                "year": paper.year,
                "doi": paper.paperId
            }
        else:
            crossref_url = f"https://api.crossref.org/works/{paper_id}"
            response = await client.get(crossref_url)
            response.raise_for_status()
            item = response.json()["message"]
            details = {
                "title": item.get("title", [""])[0],
                "authors": [creator.get("name", "") for creator in item.get("author", [])],
                "abstract": item.get("abstract", ""),
                "publication_venue": item.get("container-title", [""])[0],
                "year": item.get("created", {}).get("date-parts", [[None]])[0][0],
                "doi": item.get("DOI", "")
            }

        return json.dumps(details)
    except Exception as e:
        raise httpx.HTTPStatusError(f"Failed to fetch paper details: {str(e)}")

@mcp.tool()
async def search_by_topic(topic: str, year_range: tuple = None, limit: int = 10) -> str:
    """
    Search for papers by topic keywords, optionally filtered by year range.

    Args:
        topic: Topic keywords for the search.
        year_range: Inclusive year range as (start_year, end_year). Defaults to None.
        limit: Maximum number of results to return. Defaults to 10.

    Returns:
        A JSON string containing a list of papers matching the topic and year range.

    Raises:
        ValueError: If topic is empty or year_range is invalid.
        httpx.HTTPStatusError: If API requests fail.
    """
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty.")
    if year_range and (len(year_range) != 2 or year_range[0] > year_range[1]):
        raise ValueError("Year range must be a tuple of (start_year, end_year).")

    try:
        # Search Semantic Scholar
        query = f"{topic}"
        if year_range:
            query += f" year:{year_range[0]}-{year_range[1]}"
        results = semantic_scholar.search_paper(query, limit=limit)
        papers = [
            {
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "year": paper.year,
                "doi": paper.paperId,
                "source": "semantic_scholar"
            }
            for paper in results
        ]

        # Fallback to Crossref if needed
        if len(papers) < limit:
            crossref_query = f"{topic}"
            if year_range:
                crossref_query += f"&filter=from-pub-date:{year_range[0]},until-pub-date:{year_range[1]}"
            crossref_url = f"https://api.crossref.org/works?query={crossref_query}&rows={limit - len(papers)}"
            response = await client.get(crossref_url)
            response.raise_for_status()
            crossref_data = response.json()
            for item in crossref_data["message"]["items"]:
                papers.append({
                    "title": item.get("title", [""])[0],
                    "authors": [creator.get("name", "") for creator in item.get("author", [])],
                    "year": item.get("created", {}).get("date-parts", [[None]])[0][0],
                    "doi": item.get("DOI", ""),
                    "source": "crossref"
                })

        return json.dumps(papers[:limit])
    except Exception as e:
        raise httpx.HTTPStatusError(f"Failed to search by topic: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()