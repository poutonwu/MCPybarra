### MCP Tools Plan

#### Tool 1: `get_item_metadata`
- **Function Name**: `get_item_metadata`
- **Description**: Fetches the detailed metadata of a specified Zotero item using its unique item key.
- **Parameters**:
  - `item_key` (str): The unique identifier for the Zotero item whose metadata is to be fetched.
- **Return Value**: A dictionary containing the detailed metadata of the specified Zotero item.

#### Tool 2: `get_item_fulltext`
- **Function Name**: `get_item_fulltext`
- **Description**: Extracts the full text content of a specified Zotero item using its unique item key.
- **Parameters**:
  - `item_key` (str): The unique identifier for the Zotero item whose full text content is to be extracted.
- **Return Value**: A string containing the full text content of the specified Zotero item.

#### Tool 3: `search_items`
- **Function Name**: `search_items`
- **Description**: Searches the Zotero library flexibly based on title, creator, year, or full text and returns a formatted list of search results.
- **Parameters**:
  - `query` (str): The search query text.
  - `search_by_title` (bool, optional): Whether to include titles in the search. Defaults to True.
  - `search_by_creator` (bool, optional): Whether to include creators in the search. Defaults to True.
  - `search_by_year` (bool, optional): Whether to include publication years in the search. Defaults to False.
  - `search_by_fulltext` (bool, optional): Whether to include full text in the search. Defaults to False.
- **Return Value**: A list of dictionaries where each dictionary contains the metadata of an item that matches the search criteria.

### Server Overview
The server's purpose is to provide an interface for automatic academic literature management through a Model Context Protocol (MCP) server. It will enable users to access and manipulate a Zotero literature database by providing functionalities to retrieve item metadata, extract full text from items, and perform flexible searches within the Zotero library.

### File to be Generated
All logic will be self-contained in a single Python file named `mcp_zotero_server.py`.

### Dependencies
- `requests`: To make HTTP requests to the Zotero API.
- `mcp[cli]`: To use the MCP SDK for creating the server.
- `httpx`: For asynchronous HTTP requests if needed.