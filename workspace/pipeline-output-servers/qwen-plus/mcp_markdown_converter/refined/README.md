# mcp_markdown_converter

A Model Context Protocol (MCP) server that converts various content formats to structured Markdown while preserving document structure and metadata.

## Overview

The `mcp_markdown_converter` server provides a tool for converting documents from multiple formats—including HTML, PDF, DOCX, PPTX, and XLSX—to clean, structured Markdown. It supports content from URLs, local files, and data URIs, automatically detecting or accepting explicit content types, and returns both the converted Markdown and metadata about the original document.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

Requirements include:
- `mcp[cli]`
- `httpx`
- `python-magic`
- `markitdown`

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_markdown_converter.py
```

By default, the server will run using the `stdio` transport protocol.

## Available Tools

### `convert_to_markdown`

Converts various content sources to structured Markdown format while preserving original structure elements.

#### Description

This tool converts HTML, PDF, DOCX, PPTX, and XLSX files into structured Markdown. It supports content from HTTP/HTTPS URLs, local file paths, and base64-encoded data URIs. The output includes both the Markdown content and metadata such as source type, conversion timestamp, and document statistics.

#### Args

- **`content_source`** (str): URI or path specifying the content location. Supports:
  - HTTP/HTTPS URLs (e.g., `"https://example.com/page.html"`)
  - File system paths (e.g., `"/documents/report.docx"`)
  - Data URIs (e.g., `"data:text/html;base64,..."`)
  
- **`content_type`** (Optional[str]): Explicitly specified content type if automatic detection fails. Supported types:
  - `"text/html"`
  - `"application/pdf"`
  - `"application/vnd.openxmlformats-officedocument.wordprocessingml.document"` (DOCX)
  - `"application/vnd.openxmlformats-officedocument.presentationml.presentation"` (PPTX)
  - `"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"` (XLSX)

#### Returns

A dictionary containing:
- `"markdown"`: Structured Markdown content preserving headings, lists, links, tables, and code blocks.
- `"metadata"`: Additional information including:
  - Source type detected
  - Conversion timestamp
  - Original content statistics (size, word count, page count)

#### Raises

- `ValueError`: If input validation, content fetching, or conversion fails
- `FileNotFoundError`: If a local file path is provided but the file doesn't exist
- `httpx.HTTPStatusError`: If an HTTP request fails

#### Example

```python
convert_to_markdown(content_source="https://example.com/page.html")
```