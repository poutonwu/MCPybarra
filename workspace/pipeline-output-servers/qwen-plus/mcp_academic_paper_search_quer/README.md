# mcp_academic_paper_search_quer

## Overview
The `mcp_academic_paper_search_quer` is an MCP (Model Context Protocol) server that enables Large Language Models (LLMs) to search for and retrieve academic papers from multiple sources, including **Semantic Scholar** and **Crossref**. It provides tools to perform keyword-based searches, topic-based searches with optional year filtering, and detailed paper information lookup.

This server is ideal for research assistance, literature review, and academic exploration tasks where access to scholarly articles and metadata is required.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` file includes the following:

```
mcp[cli]
httpx
```

---

## Running the Server

To start the server, run the following command in your terminal:

```bash
python mcp_academic_paper_search_query.py
```

By default, the server will run using the `stdio` transport protocol. If you want to use a different transport method (e.g., `sse` or `http`), modify the `mcp.run()` call in the script accordingly.

---

## Available Tools

Below are the available tools exposed by this MCP server:

### 1. `search_papers`
**Description:**  
Searches for academic papers based on provided keywords from Semantic Scholar and Crossref APIs.

**Parameters:**
- `keywords` (str): Keywords used for searching papers (required).
- `limit` (int): Maximum number of results to return (default: 5).

**Returns:**  
A JSON array containing paper information such as title, authors, year, and DOI.

---

### 2. `fetch_paper_details`
**Description:**  
Fetches detailed information about a specific paper using its ID (DOI or Semantic Scholar ID) and source.

**Parameters:**
- `paper_id` (str): Unique identifier of the paper (DOI or Semantic Scholar ID) (required).
- `source` (str): Data source ("Semantic Scholar" or "Crossref") (required).

**Returns:**  
A JSON object containing detailed paper information such as title, authors, abstract, and publication venue.

---

### 3. `search_by_topic`
**Description:**  
Searches for papers related to a specific topic, with optional filtering by year range.

**Parameters:**
- `topic` (str): Topic keywords for paper search (required).
- `year_range` (str): Year range in format "YYYY-YYYY" (optional).
- `limit` (int): Maximum number of results to return (default: 5).

**Returns:**  
A JSON array containing paper information including title, authors, year, and DOI.

--- 

For more details on how these tools work internally, refer to the server code documentation and function docstrings.