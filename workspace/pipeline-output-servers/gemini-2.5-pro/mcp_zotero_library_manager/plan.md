<thought>The user wants to create an MCP server for Zotero.
The user has provided a detailed request for the functionalities of the server.
The user also provided a detailed documentation for the MCP protocol and its Python SDK.

Based on the user's request, I need to implement the following tools:
1.  `get_item_metadata`: to get the detailed metadata of a Zotero item by its key.
2.  `get_item_fulltext`: to extract the full text content of a Zotero item.
3.  `search_items`: to perform a flexible search in the Zotero library by title, creator, year, or full text.

I have already performed a search using `tavily_technical_search` and the results confirm that `pyzotero` is the right library for this task. The search results also point to some useful methods like `Zotero.new_fulltext`. The search also provided a link to a GitHub repository that seems to have a similar implementation, which I can use as a reference.

Now I need to formulate a plan to implement the MCP server.

**Deconstruction of the Request:**

*   **Functionality 1: Get Item Metadata**
    *   **Tool Name:** `get_item_metadata`
    *   **Input:** `item_key` (string)
    *   **Output:** A dictionary or JSON string containing the detailed metadata of the specified Zotero item.
    *   **Implied Requirement:** Need a way to connect to a specific Zotero library, which means `library_id` and `api_key` will be needed for the `pyzotero` client. These should be handled securely, probably through environment variables.

*   **Functionality 2: Get Item Full Text**
    *   **Tool Name:** `get_item_fulltext`
    *   **Input:** `item_key` (string)
    *   **Output:** A string containing the extracted full text from the item's attachment (likely a PDF). If no full text is available, it should return a clear message.
    *   **Implied Requirement:** The implementation will need to find the attachment (PDF) associated with the item, download it, and extract the text. Libraries like `PyPDF2` or `pdfplumber` might be needed for text extraction from PDFs. I should check if `pyzotero` has a built-in way to do this. The search results mentioned `Zotero.new_fulltext`, which sounds promising and might handle this internally.

*   **Functionality 3: Search Items**
    *   **Tool Name:** `search_items`
    *   **Input:** A flexible query string (`query`), and potentially optional parameters to specify the search field (e.g., `field` which could be 'title', 'creator', 'year', 'fulltext'). The user request implies a flexible search, so a single query parameter that can be used against different fields seems appropriate. The user mentioned "按标题、创建者、年份或全文搜索" (search by title, creator, year, or full text). A `q` parameter for the query and an optional `qmode` (quick search mode) parameter in `pyzotero`'s `items()` method seems to be the way to go.
    *   **Output:** A formatted list of search results. Each item in the list should be a summary (e.g., dictionary with title, authors, year, item_key).

**Research Strategy (Recap):**

My initial research confirmed `pyzotero` is the right tool. I found references to `Zotero.new_fulltext`. I don't think I need another search. I have enough information to create the plan. The key will be to structure the tools correctly according to the MCP documentation provided.

**Generating the Final Plan:**

I will now create the final markdown plan.

1.  **Server Overview**: A brief description of the server's purpose.
2.  **File to be Generated**: A single Python file, `mcp_zotero_server.py`.
3.  **Dependencies**: I'll list `mcp-sdk`, `pyzotero`, and potentially a PDF text extraction library if `pyzotero` doesn't handle it out of the box. From the search, it seems `pyzotero` might handle it, but I will list a PDF library as a potential dependency to be safe. I'll also need `python-dotenv` to manage the API keys securely.
4.  **MCP Tools Plan**: This will be the core of the plan, detailing each of the three functions (`get_item_metadata`, `get_item_fulltext`, `search_items`) with their names, descriptions, parameters, and return values, as per the user's request and the MCP best practices. I'll pay close attention to the docstring format.

I will structure the final output as a single markdown block. I will not generate any python code.# MCP Server Implementation Plan: Zotero Academic Literature Management

This document outlines the detailed implementation plan for an MCP server designed to interact with a Zotero library.

## 1. Server Overview

