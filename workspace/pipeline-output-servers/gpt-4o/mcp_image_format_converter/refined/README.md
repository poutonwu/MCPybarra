# mcp_image_format_converter

## Overview

The `mcp_image_format_converter` is an MCP (Model Context Protocol) server that provides image format conversion capabilities. It allows converting images between common formats such as PNG, JPEG, BMP, and GIF while preserving transparency and performing appropriate color space conversions.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
Pillow
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_image_format_converter.py
```

By default, the server communicates via standard input/output (stdio). You can change the transport method using the `.run()` function in the code if needed.

## Available Tools

### `convert_image`

Converts an input image from one format to another (e.g., PNG, JPEG, BMP, GIF), preserving transparency and performing appropriate color space conversion.

#### Parameters:
- **source_path** (str): Path to the source image file.
- **target_format** (str): Desired output format (supported: 'JPEG', 'PNG', 'BMP', 'GIF').
- **output_directory** (str): Directory where the converted image will be saved.

#### Returns:
A JSON string containing:
- **status**: "success" or "failure"
- **message**: A detailed message about the result or error
- **output_path** (optional): The path of the converted image (if successful)

#### Example:
```python
convert_image("input/image.png", "JPEG", "output/")
```