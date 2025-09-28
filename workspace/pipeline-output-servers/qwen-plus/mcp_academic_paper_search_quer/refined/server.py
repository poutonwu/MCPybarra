import sys
import os
import httpx
import asyncio
import json
import re
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("academic_paper_search_query")

# Set up environment variables for proxy if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Create a shared async client for Semantic Scholar API
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"
CROSSREF_API = "https://api.crossref.org/works"

# Helper function to validate input parameters
def validate_input(params):
    for key, value in params.items():
        if value is None:
            raise ValueError(f"{key} parameter cannot be None")
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{key} parameter cannot be empty string")

# Helper function to format authors list
def format_authors(author_list):
    if not author_list:
        return []
    if isinstance(author_list, list):
        return [author.get('name', '') if isinstance(author, dict) else str(author) for author in author_list]
    return []

# Helper function to process Semantic Scholar paper data
def process_semantic_scholar_paper(paper):
    try:
        return {
            "title": paper.get("title", "N/A"),
            "authors": format_authors(paper.get("authors", [])),
            "year": int(paper.get("year", 0)) if paper.get("year") else 0,
            "doi": paper.get("doi", "N/A"),
            "source": "Semantic Scholar"
        }
    except Exception as e:
        raise ValueError(f"Error processing Semantic Scholar paper: {str(e)}")

# Helper function to process Crossref paper data
def process_crossref_paper(paper):
    try:
        title = paper.get("title", ["N/A"])[0] if isinstance(paper.get("title"), list) else "N/A"
        
        author_list = paper.get("author", [])
        authors = []
        for author in author_list:
            if isinstance(author, dict):
                family_name = author.get("family", "")
                given_name = author.get("given", "")
                full_name = f"{given_name} {family_name}".strip()
                authors.append(full_name)
        
        published_date = paper.get("published", {}).get("date-time", "") if isinstance(paper.get("published"), dict) else ""
        year = int(published_date[:4]) if published_date and published_date[:4].isdigit() else 0
        
        doi = paper.get("DOI", "N/A")
        
        return {
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi,
            "source": "Crossref"
        }
    except Exception as e:
        raise ValueError(f"Error processing Crossref paper: {str(e)}")

@mcp.tool()
async def search_papers(keywords: str, limit: int = 5) -> str:
    """
    Search academic papers based on keywords from Semantic Scholar and Crossref APIs.

    Args:
        keywords (str): Keywords used for searching papers (required).
        limit (int): Maximum number of results to return, default is 5 (optional).

    Returns:
        str: A JSON array containing paper information including title, authors, year, and DOI.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
        RuntimeError: If both Semantic Scholar and Crossref APIs fail.
    """
    try:
        # Input validation
        validate_input({"keywords": keywords})
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")

        # Shared HTTP client for reuse
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            # Try Semantic Scholar first
            try:
                semantic_scholar_params = {
                    "query": keywords,
                    "limit": limit,
                    "fields": "title,authors,year,doi"
                }
                
                ss_response = await client.get(SEMANTIC_SCHOLAR_API, params=semantic_scholar_params)
                ss_response.raise_for_status()
                
                ss_data = ss_response.json()
                results = [process_semantic_scholar_paper(paper) for paper in ss_data.get("data", [])]
                
                # If we don't have enough results from Semantic Scholar, supplement with Crossref
                if len(results) < limit:
                    crossref_params = {
                        "query": keywords,
                        "rows": limit - len(results)
                    }
                    
                    cr_response = await client.get(CROSSREF_API, params=crossref_params)
                    cr_response.raise_for_status()
                    
                    cr_data = cr_response.json()
                    results.extend([process_crossref_paper(paper) for paper in cr_data.get("message", {}).get("items", [])])
                
                return json.dumps(results[:limit])
            
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                # If Semantic Scholar fails, try Crossref directly
                try:
                    crossref_params = {
                        "query": keywords,
                        "rows": limit
                    }
                    
                    cr_response = await client.get(CROSSREF_API, params=crossref_params)
                    cr_response.raise_for_status()
                    
                    cr_data = cr_response.json()
                    results = [process_crossref_paper(paper) for paper in cr_data.get("message", {}).get("items", [])]
                    return json.dumps(results[:limit])
                except (httpx.HTTPStatusError, httpx.RequestError) as e2:
                    raise RuntimeError(f"Both Semantic Scholar and Crossref APIs failed: {str(e)}, {str(e2)}")

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Unexpected error in search_papers: {str(e)}")

