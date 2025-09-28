# MCP Server Implementation Plan: arXiv Paper Assistant

## Server Overview
This plan outlines the creation of an MCP server designed to automate the search, download, listing, and reading of academic papers from arXiv. The server will provide a suite of tools to manage a local library of papers, making academic research more efficient.

## File to be Generated
The entire server will be contained within a single Python file:
- `mcp_arxiv_server.py`

## Dependencies
The following third-party Python libraries are required for this implementation:
- `mcp`: For creating the MCP server and tools.
- `arxiv`: A Python wrapper for the arXiv API, used for searching and fetching paper metadata.
- `requests`: For downloading PDF files from their URLs.
- `PyMuPDF`: For extracting text content from downloaded PDF files.

---

## MCP Tools Plan

### 1. `search_papers`
- **Function Name**: `search_papers`
- **Description**: Searches the arXiv repository for papers matching a given query. It returns a list of papers with their essential metadata, such as title, authors, summary, and unique arXiv ID.
- **Parameters**:
    - `query` (str): The search query (e.g., "quantum computing", "author:John Doe"). This is a required parameter.
    - `max_results` (int): The maximum number of results to return. Defaults to 10. This is an optional parameter.
- **Return Value**:
    - A list of dictionaries, where each dictionary represents a paper and contains the following keys:
        - `id` (str): The unique arXiv ID (e.g., '2301.12345').
        - `title` (str): The title of the paper.
        - `authors` (list[str]): A list of the paper's authors.
        - `summary` (str): A brief summary of the paper.

### 2. `download_paper`
- **Function Name**: `download_paper`
- **Description**: Downloads the PDF of a specific paper using its arXiv ID and saves it to a local directory named `papers`. This allows for offline access and management.
- **Parameters**:
    - `paper_id` (str): The unique arXiv ID of the paper to download (e.g., '2301.12345'). This is a required parameter.
- **Return Value**:
    - A string message indicating the result of the download operation, such as "Successfully downloaded 'paper_id.pdf'" or "Error: Paper 'paper_id' not found."

### 3. `list_papers`
- **Function Name**: `list_papers`
- **Description**: Lists all the academic papers that have been downloaded and are stored locally in the `papers` directory.
- **Parameters**:
    - None.
- **Return Value**:
    - A list of strings, where each string is the filename of a downloaded paper (e.g., `['2301.12345.pdf', '2205.09876.pdf']`). Returns an empty list if no papers are found.

### 4. `read_paper`
- **Function Name**: `read_paper`
- **Description**: Reads the text content from a specified, locally stored PDF file. This tool extracts and returns the full text of the paper for analysis or review.
- **Parameters**:
    - `filename` (str): The filename of the paper to read from the local `papers` directory (e.g., '2301.12345.pdf'). This is a required parameter.
- **Return Value**:
    - A string containing the full extracted text of the paper. Returns an error message if the file cannot be found or read.