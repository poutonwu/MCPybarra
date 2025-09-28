import sys
import httpx
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown
from typing import Optional
from urllib.parse import unquote
import base64

# Initialize FastMCP server
mcp = FastMCP("mcp_markdown_converter")

@mcp.tool()
def convert_to_markdown(input_source: str, preserve_structure: bool = True) -> str:
    """
    Converts various input formats (HTTP/HTTPS web pages, local files, and data URIs) into structured Markdown.

    Args:
        input_source: The source to convert (e.g., "https://example.com", "file:///path/to/file.html", or "data:text/html,...").
        preserve_structure: If True, retains original formatting (default: True).

    Returns:
        A string containing the structured Markdown output.

    Raises:
        ValueError: If the input source is invalid or unsupported.
        httpx.HTTPStatusError: If fetching web content fails.
        FileNotFoundError: If local file cannot be found.
        PermissionError: If local file cannot be accessed.
    """
    md = MarkItDown()
    result: Optional[str] = None

    try:
        if input_source.startswith(("http://", "https://")):
            # Fetch web content
            with httpx.Client() as client:
                response = client.get(input_source)
                response.raise_for_status()
                content = response.text
                result = md.convert(content, preserve_structure=preserve_structure)
        elif input_source.startswith("file://"):
            # Read local file
            file_path = unquote(input_source[7:])  # Remove 'file://' prefix and decode URL-escaped characters
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            result = md.convert(content, preserve_structure=preserve_structure)
        elif input_source.startswith("data:"):
            # Process data URI
            # Extract MIME type and content
            parts = input_source.split(',', 1)
            if len(parts) < 2:
                raise ValueError("Invalid data URI: missing content after comma")

            header, data = parts
            is_base64 = ';base64' in header

            if is_base64:
                # Decode base64 encoded content
                content = base64.b64decode(data).decode('utf-8')
            else:
                # URL-decode plain text content
                content = unquote(data)

            result = md.convert(content, preserve_structure=preserve_structure)
        else:
            raise ValueError(f"Unsupported input source: {input_source}")

        if result is None:
            raise ValueError("Conversion returned no output")

        return result.text_content if hasattr(result, 'text_content') else str(result)

    except httpx.HTTPStatusError as e:
        # Properly re-raise HTTPStatusError with required response parameter
        raise httpx.HTTPStatusError(message=str(e), request=e.request, response=e.response)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {input_source}")
    except PermissionError:
        raise PermissionError(f"Permission denied accessing file: {input_source}")
    except Exception as e:
        raise ValueError(f"Conversion failed: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()