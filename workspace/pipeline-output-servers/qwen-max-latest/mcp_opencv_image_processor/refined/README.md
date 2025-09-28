# mcp_opencv_image_processor

## Overview

`mcp_opencv_image_processor` is an MCP (Model Context Protocol) server that provides a suite of image processing tools powered by OpenCV. It allows large language models (LLMs) to interact with and manipulate image files through a set of well-defined tools.

This server supports operations such as saving, resizing, cropping, filtering, and analyzing images, making it ideal for integrating image processing capabilities into LLM-based applications.

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10 or higher installed.
2. Install the MCP SDK and other dependencies:

```bash
pip install mcp[cli] opencv-python numpy
```

3. If you have a `requirements.txt` file, install dependencies using:

```bash
pip install -r requirements.txt
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_opencv_image_processor.py
```

By default, the server uses the `stdio` transport protocol, which is suitable for local testing and integration with LLM tools.

## Available Tools

Here is a list of available tools provided by the server:

### 1. `save_image_tool`
Saves an image from a source path to a new destination path.

### 2. `resize_image_tool`
Resizes an image to the specified width and height and saves it to a new destination.

### 3. `crop_image_tool`
Crops an image using the specified coordinates and dimensions, then saves the result.

### 4. `get_image_stats_tool`
Retrieves statistical information about an image (e.g., shape, mean, standard deviation).

### 5. `apply_filter_tool`
Applies a filter (e.g., blur or sharpen) to an image and saves the filtered result.

### 6. `detect_edges_tool`
Detects edges in an image using the Canny edge detection algorithm and saves the result.

### 7. `apply_threshold_tool`
Applies a binary threshold to an image and saves the thresholded image.

### 8. `detect_contours_tool`
Detects contours in an image and draws them on the image for visualization.

### 9. `find_shapes_tool`
Detects and highlights shapes in an image by drawing bounding rectangles around them.

Each tool includes detailed parameter descriptions, error handling, and return value documentation to ensure clarity and robustness when used by LLMs or other clients.