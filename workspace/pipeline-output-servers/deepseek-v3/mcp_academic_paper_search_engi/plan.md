Here is the detailed implementation plan for the MCP server based on the user's request:

---

### **MCP Tools Plan**

#### 1. **`search_papers`**
- **Description**: Searches for academic papers based on keywords and a result limit, returning formatted paper lists from Semantic Scholar and Crossref. The list includes title, authors, year, and DOI.
- **Parameters**:
  - `keywords` (str): The search query for academic papers.
  - `limit` (int, optional): Maximum number of results to return. Defaults to 10.
- **Return Value**: A list of dictionaries, each containing:
  - `title` (str): Paper title.
  - `authors` (list): List of author names.
  - `year` (int): Publication year.
  - `doi` (str): Digital Object Identifier (DOI) for the paper.
  - `source` (str): Source of the paper (Semantic Scholar or Crossref).

#### 2. **`fetch_paper_details`**
- **Description**: Fetches detailed information for a paper using its ID (DOI or Semantic Scholar ID) and a specified source (Semantic Scholar or Crossref). Details include title, authors, abstract, and publication venue.
- **Parameters**:
  - `paper_id` (str): The paper's DOI or Semantic Scholar ID.
  - `source` (str): The source to fetch from (`semantic_scholar` or `crossref`).
- **Return Value**: A dictionary containing:
  - `title` (str): Paper title.
  - `authors` (list): List of author names.
  - `abstract` (str): Paper abstract.
  - `publication_venue` (str): Journal or conference name.
  - `year` (int): Publication year.
  - `doi` (str): Digital Object Identifier (DOI).

#### 3. **`search_by_topic`**
- **Description**: Searches for papers by topic keywords, optionally filtered by year range and result limit. Prioritizes Semantic Scholar and falls back to a generic search if needed.
- **Parameters**:
  - `topic` (str): Topic keywords for the search.
  - `year_range` (tuple, optional): Inclusive year range as `(start_year, end_year)`. Defaults to `None`.
  - `limit` (int, optional): Maximum number of results to return. Defaults to 10.
- **Return Value**: A list of dictionaries, each containing:
  - `title` (str): Paper title.
  - `authors` (list): List of author names.
  - `year` (int): Publication year.
  - `doi` (str): Digital Object Identifier (DOI).
  - `source` (str): Source of the paper (Semantic Scholar or Crossref).

---

### **Server Overview**
The MCP server will automate academic paper searches and queries, providing three core functionalities:
1. Keyword-based paper searches with result limits (`search_papers`).
2. Detailed paper information retrieval by ID and source (`fetch_paper_details`).
3. Topic-based searches with optional year filtering and fallback support (`search_by_topic`).

The server will integrate with Semantic Scholar and Crossref APIs to fetch and format paper data.

---

### **File to be Generated**
- **Filename**: `mcp_paper_server.py`

---

### **Dependencies**
- `httpx`: For making HTTP requests to Semantic Scholar and Crossref APIs.
- `mcp[cli]`: MCP SDK for server implementation.
- Optional: `python-dotenv` for managing API keys (if authentication is required).

--- 

This plan adheres strictly to the user's request and focuses on the required functionalities without adding unnecessary features.