import os
import sys
import json
from dotenv import load_dotenv
from tavily import TavilyClient
from mcp.server.fastmcp import FastMCP
from typing import List, Optional

# Load environment variables from .env file
load_dotenv()

# --- Configuration Management ---
# Retrieve Tavily API key from environment variables
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# --- Proxy Support (optional) ---
# Uncomment the following lines if you need to use a proxy
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize FastMCP Server
mcp = FastMCP("tavily_server")

# --- Robustness: Initialize Tavily Client ---
# Check for API key availability before initializing the client
if not TAVILY_API_KEY:
    # --- Transparency: Clear error for missing configuration ---
    print("FATAL: TAVILY_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)

try:
    # Initialize the Tavily client (tavily-python version: 0.3.3)
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
except Exception as e:
    print(f"FATAL: Failed to initialize TavilyClient: {e}", file=sys.stderr)
    sys.exit(1)

@mcp.tool()
def tavily_web_search(
    query: str,
    search_depth: str = 'basic',
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> str:
    """
    Performs a comprehensive web search using the Tavily API.

    This function supports customizable search depth and allows for fine-grained
    control over the search scope by including or excluding specific domains.

    Args:
        query (str): The search query string. (Required)
        search_depth (str, optional): The depth of the search. Can be 'basic' for
                                     quick results or 'advanced' for more in-depth
                                     analysis. Defaults to 'basic'.
        include_domains (List[str], optional): A list of domains to specifically
                                               include in the search results.
        exclude_domains (List[str], optional): A list of domains to specifically
                                               exclude from the search results.
        max_results (int, optional): The maximum number of search results to
                                     return. Defaults to 5.

    Returns:
        str: A JSON string representing a list of dictionaries, where each
             dictionary contains a search result with 'title', 'url', and 'content'.
             In case of an error, a JSON string with an 'error' key is returned.

    Example:
        tavily_web_search(
            query="latest advancements in AI",
            search_depth="advanced",
            include_domains=["techcrunch.com"],
            max_results=3
        )
    """
    try:
        # --- Robustness: Input Validation ---
        if not query or not isinstance(query, str):
            raise ValueError("The 'query' parameter must be a non-empty string.")
        if search_depth not in ['basic', 'advanced']:
            raise ValueError("The 'search_depth' parameter must be 'basic' or 'advanced'.")
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("The 'max_results' parameter must be a positive integer.")

        # --- Functionality: Core Logic ---
        response = tavily_client.search(
            query=query,
            search_depth=search_depth,
            include_domains=include_domains or [],
            exclude_domains=exclude_domains or [],
            max_results=max_results,
        )

        # Ensure 'results' key exists and is a list
        results = response.get('results', [])
        if not isinstance(results, list):
             return json.dumps({"error": "Invalid response format from Tavily API", "details": "Expected 'results' to be a list."})

        # --- Data Serialization ---
        return json.dumps(results)

    except ValueError as ve:
        # --- Transparency: Clear Error Messages ---
        return json.dumps({"error": "Validation Error", "details": str(ve)})
    except Exception as e:
        # --- Robustness: General Exception Handling ---
        return json.dumps({"error": "An unexpected error occurred", "details": str(e)})

@mcp.tool()
def tavily_answer_search(query: str, max_results: int = 5) -> str:
    """
    Conducts a search to find a direct answer to a specific question.

    This tool leverages Tavily's advanced search capabilities to generate a
    concise answer supported by evidence from search results. It always uses
    'advanced' search depth and requests an answer.

    Args:
        query (str): The question or query for which a direct answer is sought. (Required)
        max_results (int, optional): The maximum number of supporting search results
                                     to return alongside the answer. Defaults to 5.

    Returns:
        str: A JSON string containing a dictionary with two keys: 'answer' (str),
             which holds the direct answer, and 'results' (List[dict]), a list
             of supporting search result dictionaries. In case of an error, a
             JSON string with an 'error' key is returned.

    Example:
        tavily_answer_search(query="What is the capital of France?")
    """
    try:
        # --- Robustness: Input Validation ---
        if not query or not isinstance(query, str):
            raise ValueError("The 'query' parameter must be a non-empty string.")
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("The 'max_results' parameter must be a positive integer.")

        # --- Functionality: Core Logic ---
        # The plan specifies using 'advanced' search and including an answer.
        response = tavily_client.search(
            query=query,
            search_depth='advanced',
            include_answer=True,
            max_results=max_results
        )

        # --- Data Serialization ---
        # Structure the response as per the plan.
        structured_response = {
            "answer": response.get("answer", "No direct answer found."),
            "results": response.get("results", [])
        }
        return json.dumps(structured_response)

    except ValueError as ve:
        # --- Transparency: Clear Error Messages ---
        return json.dumps({"error": "Validation Error", "details": str(ve)})
    except Exception as e:
        # --- Robustness: General Exception Handling ---
        return json.dumps({"error": "An unexpected error occurred", "details": str(e)})

@mcp.tool()
def tavily_news_search(
    query: str,
    max_days_ago: int = 7,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> str:
    """
    Specializes in searching for recent news articles.

    It allows filtering articles by their publication date (up to 365 days old)
    and by specific news sources.

    Args:
        query (str): The topic or keyword for the news search. (Required)
        max_days_ago (int, optional): The maximum age of news articles in days.
                                      Must be between 1 and 365. Defaults to 7.
        include_domains (List[str], optional): A list of news source domains to
                                               include (e.g., ['reuters.com']).
        exclude_domains (List[str], optional): A list of news source domains to
                                               exclude.
        max_results (int, optional): The maximum number of news articles to return.
                                     Defaults to 5.

    Returns:
        str: A JSON string representing a list of dictionaries, where each
             dictionary is a news article with 'title', 'url', and 'content'.
             In case of an error, a JSON string with an 'error' key is returned.

    Example:
        tavily_news_search(
            query="tech earnings report",
            max_days_ago=14,
            include_domains=["bloomberg.com"]
        )
    """
    try:
        # --- Robustness: Input Validation ---
        if not query or not isinstance(query, str):
            raise ValueError("The 'query' parameter must be a non-empty string.")
        if not isinstance(max_days_ago, int) or not (1 <= max_days_ago <= 365):
            raise ValueError("The 'max_days_ago' parameter must be an integer between 1 and 365.")
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("The 'max_results' parameter must be a positive integer.")

        # --- Functionality: Core Logic ---
        # The plan specifies using topic="news" to filter for news articles.
        response = tavily_client.search(
            query=query,
            topic="news",
            days=max_days_ago,
            include_domains=include_domains or [],
            exclude_domains=exclude_domains or [],
            max_results=max_results,
        )

        results = response.get('results', [])
        if not isinstance(results, list):
             return json.dumps({"error": "Invalid response format from Tavily API", "details": "Expected 'results' to be a list."})

        # --- Data Serialization ---
        return json.dumps(results)

    except ValueError as ve:
        # --- Transparency: Clear Error Messages ---
        return json.dumps({"error": "Validation Error", "details": str(ve)})
    except Exception as e:
        # --- Robustness: General Exception Handling ---
        return json.dumps({"error": "An unexpected error occurred", "details": str(e)})

if __name__ == "__main__":
    # Ensure UTF-8 encoding for standard output
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    # Run the MCP server
    mcp.run()