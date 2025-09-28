import os
import json
import re
import asyncio
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
import arxiv
from PyPDF2 import PdfReader

class AsyncArxivClient:
    """Wrapper to make arxiv.Client compatible with async iteration."""
    def __init__(self, page_size=100, delay_seconds=3.0, num_retries=3):
        self.client = arxiv.Client(page_size=page_size, 
                                 delay_seconds=delay_seconds, 
                                 num_retries=num_retries)

    async def results(self, search: arxiv.Search) -> Any:
        """Async generator that yields results from arxiv search."""
        loop = asyncio.get_event_loop()
        # Run the synchronous iteration in a thread pool
        return await loop.run_in_executor(None, list, self.client.results(search))

class ArxivPaperManager:
    def __init__(self):
        self.client = AsyncArxivClient()
        self.local_papers_dir = "workspace/papers/"
        os.makedirs(self.local_papers_dir, exist_ok=True)

    async def search_papers_async(self, query: str) -> str:
        """Searches arXiv for papers based on a user-provided query and returns a list of matching papers.

        Args:
            query: A string containing the search query (e.g., 'quantum computing').

        Returns:
            A JSON-formatted string representing a list of dictionaries, where each dictionary contains details 
            about a paper such as its title, authors, abstract, and arXiv ID.

        Raises:
            ValueError: If the query is empty or invalid.
            Exception: If an error occurs during the API request.
        """
        if not query or not isinstance(query, str):
            raise ValueError("query must be a non-empty string")

        try:
            search = arxiv.Search(
                query=query,
                max_results=10,
                sort_by=arxiv.SortCriterion.Relevance
            )
            results = await self.client.results(search)
            
            papers = []
            for result in results:
                papers.append({
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "abstract": result.summary,
                    "paper_id": result.entry_id.split('/')[-1]
                })
            
            return json.dumps(papers, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"An error occurred while searching for papers: {str(e)}")

    async def download_paper_async(self, paper_id: str) -> str:
        """Downloads the PDF of a specified arXiv paper using its arXiv ID and saves it locally.

        Args:
            paper_id: The unique arXiv identifier for the paper (e.g., '2107.12345v1').

        Returns:
            A JSON-formatted string indicating the success or failure of the download operation and
            the local file path where the paper is stored.

        Raises:
            ValueError: If the paper ID is invalid or missing.
            Exception: If an error occurs during the download process.
        """
        if not paper_id or not isinstance(paper_id, str):
            raise ValueError("paper_id must be a non-empty string")
            
        # Basic validation of paper ID format
        paper_id_pattern = r'^\d{4}\.\d{4,5}(v\d+)?$'
        if not re.match(paper_id_pattern, paper_id):
            raise ValueError(f"Invalid paper ID format: '{paper_id}'. Expected format: 'YYMM.NNNNN' or 'YYMM.NNNNNv#'")

        try:
            search = arxiv.Search(id_list=[paper_id])
            loop = asyncio.get_event_loop()
            # Run the synchronous search in a thread pool
            results = await loop.run_in_executor(None, next, self.client.client.results(search))
            
            file_path = os.path.join(self.local_papers_dir, f"{paper_id}.pdf")
            results.download_pdf(filename=file_path)
            
            return json.dumps({
                "status": "success",
                "message": "Paper downloaded successfully.",
                "file_path": file_path
            }, ensure_ascii=False)
        except StopIteration:
            raise ValueError(f"No paper found with ID '{paper_id}'.")
        except Exception as e:
            raise Exception(f"An error occurred while downloading the paper: {str(e)}")

    async def list_papers_async(self, filter_query: str = None) -> str:
        """Lists all papers that have been downloaded and stored locally, with optional filtering capabilities.

        Args:
            filter_query: An optional keyword to filter the list of papers by title or author.

        Returns:
            A JSON-formatted string representing a list of dictionaries, where each dictionary contains information
            about a locally stored paper, including its title, authors, and file path.

        Raises:
            Exception: If an error occurs while listing the papers.
        """
        try:
            papers = []
            for file_name in os.listdir(self.local_papers_dir):
                match = re.match(r"(\d{4}\.\d{4,5}(v\d+)?)\.pdf$", file_name)
                if match:
                    paper_id = match.group(1)
                    
                    # Try to get paper metadata from arXiv
                    search = arxiv.Search(id_list=[paper_id])
                    try:
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, next, self.client.client.results(search))
                    except StopIteration:
                        continue

                    # Apply filtering if filter_query exists
                    if filter_query:
                        filter_text = filter_query.lower()
                        if (filter_text not in result.title.lower() and 
                            not any(filter_text in author.name.lower() for author in result.authors)):
                            continue

                    papers.append({
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "file_path": os.path.join(self.local_papers_dir, file_name)
                    })
            return json.dumps(papers, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"An error occurred while listing papers: {str(e)}")

    async def read_paper_async(self, paper_id: str) -> str:
        """Reads the content of a specified paper from the local storage and provides access to its text.

        Args:
            paper_id: The unique arXiv identifier for the paper (e.g., '2107.12345v1').

        Returns:
            A JSON-formatted string containing the text content of the paper, if available.

        Raises:
            ValueError: If the paper ID is invalid or missing.
            Exception: If an error occurs while reading the paper content.
        """
        if not paper_id or not isinstance(paper_id, str):
            raise ValueError("paper_id must be a non-empty string")

        try:
            file_path = os.path.join(self.local_papers_dir, f"{paper_id}.pdf")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Paper with ID '{paper_id}' not found in local storage.")

            reader = PdfReader(file_path)
            text_content = "\n".join(page.extract_text() or "" for page in reader.pages)
            return json.dumps({
                "status": "success",
                "message": "Paper content retrieved successfully.",
                "content": text_content
            }, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"An error occurred while reading the paper content: {str(e)}")

