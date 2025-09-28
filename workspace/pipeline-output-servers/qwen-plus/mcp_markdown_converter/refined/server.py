import sys
import os
import re
import base64
import ssl  # Added missing ssl import
import mimetypes
from io import BytesIO
from typing import Optional, Dict, Any, Union, Tuple

import magic
import httpx
from markitdown import MarkItDown, DocumentConverterResult, StreamInfo
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_markdown_converter")

# Configure proxy if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Supported content types
SUPPORTED_CONTENT_TYPES = {
    "text/html": ".html",
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx"
}


def fetch_content(content_source: str) -> Tuple[bytes, str, str]:
    """
    Fetch content from various sources and detect its type.

    Args:
        content_source: URI or path specifying the content location. Supports:
            * HTTP/HTTPS URLs (e.g., "https://example.com/page.html")
            * File system paths (e.g., "/documents/report.docx")
            * Data URIs (e.g., "data:text/html;base64,...")

    Returns:
        A tuple containing:
            - The content as bytes
            - The detected content type
            - The source type (url, file, data_uri)

    Raises:
        ValueError: If the content source format is invalid or unsupported
        FileNotFoundError: If a local file does not exist
        httpx.HTTPStatusError: If an HTTP request fails
    """
    # Check if it's a data URI
    if content_source.startswith('data:'):
        try:
            # Parse data URI
            header, data = content_source.split(',', 1)
            mime_type_match = re.search(r'([^;,]+)', header)
            if not mime_type_match:
                raise ValueError("Invalid data URI format")
            
            mime_type = mime_type_match.group(1)

            # Handle base64 encoding
            is_base64 = ';base64' in header
            
            # Validate base64 padding
            if is_base64:
                # Add missing padding if necessary
                padding = len(data) % 4
                if padding:
                    data += '=' * (4 - padding)
                
                content_bytes = base64.b64decode(data)
            else:
                content_bytes = data.encode('utf-8')

            return content_bytes, mime_type, 'data_uri'
        except Exception as e:
            raise ValueError(f"Invalid data URI: {str(e)}")

    # Check if it's a URL
    elif content_source.startswith(('http://', 'https://')):
        try:
            # Create SSL context with proper configuration
            ssl_context = ssl.create_default_context()
            with httpx.Client(timeout=30, verify=ssl_context) as client:
                response = client.get(content_source)
                response.raise_for_status()
                content_bytes = response.content
                content_type = response.headers.get('content-type', '')
                return content_bytes, content_type, 'url'
        except httpx.RequestError as e:
            raise ValueError(f"HTTP request failed: {str(e)}")

    # Assume it's a local file path
    else:
        try:
            if not os.path.exists(content_source):
                raise FileNotFoundError(f"File not found: {content_source}")
                
            with open(content_source, 'rb') as f:
                content_bytes = f.read()

            # Get MIME type from file extension
            mime_type, _ = mimetypes.guess_type(content_source)
            if not mime_type:
                # Use python-magic to detect MIME type if we can't guess it from extension
                mime = magic.Magic(mime=True)
                mime_type = mime.from_buffer(content_bytes[:2048])

            return content_bytes, mime_type or '', 'file'
        except Exception as e:
            raise ValueError(f"Failed to read file: {str(e)}")


