# mcp_opencv_image_toolkit

## Overview

`mcp_opencv_image_toolkit` is an MCP (Model Context Protocol) server that provides a set of tools for image processing using OpenCV. It enables external systems, including large language models (LLMs), to interact with and manipulate images through a standardized interface.

This toolkit supports common operations such as resizing, cropping, filtering, edge detection, shape recognition, and more — all via Base64-encoded image data.

---

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your environment includes Python 3.10 or later and the following libraries:

- `opencv-python`
- `numpy`
- `mcp[cli]`

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_opencv_image_toolkit.py
```

This will launch the MCP server using the default `stdio` transport protocol.

---

## Available Tools

Below is a list of available tools provided by the server, along with a brief description extracted from their docstrings.

### 1. `save_image`

**Description:** Decodes a Base64-encoded image string and saves it to a specified file path.

**Arguments:**
- `image_data`: Base64-encoded image string.
- `file_path`: Path where the image should be saved (e.g., `'output/image.png'`).

---

### 2. `resize_image`

**Description:** Resizes an image to specified dimensions.

**Arguments:**
- `image_data`: Base64-encoded image string.
- `width`: Target width in pixels.
- `height`: Target height in pixels.

---

### 3. `crop_image`

**Description:** Crops a rectangular area from an image.

**Arguments:**
- `image_data`: Base64-encoded image string.
- `x`, `y`: Top-left corner coordinates of the crop area.
- `width`, `height`: Dimensions of the crop area.

---

### 4. `get_image_stats`

**Description:** Retrieves basic statistics about an image (e.g., size, color channels, average pixel values).

**Arguments:**
- `image_data`: Base64-encoded image string.

---

### 5. `apply_filter`

**Description:** Applies a filter to an image. Supported filters: `blur`, `grayscale`, `sharpen`.

**Arguments:**
- `image_data`: Base64-encoded image string.
- `filter_type`: Type of filter to apply.

---

### 6. `detect_edges`

**Description:** Detects edges in an image using the Canny edge detection algorithm.

**Arguments:**
- `image_data`: Base64-encoded image string.
- `low_threshold`: Lower threshold for edge detection.
- `high_threshold`: Upper threshold for edge detection.

---

### 7. `apply_threshold`

**Description:** Converts a grayscale image into a binary image using a fixed threshold.

**Arguments:**
- `image_data`: Base64-encoded image string.
- `threshold_value`: Pixel value used as the threshold.
- `max_value`: Value assigned to pixels exceeding the threshold.

---

### 8. `detect_contours`

**Description:** Detects contours in a binary image.

**Arguments:**
- `image_data`: Base64-encoded binary image string.

---

### 9. `find_shapes`

**Description:** Identifies simple geometric shapes (triangle, square, rectangle, circle) in an image.

**Arguments:**
- `image_data`: Base64-encoded image string.

---