import sys
import httpx
import asyncio
import os
import re
import base64
from urllib.parse import urlparse
from mcp.server.fastmcp import FastMCP
from markitdown import MarkItDown

# Initialize FastMCP server
mcp = FastMCP("markdown_converter")

# Create MarkItDown instance
markitdown = MarkItDown()

async def fetch_content(source: str) -> str:
    """
    Fetch content from various sources including URLs, local files, and data URIs.

    Args:
        source: The source of the content (HTTP/HTTPS URL, file path, or data URI).

    Returns:
        The fetched content as a string.

    Raises:
        ValueError: If the source type is not supported or fetching fails.
    """
    # Parse the source URL
    parsed = urlparse(source)
    
    # Handle HTTP/HTTPS URLs
    if parsed.scheme in ['http', 'https']:
        async with httpx.AsyncClient() as client:
            response = await client.get(source)
            response.raise_for_status()
            return response.text
    
    # Handle local files
    elif parsed.scheme == 'file' or os.path.exists(source):
        try:
            with open(source, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file {source}: {str(e)}")
    
    # Handle data URIs
    elif parsed.scheme == 'data':
        # Parse data URI
        data_parts = parsed.path.split(',', 1)
        if len(data_parts) != 2:
            raise ValueError("Invalid data URI format")
        
        # Extract content
        content = data_parts[1]
        if data_parts[0].endswith(';base64'):
            try:
                return base64.b64decode(content).decode('utf-8')
            except Exception as e:
                raise ValueError(f"Failed to decode base64 data: {str(e)}")
        return content
    
    # Unsupported source type
    else:
        raise ValueError(f"Unsupported source type: {source}")

@mcp.tool()
async def convert_to_markdown(source: str) -> str:
    """
    Convert content from various sources to structured Markdown format.

    Args:
        source: The source of the content (HTTP/HTTPS URL, file path, or data URI).

    Returns:
        The converted content in Markdown format.

    Raises:
        ValueError: If the source type is not supported or conversion fails.
    """
    # Fetch content from the source
    raw_content = await fetch_content(source)
    
    # Convert content to Markdown
    try:
        markdown_content = markitdown.convert(raw_content)
        return markdown_content
    except Exception as e:
        raise ValueError(f"Failed to convert content to Markdown: {str(e)}")

async def main():
    """Main function to run the server."""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        await mcp.run_stdio_async()  # Support stdio transport protocol
    finally:
        print("Server shutdown completed.")

if __name__ == "__main__":
    asyncio.run(main())