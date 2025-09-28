# mcp_opencv_image_processing

## Overview
This MCP server provides a set of image processing tools using OpenCV. It enables external applications and LLMs to perform common image manipulation tasks such as resizing, cropping, filtering, edge detection, and basic image analysis.

## Installation
First, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes:
```
mcp[cli]
opencv-python
```

## Running the Server
To start the server, run the Python script from the command line:

```bash
python mcp_opencv_image_processing.py
```

By default, the server will run using the standard input/output (stdio) transport protocol.

## Available Tools

### `save_image_tool(image_path: str, output_path: str)`
Saves an image to the file system in the desired format.

**Example**:  
```python
save_image_tool("input.jpg", "output.png")
```

---

### `resize_image_tool(image_path: str, width: int, height: int)`
Resizes the image to specific dimensions.

**Example**:  
```python
resize_image_tool("input.jpg", 800, 600)
```

---

### `crop_image_tool(image_path: str, x: int, y: int, width: int, height: int)`
Crops a specific rectangular region from the image.

**Example**:  
```python
crop_image_tool("input.jpg", 10, 10, 100, 100)
```

---

### `get_image_stats_tool(image_path: str)`
Retrieves basic statistics about the image, including dimensions and pixel intensity histograms.

**Example**:  
```python
get_image_stats_tool("input.jpg")
```

---

### `apply_filter_tool(image_path: str, filter_type: str, kernel_size: int)`
Applies a specified filter to the image (e.g., Gaussian blur, median blur).

**Example**:  
```python
apply_filter_tool("input.jpg", "gaussian", 5)
```

---

### `detect_edges_tool(image_path: str, threshold1: float, threshold2: float)`
Detects edges in the image using OpenCV's Canny edge detection algorithm.

**Example**:  
```python
detect_edges_tool("input.jpg", 50.0, 150.0)
```

---

### `apply_threshold_tool(image_path: str, threshold_value: float, max_value: float)`
Applies a thresholding operation to the image.

**Example**:  
```python
apply_threshold_tool("input.jpg", 127.0, 255.0)
```

---

### `detect_contours_tool(image_path: str)`
Detects contours in the image.

**Example**:  
```python
detect_contours_tool("thresholded_image.jpg")
```

---

### `find_shapes_tool(image_path: str)`
Identifies and classifies simple geometric shapes (e.g., circles, squares) in the image.

**Example**:  
```python
find_shapes_tool("thresholded_image.jpg")
```