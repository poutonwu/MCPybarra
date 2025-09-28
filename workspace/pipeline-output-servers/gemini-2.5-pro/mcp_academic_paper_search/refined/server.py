import sys
import os
import json
import asyncio
import re
from mcp.server.fastmcp import FastMCP
import httpx
from semanticscholar import SemanticScholar
from crossref.restful import Works
import urllib.parse

# Set proxies if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize FastMCP server
mcp = FastMCP("mcp_academic_paper_search")

# Initialize API clients
# semanticscholar library version: 0.7.0
# crossrefapi version: 1.5.0
sch = SemanticScholar()
works = Works()

def format_semantic_scholar_paper(paper):
    """Formats a paper from Semantic Scholar."""
    return {
        "title": paper.get("title"),
        "authors": [author["name"] for author in paper.get("authors", [])],
        "year": paper.get("year"),
        "doi": paper.get("externalIds", {}).get("DOI"),
        "source": "Semantic Scholar"
    }

def format_crossref_paper(paper):
    """Formats a paper from Crossref."""
    authors = []
    if "author" in paper and paper["author"]:
        authors = [f"{author.get('given', '')} {author.get('family', '')}".strip() for author in paper["author"]]
    
    year = None
    if "published-print" in paper and "date-parts" in paper["published-print"] and paper["published-print"]["date-parts"]:
        year = paper["published-print"]["date-parts"][0][0]
    elif "created" in paper and "date-parts" in paper["created"] and paper["created"]["date-parts"]:
        year = paper["created"]["date-parts"][0][0]

    return {
        "title": paper.get("title", [None])[0],
        "authors": authors,
        "year": year,
        "doi": paper.get("DOI"),
        "source": "Crossref"
    }

