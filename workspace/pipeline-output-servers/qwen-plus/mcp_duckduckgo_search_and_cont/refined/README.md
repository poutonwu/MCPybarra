# mcp_duckduckgo_search_and_cont

## Overview

This MCP server provides tools for performing DuckDuckGo searches and fetching webpage content. It allows large language models to interact with external data sources by retrieving search results or scraping and cleaning web content.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt** should include:

```
mcp[cli]
httpx
beautifulsoup4
duckduckgo-search
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_duckduckgo_search_and_cont.py
```

By default, the server uses `stdio` transport. You can change this by modifying the `mcp.run()` call in the script if needed.

---

## Available Tools

### 1. `duck_duck_go_search`

Performs a text search on DuckDuckGo and returns structured results.

**Args:**
- `query`: Search keywords or phrases (required).
- `max_results`: Maximum number of results to return (default: 5, range: 1–10).

**Returns:**
A list of dictionaries containing:
- `title`: Result title.
- `link`: Full URL of the result.
- `snippet`: Summary text of the result.
- `source`: Domain name of the source.

**Raises:**
- `ValueError` for invalid input.
- `RuntimeError` if the search fails.

---

### 2. `fetch_content`

Fetches and extracts the main textual content from a given URL, optionally removing ads and other non-content elements.

**Args:**
- `url`: Webpage URL to fetch (required).
- `remove_ads`: Whether to attempt ad removal (default: True).
- `timeout`: Request timeout in seconds (default: 10).

**Returns:**
A dictionary containing:
- `title`: Page title.
- `content`: Cleaned text content.
- `domain`: Website domain.
- `status_code`: HTTP response code.
- `word_count`: Number of words in the content.

**Raises:**
- `ValueError` for invalid URLs.
- `httpx.HTTPStatusError` for failed HTTP requests.