# mcp_academic_paper_search_engi

A Model Context Protocol (MCP) server that provides tools for searching and retrieving academic paper information from Semantic Scholar and Crossref.

## Overview

This server enables LLMs to search for academic papers using keywords or topics, optionally filtered by year range, and fetch detailed information about specific papers using their IDs. It combines results from Semantic Scholar and Crossref APIs to provide comprehensive academic paper search capabilities.

## Installation

1. Install Python 3.10+
2. Install MCP SDK and httpx:
```bash
pip install mcp[cli] httpx
```
3. Install any other required dependencies (see requirements.txt)

## Running the Server

```bash
python mcp_academic_paper_search_engine.py
```

## Available Tools

### 1. `search_papers`

Search for academic papers based on keywords.

**Args:**
- `keywords`: The search query for academic papers.
- `limit`: Maximum number of results to return (defaults to 10).

**Returns:**
A JSON string containing a list of papers with title, authors, year, and DOI.

### 2. `fetch_paper_details`

Fetch detailed information for a specific paper.

**Args:**
- `paper_id`: The paper's DOI or Semantic Scholar ID.
- `source`: The source to fetch from ('semantic_scholar' or 'crossref').

**Returns:**
A JSON string containing detailed paper information including title, authors, abstract, publication venue, year, and DOI.

### 3. `search_by_topic`

Search for papers by topic keywords, optionally filtered by year range.

**Args:**
- `topic`: Topic keywords for the search.
- `year_range`: Inclusive year range as (start_year, end_year) (optional).
- `limit`: Maximum number of results to return (defaults to 10).

**Returns:**
A JSON string containing a list of papers matching the topic and year range.