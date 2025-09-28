# mcp_image_format_converter

## Overview

The `mcp_image_format_converter` is a Model Context Protocol (MCP) server that provides image format conversion capabilities. It allows users to convert images between common formats such as JPEG, PNG, BMP, and GIF, while ensuring robust input validation, security checks, and handling of special cases like transparency.

This server is built using the `FastMCP` framework from the MCP SDK and follows best practices for functionality, robustness, security, performance, and transparency.

## Installation

To install the required dependencies, ensure you have Python 3.10+ installed and run:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
Pillow==10.4.0
```

## Running the Server

You can start the server by running the Python script directly:

```bash
python mcp_image_format_converter.py
```

By default, the server will use the standard input/output transport (`stdio`). To specify a different transport method (e.g., `sse` or `http`), modify the `mcp.run()` call in the script or pass it as an argument if supported.

## Available Tools

### `convert_image`

Converts an image file from one format to another.

**Description:**  
This tool handles image conversion with support for transparency (RGBA) by converting to RGB when necessary (e.g., for JPEG). It includes strong input validation and path traversal protection.

**Arguments:**
- `source_path`: The absolute or relative path to the source image file.
- `output_dir`: The directory where the converted image will be saved (must exist).
- `target_format`: The desired output image format (e.g., 'JPEG', 'PNG', 'BMP', 'GIF').

**Returns:**
- A JSON string indicating success or failure, including:
  - `"status"`: `"success"` or `"error"`
  - `"message"`: Descriptive message
  - `"output_path"`: Path to the converted image (on success)

**Example Usage:**
```python
convert_image(source_path="images/sample.png", output_dir="images/output", target_format="JPEG")
```

**Error Handling:**
- Raises errors for invalid paths, unsupported formats, corrupted files, or path traversal attempts.
- Returns structured error messages for both expected and unexpected failures.