import sys
import re
import base64
import os
import binascii
from urllib.parse import urlparse
import requests
from mcp.server.fastmcp import FastMCP
from markdownify import markdownify as md

# Initialize FastMCP server
mcp = FastMCP("markdown_converter")

@mcp.tool()
async def convert_to_markdown(source: str) -> str:
    """Converts content from various sources (HTTP/S webpages, local file paths, or Data URIs) into structured Markdown.

    The tool automatically detects the source type and processes it accordingly. It preserves structural
    elements like headings, lists, tables, and links.

    Args:
        source (str): The source of the content to be converted. This can be:
                      - An HTTP or HTTPS URL (e.g., "https://example.com").
                      - A local file path (e.g., "./my_document.html").
                      - A Data URI (e.g., "data:text/html;base64,PGgxPlRlc3Q8L2gxPg==").

    Returns:
        A string containing the content converted to structured Markdown.

    Raises:
        ValueError: If the source is invalid, content cannot be fetched, or the source type is unsupported.
        requests.exceptions.RequestException: If a network error occurs while fetching a URL.
    """
    if not source or not source.strip():
        raise ValueError("The 'source' parameter cannot be empty.")

    source = source.strip()
    html_content = ""

    try:
        # 1. Detect and handle URL source
        if re.match(r'^https?://', source):
            # Security: Basic SSRF prevention by parsing the URL
            parsed_url = urlparse(source)
            if not (parsed_url.scheme in ['http', 'https'] and parsed_url.netloc):
                raise ValueError(f"Invalid or unsupported URL scheme: {source}")
            
            # Set a user-agent to avoid being blocked by some websites
            headers = {
                'User-Agent': 'mcp-markdown-converter/1.0'
            }
            # Performance: Use a timeout to prevent long-running requests
            response = requests.get(source, headers=headers, timeout=15)
            # Robustness: Check for successful response
            response.raise_for_status()
            html_content = response.text

        # 2. Detect and handle Data URI source
        elif source.startswith('data:'):
            match = re.match(r'data:(?P<mime_type>[^;]+);base64,(?P<data>.+)', source)
            if not match:
                raise ValueError("Invalid Data URI format. Expected format: 'data:<mime_type>;base64,<data>'")
            
            mime_type = match.group('mime_type')
            if 'text/html' not in mime_type and 'text/plain' not in mime_type:
                raise ValueError(f"Unsupported MIME type in Data URI: '{mime_type}'. Only 'text/html' and 'text/plain' are supported.")

            base64_data = match.group('data')
            # Robustness: Handle potential base64 decoding errors
            try:
                decoded_bytes = base64.b64decode(base64_data)
                html_content = decoded_bytes.decode('utf-8')
            except (binascii.Error, UnicodeDecodeError) as e:
                raise ValueError(f"Failed to decode Data URI content: {e}")

        # 3. Handle local file path source
        else:
            # Security: Prevent path traversal attacks
            abs_path = os.path.abspath(source)
            cwd = os.getcwd()
            if not abs_path.startswith(cwd):
                raise ValueError(f"Security error: File path '{source}' is outside the allowed directory.")

            if not os.path.isfile(abs_path):
                raise ValueError(f"File not found at path: {source}")

            # Robustness: Read file with specified encoding
            try:
                with open(abs_path, 'r', encoding='utf-8-sig') as f:
                    html_content = f.read()
            except Exception as e:
                raise IOError(f"Error reading file '{source}': {e}")
        
        if not html_content:
            return "The source content is empty."

        # Functionality: Convert HTML to Markdown
        return md(html_content, heading_style="ATX")

    except requests.exceptions.RequestException as e:
        # Transparency: Provide clear network error messages
        raise ValueError(f"Network error fetching URL '{source}': {e}")
    except Exception as e:
        # Transparency: Re-raise other exceptions with context
        raise ValueError(f"An error occurred while processing source '{source}': {e}")

if __name__ == "__main__":
    # Ensure UTF-8 output for all transport protocols
    if sys.stdout.encoding != 'utf-8':
         sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()