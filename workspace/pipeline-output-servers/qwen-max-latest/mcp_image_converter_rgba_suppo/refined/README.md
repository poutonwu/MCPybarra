# mcp_image_converter_rgba_suppo

## Overview

The `mcp_image_converter_rgba_suppo` is an MCP server that provides image format conversion capabilities. It supports converting images between common formats such as PNG, JPEG, BMP, and GIF, while preserving transparency for RGBA images when converting to compatible formats.

This server uses the Pillow (PIL) library to perform image processing and ensures correct color space conversion when necessary (e.g., converting RGBA images to RGB when saving in non-transparent formats like JPEG).

---

## Installation

Before running the server, ensure you have Python 3.10+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
Pillow
```

---

## Running the Server

To start the server, run the following command:

```bash
python mcp_image_converter_rgba_suppo.py
```

This will launch the MCP server using the default `stdio` transport protocol.

---

## Available Tools

### `convert_image`

Converts images from one format to another (e.g., PNG, JPEG, BMP, GIF), preserving transparency for RGBA images where possible.

#### Description

This tool accepts an input image path, a target output directory, and a desired output format. It converts the image accordingly and saves it to the specified location.

- Automatically handles RGBA to RGB conversion for non-transparent formats.
- Ensures the output directory exists before saving.
- Returns a JSON response indicating success or failure with descriptive messages.

#### Parameters

| Parameter      | Type   | Description |
|----------------|--------|-------------|
| `input_path`   | string | Path to the source image file. |
| `output_path`  | string | Directory path where the converted image will be saved. |
| `output_format` | string | Target image format (e.g., "PNG", "JPEG", "BMP", "GIF"). |

#### Example Usage

```python
convert_image(
    input_path="/path/to/input/image.png",
    output_path="/path/to/output/",
    output_format="JPEG"
)
```

#### Returns

A dictionary containing:
- `"status"`: `"success"` or `"failure"`
- `"message"`: A description of the result or error encountered.