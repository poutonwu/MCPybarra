# mcp_content_to_markdown_conver

## Overview

The `mcp_content_to_markdown_conver` is an MCP (Model Context Protocol) server that provides a tool for converting content from various sources—such as HTTP/S webpages, local HTML files, or Data URIs—into structured Markdown format. This server enables seamless integration with LLMs and tools that consume Markdown-formatted content.

## Installation

To install the required dependencies, ensure you have Python 3.10+ installed, then run:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following packages:

```
mcp[cli]
requests
markdownify
```

## Running the Server

To start the server using the default `stdio` transport protocol, run:

```bash
python mcp_content_to_markdown_conver.py
```

Replace `mcp_content_to_markdown_conver.py` with the actual filename of your server script.

## Available Tools

### `convert_to_markdown`

**Description:**  
Converts content from various sources into structured Markdown. Supported sources include:

- **HTTP/S URLs**: e.g., `"https://example.com"`
- **Local file paths**: e.g., `"./my_document.html"`
- **Data URIs**: e.g., `"data:text/html;base64,PGgxPlRlc3Q8L2gxPg=="`

**Function Signature:**

```python
async def convert_to_markdown(source: str) -> str
```

**Parameters:**

- `source`: A string representing the source of HTML or plain text content to be converted.

**Returns:**

A string containing the converted Markdown content.

**Raises:**

- `ValueError`: If the source is invalid, empty, or unsupported.
- `requests.exceptions.RequestException`: If there's a network error when fetching content from a URL.

**Example Usage:**

```python
await convert_to_markdown("https://example.com")
await convert_to_markdown("./sample.html")
await convert_to_markdown("data:text/html;base64,PGgxPlRlc3Q8L2gxPg==")
```