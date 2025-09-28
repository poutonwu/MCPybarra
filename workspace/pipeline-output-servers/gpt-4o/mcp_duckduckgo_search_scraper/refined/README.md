# mcp_duckduckgo_search_scraper

## Overview

The `mcp_duckduckgo_search_scraper` is an MCP (Model Context Protocol) server that provides tools for performing DuckDuckGo searches and extracting content from webpages. It enables LLMs to perform real-time searches and scrape textual content from URLs, supporting `http://`, `https://`, and `file://` protocols.

This server includes robust error handling, rate-limiting protection with exponential backoff, and retry mechanisms for reliable operation.

## Installation

Before running the server, install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

### Requirements (`requirements.txt`)

Ensure your `requirements.txt` file includes the following packages:

```
mcp[cli]
requests
beautifulsoup4
duckduckgo-search
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_duckduckgo_search_scraper.py
```

Make sure the script file is named appropriately (e.g., `mcp_duckduckgo_search_scraper.py`) and is executable.

## Available Tools

The server exposes the following MCP tools:

### 1. `DuckDuckGo_search`

**Description:**  
Performs a text search on DuckDuckGo using the provided query string and returns structured results including title, URL, and snippet.

**Args:**
- `query` (str): The search query string (required).

**Returns:**
- A JSON list of search results, each containing:
  - `title`: Title of the result.
  - `url`: Link to the result.
  - `snippet`: Brief summary of the result.

**Raises:**
- `ValueError`: If the query is empty or invalid.
- `Exception`: If the API call fails or no results are found due to rate limiting.

**Example:**
```python
DuckDuckGo_search(query="Python web scraping tutorial")
```

---

### 2. `fetch_content`

**Description:**  
Fetches and extracts the main textual content from a given URL or local file path.

**Args:**
- `url` (str): The URL or file path (supports `http://`, `https://`, and `file://` protocols).

**Returns:**
- A JSON object containing:
  - `content`: Cleaned and extracted text from the page or file.

**Raises:**
- `ValueError`: If the URL is empty or invalid.
- `Exception`: If the request fails or the content cannot be parsed.

**Example:**
```python
fetch_content(url="https://example.com/article")
```

---

This server is designed with **robustness**, **transparency**, and **performance** in mind, ensuring reliable access to external data sources for large language models.