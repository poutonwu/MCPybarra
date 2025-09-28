# mcp_arxiv_paper_manager

## Overview

`mcp_arxiv_paper_manager` is an MCP (Model Context Protocol) server that provides a set of tools for interacting with academic papers on arXiv. It enables large language models (LLMs) to search, download, list, and read research papers directly from the arXiv database.

Key capabilities include:
- Searching for papers by keyword
- Downloading papers by ID
- Listing locally stored papers
- Reading the content of downloaded papers

This server is ideal for use cases involving research assistance, literature review, and knowledge extraction from academic publications.

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes the following packages:

```
mcp[cli]
arxiv
PyPDF2
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_arxiv_paper_manager.py
```

The server will initialize and begin listening for MCP client connections via standard input/output.

## Available Tools

Below is a list of available MCP tools and their functionality:

### `search_papers(query: str)`

Searches arXiv for papers based on a user-provided query.

**Example:**
```python
search_papers(query="quantum computing")
```

**Returns:**  
A JSON-formatted list of matching papers, including title, authors, abstract, and paper ID.

---

### `download_paper(paper_id: str)`

Downloads a paper from arXiv using its unique ID and saves it locally.

**Example:**
```python
download_paper(paper_id="2107.12345v1")
```

**Returns:**  
A JSON response indicating success or failure, along with the local file path where the PDF was saved.

---

### `list_papers(filter_query: str = None)`

Lists all downloaded papers in local storage, optionally filtered by a keyword.

**Example:**
```python
list_papers(filter_query="quantum")
```

**Returns:**  
A JSON-formatted list of locally stored papers, including titles, authors, and file paths.

---

### `read_paper(paper_id: str)`

Reads the full text of a locally stored paper by its arXiv ID.

**Example:**
```python
read_paper(paper_id="2107.12345v1")
```

**Returns:**  
A JSON-formatted string containing the extracted text content of the paper.