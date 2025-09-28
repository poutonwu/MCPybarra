# mcp_opencv_image_processor

## Overview

This is an MCP (Model Context Protocol) server that provides a set of tools for image processing using OpenCV. The server enables external systems, including large language models (LLMs), to interact with common image manipulation tasks such as saving, resizing, cropping, filtering, and analyzing images.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
opencv-python
numpy
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_opencv_image_processor.py
```

By default, the server communicates over standard input/output (stdio).

## Available Tools

Below is a list of available tools provided by this MCP server:

### 1. `save_image_tool`
Saves raw image data in bytes to a specified file path.

**Args:**
- `image_path`: Path where the image will be saved.
- `image_data`: Image data in bytes.

**Returns:**  
`True` if the image was saved successfully, `False` otherwise.

---

### 2. `resize_image_tool`
Resizes an image to specified dimensions.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the resized image.
- `width`: Target width in pixels.
- `height`: Target height in pixels.

**Returns:**  
`True` if resizing was successful, `False` otherwise.

---

### 3. `crop_image_tool`
Crops a region from an image.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the cropped image.
- `x`: X-coordinate of the top-left corner of the crop region.
- `y`: Y-coordinate of the top-left corner of the crop region.
- `width`: Width of the crop region.
- `height`: Height of the crop region.

**Returns:**  
`True` if cropping was successful, `False` otherwise.

---

### 4. `get_image_stats_tool`
Retrieves basic statistics about an image.

**Args:**
- `image_path`: Path to the input image.

**Returns:**  
A dictionary containing:
- `width`: Image width.
- `height`: Image height.
- `channels`: Number of color channels.
- `dtype`: Data type of the image.

---

### 5. `apply_filter_tool`
Applies a filter (e.g., blur or sharpen) to an image.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the filtered image.
- `filter_type`: Type of filter (`"blur"` or `"sharpen"`).
- `kernel_size`: Kernel size for the filter (must be odd for blur).

**Returns:**  
`True` if filtering was successful, `False` otherwise.

---

### 6. `detect_edges_tool`
Detects edges in an image using Canny edge detection.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the edge-detected image.
- `threshold1`: First threshold for hysteresis procedure (default: 100).
- `threshold2`: Second threshold for hysteresis procedure (default: 200).

**Returns:**  
`True` if edge detection was successful, `False` otherwise.

---

### 7. `apply_threshold_tool`
Applies binary or adaptive thresholding to an image.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the thresholded image.
- `threshold_type`: Type of thresholding (`"binary"` or `"adaptive"`).
- `threshold_value`: Threshold value (used for binary thresholding).

**Returns:**  
`True` if thresholding was successful, `False` otherwise.

---

### 8. `detect_contours_tool`
Detects contours in an image.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the contour-detected image.

**Returns:**  
A list of detected contours.

---

### 9. `find_shapes_tool`
Identifies shapes (e.g., circles, rectangles, triangles) in an image.

**Args:**
- `input_path`: Path to the input image.
- `output_path`: Path to save the shape-detected image.

**Returns:**  
A list of detected shapes with their properties.