The server will provide an interface for managing academic literature in a Zotero library. It will enable clients to access and manipulate Zotero data through a set of well-defined tools. The core functionalities include retrieving detailed metadata for specific library items, extracting full-text content from attached documents, and performing flexible searches across the library based on criteria such as title, author, year, or full-text content.

## 2. File to be Generated

All the server logic will be contained within a single Python file:
*   `mcp_zotero_server.py`

## 3. Dependencies

The following third-party Python libraries will be required for the implementation:

*   **`mcp-sdk`**: The core library for creating the MCP server.
*   **`pyzotero`**: The client library for interacting with the Zotero Web API.
*   **`python-dotenv`**: To manage Zotero API credentials (library ID, API key) securely from a `.env` file.
*   **`pypdf`**: A library to extract text from PDF files, which will be used for the full-text extraction functionality.

A `requirements.txt` file should be created with the following content:
```
mcp-sdk
pyzotero
python-dotenv
pypdf
```

## 4. MCP Tools Plan

The server will expose the following tools, accessible via the MCP protocol.

---

### **Tool 1: Get Item Metadata**

*   **Function Name**: `get_item_metadata`
*   **Description**: Retrieves the complete metadata for a single item in the Zotero library using its unique item key. This provides detailed information such as title, authors, publication date, abstract, and tags.
*   **Parameters**:
    *   `item_key` (str): The unique identifier for the Zotero item. This key can be found in the Zotero application or through the API. This parameter is required.
*   **Return Value**:
    *   **Type**: `dict`
    *   **Description**: A dictionary containing the detailed metadata of the specified Zotero item. If the item is not found, an error will be raised.
    *   **Example**:
        ```json
        {
          "key": "ABCDE123",
          "version": 100,
          "itemType": "journalArticle",
          "title": "The Structure of Scientific Revolutions",
          "creators": [
            {"creatorType": "author", "firstName": "Thomas S.", "lastName": "Kuhn"}
          ],
          "abstractNote": "A book about the history of science...",
          "publicationTitle": "International Encyclopedia of Unified Science",
          "date": "1962",
          ...
        }
        ```

---

### **Tool 2: Get Item Full Text**

*   **Function Name**: `get_item_fulltext`
*   **Description**: Extracts and returns the full text content from the primary PDF attachment of a specified Zotero item. It first identifies the PDF attachment associated with the item key, downloads it, and then extracts its text content.
*   **Parameters**:
    *   `item_key` (str): The unique identifier for the Zotero item whose full text is to be extracted. This parameter is required.
*   **Return Value**:
    *   **Type**: `str`
    *   **Description**: A string containing the complete, extracted plain text from the item's PDF attachment. If the item has no PDF attachment or if the text cannot be extracted, it will return a message indicating that full text is not available.
    *   **Example**:
        ```
        "Chapter 1: Introduction to Paradigms... The normal-scientific tradition that emerges from a scientific revolution is not only incompatible but often actually incommensurable with that which has gone before..."
        ```

---

### **Tool 3: Search Items**

*   **Function Name**: `search_items`
*   **Description**: Performs a flexible search within the Zotero library. It can search by title, creator (author), year, or within the full text of attachments. The function returns a list of matching items with their essential metadata.
*   **Parameters**:
    *   `query` (str): The search term or phrase to look for. This parameter is required.
    *   `search_field` (str, optional): The specific field to search within. Accepted values are `'title'`, `'creator'`, `'year'`, or `'fulltext'`. If not provided, it defaults to a general-purpose search across all fields (Zotero's "everything" search).
    *   `limit` (int, optional): The maximum number of search results to return. Defaults to `25`.
*   **Return Value**:
    *   **Type**: `list[dict]`
    *   **Description**: A list of dictionaries, where each dictionary represents a found Zotero item and contains its key metadata (e.g., item key, title, creators, year). If no items are found, an empty list is returned.
    *   **Example**:
        ```json
        [
          {
            "item_key": "XYZW4567",
            "title": "The Logic of Scientific Discovery",
            "creators": "Karl Popper",
            "year": "1959"
          },
          {
            "item_key": "FGHI8910",
            "title": "Against Method: Outline of an Anarchistic Theory of Knowledge",
            "creators": "Paul Feyerabend",
            "year": "1975"
          }
        ]
        ```