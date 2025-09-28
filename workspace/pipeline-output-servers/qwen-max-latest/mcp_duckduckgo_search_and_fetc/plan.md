### MCP Tools Plan

#### Tool 1: `DuckDuckGo_search`
- **Description**: This tool implements a method to search DuckDuckGo and return structured results based on the user's query.
- **Parameters**:
  - `query` (str): The search query string provided by the user.
- **Return Value**: A list of dictionaries containing search result titles, URLs, and snippets.

#### Tool 2: `fetch_content`
- **Description**: This tool fetches and parses the main textual content from a webpage given its URL, removing irrelevant elements.
- **Parameters**:
  - `url` (str): The URL of the webpage whose content needs to be fetched and parsed.
- **Return Value**: A string representing the cleaned main textual content of the webpage.

### Server Overview
The purpose of this server is to provide automated tools for performing searches on DuckDuckGo and fetching the main content from webpages specified by URLs. It will expose these functionalities through an MCP interface.

### File to be Generated
- **File Name**: `mcp_server.py`

### Dependencies
- `duckduckgo-search-api`: For querying DuckDuckGo search engine.
- `beautifulsoup4`: For parsing and extracting content from HTML documents.
- `requests`: For making HTTP requests to fetch web page content.