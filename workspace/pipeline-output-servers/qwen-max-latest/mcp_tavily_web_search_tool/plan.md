### MCP Tools Plan

#### Tool 1: `tavily_web_search`
- **Description**: Performs a comprehensive web search using the Tavily API. Supports basic or advanced search depth and allows precise control over the search scope by including or excluding specific domains.
- **Parameters**:
  - `query` (str): The search query for technical information, APIs, or code examples.
  - `search_depth` (str): Search depth: 'basic' for quick results, 'advanced' for more comprehensive analysis.
  - `include_domains` (list of str, optional): A list of domains to specifically include in the search results.
  - `exclude_domains` (list of str, optional): A list of domains to specifically exclude from the search results.
  - `max_results` (int): Maximum number of search results to return.
- **Return Value**: A list of search results, each containing the title, URL, and content summary.

#### Tool 2: `tavily_answer_search`
- **Description**: Generates a direct answer based on the query content with supporting evidence using the Tavily API. Suitable for queries requiring specific answers, defaulting to advanced search depth.
- **Parameters**:
  - `query` (str): The search query for which an answer is needed.
  - `max_results` (int): Maximum number of search results to return.
- **Return Value**: A string containing the generated answer along with supporting evidence.

#### Tool 3: `tavily_news_search`
- **Description**: Searches recent news articles using the Tavily API. Supports limiting the query by time (up to 365 days) and specifying included or excluded news sources, ideal for current events and trend reporting.
- **Parameters**:
  - `query` (str): The search query for news articles.
  - `days_back` (int): Number of days back to search for news articles (maximum 365).
  - `include_sources` (list of str, optional): Specific news sources to include in the search results.
  - `exclude_sources` (list of str, optional): Specific news sources to exclude from the search results.
  - `max_results` (int): Maximum number of search results to return.
- **Return Value**: A list of recent news article results, each containing the title, URL, and content summary.

### Server Overview
The server will be designed to automate web search processing through the Tavily API. It will offer three main functionalities: comprehensive web searching with adjustable depth and domain filtering, direct answering of queries with evidence, and specialized news article searching with temporal and source filters.

### File to be Generated
- `mcp_server.py`: This single Python file will contain all logic necessary to run the MCP server, including tool implementations, FastMCP setup, and any necessary configurations.

### Dependencies
- `httpx`: For making asynchronous HTTP requests to the Tavily API.
- `mcp[cli]`: For implementing the Model Context Protocol (MCP) server and tools interface.
- `pydantic`: Optional, for data validation and settings management if further robustness is required.