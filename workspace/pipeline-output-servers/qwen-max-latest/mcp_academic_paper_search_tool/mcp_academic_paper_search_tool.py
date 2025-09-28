import os
import re
import json
import sys
from mcp.server.fastmcp import FastMCP
from semanticscholar import SemanticScholar
from crossref.restful import Works

class AcademicPaperSearch:
    def __init__(self):
        self.semantic_scholar = SemanticScholar()
        self.crossref_works = Works()

    def search_papers(self, keywords: str, max_results: int) -> list:
        """
        Searches for academic papers based on keywords and limits the number of results.

        Args:
            keywords (str): The search terms or phrases to look for in academic papers.
            max_results (int): The maximum number of results to return.

        Returns:
            A list of dictionaries, each representing a paper with keys for `title`, `authors`, `year`, and `doi`.

        Example:
            search_papers(keywords="machine learning", max_results=5)
        """
        try:
            # Search Semantic Scholar
            semantic_results = self.semantic_scholar.search_paper(keywords, limit=max_results)
            formatted_semantic_results = [
                {
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "year": paper.year,
                    "doi": paper.doi
                }
                for paper in semantic_results
            ]

            # Search Crossref
            crossref_query = self.crossref_works.query(keywords).sort("relevance").order("desc")[:max_results]
            formatted_crossref_results = [
                {
                    "title": work.get('title', [''])[0],
                    "authors": [f"{author['family']}, {author['given']}" for author in work.get('author', [])],
                    "year": work.get('published-print', {}).get('date-parts', [[None]])[0][0],
                    "doi": work.get('DOI', '')
                }
                for work in crossref_query
            ]

            return formatted_semantic_results + formatted_crossref_results

        except Exception as e:
            raise RuntimeError(f"Error while searching papers: {e}")

    def fetch_paper_details(self, paper_id: str, source: str) -> dict:
        """
        Retrieves detailed information about a specific paper based on its ID and source.

        Args:
            paper_id (str): The unique identifier of the paper (either DOI or Semantic Scholar ID).
            source (str): The source to fetch details from (`Semantic Scholar` or `Crossref`).

        Returns:
            A dictionary containing the `title`, `authors`, `abstract`, and `publication_venue` of the specified paper.

        Example:
            fetch_paper_details(paper_id="10.1093/mind/lix.236.433", source="Semantic Scholar")
        """
        try:
            if source == "Semantic Scholar":
                paper = self.semantic_scholar.get_paper(paper_id)
                return {
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "abstract": paper.abstract,
                    "publication_venue": paper.venue
                }
            elif source == "Crossref":
                work = self.crossref_works.doi(paper_id)
                return {
                    "title": work.get('title', [''])[0],
                    "authors": [f"{author['family']}, {author['given']}" for author in work.get('author', [])],
                    "abstract": work.get('abstract', ''),
                    "publication_venue": work.get('container-title', [''])[0]
                }
            else:
                raise ValueError("Invalid source. Please choose 'Semantic Scholar' or 'Crossref'.")

        except Exception as e:
            raise RuntimeError(f"Error while fetching paper details: {e}")

    def search_by_topic(self, topic_keywords: str, year_range: tuple = None, max_results: int = 10) -> list:
        """
        Searches for papers based on topic keywords, with optional filters for year range and result count limit.

        Args:
            topic_keywords (str): Keywords related to the topic of interest.
            year_range (tuple of int, optional): A tuple specifying the start and end years for filtering results.
            max_results (int, optional): The maximum number of results to return.

        Returns:
            A list of dictionaries, each representing a paper with keys for `title`, `authors`, `year`, and `doi`.

        Example:
            search_by_topic(topic_keywords="AI ethics", year_range=(2015, 2020), max_results=5)
        """
        try:
            # Try searching in Semantic Scholar first
            semantic_results = self.semantic_scholar.search_paper(topic_keywords, limit=max_results)

            if year_range:
                filtered_results = [
                    paper for paper in semantic_results
                    if paper.year and year_range[0] <= paper.year <= year_range[1]
                ]
            else:
                filtered_results = semantic_results

            formatted_results = [
                {
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "year": paper.year,
                    "doi": paper.doi
                }
                for paper in filtered_results
            ]

            return formatted_results

        except Exception as e:
            raise RuntimeError(f"Error while searching by topic: {e}")

# Initialize FastMCP server
mcp = FastMCP("academic_paper_search")

# Instantiate the AcademicPaperSearch class
paper_search = AcademicPaperSearch()

@mcp.tool()
def search_papers_tool(keywords: str, max_results: int) -> str:
    """
    Searches for academic papers based on keywords and limits the number of results.

    Args:
        keywords (str): The search terms or phrases to look for in academic papers.
        max_results (int): The maximum number of results to return.

    Returns:
        A JSON string representing a list of dictionaries, each containing `title`, `authors`, `year`, and `doi`.

    Example:
        search_papers_tool(keywords="machine learning", max_results=5)
    """
    try:
        results = paper_search.search_papers(keywords, max_results)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in search_papers_tool: {e}")

@mcp.tool()
def fetch_paper_details_tool(paper_id: str, source: str) -> str:
    """
    Retrieves detailed information about a specific paper based on its ID and source.

    Args:
        paper_id (str): The unique identifier of the paper (either DOI or Semantic Scholar ID).
        source (str): The source to fetch details from (`Semantic Scholar` or `Crossref`).

    Returns:
        A JSON string containing the `title`, `authors`, `abstract`, and `publication_venue` of the specified paper.

    Example:
        fetch_paper_details_tool(paper_id="10.1093/mind/lix.236.433", source="Semantic Scholar")
    """
    try:
        details = paper_search.fetch_paper_details(paper_id, source)
        return json.dumps(details, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in fetch_paper_details_tool: {e}")

@mcp.tool()
def search_by_topic_tool(topic_keywords: str, year_range_start: int = None, year_range_end: int = None, max_results: int = 10) -> str:
    """
    Searches for papers based on topic keywords, with optional filters for year range and result count limit.

    Args:
        topic_keywords (str): Keywords related to the topic of interest.
        year_range_start (int, optional): Start year for filtering results.
        year_range_end (int, optional): End year for filtering results.
        max_results (int, optional): The maximum number of results to return.

    Returns:
        A JSON string representing a list of dictionaries, each containing `title`, `authors`, `year`, and `doi`.

    Example:
        search_by_topic_tool(topic_keywords="AI ethics", year_range_start=2015, year_range_end=2020, max_results=5)
    """
    try:
        year_range = (year_range_start, year_range_end) if year_range_start is not None and year_range_end is not None else None
        results = paper_search.search_by_topic(topic_keywords, year_range, max_results)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in search_by_topic_tool: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()