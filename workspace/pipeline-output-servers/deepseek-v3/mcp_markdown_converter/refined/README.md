# mcp_markdown_converter

## Overview

The `mcp_markdown_converter` is an MCP (Model Context Protocol) server that provides a tool for converting various input formats (such as HTML web pages, local files, and data URIs) into structured Markdown. It supports multiple input sources and allows for optional preservation of original formatting.

This server enables seamless integration with LLMs by exposing a single, well-documented tool that handles complex input types and returns clean, structured Markdown output.

## Installation

Before running the server, ensure you have Python 3.10 or higher installed.

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, make sure to install the required packages manually:

```bash
pip install mcp[cli] httpx
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_markdown_converter.py
```

This will launch the MCP server using the default `stdio` transport protocol.

## Available Tools

### `convert_to_markdown`

Converts various input formats (HTTP/HTTPS web pages, local files, and data URIs) into structured Markdown.

#### Args:
- `input_source`: The source to convert (e.g., `"https://example.com"`, `"file:///path/to/file.html"`, or `"data:text/html,<html>..."`).
- `preserve_structure`: If `True`, retains original formatting (default: `True`).

#### Returns:
A string containing the structured Markdown output.

#### Raises:
- `ValueError`: If the input source is invalid or unsupported.
- `httpx.HTTPStatusError`: If fetching web content fails.
- `FileNotFoundError`: If a local file cannot be found.
- `PermissionError`: If a local file cannot be accessed.