@mcp.tool()
async def fetch_paper_details(paper_id: str, source: str) -> str:
    """
    Fetch detailed information about a specific paper based on its ID and source.

    Args:
        paper_id (str): Unique identifier of the paper (DOI or Semantic Scholar ID) (required).
        source (str): Data source ("Semantic Scholar" or "Crossref") (required).

    Returns:
        str: A JSON object containing detailed paper information including title, authors, abstract, and publication venue.

    Raises:
        ValueError: If input validation fails or invalid source is provided.
        httpx.HTTPStatusError: If API request fails.
        RuntimeError: If paper details cannot be retrieved.
    """
    try:
        # Input validation
        validate_input({"paper_id": paper_id, "source": source})
        
        if source not in ["Semantic Scholar", "Crossref"]:
            raise ValueError(f"Invalid source: {source}. Must be 'Semantic Scholar' or 'Crossref'")

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            if source == "Semantic Scholar":
                try:
                    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
                    params = {"fields": "title,authors,abstract,venue"}
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    paper_data = response.json()
                    processed_data = {
                        "title": paper_data.get("title", "N/A"),
                        "authors": format_authors(paper_data.get("authors", [])),
                        "abstract": paper_data.get("abstract", "N/A"),
                        "publication_venue": paper_data.get("venue", "N/A")
                    }
                    return json.dumps(processed_data)
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    raise RuntimeError(f"Failed to fetch details from Semantic Scholar: {str(e)}")
            
            else:  # Crossref
                try:
                    url = f"https://api.crossref.org/works/{paper_id}"
                    response = await client.get(url)
                    response.raise_for_status()
                    
                    paper_data = response.json().get("message", {})
                    
                    title = paper_data.get("title", ["N/A"])[0] if isinstance(paper_data.get("title"), list) else "N/A"
                    
                    author_list = paper_data.get("author", [])
                    authors = []
                    for author in author_list:
                        if isinstance(author, dict):
                            family_name = author.get("family", "")
                            given_name = author.get("given", "")
                            full_name = f"{given_name} {family_name}".strip()
                            authors.append(full_name)
                    
                    abstract = paper_data.get("abstract", "N/A") if isinstance(paper_data.get("abstract"), str) else "N/A"
                    
                    venue = "N/A"
                    if paper_data.get("container-title") and isinstance(paper_data["container-title"], list):
                        venue = paper_data["container-title"][0] if paper_data["container-title"][0] else "N/A"
                    
                    processed_data = {
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "publication_venue": venue
                    }
                    return json.dumps(processed_data)
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    raise RuntimeError(f"Failed to fetch details from Crossref: {str(e)}")

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Unexpected error in fetch_paper_details: {str(e)}")

@mcp.tool()
async def search_by_topic(topic: str, year_range: str = None, limit: int = 5) -> str:
    """
    Search papers by topic with optional year range filtering.

    Args:
        topic (str): Topic keywords for paper search (required).
        year_range (str): Year range in format "YYYY-YYYY" (optional).
        limit (int): Maximum number of results to return, default is 5 (optional).

    Returns:
        str: A JSON array containing paper information including title, authors, year, and DOI.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
        RuntimeError: If both search methods fail.
    """
    try:
        # Input validation
        validate_input({"topic": topic})
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        
        # Validate year range format if provided
        year_min, year_max = None, None
        if year_range:
            if not re.match(r"^\d{4}-\d{4}$", year_range):
                raise ValueError(f"Invalid year_range format: {year_range}. Expected format: YYYY-YYYY")
            year_parts = year_range.split("-")
            if len(year_parts) != 2:
                raise ValueError(f"Invalid year_range: {year_range}. Expected two years separated by hyphen.")
            try:
                year_min, year_max = map(int, year_parts)
            except ValueError:
                raise ValueError(f"Invalid year values in year_range: {year_range}")
            if year_min > year_max:
                raise ValueError(f"Invalid year_range: min year {year_min} should be less than max year {year_max}")

        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            # First try Semantic Scholar with topic search
            try:
                semantic_scholar_params = {
                    "query": topic,
                    "limit": limit,
                    "fields": "title,authors,year,doi"
                }
                
                # Add year filter if specified
                if year_range:
                    semantic_scholar_params["year"] = year_range
                
                ss_response = await client.get(SEMANTIC_SCHOLAR_API, params=semantic_scholar_params)
                ss_response.raise_for_status()
                
                ss_data = ss_response.json()
                results = [process_semantic_scholar_paper(paper) for paper in ss_data.get("data", [])]
                
                # If we don't have enough results from Semantic Scholar, use general search
                if len(results) < limit:
                    # Use search_papers as fallback
                    fallback_results = await search_papers(topic, limit - len(results))
                    results.extend(json.loads(fallback_results))
                
                return json.dumps(results[:limit])
            
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                # If Semantic Scholar fails, try general search
                try:
                    fallback_results = await search_papers(topic, limit)
                    return fallback_results
                except Exception as e2:
                    raise RuntimeError(f"Failed to search by topic: {str(e)}, {str(e2)}")

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise RuntimeError(f"Unexpected error in search_by_topic: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()