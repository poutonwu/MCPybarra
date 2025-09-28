### **MCP Tools Plan**

#### Tool 1: `search_papers`
- **Description**: Searches for academic papers based on keywords and limits the number of results. Returns a formatted list of papers including title, authors, year, and DOI from both Semantic Scholar and Crossref.
- **Parameters**:
  - `keywords` (str): The search terms or phrases to look for in academic papers.
  - `max_results` (int): The maximum number of results to return.
- **Return Value**: A list of dictionaries, each representing a paper with keys for `title`, `authors`, `year`, and `doi`.

#### Tool 2: `fetch_paper_details`
- **Description**: Retrieves detailed information about a specific paper based on its ID (DOI or Semantic Scholar ID) and source.
- **Parameters**:
  - `paper_id` (str): The unique identifier of the paper (either DOI or Semantic Scholar ID).
  - `source` (str): The source to fetch details from (`Semantic Scholar` or `Crossref`).
- **Return Value**: A dictionary containing the `title`, `authors`, `abstract`, and `publication_venue` of the specified paper.

#### Tool 3: `search_by_topic`
- **Description**: Searches for papers based on topic keywords, with optional filters for year range and result count limit. Prioritizes Semantic Scholar but can fall back to a generic search.
- **Parameters**:
  - `topic_keywords` (str): Keywords related to the topic of interest.
  - `year_range` (tuple of int, optional): A tuple specifying the start and end years for filtering results.
  - `max_results` (int, optional): The maximum number of results to return.
- **Return Value**: A list of dictionaries, each representing a paper with keys for `title`, `authors`, `year`, and `doi`.

### **Server Overview**
The purpose of this MCP server is to automate the process of searching and querying academic papers. It offers functionalities to search for papers by keywords, fetch detailed information about specific papers using their IDs, and perform topic-based searches with optional year-range filtering and fallback support.

### **File to be Generated**
- `mcp_server.py`: This single Python file will contain all the logic required for the MCP server, including tool definitions and server initialization.

### **Dependencies**
- `requests`: For making HTTP requests to external APIs such as Semantic Scholar and Crossref.
- `httpx`: An alternative asynchronous HTTP client if performance optimization through async operations becomes necessary.