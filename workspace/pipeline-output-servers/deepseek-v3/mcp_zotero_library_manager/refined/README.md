# mcp_zotero_library_manager

A Model Context Protocol (MCP) server that provides programmatic access to a Zotero library, allowing retrieval of item metadata, full-text content, and flexible searching across the library.

## Overview

This MCP server integrates with the Zotero API to provide tools for interacting with a Zotero library. It enables external applications or language models to search for items, retrieve metadata, and extract full-text content from supported entries such as PDFs.

The server is configured with a predefined Zotero user library and API key, but these can be modified in the source code for customization.

## Installation

Ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
httpx
pyzotero
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_zotero_library_manager.py
```

By default, the server uses standard input/output (`stdio`) transport.

## Available Tools

### `get_item_metadata`

**Description:** Retrieves detailed metadata for a specified Zotero entry using its unique item key.

**Arguments:**
- `item_key`: The unique identifier (string) for the Zotero entry.

**Returns:** A dictionary containing metadata like title, authors, publication year, DOI, etc.

---

### `get_item_fulltext`

**Description:** Extracts the full-text content of a Zotero attachment item (e.g., PDF, HTML, or plain text).

**Arguments:**
- `item_key`: The unique identifier (string) for the Zotero entry.

**Returns:** A string or binary data representing the full-text content (if available). Only works for attachment-type items.

---

### `search_items`

**Description:** Performs a flexible search in the Zotero library by title, creator, year, or full-text content.

**Arguments:**
- `query`: The search term (string).
- `search_type`: Specifies the search scope (`title`, `creator`, `year`, or `fulltext`). Default is `title`.

**Returns:** A list of dictionaries containing metadata for matching entries.

---