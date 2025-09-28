```markdown
# MCP Implementation Plan for Academic Paper Search and Query Server

## MCP Tools Plan

### Tool 1: `search_papers`
- **Description**: Searches for academic papers based on keywords and limits the number of results. Retrieves data from Semantic Scholar and Crossref.
- **Parameters**:
  - `keywords` (str): Search terms to query academic papers.
  - `limit` (int): Maximum number of results to return.
- **Return Value**: 
  - A list of dictionaries, each containing:
    - `title` (str): The title of the paper.
    - `authors` (list of str): A list of the authors' names.
    - `year` (int): The year of publication.
    - `doi` (str): The DOI of the paper.

### Tool 2: `fetch_paper_details`
- **Description**: Fetches detailed information about a specific paper using its ID and specified source (Semantic Scholar or Crossref).
- **Parameters**:
  - `paper_id` (str): The identifier of the paper (e.g., DOI or Semantic Scholar ID).
  - `source` (str): The source to fetch details from (`"Semantic Scholar"` or `"Crossref"`).
- **Return Value**: 
  - A dictionary containing:
    - `title` (str): The title of the paper.
    - `authors` (list of str): A list of the authors' names.
    - `abstract` (str): The abstract of the paper.
    - `venue` (str): The venue or publication source.

### Tool 3: `search_by_topic`
- **Description**: Searches for papers related to a specific topic, with optional year range and result limit. Prioritizes Semantic Scholar and falls back to general search if needed.
- **Parameters**:
  - `topic` (str): The topic keyword(s) to search for.
  - `year_range` (tuple of int, optional): A tuple specifying the start and end years for filtering results.
  - `limit` (int): Maximum number of results to return.
- **Return Value**: 
  - A list of dictionaries, each containing:
    - `title` (str): The title of the paper.
    - `authors` (list of str): A list of the authors' names.
    - `year` (int): The year of publication.
    - `doi` (str): The DOI of the paper.

---

## Server Overview

The server is an MCP-compliant system designed to automate academic paper search and query tasks. It interacts with the Semantic Scholar and Crossref APIs to provide functionalities such as keyword-based searches, fetching detailed paper information, and topic-based searches with optional year filters.

---

## File to be Generated

- **Filename**: `academic_paper_mcp_server.py`

---

## Dependencies

1. **`httpx`**: For making asynchronous HTTP requests to Semantic Scholar and Crossref APIs.
2. **`mcp[cli]`**: For implementing the MCP server.
3. **`typing`**: For type annotations in Python.
4. **`json`**: For handling JSON data returned by the APIs.
5. **`pydantic`** (optional): For input validation and data modeling.
```