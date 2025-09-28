# mcp_markdown_converter

## Overview

The `mcp_markdown_converter` is a Model Context Protocol (MCP) server that provides functionality to convert various types of content into structured Markdown format. It supports conversion from HTTP/HTTPS webpages, local files, and data URIs while preserving structural elements such as headings, lists, links, and tables.

This server uses the `FastMCP` interface to expose tools for integration with LLMs and external applications.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed.

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following packages:

```
mcp[cli]
httpx
markitdown
beautifulsoup4
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_markdown_converter.py
```

This will launch the MCP server using the default `stdio` transport protocol.

---

## Available Tools

### `convert_to_markdown`

Converts various types of content (HTTP/HTTPS webpages, local files, and data URIs) into structured Markdown format. Preserves structural elements such as headings, lists, links, and tables.

#### Parameters:

- **content_url** (`str`): The URL or path to the content that needs to be converted.
- **content_type** (`str`): The type of content being provided. Must be one of: `"http"`, `"https"`, `"file"`, or `"data_uri"`.

#### Returns:

A dictionary containing the `'result'` key with the content converted into Markdown format.

#### Raises:

- `ValueError`: If the content type is invalid or if there's an error during conversion.
- `httpx.HTTPStatusError`: If fetching HTTP/HTTPS content fails.
- `FileNotFoundError`: If the specified file does not exist or cannot be read.
- `UnicodeDecodeError`: If the file content cannot be decoded using UTF-8.

#### Example:

```python
convert_to_markdown(content_url="https://example.com", content_type="http")
convert_to_markdown(content_url="/path/to/local/file.html", content_type="file")
convert_to_markdown(content_url="data:text/plain;base64,SGVsbG8sIFdvcmxkIQ==", content_type="data_uri")
```