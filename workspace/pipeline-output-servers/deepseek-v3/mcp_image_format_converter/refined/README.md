# mcp_image_format_converter

## Overview
The `mcp_image_format_converter` is an MCP (Model Context Protocol) server that provides a tool for converting image files between different formats while preserving transparency and supporting quality settings for lossy formats.

This server enables seamless integration with LLMs by exposing image conversion capabilities through the standardized MCP protocol.

## Installation
Make sure you have Python 3.10+ installed, then install the required dependencies:

```bash
pip install mcp[cli]
pip install pillow
```

You can also use a `requirements.txt` file containing:
```
mcp[cli]
pillow
```

Then install using:
```bash
pip install -r requirements.txt
```

## Running the Server
To run the server, execute the Python script from the command line:

```bash
python mcp_image_format_converter.py
```

By default, the server communicates via standard input/output (stdio), which is suitable for local testing and integration.

## Available Tools

### `convert_image`
Converts an image file from one format to another, handling transparency and color space conversion.

#### Description
This tool allows converting images to popular formats like PNG, JPEG, BMP, and GIF. It supports options to preserve transparency and adjust compression quality for lossy formats.

#### Parameters
- **source_path** (str): Path to the source image file.
- **target_format** (str): Desired output format (e.g., "PNG", "JPEG", "BMP", "GIF").
- **output_dir** (str): Directory where the converted image will be saved.
- **preserve_alpha** (bool, optional): Whether to preserve transparency (default: True).
- **quality** (int, optional): Compression quality for lossy formats like JPEG (default: 95).

#### Returns
A dictionary containing:
- **status**: "success" or "error".
- **message**: Detailed status or error message.
- **output_path**: Path to the converted image file (only on success).

#### Raises
- **ValueError**: For invalid input paths or unsupported formats.