# mcp_computer_vision_toolkit

## Overview

The `mcp_computer_vision_toolkit` is a Model Context Protocol (MCP) server that provides a suite of computer vision tools for image manipulation and analysis. It enables integration with large language models (LLMs) to perform common image processing tasks such as resizing, cropping, filtering, edge detection, and more.

This server supports the MCP protocol via standard input/output (stdio), making it compatible with LLM tooling frameworks that support MCP integration.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

If you don't already have a `requirements.txt`, it should include at least the following:

```
mcp[cli]
opencv-python
numpy
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_computer_vision_toolkit.py
```

Ensure UTF-8 encoding is supported in your environment for correct handling of file paths and output.

---

## Available Tools

Each tool is designed to be called by an LLM using the MCP protocol. Below is a list of available tools and their functionality:

### `save_image(source_path: str, destination_path: str)`
Saves an image from a source path to a new destination path. Useful for copying or converting image formats.

### `resize_image(input_path: str, output_path: str, width: int, height: int)`
Resizes an image to the specified dimensions and saves the result.

### `crop_image(input_path: str, output_path: str, x: int, y: int, width: int, height: int)`
Crops a rectangular region from the input image and saves the cropped section.

### `get_image_stats(input_path: str)`
Returns basic statistics about the image including width, height, and number of color channels.

### `apply_filter(input_path: str, output_path: str, filter_type: str)`
Applies a filter to the image. Supported filters are `'blur'`, `'grayscale'`, and `'sharpen'`.

### `detect_edges(input_path: str, output_path: str, threshold1: float, threshold2: float)`
Detects edges in the image using Canny edge detection and saves the resulting edge map.

### `apply_threshold(input_path: str, output_path: str, threshold_value: float, max_value: float)`
Applies a binary threshold to a grayscale version of the image and saves the result.

### `detect_contours(input_path: str, output_path: str)`
Finds contours in a binary version of the image and draws them on the output image.

### `find_shapes(input_path: str, output_path: str)`
Detects and counts circles and rectangles in the image and highlights them in the output.

---