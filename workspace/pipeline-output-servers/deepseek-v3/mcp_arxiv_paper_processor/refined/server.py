import sys
import httpx
import os
import json
from mcp.server.fastmcp import FastMCP
import arxiv
import requests
from PyPDF2 import PdfReader

# Initialize FastMCP server
mcp = FastMCP("mcp_arxiv_paper_processor")

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# Constants
ARXIV_API_BASE = "http://export.arxiv.org/api/"
PDF_SAVE_DIR = "./papers"

# Ensure the papers directory exists
os.makedirs(PDF_SAVE_DIR, exist_ok=True)

@mcp.tool()
def search_papers(query: str, max_results: int = 5) -> str:
    """
    Searches arXiv for academic papers based on the provided query.

    Args:
        query: The search query string (e.g., "machine learning").
        max_results: Maximum number of results to return (default: 5).

    Returns:
        A JSON string containing a list of dictionaries with paper metadata (title, authors, arXiv ID, abstract).

    Raises:
        ValueError: If the query is empty or max_results is not a positive integer.
        httpx.HTTPStatusError: If the arXiv API request fails.
    """
    if not query:
        raise ValueError("Query cannot be empty.")
    if max_results <= 0:
        raise ValueError("max_results must be a positive integer.")

    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        results = []
        for result in client.results(search):
            results.append({
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "arxiv_id": result.entry_id.split('/')[-1],
                "abstract": result.summary
            })
        return json.dumps(results)
    except Exception as e:
        raise httpx.HTTPStatusError(f"Failed to search arXiv: {str(e)}")

@mcp.tool()
def download_paper(paper_id: str, save_path: str = PDF_SAVE_DIR) -> str:
    """
    Downloads the PDF of a specified arXiv paper and stores it locally.

    Args:
        paper_id: The arXiv ID of the paper (e.g., "2307.12345").
        save_path: Local directory path to save the PDF (default: "./papers").

    Returns:
        A JSON string with a success/failure message and the local file path.

    Raises:
        ValueError: If the paper_id is empty or invalid.
        httpx.HTTPStatusError: If the PDF download fails.
    """
    if not paper_id:
        raise ValueError("Paper ID cannot be empty.")

    try:
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        response = requests.get(pdf_url)
        response.raise_for_status()

        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"{paper_id}.pdf")
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return json.dumps({"status": "success", "file_path": file_path})
    except Exception as e:
        raise httpx.HTTPStatusError(f"Failed to download paper: {str(e)}")

@mcp.tool()
def list_papers(query: str = None) -> str:
    """
    Lists all papers stored locally, optionally filtered by a query.

    Args:
        query: Optional filter string to match against paper titles or authors.

    Returns:
        A JSON string containing a list of dictionaries with local paper details.

    Raises:
        OSError: If the papers directory cannot be accessed.
    """
    try:
        papers = []
        for filename in os.listdir(PDF_SAVE_DIR):
            if filename.endswith('.pdf'):
                paper_id = filename[:-4]
                file_path = os.path.join(PDF_SAVE_DIR, filename)
                papers.append({
                    "arxiv_id": paper_id,
                    "file_path": file_path,
                    "download_time": os.path.getmtime(file_path)
                })

        if query:
            papers = [p for p in papers if query.lower() in p["arxiv_id"].lower()]

        return json.dumps(papers)
    except Exception as e:
        raise OSError(f"Failed to list papers: {str(e)}")

@mcp.tool()
def read_paper(paper_id: str, mode: str = "text") -> str:
    """
    Reads the content of a specified locally stored paper.

    Args:
        paper_id: The arXiv ID or local filename of the paper.
        mode: "text" for raw text or "metadata" for structured data (default: "text").

    Returns:
        A JSON string with the paper content or metadata.

    Raises:
        ValueError: If the paper_id is empty or mode is invalid.
        FileNotFoundError: If the paper file does not exist.
    """
    if not paper_id:
        raise ValueError("Paper ID cannot be empty.")
    if mode not in ["text", "metadata"]:
        raise ValueError("Mode must be either 'text' or 'metadata'.")

    try:
        file_path = os.path.join(PDF_SAVE_DIR, f"{paper_id}.pdf")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Paper with ID {paper_id} not found.")

        if mode == "text":
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return json.dumps({"content": text})
        else:
            return json.dumps({
                "arxiv_id": paper_id,
                "file_path": file_path,
                "download_time": os.path.getmtime(file_path)
            })
    except Exception as e:
        raise FileNotFoundError(f"Failed to read paper: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()