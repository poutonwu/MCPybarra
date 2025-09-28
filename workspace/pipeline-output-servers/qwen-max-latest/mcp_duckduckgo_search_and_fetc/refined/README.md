# mcp_duckduckgo_search_and_fetc

## Overview

The `mcp_duckduckgo_search_and_fetc` is an MCP (Model Context Protocol) server that enables large language models to perform DuckDuckGo searches and fetch content from the top results. It provides a tool for searching the web and retrieving cleaned, structured content from relevant URLs.

This server is useful for augmenting LLM capabilities with up-to-date information from the web, while also including robust error handling, rate-limiting protection, and text cleaning functionality.

## Installation

Before running the server, ensure you have Python 3.10 or higher installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file does not exist, create one with the following minimum dependencies:

```txt
fastmcp
beautifulsoup4
duckduckgo-search
requests
urllib3
```

## Running the Server

To start the MCP server, run the Python script from the command line:

```bash
python mcp_duckduckgo_search_and_fetc.py
```

Ensure the script file is named appropriately (e.g., `mcp_duckduckgo_search_and_fetc.py`) based on your project structure.

## Available Tools

### `search_and_fetch`

**Description:**  
Performs a DuckDuckGo search for the given query and fetches the content of the top results. Returns cleaned text extracted from each page.

**Arguments:**
- `query` (str): The search query string.
- `num_results` (int): Number of top results to fetch (default: 5).

**Returns:**  
A list of dictionaries containing:
- `title`: The title of the result.
- `url`: The URL of the result.
- `content`: Cleaned and normalized text content from the page.

**Raises:**
- `ValueError`: If inputs are invalid.
- `RuntimeError`: If the search fails due to rate limiting or other errors.

**Example Use Case:**
```python
results = search_and_fetch("latest developments in AI", num_results=3)
for result in results:
    print(f"{result['title']}: {result['content'][:200]}...")
```