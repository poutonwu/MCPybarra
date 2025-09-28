# mcp_academic_paper_tool

## Overview

This server provides an MCP interface for searching and retrieving academic paper information from sources like Semantic Scholar and Crossref. It enables LLMs to search for papers by keywords or topic, optionally filter by year range, and fetch detailed paper information including titles, authors, abstracts, and DOIs.

## Installation

First, install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure you have the following packages installed:
- `mcp[cli]`
- `httpx`

## Running the Server

To start the server, run the following command:

```bash
python mcp_academic_paper_tool.py
```

Make sure your Python environment is at least version 3.10+.

## Available Tools

The server provides the following tools:

### `search_papers`

**Description:**  
Searches for academic papers based on provided keywords and limits the number of results.

**Args:**
- `keywords` (str): Search terms to query academic papers.
- `limit` (int): Maximum number of results to return.

**Returns:**  
A JSON string containing a list of dictionaries with keys:
- `title`: Title of the paper.
- `authors`: List of author names.
- `year`: Year of publication.
- `doi`: DOI of the paper.

---

### `fetch_paper_details`

**Description:**  
Fetches detailed information about a specific paper using its ID and specified source (Semantic Scholar or Crossref).

**Args:**
- `paper_id` (str): The identifier of the paper (e.g., DOI or Semantic Scholar ID).
- `source` (str): The source to fetch details from ("Semantic Scholar" or "Crossref").

**Returns:**  
A JSON string containing a dictionary with keys:
- `title`: Title of the paper.
- `authors`: List of author names.
- `abstract`: Abstract of the paper.
- `venue`: Publication venue or source.

---

### `search_by_topic`

**Description:**  
Searches for papers related to a specific topic, with optional filtering by a year range and limiting the number of results.

**Args:**
- `topic` (str): The topic keyword(s) to search for.
- `year_range` (tuple of int, optional): A tuple specifying the start and end years for filtering results.
- `limit` (int): Maximum number of results to return.

**Returns:**  
A JSON string containing a list of dictionaries with keys:
- `title`: Title of the paper.
- `authors`: List of author names.
- `year`: Year of publication.
- `doi`: DOI of the paper.