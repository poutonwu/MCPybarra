import sys
import os
import json
import arxiv
import requests
import fitz  # PyMuPDF
from mcp.server.fastmcp import FastMCP

# Create a directory to store papers if it doesn't exist
if not os.path.exists('papers'):
    os.makedirs('papers')

# Initialize FastMCP server
mcp = FastMCP("mcp_arxiv_server")

@mcp.tool()
def search_papers(query: str, max_results: int = 10) -> str:
    """
    Searches the arXiv repository for papers matching a given query.

    This function queries the arXiv API for academic papers based on a search
    term. It can search by keywords, author names, or other arXiv-supported
    syntax. The results are sorted by their submission date.

    Args:
        query (str): The search query (e.g., "quantum computing", "author:John Doe").
        max_results (int): The maximum number of results to return. Defaults to 10.

    Returns:
        str: A JSON string representing a list of papers with their metadata,
             including ID, title, authors, and summary. Returns a JSON object
             with an "error" key if the search fails.
    """
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        client = arxiv.Client()
        results = client.results(search)
        papers = []
        for r in results:
            papers.append({
                "id": r.get_short_id(),
                "title": r.title,
                "authors": [str(author) for author in r.authors],
                "summary": r.summary
            })
        return json.dumps(papers)
    except Exception as e:
        return json.dumps({"error": f"An error occurred during search: {str(e)}"})

@mcp.tool()
def download_paper(paper_id: str) -> str:
    """
    Downloads the PDF of a specific paper using its arXiv ID.

    This function fetches a paper's metadata from arXiv using its unique ID,
    retrieves the PDF URL, and downloads the file into a local 'papers'
    directory. The downloaded file is named using its arXiv ID (e.g., '2301.12345.pdf').

    Args:
        paper_id (str): The unique arXiv ID of the paper to download (e.g., '2301.12345').

    Returns:
        str: A JSON string indicating the result of the download operation.
             On success, it returns a message confirming the download. On failure,
             it returns a JSON object with an "error" key.
    """
    try:
        search = arxiv.Search(id_list=[paper_id])
        client = arxiv.Client()
        paper = next(client.results(search))
        
        # The 'paper' object will exist if the StopIteration is not raised.
        # The 'if paper:' check is redundant here and has been removed.
        pdf_url = paper.pdf_url
        file_path = os.path.join('papers', f"{paper_id}.pdf")
        
        response = requests.get(pdf_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        return json.dumps({"message": f"Successfully downloaded '{paper_id}.pdf'"})
    except StopIteration:
        return json.dumps({"error": f"Paper '{paper_id}' not found."})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Failed to download paper '{paper_id}': {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})

@mcp.tool()
def list_papers() -> str:
    """
    Lists all the academic papers that have been downloaded locally.

    This function scans the 'papers' directory and returns a list of all
    files that end with the '.pdf' extension. This provides a quick way to see
    which papers are available for local reading.

    Returns:
        str: A JSON string representing a list of filenames of downloaded papers.
             If the directory doesn't exist or is empty, it returns an empty list.
             Returns a JSON object with an "error" key if an unexpected error occurs.
    """
    try:
        papers_dir = 'papers'
        if not os.path.exists(papers_dir):
            return json.dumps([])
        
        papers = [f for f in os.listdir(papers_dir) if f.endswith('.pdf')]
        return json.dumps(papers)
    except Exception as e:
        return json.dumps({"error": f"An error occurred while listing papers: {str(e)}"})

@mcp.tool()
def read_paper(filename: str) -> str:
    """
    Reads the text content from a specified, locally stored PDF file.

    This function opens a PDF from the local 'papers' directory and uses the
    PyMuPDF library (fitz) to extract all text content from its pages.
    The extracted text is returned as a single string.

    Args:
        filename (str): The filename of the paper to read from the 'papers'
                        directory (e.g., '2301.12345.pdf').

    Returns:
        str: A JSON string containing the filename and the full extracted text
             of the paper. If the file is not found or an error occurs during
             reading, it returns a JSON object with an "error" key.
    """
    try:
        file_path = os.path.join('papers', filename)
        
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File '{filename}' not found."})
        
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        return json.dumps({"filename": filename, "content": text})
    except Exception as e:
        return json.dumps({"error": f"An error occurred while reading the paper: {str(e)}"})

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout on Windows to prevent UnicodeEncodeError
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()