import os
import sys
import httpx
import json
import re
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from arxiv import Search, Client as ArxivClient
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

# Initialize FastMCP server
mcp = FastMCP("arxiv_paper_manager")

# Configure proxy if necessary (uncomment and set your proxy settings)
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Shared HTTP client for API requests
client = httpx.AsyncClient()

# Directory to store downloaded papers
PAPERS_DIR = "workspace/papers/"

if not os.path.exists(PAPERS_DIR):
    os.makedirs(PAPERS_DIR)

@mcp.tool()
async def search_papers(query: str) -> str:
    """
    Searches for academic papers on arXiv based on user-provided query conditions and returns a list of matching papers.

    Args:
        query: A string containing the search query (e.g., keywords, author names, or other criteria).

    Returns:
        A JSON-formatted string containing a list of paper metadata (titles, authors, abstracts, and arXiv IDs).

    Example:
        search_papers(query="quantum computing")
    """
    try:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty or contain only whitespace.")

        search = Search(query=query, max_results=10)
        arxiv_client = ArxivClient()
        results = arxiv_client.results(search)

        papers = []
        for result in results:
            papers.append({
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "arxiv_id": result.entry_id.split('/')[-1]
            })

        return json.dumps(papers, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"An error occurred while searching for papers: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
async def download_paper(paper_id: str) -> str:
    """
    Downloads the PDF file of a specified arXiv paper using its arXiv ID and stores it locally.

    Args:
        paper_id: A string representing the unique identifier of the arXiv paper (e.g., '1706.03762').

    Returns:
        A JSON-formatted string message indicating success or failure of the download operation.

    Example:
        download_paper(paper_id="1706.03762")
    """
    try:
        if not re.match(r"^\\d{4}\\.\\d{4,5}$", paper_id):
            raise ValueError(f"Invalid arXiv ID format: '{paper_id}'. Expected format is 'YYYY.XXXXX'.")

        search = Search(id_list=[paper_id])
        arxiv_client = ArxivClient()
        paper = next(arxiv_client.results(search))

        # Download the PDF
        pdf_path = os.path.join(PAPERS_DIR, f"{paper_id}.pdf")
        paper.download_pdf(filename=pdf_path)

        return json.dumps({"message": f"Paper successfully downloaded and saved at {pdf_path}"}, ensure_ascii=False)

    except StopIteration:
        return json.dumps({"error": f"No paper found with ID: {paper_id}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"An error occurred while downloading the paper: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
async def list_papers() -> str:
    """
    Lists all papers that have been downloaded and stored locally, providing an interface for querying and managing these papers.

    Returns:
        A JSON-formatted string containing a list of locally stored papers' metadata (titles, authors, and local file paths).

    Example:
        list_papers()
    """
    try:
        papers = []
        for filename in os.listdir(PAPERS_DIR):
            if filename.endswith(".pdf"):
                paper_id = filename[:-4]  # Remove '.pdf' extension
                pdf_path = os.path.join(PAPERS_DIR, filename)

                try:
                    reader = PdfReader(pdf_path)

                    # Extract basic metadata from the PDF
                    title = "Unknown Title"
                    authors = ["Unknown Author"]
                    if reader.metadata:
                        title = reader.metadata.get('/Title', title)
                        authors = [reader.metadata.get('/Author', authors[0])] if reader.metadata.get('/Author') else authors

                    papers.append({
                        "title": title,
                        "authors": authors,
                        "file_path": pdf_path
                    })
                except PdfReadError as pre:
                    papers.append({
                        "title": "Corrupted File",
                        "authors": ["N/A"],
                        "file_path": pdf_path,
                        "error": f"Failed to read PDF: {str(pre)}"
                    })

        return json.dumps(papers, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"An error occurred while listing papers: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
async def read_paper(paper_id: str) -> str:
    """
    Reads and provides access to the textual content of a specified academic paper by parsing its locally stored PDF file.

    Args:
        paper_id: A string representing the unique identifier of the arXiv paper whose content needs to be accessed.

    Returns:
        A JSON-formatted string containing the parsed text content of the specified paper.

    Example:
        read_paper(paper_id="1706.03762")
    """
    try:
        pdf_path = os.path.join(PAPERS_DIR, f"{paper_id}.pdf")

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"No downloaded paper found with ID: {paper_id}")

        reader = PdfReader(pdf_path)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"

        return json.dumps({"text_content": text_content}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"An error occurred while reading the paper: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()