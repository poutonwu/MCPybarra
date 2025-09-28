# mcp_image_format_converter

## Overview

The `mcp_image_format_converter` is an MCP (Model Context Protocol) server that provides a tool for converting image files between different formats such as JPEG, PNG, BMP, and GIF. It enables seamless integration with LLMs by exposing a well-documented function via the MCP protocol.

This server allows users to convert images while ensuring robust input validation, handling edge cases like missing files or incompatible image modes (e.g., RGBA to RGB conversion for JPEG output).

---

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install mcp[cli]
pip install pillow
```

Optionally, you can create a `requirements.txt` file containing:

```
mcp[cli]
pillow
```

Then install using:

```bash
pip install -r requirements.txt
```

---

## Running the Server

To start the server, run the following command in your terminal:

```bash
python mcp_image_format_converter.py
```

Make sure the script file is named `mcp_image_format_converter.py` or adjust the command accordingly.

---

## Available Tools

### `convert_image`

Converts an image file to a specified format and saves it to a given directory.

#### Parameters:
- **input_path**: The path to the input image file (string, required).
- **output_format**: The desired output format (e.g., 'PNG', 'JPEG', 'BMP', 'GIF') (string, required).
- **output_dir**: The directory where the converted image will be saved (string, required).

#### Returns:
A dictionary with keys:
- `'success'`: Boolean indicating whether the conversion was successful.
- `'output_path'`: Path to the converted image file if successful.
- `'error'`: Error message if the conversion failed.

#### Example:
```python
convert_image(input_path="image.jpg", output_format="PNG", output_dir="converted_images")
# Returns: {'success': True, 'output_path': 'converted_images/image.png', 'error': None}
```

#### Raises:
- `ValueError`: For invalid parameters or missing input file.
- `OSError`: For issues reading the input or writing the output.
- `Exception`: For any unexpected errors during conversion.