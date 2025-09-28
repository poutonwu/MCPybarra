import sys
import os
import httpx
import base64
from markitdown import MarkItDown
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("mcp_markdown_converter")

@mcp.tool()
def convert_to_markdown(source: str, source_type: str) -> str:
    """
    Converts various content formats (HTTP/HTTPS webpages, local files, and data URIs) into structured Markdown format.

    Args:
        source (str): The source to convert to Markdown. This can be a URL (HTTP or HTTPS), a local file path, or a data URI.
            Example: "https://example.com" or "/path/to/local/file.txt" or "data:text/plain;base64,SGVsbG8gd29ybGQ="
        source_type (str): Specifies the type of the source ("url", "file", or "data_uri").
            Example: "url"

    Returns:
        str: A string containing the Markdown representation of the input content. This will retain structural elements like headings, lists, links, and tables.

    Raises:
        ValueError: If the source_type is not one of "url", "file", or "data_uri".
        httpx.HTTPStatusError: If the HTTP request fails for a URL source.
        FileNotFoundError: If the local file does not exist.
        Exception: For general errors during conversion.

    Example:
        convert_to_markdown("https://example.com", "url")
    """
    try:
        md = MarkItDown()

        if source_type == "url":
            # Fetch content from URL
            response = httpx.get(source)
            response.raise_for_status()
            content = response.text

        elif source_type == "file":
            # Read content from local file
            if not os.path.exists(source):
                raise FileNotFoundError(f"File not found: {source}")

            # Detect binary files
            try:
                with open(source, "r", encoding="utf-8-sig") as file:
                    content = file.read()
            except UnicodeDecodeError:
                raise Exception(f"Binary files are not supported: {source}. Please provide text-based files only.")

        elif source_type == "data_uri":
            # Decode content from data URI
            if not source.startswith("data:"):
                raise ValueError("Invalid data URI format.")
            comma_index = source.find(",")
            if comma_index == -1:
                raise ValueError("Invalid data URI format.")
            base64_content = source[comma_index + 1:]
            content = base64.b64decode(base64_content).decode("utf-8")

        else:
            raise ValueError(f"Unsupported source_type: {source_type}")

        # Convert content to Markdown
        result = md.convert(content)
        return result

    except httpx.HTTPStatusError as e:
        # Ensure we have proper request and response objects in the exception
        if not hasattr(e, 'request') or not hasattr(e, 'response'):
            raise httpx.HTTPStatusError(
                message=str(e),
                request=e.request if hasattr(e, 'request') else httpx.Request("GET", source),
                response=e.response if hasattr(e, 'response') else response if 'response' in locals() else None
            ) from e
        raise
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File error: {str(e)}") from e
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}") from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()