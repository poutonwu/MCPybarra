# mcp_zotero_library_manager

A Model Context Protocol (MCP) server that provides access to Zotero library items, metadata, and full-text content.

## Overview

This MCP server integrates with a Zotero library to allow language models to:

- Retrieve item metadata (title, authors, year, DOI)
- Extract full text from PDF attachments
- Search for items by title, author, year, or full text

The server uses environment variables for secure configuration and validates inputs to ensure robust usage.

## Installation

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Ensure your `requirements.txt` includes:
```
pyzotero
PyPDF2
mcp[cli]
```

## Running the Server

```bash
python mcp_zotero_library_manager.py
```

Make sure to set the required environment variables before running:
- `ZOTERO_LIBRARY_ID`
- `ZOTERO_LIBRARY_TYPE` (`user` or `group`)
- `ZOTERO_API_KEY`

Optional: Set `ZOTERO_LOCAL="true"` if using a local Zotero client.

## Available Tools

### `get_item_metadata(item_key: str)`
Fetches detailed bibliographic metadata for a Zotero item using its unique 8-character key.

Returns:
- Title
- Creators/authors
- Publication year
- Publisher
- DOI

### `get_item_fulltext(item_key: str)`
Extracts and returns the full text content from a Zotero item's PDF attachment.

Useful for accessing the complete content of research papers and documents stored in your Zotero library.

### `search_items(title: str = None, creators: str = None, year: int = None, fulltext: str = None)`
Searches your Zotero library based on one or more criteria and returns matching items.

Supports searching by:
- Title
- Creator/author name
- Publication year
- Full-text content