# MCP Tools Plan

This section details the design of the single MCP tool required to fulfill the user's request.

### **Tool: `convert_to_markdown`**

*   **Function Name**: `convert_to_markdown`
*   **Description**: Converts content from various sources (HTTP/S webpages, local file paths, or Data URIs) into structured Markdown. The tool automatically detects the source type and processes it accordingly. It preserves structural elements like headings, lists, tables, and links.
*   **Parameters**:
    *   `source` (string, required): The source of the content to be converted. This can be:
        *   An HTTP or HTTPS URL (e.g., `"https://example.com"`).
        *   A local file path (e.g., `"./my_document.html"`).
        *   A Data URI (e.g., `"data:text/html;base64,PGgxPlRlc3Q8L2gxPg=="`).
*   **Return Value**:
    *   A string containing the content converted to structured Markdown. In case of an error (e.g., invalid URL, file not found), an exception with a descriptive message will be raised.

# Server Overview

The MCP server, named `markdown_converter`, is designed to provide a single, powerful tool: `convert_to_markdown`. Its sole mission is to accept a string identifying a content source—be it a live webpage, a local file, or a Data URI—and convert that content into well-structured Markdown format. The server leverages the `markdownify` library to ensure that important structural elements like headings, lists, tables, and links are accurately preserved in the final output. The server will be accessible via the standard MCP transport protocols (stdio, sse, http).

# File to be Generated

All the server logic, including the tool definition and dependencies, will be contained within a single Python file.

*   **Filename**: `mcp_markdown_converter.py`

# Dependencies

The following third-party Python libraries are required for the server to function correctly. These should be installed via pip.

*   `mcp`: The core SDK for creating the FastMCP server.
*   `markdownify`: To handle the conversion from HTML to Markdown.
*   `requests`: To fetch content from HTTP and HTTPS URLs.
*   `beautifulsoup4`: A dependency for `markdownify` and useful for parsing HTML content.