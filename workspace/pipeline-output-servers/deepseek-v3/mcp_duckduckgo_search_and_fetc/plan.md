### **Final Plan for MCP Server Implementation**

---

#### **1. MCP Tools Plan**

##### **Tool 1: `duckduckgo_search`**
- **Description**: Performs a search on DuckDuckGo based on user-provided queries and returns structured search results.
- **Parameters**:
  - `query` (str, required): The search term or phrase to query on DuckDuckGo.
  - `max_results` (int, optional, default=5): Maximum number of search results to return (limited to 10).
- **Return Value**: 
  - A JSON-formatted string containing:
    - `results`: List of dictionaries, each with keys `title`, `url`, and `snippet` (summary of the result).

##### **Tool 2: `fetch_content`**
- **Description**: Fetches and parses the main text content of a webpage, removing ads, navigation, and other non-essential elements.
- **Parameters**:
  - `url` (str, required): The URL of the webpage to scrape.
- **Return Value**: 
  - A string containing the cleaned, main text content of the webpage.

---

#### **2. Server Overview**
- **Purpose**: 
  - Automate DuckDuckGo searches and web content extraction via MCP-compliant JSON-RPC endpoints.
  - Expose two tools:
    1. `duckduckgo_search`: For retrieving structured search results.
    2. `fetch_content`: For scraping and cleaning webpage text.

---

#### **3. File to be Generated**
- **Filename**: `mcp_duckduckgo_server.py`
- **Structure**:
  - Single Python file containing:
    - FastMCP server initialization.
    - Both tools (`duckduckgo_search` and `fetch_content`) with full annotations.
    - Dependency imports (e.g., `httpx`, `beautifulsoup4`).

---

#### **4. Dependencies**
- **Required Libraries**:
  - `mcp[cli]`: For MCP server implementation.
  - `httpx`: For HTTP requests (DuckDuckGo and webpage fetching).
  - `beautifulsoup4` + `lxml`: For parsing and cleaning HTML content.
- **Installation Command**:
  ```bash
  pip install mcp[cli] httpx beautifulsoup4 lxml
  ```

--- 

### **Notes**
- **Error Handling**: Both tools will validate inputs (e.g., URL format, query non-emptiness) and raise descriptive exceptions.
- **Performance**: Use asynchronous HTTP requests (`httpx.AsyncClient`) for concurrent operations.
- **Security**: Sanitize inputs to prevent injection attacks (e.g., malicious URLs). 

This plan adheres strictly to the user's request and avoids unnecessary features.