@mcp.tool()
async def search_papers(query: str, limit: int = 10) -> str:
    """
    Concurrently searches for academic papers on Semantic Scholar and Crossref
    and returns a combined list of results. This tool is useful for broad
    searches across multiple academic databases to get a comprehensive overview
    of the literature on a given topic.

    Args:
        query (str): The search keywords for finding papers. This can be a
            paper title, author names, or general topics.
        limit (int): The maximum number of papers to return from each source.
            The total number of results may be up to 2 * limit. Defaults to 10.

    Returns:
        str: A JSON string representing a list of dictionaries. Each dictionary
            represents a found paper and contains keys for 'title', 'authors',
            'year', 'doi', and 'source' (either 'Semantic Scholar' or 'Crossref').
            If an error occurs, a JSON string with an 'error' key is returned.

    Example:
        search_papers(query="reinforcement learning from human feedback", limit=5)
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string.")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")

    try:
        # Add timeout for API calls
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Run searches concurrently
            results = await asyncio.gather(
                search_semantic_scholar(query, limit, client),
                search_crossref(query, limit, client)
            )
            
            # Flatten the list of lists and return as JSON
            all_papers = [paper for result_list in results for paper in result_list]
            return json.dumps(all_papers)

    except httpx.TimeoutException:
        return json.dumps({"error": "API request timed out. Please try again later."})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})

async def search_semantic_scholar(query, limit, client):
    """Helper for Semantic Scholar search with proper encoding."""
    try:
        # Encode query parameters properly using urllib.parse.quote
        encoded_query = urllib.parse.quote(query)
        search_results = sch.search_paper(encoded_query, limit=limit)
        papers = [paper for paper in search_results]
        return [format_semantic_scholar_paper(paper) for paper in papers]
    except Exception as e:
        # Log error for debugging
        print(f"Semantic Scholar search error: {str(e)}")
        return []

async def search_crossref(query, limit, client):
    """Helper for Crossref search with proper encoding."""
    try:
        # Use proper query encoding for Crossref
        crossref_results = works.query(bibliographic=query).sample(limit)
        return [format_crossref_paper(paper) for paper in crossref_results]
    except Exception as e:
        # Log error for debugging
        print(f"Crossref search error: {str(e)}")
        return []

@mcp.tool()
async def fetch_paper_details(paper_id: str, source: str) -> str:
    """
    Fetches detailed information for a specific paper from either Semantic
    Scholar or Crossref. This is an async function to better handle API requests.

    Args:
        paper_id (str): The identifier of the paper. For Crossref, this should
            be a DOI. For Semantic Scholar, it can be a DOI or its specific ID.
        source (str): The data source to query. Must be either 'Semantic Scholar'
            or 'Crossref'.

    Returns:
        str: A JSON string containing the paper's details, including 'title',
            'authors', 'abstract', and 'venue'. Returns a JSON object with an
            'error' key if the paper is not found or an API error occurs.

    Example:
        fetch_paper_details(paper_id="10.1109/5.771073", source="Crossref")
    """
    if not paper_id or not isinstance(paper_id, str):
        raise ValueError("Paper ID must be a non-empty string.")
    if source not in ["Semantic Scholar", "Crossref"]:
        raise ValueError("Source must be either 'Semantic Scholar' or 'Crossref'.")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if source == "Semantic Scholar":
                # Use the async implementation
                paper = await asyncio.get_event_loop().run_in_executor(None, sch.get_paper, paper_id, ['title', 'authors', 'abstract', 'venue'])
                if not paper:
                    return json.dumps({"error": "Paper not found on Semantic Scholar."})
                
                details = {
                    "title": paper.get("title"),
                    "authors": [author["name"] for author in paper.get("authors", [])],
                    "abstract": paper.get("abstract"),
                    "venue": paper.get("venue")
                }
            else:  # Crossref
                # Use the async client for Crossref
                # Properly encode the paper_id using urllib.parse.quote
                url = f"https://api.crossref.org/works/{urllib.parse.quote(paper_id)}"
                response = await client.get(url)
                if response.status_code == 404:
                    return json.dumps({"error": "Paper not found on Crossref."})
                
                response.raise_for_status()
                paper = response.json()["message"]
                
                authors = []
                if "author" in paper and paper["author"]:
                    authors = [f"{author.get('given', '')} {author.get('family', '')}".strip() for author in paper["author"]]

                details = {
                    "title": paper.get("title", [None])[0],
                    "authors": authors,
                    "abstract": paper.get("abstract"),
                    "venue": (paper.get("container-title") or [None])[0]
                }
            
            return json.dumps(details)

    except httpx.TimeoutException:
        return json.dumps({"error": "API request timed out. Please try again later."})
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"API request failed with status {e.response.status_code}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})

@mcp.tool()
async def search_by_topic(topic_keywords: str, year_range: str = None, limit: int = 10) -> str:
    """
    Searches for papers on a specific topic, with an optional filter for a
    range of years. This tool prioritizes Semantic Scholar for its relevance
    ranking and falls back to Crossref if needed. It's ideal for focused
    literature reviews within a specific timeframe.

    Args:
        topic_keywords (str): The topic keywords to search for (e.g., "quantum computing").
        year_range (str, optional): A string representing the year range in
            "YYYY-YYYY" format (e.g., "2020-2023"). Defaults to None, which
            means no year filter is applied.
        limit (int): The maximum number of results to return. Defaults to 10.

    Returns:
        str: A JSON string representing a list of dictionaries, where each
            dictionary is a paper. Returns a JSON object with an 'error' key
            if an issue occurs.

    Example:
        search_by_topic(topic_keywords="large language models", year_range="2021-2022", limit=5)
    """
    if not topic_keywords or not isinstance(topic_keywords, str):
        raise ValueError("Topic keywords must be a non-empty string.")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Limit must be a positive integer.")
    
    year_filter = None
    if year_range:
        # Validate and handle year range
        if not re.match(r"^\d{4}-\d{4}$", year_range):
            raise ValueError("Year range must be in 'YYYY-YYYY' format.")
        
        start_year, end_year = map(int, year_range.split('-'))
        if start_year > end_year:
            # Swap years if they're reversed
            start_year, end_year = end_year, start_year
            year_filter = f"{start_year}-{end_year}"
            # Return warning about swapped years
            return json.dumps({
                "warning": f"Years were reversed, searching from {start_year} to {end_year}",
                "results": []
            })
        else:
            year_filter = year_range

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Prioritize Semantic Scholar
            semantic_results = []
            try:
                # Properly encode query parameters
                encoded_topic = urllib.parse.quote(topic_keywords)
                search_results = await asyncio.get_event_loop().run_in_executor(None, 
                    sch.search_paper, encoded_topic, limit, year_filter)
                papers = [p for p in search_results]
                if papers:
                    formatted_papers = [format_semantic_scholar_paper(paper) for paper in papers]
                    semantic_results = formatted_papers
            except Exception as e:
                print(f"Semantic Scholar search error: {str(e)}")
                # Continue to Crossref even if Semantic Scholar fails

            # Always try Crossref, even if Semantic Scholar succeeded
            crossref_results = []
            try:
                query = works.query(bibliographic=topic_keywords)
                if year_filter:
                    start_year, end_year = year_filter.split('-')
                    query = query.filter(from_pub_date=f'{start_year}-01-01', until_pub_date=f'{end_year}-12-31')
                
                crossref_papers = await asyncio.get_event_loop().run_in_executor(None, query.sample, limit)
                formatted_papers = [format_crossref_paper(paper) for paper in crossref_papers]
                crossref_results = formatted_papers
            except Exception as e:
                print(f"Crossref search error: {str(e)}")
                
            # Combine results from both sources
            all_results = semantic_results + crossref_results
            
            # If we have results from Crossref but not Semantic Scholar, return them
            if crossref_results and not semantic_results:
                return json.dumps(crossref_results)
            
            # If no results from either source
            if not all_results:
                return json.dumps({"error": "Failed to retrieve results from both Semantic Scholar and Crossref."})
            
            # Return all results
            return json.dumps(all_results)

    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})

if __name__ == "__main__":
    if sys.platform == "win32":
        # Prevents UnicodeEncodeError on Windows
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()