# mcp_duckduckgo_search_and_fetch

## Overview

This MCP server provides DuckDuckGo search and web content fetching capabilities. It allows LLMs to perform web searches and extract meaningful content from web pages, making it easier to retrieve and process real-time or external information.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following:

```
mcp[cli]
httpx
beautifulsoup4
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_duckduckgo_search_and_fetch.py
```

This will launch the MCP server using the default `stdio` transport protocol.

## Available Tools

### `duckduckgo_search`

Performs a search on DuckDuckGo and returns structured results.

**Arguments:**
- `query`: The search term or phrase (required).
- `max_results`: Maximum number of results to return (default: 5, max: 10).

**Returns:**
A dictionary containing search results with:
- `title`: Title of the result.
- `url`: Link to the result.
- `snippet`: Short description or text snippet from the result.

**Raises:**
- `ValueError` for invalid input.
- `httpx.HTTPStatusError` for failed API requests.

---

### `fetch_content`

Fetches and extracts the main textual content from a given URL.

**Argument:**
- `url`: The URL of the webpage to scrape (required).

**Returns:**
A string containing the cleaned, readable text content from the page.

**Raises:**
- `ValueError` for invalid or empty URL.
- `httpx.HTTPStatusError` for failed HTTP requests.

---