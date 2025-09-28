# mcp_zotero_manager

A Model Context Protocol (MCP) server that provides an interface to interact with the Zotero API, allowing retrieval of item metadata, full text content, and flexible searching across the Zotero library.

## Installation

Ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

If a `requirements.txt` file does not exist, create one with the following minimum dependencies:

```txt
mcp[cli]
requests
```

Then install using the command above.

## Running the Server

To start the MCP server, run the Python script from the command line:

```bash
python mcp_zotero_manager.py
```

Make sure the script file is properly configured with the correct Zotero API credentials and proxy settings if needed.

## Available Tools

### `get_item_metadata`

Fetches detailed metadata for a specific Zotero item using its unique item key.

**Args:**
- `item_key`: The unique identifier for the Zotero item.

**Returns:** JSON string containing the item's metadata.

---

### `get_item_fulltext`

Extracts and returns the full text content of a specific Zotero item using its unique item key.

**Args:**
- `item_key`: The unique identifier for the Zotero item.

**Returns:** JSON string containing the item's full text content.

---

### `search_items`

Searches the Zotero library based on title, creator, year, or full text and returns matching items.

**Args:**
- `query`: The search query text.
- `search_by_title`: Whether to include titles in the search (default: `True`).
- `search_by_creator`: Whether to include creators in the search (default: `True`).
- `search_by_year`: Whether to include publication years in the search (default: `False`).
- `search_by_fulltext`: Whether to include full text in the search (default: `False`).

**Returns:** JSON string containing a list of matching item metadata objects.