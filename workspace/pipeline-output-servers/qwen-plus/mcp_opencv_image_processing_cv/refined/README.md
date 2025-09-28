# mcp_opencv_image_processing_cv

## Overview
This server provides a set of image processing tools using OpenCV. It allows clients to perform common image manipulation and analysis tasks such as resizing, cropping, filtering, edge detection, and more.

The server supports Unicode file paths and ensures proper handling of image files across different operating systems.

## Installation
1. Install Python 3.10 or higher
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Where your `requirements.txt` should include:
```
mcp[cli]
opencv-python
numpy
```

## Running the Server
To start the server, run the following command:
```bash
python mcp_opencv_image_processing_cv.py
```

Make sure to replace `mcp_opencv_image_processing_cv.py` with the actual filename containing your server code.

## Available Tools

### save_image_tool
Saves an image file to a specified location.
- Args: `image_path` (str), `output_path` (str)

### resize_image_tool
Resizes an image to specified dimensions.
- Args: `image_path` (str), `width` (int), `height` (int)

### crop_image_tool
Crops a specific region from an image.
- Args: `image_path` (str), `x` (int), `y` (int), `width` (int), `height` (int)

### get_image_stats_tool
Retrieves image statistics including dimensions, color space, and pixel value ranges.
- Args: `image_path` (str)

### apply_filter_tool
Applies various filters to an image (gaussian, median, blur, bilateral).
- Args: `image_path` (str), `filter_type` (str), `kernel_size` (int)

### detect_edges_tool
Detects edges in an image using Canny edge detection.
- Args: `image_path` (str), `method` (str), `threshold1` (int), `threshold2` (int)

### apply_threshold_tool
Performs binary thresholding on an image.
- Args: `image_path` (str), `threshold_value` (int), `max_value` (int)

### detect_contours_tool
Detects contours in an image.
- Args: `image_path` (str), `mode` (str), `method` (str)

### find_shapes_tool
Identifies specific shapes (circles, rectangles, triangles, polygons) in an image.
- Args: `image_path` (str), `shape_type` (str)