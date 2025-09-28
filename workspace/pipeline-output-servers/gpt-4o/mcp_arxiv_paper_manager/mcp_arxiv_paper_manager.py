import os
import sys
import arxiv
import json
from datetime import datetime
from PyPDF2 import PdfReader
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("mcp_arxiv_paper_manager")

# Directory to store downloaded papers
LOCAL_STORAGE_DIR = "./downloaded_papers"
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)

@mcp.tool()
def search_papers(query: str, max_results: int = 10, sort_by: str = "relevance", sort_order: str = "descending") -> str:
    """
    Searches arXiv for academic papers based on user-provided query parameters.

    Args:
        query (str): Search query string (e.g., "quantum computing").
        max_results (int): Maximum number of results to retrieve (default: 10).
        sort_by (str): Sorting criteria (e.g., "relevance", "lastUpdatedDate").
        sort_order (str): Sort order, either "ascending" or "descending" (default: "descending").

    Returns:
        str: JSON string containing a list of dictionaries, each with metadata about a paper.

    Example:
        search_papers(query="quantum computing", max_results=5, sort_by="relevance", sort_order="descending")
    """
    try:
        sort_criteria = arxiv.SortCriterion.Relevance if sort_by == "relevance" else arxiv.SortCriterion.LastUpdatedDate
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criteria,
            sort_order=arxiv.SortOrder.Descending if sort_order == "descending" else arxiv.SortOrder.Ascending
        )
        results = []
        for result in search.results():
            results.append({
                "id": result.entry_id,
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "pdf_url": result.pdf_url
            })
        return json.dumps(results)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def download_paper(paper_id: str) -> str:
    """
    Downloads the PDF of a specified arXiv paper and stores it locally.

    Args:
        paper_id (str): The unique identifier of the paper (e.g., "arXiv:1234.56789").

    Returns:
        str: JSON string containing the download status and file path.

    Example:
        download_paper(paper_id="arXiv:1234.56789")
    """
    try:
        search = arxiv.Search(id_list=[paper_id])
        paper = next(search.results())
        filename = f"{paper_id.replace(':', '_')}.pdf"
        file_path = os.path.join(LOCAL_STORAGE_DIR, filename)
        paper.download_pdf(dirpath=LOCAL_STORAGE_DIR, filename=filename)
        return json.dumps({"status": "success", "file_path": file_path})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def list_papers(filter_by: str = None, sort_by: str = None) -> str:
    """
    Lists all locally stored papers, with options to filter or sort them.

    Args:
        filter_by (str): Optional filter criteria (e.g., "author:John Doe").
        sort_by (str): Sorting criteria (e.g., "title", "download_date").

    Returns:
        str: JSON string containing a list of dictionaries describing the locally stored papers.

    Example:
        list_papers(filter_by="author:John Doe", sort_by="title")
    """
    try:
        papers = []
        for file_name in os.listdir(LOCAL_STORAGE_DIR):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(LOCAL_STORAGE_DIR, file_name)
                download_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d")
                papers.append({
                    "file_name": file_name,
                    "title": file_name.replace(".pdf", ""),
                    "download_date": download_date,
                    "file_path": file_path
                })
        if sort_by:
            papers = sorted(papers, key=lambda x: x.get(sort_by, ""))
        return json.dumps(papers)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def read_paper(file_path: str) -> str:
    """
    Extracts and returns the text content of a specified PDF file.

    Args:
        file_path (str): Path to the locally stored PDF file.

    Returns:
        str: JSON string containing the text content of the PDF.

    Example:
        read_paper(file_path="./downloaded_papers/Paper_Title.pdf")
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages])
        return json.dumps({"content": text})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()