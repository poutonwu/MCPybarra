# mcp_duckduckgo_search_fetcher

## Overview
The `mcp_duckduckgo_search_fetcher` is an MCP (Model Context Protocol) server that provides two tools for interacting with web content:

- **DuckDuckGo Search**: Perform a search using DuckDuckGo and return structured results.
- **Fetch Content**: Retrieve and extract the main textual content from a given URL.

This server enables LLMs to perform web searches and fetch webpage content programmatically, enhancing their ability to access real-time or external information.

## Installation
Before running the server, ensure you have Python 3.10+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:
```
mcp[cli]
httpx
beautifulsoup4
```

## Running the Server
To start the MCP server, run the Python script from the command line:

```bash
python mcp_duckduckgo_search_fetcher.py
```

By default, the server uses the `stdio` transport protocol.

## Available Tools

### 1. `DuckDuckGo_search`
**Description:**  
Performs a search on DuckDuckGo using the provided query and returns results in JSON format containing titles, links, and snippets.

**Arguments:**
- `query` (str): The search term or phrase (required).

**Returns:**  
A JSON string representing a list of search results, each with:
- `title`: Title of the result
- `link`: URL to the result
- `snippet`: Short description of the result

**Example Output:**
```json
[
  {
    "title": "Official Python Website",
    "link": "https://www.python.org",
    "snippet": "The official home of the Python Programming Language..."
  }
]
```

**Raises:**
- `ValueError`: If the query is empty or whitespace-only.
- `httpx.HTTPStatusError`: If the API request fails.

---

### 2. `fetch_content`
**Description:**  
Fetches and extracts the main text content from a specified URL, removing boilerplate elements like ads or navigation bars.

**Arguments:**
- `url` (str): A valid HTTP/HTTPS URL (required).

**Returns:**  
A single string containing the cleaned text content, with paragraphs separated by newlines.

**Raises:**
- `ValueError`: If the URL is invalid or not properly formatted.
- `httpx.RequestError`: If there's a network issue fetching the page.
- `RuntimeError`: For parsing or unexpected errors during processing.