# mcp_markdown_converter

## Overview

The `mcp_markdown_converter` is a Model Context Protocol (MCP) server that provides a tool for converting various content formats—such as web pages, local files, and data URIs—into structured Markdown format. This server enables seamless integration with LLM applications by exposing a standardized interface for content conversion.

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10 or later installed.
2. Install the MCP SDK and `httpx` library:
   ```bash
   pip install mcp[cli] httpx
   ```
3. Install any additional dependencies listed in your `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

To run the server, execute the following command from the terminal:

```bash
python mcp_markdown_converter.py
```

By default, the server uses the `stdio` transport protocol. You can modify the `run()` method in the code to use other transports like `"sse"` or `"http"` if needed.

## Available Tools

### `convert_to_markdown(source: str, source_type: str) -> str`

Converts content from a specified source into structured Markdown format. Supports three types of sources:

- **URL**: Fetches and converts content from an HTTP/HTTPS webpage.
- **File**: Converts the contents of a local text-based file.
- **Data URI**: Decodes and converts a base64-encoded data URI.

#### Parameters:
- `source`: The input source (URL, file path, or data URI).
- `source_type`: Specifies the type of the source (`"url"`, `"file"`, or `"data_uri"`).

#### Returns:
A string containing the Markdown representation of the input content.

#### Raises:
- `ValueError`: If the source type is invalid or the data URI format is incorrect.
- `FileNotFoundError`: If a specified file does not exist.
- `httpx.HTTPStatusError`: If a URL request fails.
- `Exception`: For general decoding or processing errors.

#### Example:
```python
convert_to_markdown("https://example.com", "url")
```