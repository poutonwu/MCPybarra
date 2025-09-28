# mcp_tavily_web_search_api

## Overview

This server provides a set of MCP tools for performing web searches, answering queries, and fetching recent news using the Tavily API. It enables LLMs to access real-time information and external knowledge sources.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
mcp[cli]
httpx
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_tavily_web_search_api.py
```

Make sure to replace `mcp_tavily_web_search_api.py` with the actual filename containing your server code.

## Available Tools

### 1. `tavily_web_search`

Performs a comprehensive web search using the Tavily API.

**Parameters:**
- `query`: Search query (required)
- `search_depth`: "basic" (default) or "advanced"
- `include_domains`: List of domains to include in results
- `exclude_domains`: List of domains to exclude from results
- `max_results`: Number of results to return (default: 5, max: 10)

**Returns:** JSON string with search results including title, URL, and summary.

---

### 2. `tavily_answer_search`

Generates direct answers to queries using the Tavily API, along with supporting evidence.

**Parameters:**
- `query`: Query requiring a direct answer (required)
- `max_results`: Number of supporting evidence items (default: 5, max: 10)

**Returns:** JSON string containing an 'answer' and 'evidence' (list of title, URL, and summary).

---

### 3. `tavily_news_search`

Searches for recent news articles using the Tavily API.

**Parameters:**
- `query`: News search query (required)
- `time_limit_days`: Maximum age of articles (default: 30, max: 365)
- `include_sources`: List of news sources to include
- `exclude_sources`: List of news sources to exclude
- `max_results`: Number of articles to return (default: 5, max: 10)

**Returns:** JSON string with news articles including title, URL, summary, and publication date.