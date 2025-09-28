import sys
import httpx
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown
from bs4 import BeautifulSoup
import os
from urllib.parse import unquote
import base64

def initialize_markdown_converter():
    """
    Initializes and returns a MarkItDown converter instance with proper configuration.
    Uses BeautifulSoup to preprocess HTML content for better compatibility.
    """
    return MarkItDown(enable_plugins=True)

# Initialize FastMCP server
mcp = FastMCP("markdown_converter")

# Initialize MarkItDown converter
markdown_converter = initialize_markdown_converter()

@mcp.tool()
def convert_to_markdown(content_url: str, content_type: str) -> dict:
    """
    Converts various types of content (HTTP/HTTPS webpages, local files, and data URIs) into structured Markdown format. 
    Preserves structural elements such as headings, lists, links, and tables.

    Args:
        content_url: The URL or path to the content that needs to be converted. This could be an HTTP/HTTPS webpage, a local file path, or a data URI.
        content_type: The type of content being provided (e.g., "http", "https", "file", "data_uri").

    Returns:
        A dictionary containing the 'result' key with the content converted into Markdown format.

    Raises:
        ValueError: If the content type is invalid or if there is an error during conversion.
        httpx.HTTPStatusError: If fetching HTTP/HTTPS content fails.
        FileNotFoundError: If the specified file does not exist or cannot be read.
        UnicodeDecodeError: If the file content cannot be decoded using UTF-8.

    Example:
        To convert an HTTP webpage:
        convert_to_markdown(content_url="https://example.com", content_type="http")

        To convert a local file:
        convert_to_markdown(content_url="/path/to/local/file.html", content_type="file")

        To convert a data URI:
        convert_to_markdown(content_url="data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==", content_type="data_uri")
    """

    try:
        # Validate content_type
        if content_type not in ["http", "https", "file", "data_uri"]:
            raise ValueError(f"Invalid content_type: {content_type}. Must be one of ['http', 'https', 'file', 'data_uri'].")

        # Fetch content based on content_type
        if content_type in ["http", "https"]:
            response = httpx.get(content_url)
            response.raise_for_status()  # Raise exception for HTTP errors
            content = response.text
            
            # Use BeautifulSoup to preprocess HTML content
            soup = BeautifulSoup(content, 'html.parser')
            content = str(soup)
            
        elif content_type == "file":
            if not os.path.isfile(content_url):
                raise FileNotFoundError(f"The file '{content_url}' does not exist.")
            
            # Handle special characters in file paths
            content_url = unquote(content_url)
            
            # Try to handle different file types with MarkItDown's built-in converters
            try:
                result = markdown_converter.convert(content_url)
                content = result.text_content if hasattr(result, 'text_content') else str(result)
            except Exception as e:
                # Fallback to reading as text if MarkItDown can't handle it
                with open(content_url, 'r', encoding='utf-8-sig') as file:
                    content = file.read()
                    
                    # Use BeautifulSoup to preprocess HTML content
                    if content_url.lower().endswith('.html') or content_url.lower().endswith('.htm'):
                        soup = BeautifulSoup(content, 'html.parser')
                        content = str(soup)
                        
        elif content_type == "data_uri":
            try:
                header, encoded = content_url.split(",", 1)
                decoded = base64.b64decode(encoded)
                
                # Directly use the decoded bytes as content
                content = decoded.decode('utf-8')
                
                # Wrap data URI content in a StringIO-like object for MarkItDown
                from io import StringIO
                fake_file = StringIO(content)
                fake_file.name = "data_uri_content.html"  # Give it a name so MarkItDown treats it like a file
                
                # Use BeautifulSoup to preprocess HTML content
                soup = BeautifulSoup(content, 'html.parser')
                content = str(soup)
                
            except (ValueError, base64.binascii.Error) as e:
                raise ValueError("Invalid data URI format.") from e

        # Convert fetched content to Markdown using MarkItDown
        markdown_result = markdown_converter.convert(content)
        
        # Handle cases where the result has text_content attribute (for files)
        final_result = markdown_result.text_content if hasattr(markdown_result, 'text_content') else str(markdown_result)

        # Return the result as JSON string
        return {"result": final_result}

    except Exception as e:
        # Handle exceptions and return meaningful error messages
        return {"error": f"An error occurred during conversion: {str(e)}"}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()