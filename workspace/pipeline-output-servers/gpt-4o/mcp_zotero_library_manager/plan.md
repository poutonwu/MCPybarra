```markdown
# MCP Server Implementation Plan for Zotero Integration

## Server Overview
This MCP server will automate academic literature management by integrating with the Zotero API. It will provide three primary tools:
1. **Get Item Metadata**: Fetch detailed metadata for a Zotero item using its item key.
2. **Get Item Full-Text**: Extract the full text content of a Zotero item.
3. **Search Items**: Perform flexible searches in the Zotero library by title, creators, year, or full text.

The server will use JSON-RPC 2.0 protocol for communication, leveraging the MCP SDK.

## File to be Generated
The server implementation will be contained in a single Python file:
- **File Name**: `zotero_mcp_server.py`

## Dependencies
The following Python libraries are required:
1. **mcp[cli]**: MCP SDK for server implementation.
2. **pyzotero**: Python client for the Zotero API.
3. **httpx**: HTTP client for making API requests.
4. **PyPDF2**: For extracting text from PDFs (used in full-text extraction).

Ensure these dependencies are installed via pip:
```bash
pip install mcp[cli] pyzotero httpx PyPDF2
```

## MCP Tools Plan

### 1. Tool: `get_item_metadata`
- **Function Name**: `get_item_metadata`
- **Description**: Fetch detailed metadata of a Zotero item using its unique item key.
- **Parameters**:
  - `item_key` (str): The unique key identifying the Zotero item.
- **Return Value**:
  - A dictionary containing item metadata, such as title, creators, publication year, and other bibliographic details.
  - Example:
    ```json
    {
      "title": "Sample Title",
      "creators": ["John Doe", "Jane Smith"],
      "year": 2023,
      "publisher": "Sample Publisher",
      "DOI": "10.1234/sample.doi"
    }
    ```

### 2. Tool: `get_item_fulltext`
- **Function Name**: `get_item_fulltext`
- **Description**: Extract the full text content of a Zotero item. If the item contains a PDF, extract text from the PDF file.
- **Parameters**:
  - `item_key` (str): The unique key identifying the Zotero item.
- **Return Value**:
  - A string containing the extracted full text content of the item.
  - Example:
    ```json
    "This is the extracted full text content of the PDF associated with the Zotero item."
    ```

### 3. Tool: `search_items`
- **Function Name**: `search_items`
- **Description**: Search the Zotero library based on specified criteria and return a list of formatted search results.
- **Parameters**:
  - `title` (str, optional): Search by title.
  - `creators` (str, optional): Search by creators.
  - `year` (int, optional): Search by publication year.
  - `fulltext` (str, optional): Perform a full-text search.
- **Return Value**:
  - A list of dictionaries, each containing metadata for a matching item.
  - Example:
    ```json
    [
      {
        "title": "Sample Title",
        "creators": ["John Doe", "Jane Smith"],
        "year": 2023,
        "DOI": "10.1234/sample.doi"
      },
      {
        "title": "Another Title",
        "creators": ["Alice Johnson"],
        "year": 2022,
        "DOI": "10.5678/another.doi"
      }
    ]
    ```

---

This implementation plan ensures the MCP server meets the user's requirements, leveraging the Zotero API and Python tools effectively.
```