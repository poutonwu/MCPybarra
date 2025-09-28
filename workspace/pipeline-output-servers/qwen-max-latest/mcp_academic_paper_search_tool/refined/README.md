# mcp_academic_paper_search_tool

## Overview
This server provides academic paper search capabilities through the Model Context Protocol (MCP). It enables integration with large language models to search for research papers from Semantic Scholar and Crossref, fetch detailed paper information, and perform topic-based searches with optional year range filtering.

## Installation
Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:
```
mcp[cli]
semanticscholar
requests
```

## Running the Server
To start the server, run the following command in your terminal:

```bash
python mcp_academic_paper_search_tool.py
```

Ensure that the server file is named appropriately (e.g., `mcp_academic_paper_search_tool.py`) and located in your working directory.

## Available Tools

### `search_papers_tool`
Searches for academic papers based on provided keywords and returns a list of results with title, authors, year, and DOI.  
**Example usage:**
```python
search_papers_tool(keywords="machine learning", max_results=5)
```

### `fetch_paper_details_tool`
Fetches detailed information about a specific paper using its ID and source (either 'Semantic Scholar' or 'Crossref'). Returns title, authors, abstract, and publication venue.  
**Example usage:**
```python
fetch_paper_details_tool(paper_id="10.1093/mind/lix.236.433", source="Semantic Scholar")
```

### `search_by_topic_tool`
Performs an advanced search for papers related to a specific topic, optionally filtered by a year range and limited by result count.  
**Example usage:**
```python
search_by_topic_tool(topic_keywords="AI ethics", year_range_start=2015, year_range_end=2020, max_results=5)
```