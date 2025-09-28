# mcp_tavily_web_search

## Overview

This server provides a set of tools for performing web searches using the Tavily API. It supports general web search, answer-focused search, and news-specific search capabilities, allowing users to retrieve information with varying depth and specificity.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:
```
tavily
python-dotenv
mcp[cli]
```

## Running the Server

Set your Tavily API key in the `.env` file or export it in the environment, then run the server:

```bash
python mcp_tavily_web_search.py
```

If needed, configure proxy settings by uncommenting and adjusting the proxy lines in the script.

## Available Tools

### 1. `tavily_web_search`

Performs a comprehensive web search with customizable depth and domain filtering. Supports both basic and advanced search modes.

**Parameters:**
- `query`: The search query string (required).
- `search_depth`: 'basic' or 'advanced' (default: 'basic').
- `include_domains`: Optional list of domains to include.
- `exclude_domains`: Optional list of domains to exclude.
- `max_results`: Maximum number of results to return (default: 5).

### 2. `tavily_answer_search`

Conducts an advanced search focused on finding a direct answer to a specific question, supported by evidence from search results.

**Parameters:**
- `query`: The question or query for which a direct answer is sought (required).
- `max_results`: Maximum number of supporting results (default: 5).

### 3. `tavily_news_search`

Searches for recent news articles filtered by topic, date range, and domain inclusion/exclusion.

**Parameters:**
- `query`: The topic or keyword for the news search (required).
- `max_days_ago`: Maximum age of articles in days (1–365, default: 7).
- `include_domains`: Optional list of news domains to include.
- `exclude_domains`: Optional list of news domains to exclude.
- `max_results`: Maximum number of news articles to return (default: 5).