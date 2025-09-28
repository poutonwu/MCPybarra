# mcp_zotero_library_manager

A Model Context Protocol (MCP) server that provides access to a Zotero library, enabling tools for retrieving item metadata, extracting full-text content from PDFs, and performing flexible searches.

## Overview

The `mcp_zotero_library_manager` server connects to a Zotero library via the Zotero API and exposes three primary functions:

- Retrieve detailed metadata of a Zotero item by its key.
- Extract full-text content from the primary PDF attachment of an item.
- Perform flexible searches across the Zotero library using keywords and optional filters.

This server enables integration with large language models (LLMs) through the MCP protocol, allowing intelligent querying and processing of bibliographic data and document content.

## Installation

Ensure you have Python 3.10 or later installed. Then install dependencies using pip:

```bash
pip install -r requirements.txt
```

Make sure your environment includes:

- `mcp[cli]`
- `pyzotero`
- `PyPDF2`
- `python-dotenv`

## Running the Server

Before running, set up your Zotero credentials in a `.env` file:

```env
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_API_KEY=your_api_key
ZOTERO_LIBRARY_TYPE=user  # or 'group'
HTTP_PROXY=http://your.proxy.server:port  # if needed
HTTPS_PROXY=https://your.proxy.server:port  # if needed
```

Then run the server:

```bash
python mcp_zotero_library_manager.py
```

## Available Tools

### `get_item_metadata(item_key: str) -> str`

Retrieves complete metadata for a Zotero item by its unique key. Returns the result as a formatted JSON string.

**Example usage:**
```python
get_item_metadata("ABCDE123")
```

### `get_item_fulltext(item_key: str) -> str`

Extracts and returns the full text from the first PDF attachment of the specified Zotero item.

**Example usage:**
```python
get_item_fulltext("ABCDE123")
```

### `search_items(query: str, search_field: str = 'everything', limit: int = 25) -> str`

Performs a flexible search across the Zotero library based on a query string, optionally restricted to specific fields like title, author, or year. Returns a list of matching items with key metadata.

**Example usage:**
```python
search_items("machine learning", search_field="title", limit=10)
```