# Initialize FastMCP server
mcp = FastMCP("mcp_arxiv_paper_manager")
paper_manager = ArxivPaperManager()

@mcp.tool()
async def search_papers(query: str) -> str:
    """Searches arXiv for papers based on a user-provided query and returns a list of matching papers.

    Args:
        query: A string containing the search query (e.g., 'quantum computing').

    Returns:
        A JSON-formatted string representing a list of dictionaries, where each dictionary contains details 
        about a paper such as its title, authors, abstract, and arXiv ID.

    Example:
        search_papers(query="quantum computing")
    """
    return await paper_manager.search_papers_async(query)

@mcp.tool()
async def download_paper(paper_id: str) -> str:
    """Downloads the PDF of a specified arXiv paper using its arXiv ID and saves it locally.

    Args:
        paper_id: The unique arXiv identifier for the paper (e.g., '2107.12345v1').

    Returns:
        A JSON-formatted string indicating the success or failure of the download operation and
        the local file path where the paper is stored.

    Example:
        download_paper(paper_id="2107.12345v1")
    """
    return await paper_manager.download_paper_async(paper_id)

@mcp.tool()
async def list_papers(filter_query: str = None) -> str:
    """Lists all papers that have been downloaded and stored locally, with optional filtering capabilities.

    Args:
        filter_query: An optional keyword to filter the list of papers by title or author.

    Returns:
        A JSON-formatted string representing a list of dictionaries, where each dictionary contains information
        about a locally stored paper, including its title, authors, and file path.

    Example:
        list_papers(filter_query="quantum")
    """
    return await paper_manager.list_papers_async(filter_query)

@mcp.tool()
async def read_paper(paper_id: str) -> str:
    """Reads the content of a specified paper from the local storage and provides access to its text.

    Args:
        paper_id: The unique arXiv identifier for the paper (e.g., '2107.12345v1').

    Returns:
        A JSON-formatted string containing the text content of the paper, if available.

    Example:
        read_paper(paper_id="2107.12345v1")
    """
    return await paper_manager.read_paper_async(paper_id)

if __name__ == "__main__":
    mcp.run()