def convert_with_markitdown(content_bytes: bytes, content_type: str, explicit_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert content to Markdown using MarkItDown library.

    Args:
        content_bytes: The binary content to convert
        content_type: The detected content type
        explicit_type: Optional explicitly specified content type

    Returns:
        A dictionary containing the converted Markdown and metadata

    Raises:
        ValueError: If the content type is unsupported or conversion fails
    """
    # Determine which content type to use
    use_type = explicit_type or content_type

    # Validate content type
    if use_type not in SUPPORTED_CONTENT_TYPES:
        supported_types = ', '.join(SUPPORTED_CONTENT_TYPES.keys())
        raise ValueError(f"Unsupported content type: {use_type}. Supported types are: {supported_types}")

    try:
        # Create a stream info object with proper kwargs handling
        stream_info = StreamInfo(
            name="converted_document",
            mime_type=use_type,
            ext=SUPPORTED_CONTENT_TYPES[use_type]
        )

        # Create a BytesIO stream from content bytes
        file_stream = BytesIO(content_bytes)

        # Initialize MarkItDown converter
        md = MarkItDown(enable_plugins=True)

        # Perform conversion
        result = md.convert(file_stream, stream_info)

        # Return results as dictionary
        return {
            "markdown": result.text_content,
            "metadata": {
                "source_type": use_type,
                "conversion_timestamp": result.conversion_date.isoformat() if result.conversion_date else None,
                "original_stats": {
                    "size_bytes": len(content_bytes),
                    "page_count": result.page_count,
                    "word_count": result.word_count
                },
                "detected_mime_type": content_type,
                "used_explicit_type": bool(explicit_type)
            }
        }
    except Exception as e:
        raise ValueError(f"Conversion failed: {str(e)}")


def validate_input(content_source: str, content_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate input parameters and fetch content for conversion.

    Args:
        content_source: URI or path specifying the content location
        content_type: Optional explicit content type

    Returns:
        A dictionary containing validated content and type information

    Raises:
        ValueError: If input validation or content fetching fails
    """
    # Validate content_source
    if not content_source or not isinstance(content_source, str):
        raise ValueError("content_source must be a non-empty string")

    # Fetch content
    try:
        content_bytes, detected_type, source_type = fetch_content(content_source)
    except Exception as e:
        raise ValueError(f"Failed to fetch content: {str(e)}")

    # Validate content type
    if content_type:
        if content_type not in SUPPORTED_CONTENT_TYPES:
            supported_types = ', '.join(SUPPORTED_CONTENT_TYPES.keys())
            raise ValueError(f"Unsupported content type: {content_type}. Supported types are: {supported_types}")
    else:
        # Auto-detect content type if not provided
        content_type = detected_type

        # If auto-detection still fails, try using python-magic on the content
        if not content_type:
            mime = magic.Magic(mime=True)
            content_type = mime.from_buffer(content_bytes[:2048])

    if not content_type or content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValueError("Could not determine or validate content type. Please provide an explicit content_type.")

    return {
        "content_bytes": content_bytes,
        "content_type": content_type,
        "detected_type": detected_type,
        "source_type": source_type
    }


@mcp.tool()
def convert_to_markdown(content_source: str, content_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Converts various content sources to structured Markdown format while preserving original structure elements.

    Args:
        content_source: URI or path specifying the content location. Supports:
            * HTTP/HTTPS URLs (e.g., "https://example.com/page.html")
            * File system paths (e.g., "/documents/report.docx")
            * Data URIs (e.g., "data:text/html;base64,...")
        content_type: Optional explicitly specified content type when automatic detection fails. Supported types:
            * "text/html"
            * "application/pdf"
            * "application/vnd.openxmlformats-officedocument.wordprocessingml.document" (DOCX)
            * "application/vnd.openxmlformats-officedocument.presentationml.presentation" (PPTX)
            * "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" (XLSX)

    Returns:
        A dictionary containing:
            * "markdown": Structured Markdown content preserving:
                * Heading hierarchy (# H1, ## H2, etc.)
                * Ordered and unordered lists
                * Hyperlinks ([text](url))
                * Tables (pipe-style)
                * Code blocks (fenced)
            * "metadata": Additional information including:
                * Source type detected
                * Conversion timestamp
                * Original content statistics (word count, page count, etc.)

    Raises:
        ValueError: If input validation, content fetching, or conversion fails
        FileNotFoundError: If a local file path is provided but the file doesn't exist
        httpx.HTTPStatusError: If an HTTP request fails

    Example:
        >>> convert_to_markdown(content_source="https://example.com/page.html")
        {
            "markdown": "# Example Page\\nThis is an example HTML page that has been converted to Markdown.",
            "metadata": {
                "source_type": "text/html",
                "conversion_timestamp": "2025-04-05T12:34:56.789Z",
                "original_stats": {
                    "size_bytes": 12345,
                    "page_count": 1,
                    "word_count": 250
                },
                "detected_mime_type": "text/html",
                "used_explicit_type": False
            }
        }
    """
    try:
        # Validate input and fetch content
        validation_result = validate_input(content_source, content_type)

        # Convert content to markdown
        conversion_result = convert_with_markitdown(
            validation_result["content_bytes"],
            validation_result["content_type"],
            content_type  # Use explicit type if provided
        )

        return conversion_result
    except Exception as e:
        # Log error and re-raise
        print(f"Error in convert_to_markdown: {str(e)}")
        raise


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8-sig')
    mcp.run()