# MCP Server Implementation Plan for Tavily Web Search

## MCP Tools Plan

### 1. `tavily_web_search`
- **Description**: Performs comprehensive web search using Tavily API with domain filtering and configurable search depth
- **Parameters**:
  - `query` (str): Search query string
  - `search_depth` (str, optional): "basic" or "advanced", default: "basic"
  - `include_domains` (List[str], optional): Domains to include in results
  - `exclude_domains` (List[str], optional): Domains to exclude from results
  - `max_results` (int, optional): Number of results to return (1-5), default: 5
- **Return Value**:
  ```python
  List[Dict[str, str]] = [
    {
      "title": "Page title",
      "url": "https://example.com",
      "content": "Page content summary"
    }
  ]
  ```

### 2. `tavily_answer_search`
- **Description**: Generates direct answers to questions with evidence using Tavily's Q&A capability
- **Parameters**:
  - `query` (str): Question to answer
  - - `search_depth` (str, optional): "basic" or "advanced", default: "advanced"
- **Return Value**:
  ```python
  Dict[str, Union[str, List[Dict]]] = {
    "answer": "Concise answer to the question",
    "evidence": [
      {
        "title": "Source page title",
        "url": "https://source.com",
        "content": "Relevant supporting content"
      }
    ]
  }
  ```

### 3. `tavily_news_search`
- **Description**: Searches for recent news articles with source filtering
- **Parameters**:
  - `query` (str): News search query
  - `days` (int, optional): Days to look back (1-365), default: 7
  - `include_domains` (List[str], optional): News sources to include
  - `exclude_domains` (List[str], optional): News sources to exclude
  - `max_results` (int, optional): Number of results to return (1-5), default: 5
- **Return Value**:
  ```python
  List[Dict[str, str]] = [
    {
      "title": "News article title",
      "url": "https://news.example.com",
      "content": "Article content summary"
    }
  ]
  ```

## Server Overview
The server implements a search processing system using the Tavily API, providing three core capabilities:
1. Comprehensive web search with domain filtering
2. Question answering with evidence citation
3. Recent news article search with time constraints

## File to be Generated
- **File Name**: `tavily_mcp_server.py`
- Will contain complete implementation including:
  - FastMCP server initialization
  - Tavily API client integration
  - All three tool implementations with proper error handling
  - Async support and environment configuration

## Dependencies
- `mcp[cli]`: For MCP protocol implementation
- `tavily-python`: Official Tavily Python SDK
- `httpx`: For HTTP requests handling
- `pydantic`: For data validation models
- `python-dotenv`: For environment variable management