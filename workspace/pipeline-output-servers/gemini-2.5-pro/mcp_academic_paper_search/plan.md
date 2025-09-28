# MCP Tools Plan

### 1. search_papers

*   **Function Name**: `search_papers`
*   **Description**: Concurrently searches for academic papers on Semantic Scholar and Crossref using a given query. It then merges and formats the results into a unified list.
*   **Parameters**:
    *   `query` (str): The search keywords for finding papers.
    *   `limit` (int): The maximum number of papers to return from each source.
*   **Return Value**: A list of dictionaries, where each dictionary represents a paper and contains the keys `title`, `authors`, `year`, and `doi`.

### 2. fetch_paper_details

*   **Function Name**: `fetch_paper_details`
*   **Description**: Fetches detailed information for a specific paper from either Semantic Scholar or Crossref using its unique identifier.
*   **Parameters**:
    *   `paper_id` (str): The identifier of the paper (e.g., DOI or Semantic Scholar ID).
    *   `source` (str): The data source to query. Must be either 'Semantic Scholar' or 'Crossref'.
*   **Return Value**: A dictionary containing the paper's details, including `title`, `authors`, `abstract`, and `venue` (publication place).

### 3. search_by_topic

*   **Function Name**: `search_by_topic`
*   **Description**: Searches for papers on a specific topic, with an optional year range. It prioritizes Semantic Scholar for the search and uses Crossref as a fallback if the primary search yields no results.
*   **Parameters**:
    *   `topic_keywords` (str): The topic keywords to search for.
    *   `year_range` (str, optional): A string representing the year range for the search (e.g., "2020-2023"). Defaults to None.
    *   `limit` (int): The maximum number of results to return.
*   **Return Value**: A list of dictionaries, where each dictionary represents a paper and contains keys such as `title`, `authors`, `year`, and `doi`.

# Server Overview

The MCP server will provide a suite of tools for automating academic paper searches and queries. It will interact with the Semantic Scholar and Crossref APIs to offer functionalities for searching papers by keywords, fetching detailed paper information by ID, and performing topic-based searches with optional filters.

# File to be Generated

*   `mcp_academic_search_server.py`

# Dependencies

*   `mcp`
*   `httpx`
*   `semanticscholar`
*   `crossref-commons`