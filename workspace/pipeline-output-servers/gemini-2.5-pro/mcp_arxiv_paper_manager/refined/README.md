# mcp_arxiv_paper_manager

## Overview

The `mcp_arxiv_paper_manager` is an MCP (Model Context Protocol) server that provides tools for managing and retrieving academic papers from arXiv. It allows large language models (LLMs) to interact with external paper data sources through a standardized interface using JSON-RPC 2.0.

This server exposes functions to search, retrieve metadata, and fetch content from arXiv, making it easier for LLMs to access up-to-date scientific literature.

## Installation

Before running the server, ensure you have Python 3.10 or later installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
httpx
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_arxiv_paper_manager.py
```

By default, the server will run using the `stdio` transport protocol. You can modify the `run()` method in the code to use other transports like `sse` or `http` if needed.

## Available Tools

The server provides the following tools for interacting with arXiv data:

### `search_papers`

**Description:**  
Searches for academic papers on arXiv based on a query string.

**Parameters:**
- `query`: A string representing the search term or phrase (e.g., "machine learning", "quantum computing").

**Returns:**  
A JSON-formatted string containing a list of matching papers, including titles, authors, abstracts, and links.

**Raises:**
- `httpx.HTTPStatusError`: If the API request fails.

---

### `get_paper_metadata`

**Description:**  
Retrieves metadata for a specific paper identified by its arXiv ID.

**Parameters:**
- `paper_id`: A string representing the unique arXiv identifier (e.g., "2106.14859").

**Returns:**  
A JSON-formatted string containing detailed metadata about the paper, such as title, authors, publication date, and categories.

**Raises:**
- `httpx.HTTPStatusError`: If the API request fails.

---

### `fetch_paper_content`

**Description:**  
Fetches the full content or summary of a paper by its arXiv ID.

**Parameters:**
- `paper_id`: A string representing the unique arXiv identifier.

**Returns:**  
A JSON-formatted string containing the paper's abstract or full text, depending on availability.

**Raises:**
- `httpx.HTTPStatusError`: If the API request fails.

--- 

These tools are designed to be robust, secure, and efficient, providing LLMs with seamless access to academic knowledge via the arXiv database.