# mcp_tavily_web_search_tool

## Overview

This MCP server provides web search capabilities using the Tavily API, allowing language models to access up-to-date information from the web. It supports three types of searches:

- Comprehensive web search
- Answer-focused search with supporting evidence
- Recent news article search

## Installation

1. Install Python 3.10 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

Make sure you have a valid Tavily API key set in your environment variables:
```bash
export TAVILY_API_KEY=your_api_key_here
```

## Running the Server

To start the server, run:
```bash
python mcp_tavily_web_search_tool.py
```

## Available Tools

### 1. `tavily_web_search`
Performs a comprehensive web search using the Tavily API. Returns results with titles, URLs, and content.

**Parameters:**
- `query`: Search query string
- `search_depth`: "basic" for quick results or "advanced" for more thorough analysis
- `include_domains`: Optional list of domains to include in results
- `exclude_domains`: Optional list of domains to exclude from results
- `max_results`: Maximum number of results to return (default 5)

### 2. `tavily_answer_search`
Generates a direct answer to a specific question based on Tavily's search results with supporting evidence.

**Parameters:**
- `query`: Question to be answered
- `max_results`: Maximum number of sources to use for the answer (default 5)

### 3. `tavily_news_search`
Searches for recent news articles through the Tavily API.

**Parameters:**
- `query`: News search query
- `days_back`: Number of days to look back (up to 365)
- `include_sources`: Optional list of news sources to include
- `exclude_sources`: Optional list of news sources to exclude
- `max_results`: Maximum number of news articles to return (default 5)