import sys
import os
import json
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# Proxy Support: If any network requests are involved, add proxy support.
# To use a proxy, uncomment the following lines and set the correct proxy address.
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize FastMCP Server
# The server name is set based on the development plan.
mcp = FastMCP("mcp_duckduckgo_search_fetcher")

# Shared httpx.AsyncClient for performance improvement
# This client is reused across multiple requests to enhance performance.
# Dependencies: httpx, beautifulsoup4
client = httpx.AsyncClient()

@mcp.tool()
async def DuckDuckGo_search(query: str) -> str:
    """
    Performs a search on DuckDuckGo using the provided query and returns the results in a structured format.
    This tool is designed to give users quick access to search results without needing to manually open a browser.

    Args:
        query (str): The search term or phrase that the user wants to look up. This parameter is mandatory.
                     Example: "Python programming language"

    Returns:
        str: A JSON formatted string representing a list of search results. Each item in the list
             is an object containing 'title', 'link', and 'snippet'.
             Example:
             "[{\"title\": \"Official Python Website\", \"link\": \"https://www.python.org\", \"snippet\": \"The official home of the Python Programming Language...\"}]"

    Raises:
        ValueError: If the query parameter is empty or contains only whitespace.
        httpx.HTTPStatusError: If the request to the DuckDuckGo API fails.
    """
    if not query or not query.strip():
        raise ValueError("The 'query' parameter cannot be empty.")

    try:
        api_url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1}

        response = await client.get(api_url, params=params)
        response.raise_for_status()

        data = response.json()

        results = []
        if data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                # Ensure we are processing topics that have a 'FirstURL' and 'Text'
                if "FirstURL" in topic and "Text" in topic:
                    # Handle cases where 'Text' might not contain a separator
                    if " - " in topic["Text"]:
                        title, snippet = topic["Text"].split(" - ", 1)
                    else:
                        title, snippet = topic["Text"], ""

                    results.append({
                        "title": title,
                        "link": topic.get("FirstURL", ""),
                        "snippet": snippet
                    })

        return json.dumps(results, ensure_ascii=False)

    except httpx.HTTPStatusError as e:
        # Re-raise with a more informative message for transparency
        raise httpx.HTTPStatusError(f"API request failed with status {e.response.status_code}: {e.response.text}", request=e.request, response=e.response)
    except Exception as e:
        # Catch any other unexpected errors during the process
        raise RuntimeError(f"An unexpected error occurred during DuckDuckGo search: {str(e)}")


@mcp.tool()
async def fetch_content(url: str) -> str:
    """
    Fetches the content from a given URL, parses the HTML, and extracts the primary text content.
    It aims to remove boilerplate elements like navigation, ads, and footers.

    Args:
        url (str): The full URL of the webpage from which to extract content. This parameter is mandatory.
                   Example: "https://www.python.org/doc/"

    Returns:
        str: A single string containing the cleaned, primary text content of the webpage.
             Paragraphs are separated by newlines.
             Example:
             "The Python programming language is a versatile and powerful tool...\\n\\nThis article will explore..."

    Raises:
        ValueError: If the URL is invalid or empty.
        httpx.RequestError: If there is a problem with the network request.
    """
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("A valid URL starting with 'http://' or 'https://' is required.")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = await client.get(url, headers=headers, follow_redirects=True)
        response.raise_for_status()

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # A common technique to extract main content is to find all paragraph tags (<p>).
        # This is a robust starting point for many websites.
        paragraphs = soup.find_all('p')
        if not paragraphs:
            # Fallback to getting all text if no <p> tags are found
            return soup.get_text(separator='\n\n', strip=True)

        content = [p.get_text(strip=True) for p in paragraphs]
        return "\n\n".join(content)

    except httpx.HTTPStatusError as e:
        raise httpx.HTTPStatusError(f"Failed to fetch content due to HTTP status {e.response.status_code} for URL: {url}", request=e.request, response=e.response)
    except httpx.RequestError as e:
        raise httpx.RequestError(f"A network error occurred while trying to fetch the URL: {url}. Details: {str(e)}", request=e.request)
    except Exception as e:
        # Catch any other unexpected errors during parsing
        raise RuntimeError(f"An unexpected error occurred during content fetching or parsing: {str(e)}")


if __name__ == "__main__":
    # Ensure UTF-8 encoding for standard output to handle various characters.
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    # Run the MCP server. It listens for requests based on the specified transport.
    # Default is "stdio" if not specified.
    mcp.run()