# mcp_tavily_web_tools

## Overview

The `mcp_tavily_web_tools` server provides a set of tools for integrating web search capabilities into LLM workflows using the Tavily API. It supports three primary functions:

- **Web Search**: Perform general web searches with domain filtering and result limits.
- **Answer Search**: Retrieve concise answers to specific questions with supporting evidence.
- **News Search**: Find recent news articles within a specified time range.

These tools enable models to access up-to-date information from the web in a structured and controlled manner.

## Installation

Make sure you have Python 3.10 or higher installed.

1. Clone or download the project.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Ensure your environment includes the following packages:
- `mcp[cli]`
- `httpx`
- `pydantic`
- `python-dotenv` (if used)

Set the required environment variable:
```bash
export TAVILY_API_KEY="your_api_key_here"
```

Replace `"your_api_key_here"` with your actual Tavily API key.

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_tavily_web_tools.py
```

By default, the server uses standard input/output (`stdio`) for communication. You can customize the transport protocol by modifying the `mcp.run()` call in the code if needed.

## Available Tools

### 1. `tavily_web_search`

**Description:** Conducts a comprehensive web search using the Tavily API.

**Parameters:**
- `query`: The search query.
- `search_depth`: `"basic"` or `"advanced"`.
- `include_domains`: List of domains to prioritize.
- `exclude_domains`: List of domains to ignore.
- `max_results`: Number of results to return (1–10).

**Returns:** JSON string containing search results.

---

### 2. `tavily_answer_search`

**Description:** Retrieves a direct answer to a question with supporting evidence from the web.

**Parameters:**
- `query`: The question or query.
- `search_depth`: `"basic"` or `"advanced"` (default: `"advanced"`).
- `max_results`: Number of results to return (1–10).

**Returns:** JSON string containing the answer and source links.

---

### 3. `tavily_news_search`

**Description:** Searches for recent news articles based on a query.

**Parameters:**
- `query`: The topic or keyword to search for.
- `time_range`: Number of days to look back (0–365).
- `include_sources`: News sources to include.
- `exclude_sources`: News sources to exclude.
- `max_results`: Number of articles to return (1–10).

**Returns:** JSON string containing recent news articles.