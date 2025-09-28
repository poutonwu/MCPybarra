### **MCP Tools Plan**

#### **1. `get_item_metadata`**
- **Description**: Retrieves detailed metadata for a specified Zotero entry using its unique item key.  
- **Parameters**:  
  - `item_key` (str, required): The unique identifier for the Zotero entry.  
- **Return Value**:  
  - A JSON object containing the entry's metadata (e.g., title, authors, publication year, DOI, etc.).  

#### **2. `get_item_fulltext`**  
- **Description**: Extracts the full-text content of a Zotero entry (e.g., PDF, HTML, or plain text).  
- **Parameters**:  
  - `item_key` (str, required): The unique identifier for the Zotero entry.  
- **Return Value**:  
  - A string or binary data representing the full-text content (if available).  

#### **3. `search_items`**  
- **Description**: Performs a flexible search in the Zotero library, supporting queries by title, creator, year, or full-text content.  
- **Parameters**:  
  - `query` (str, required): The search term (e.g., title, author name, year, or keyword).  
  - `search_type` (str, optional): Specifies the search scope (`title`, `creator`, `year`, `fulltext`). Default: `title`.  
- **Return Value**:  
  - A formatted list of search results, each including metadata for matching entries.  

---

### **Server Overview**  
The MCP server will provide automated academic literature management by interacting with a Zotero library. It supports:  
- Retrieving detailed metadata for specific entries.  
- Extracting full-text content from entries.  
- Flexible searching across titles, authors, years, or full text.  

---

### **File to be Generated**  
- **Filename**: `mcp_zotero_server.py`  
- **Contents**:  
  - Implementation of the three tools (`get_item_metadata`, `get_item_fulltext`, `search_items`) using the `pyzotero` library.  
  - FastMCP server setup and tool registration.  

---

### **Dependencies**  
- **Required Libraries**:  
  - `pyzotero` (for Zotero API access).  
  - `httpx` (for asynchronous HTTP requests).  
  - `mcp[cli]` (MCP SDK for server setup).  

Install via:  
```bash
pip install pyzotero httpx mcp[cli]
```  

--- 

This plan adheres strictly to the user's request, leveraging the `pyzotero` library for Zotero integration and following MCP protocol best practices. No additional tools or functionalities are included.