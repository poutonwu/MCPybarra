<thought>### **4. Analyze Research Results & Finalize Plan**

My research has yielded the necessary components for the implementation plan.

*   **For `DuckDuckGo_search`**: The research points to two primary options: the official DuckDuckGo Search API and third-party services like SerpApi. The official API, accessible via `http://api.duckduckgo.com/?q=...&format=json`, is the most direct and dependency-free method. It provides structured JSON, which is exactly what the user's request implies. I will choose this method to minimize external dependencies and stick to an official source. I will use the `httpx` library, as recommended in the MCP documentation, to make the asynchronous web request.

*   **For `fetch_content`**: The search results consistently recommend `BeautifulSoup` for parsing HTML and extracting text. This is a standard and powerful library for this task. To get the webpage content, I will again use `httpx` for the download. The core challenge is to isolate the *main* text. A common technique with BeautifulSoup is to find common tags for main content like `<article>`, `<main>`, or `<p>`, and then join their text. I will plan to implement a simple version of this logic, focusing on extracting text from paragraph (`<p>`) tags as a robust starting point.

Now, I will proceed to generate the final, detailed implementation plan in the required Markdown format. I will structure the plan with the mandatory sections: `MCP Tools Plan`, `Server Overview`, `File to be Generated`, and `Dependencies`. The `MCP Tools Plan` will be the most detailed section, outlining each tool's function, parameters, and return values as specified in the prompt.# Automata MCP Server: Implementation Plan

## Server Overview

This document outlines the implementation plan for an MCP server designed to automate web search and content retrieval tasks. The server will provide two primary tools accessible via the MCP protocol: one for performing searches on DuckDuckGo and another for fetching the primary text content from a given webpage URL. The goal is to provide structured, clean data in response to user requests.

## File to be Generated

All the server code will be contained within a single Python file named `mcp_search_server.py`.

## Dependencies

The following third-party Python libraries will be required for this project and should be installed:

*   `mcp-sdk`: For building the core MCP server.
*   `httpx`: For making asynchronous HTTP requests to the DuckDuckGo API and fetching webpage content.
*   `beautifulsoup4`: For parsing HTML and extracting text content from webpages.

## MCP Tools Plan

### Tool 1: DuckDuckGo Search

*   **Function Name**: `DuckDuckGo_search`
*   **Description**: Performs a search on DuckDuckGo using the provided query and returns the results in a structured format. This tool is designed to give users quick access to search results without needing to manually open a browser.
*   **Parameters**:
    *   `query` (str): The search term or phrase that the user wants to look up. This parameter is mandatory.
*   **Return Value**:
    *   **Type**: `str`
    *   **Content**: A JSON formatted string representing a list of search results. Each item in the list will be an object containing the following keys:
        *   `title`: The title of the search result.
        *   `link`: The direct URL to the search result.
        *   `snippet`: A brief summary or description of the result.
    *   **Example Return**:
        ```json
        "[{\"title\": \"Official Python Website\", \"link\": \"https://www.python.org\", \"snippet\": \"The official home of the Python Programming Language...\"}, {\"title\": \"Python (programming language) - Wikipedia\", \"link\": \"https://en.wikipedia.org/wiki/Python_(programming_language)\", \"snippet\": \"Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability...\"}]"
        ```

### Tool 2: Fetch Web Content

*   **Function Name**: `fetch_content`
*   **Description**: Fetches the content from a given URL, parses the HTML, and extracts the primary text content. It aims to remove boilerplate elements like navigation bars, ads, and footers, returning only the core article or body text.
*   **Parameters**:
    *   `url` (str): The full URL of the webpage from which to extract content. This parameter is mandatory.
*   **Return Value**:
    *   **Type**: `str`
    *   **Content**: A single string containing the cleaned, primary text content of the webpage. Paragraphs will be separated by newlines. If the content cannot be fetched or parsed, an error will be raised.
    *   **Example Return**:
        ```text
        "The Python programming language is a versatile and powerful tool for developers. Its clear syntax and readability make it an excellent choice for beginners and experts alike.\n\nThis article will explore the core features of Python and demonstrate how to get started with your first program."
        ```