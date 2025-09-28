# MCP Server Implementation Plan: OpenCV Image Processor

This document outlines the implementation plan for an MCP server designed to provide a suite of image processing and computer vision tools using the OpenCV library.

## 1. Server Overview

The server will act as an MCP interface to a set of OpenCV-powered tools. It will allow clients to perform both basic and advanced image manipulation tasks. The server will expose functionalities such as saving, resizing, and cropping images, as well as more complex operations like applying filters, detecting edges, performing thresholding, and identifying contours and shapes within an image. Each tool will operate on image files by reading from a specified input path and writing the result to a designated output path.

## 2. File to be Generated

All the server logic, including tool definitions and the MCP server setup, will be contained within a single Python file named `mcp_opencv_server.py`.

## 3. Dependencies

The following third-party Python libraries are required for this project:

*   `mcp-sdk`: For creating the MCP server.
*   `opencv-python`: The core library for all image processing functionalities.
*   `numpy`: A dependency of OpenCV, used for handling image data as arrays.

These can be installed using pip:
```bash
pip install "mcp-sdk[cli]" opencv-python numpy
```

## 4. MCP Tools Plan

Here is a detailed plan for each MCP tool to be implemented.

---

### **Tool: `save_image`**

*   **Function Name**: `save_image`
*   **Description**: Saves an image from a source path to a destination path. This tool is useful for creating copies or changing the format of an image file. It essentially performs a file copy operation, ensuring the source image is valid.
*   **Parameters**:
    *   `source_path` (str): The full path to the existing image file that needs to be saved.
    *   `destination_path` (str): The full path where the new image file will be saved.
*   **Return Value**: (str) A confirmation message indicating the path where the image was successfully saved.

---

### **Tool: `resize_image`**

*   **Function Name**: `resize_image`
*   **Description**: Changes the dimensions of an image to a specified width and height.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file.
    *   `output_path` (str): The path to save the resized image file.
    *   `width` (int): The target width for the resized image in pixels.
    *   `height` (int): The target height for the resized image in pixels.
*   **Return Value**: (str) A confirmation message indicating the path of the newly created resized image.

---

### **Tool: `crop_image`**

*   **Function Name**: `crop_image`
*   **Description**: Extracts a rectangular region from an image. The region is defined by a starting coordinate (top-left corner) and its dimensions.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file.
    *   `output_path` (str): The path to save the cropped image file.
    *   `x` (int): The x-coordinate of the top-left corner of the crop area.
    *   `y` (int): The y-coordinate of the top-left corner of the crop area.
    *   `width` (int): The width of the crop rectangle.
    *   `height` (int): The height of the crop rectangle.
*   **Return Value**: (str) A confirmation message indicating the path of the newly created cropped image.

---

### **Tool: `get_image_stats`**

*   **Function Name**: `get_image_stats`
*   **Description**: Retrieves basic statistical information about an image, such as its dimensions and number of color channels.
*   **Parameters**:
    *   `input_path` (str): The path to the image file to be analyzed.
*   **Return Value**: (dict) A dictionary containing the image's statistics: `{'width': int, 'height': int, 'channels': int}`.

---

### **Tool: `apply_filter`**

*   **Function Name**: `apply_filter`
*   **Description**: Applies a pre-defined filter to an image. Supported filters are 'blur', 'grayscale', and 'sharpen'.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file.
    *   `output_path` (str): The path to save the filtered image file.
    *   `filter_type` (str): The type of filter to apply. Must be one of 'blur', 'grayscale', or 'sharpen'.
*   **Return Value**: (str) A confirmation message indicating the path of the newly created filtered image.

---

### **Tool: `detect_edges`**

*   **Function Name**: `detect_edges`
*   **Description**: Detects and highlights edges in an image using the Canny edge detection algorithm.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file.
    *   `output_path` (str): The path to save the resulting edge-detected image.
    *   `threshold1` (float): The first (lower) threshold for the hysteresis procedure in the Canny algorithm.
    *   `threshold2` (float): The second (higher) threshold for the hysteresis procedure in the Canny algorithm.
*   **Return Value**: (str) A confirmation message indicating the path of the newly created edge-map image.

---

### **Tool: `apply_threshold`**

*   **Function Name**: `apply_threshold`
*   **Description**: Applies a fixed-level binary threshold to a grayscale image. Pixels with intensity higher than the threshold are set to a maximum value, and others are set to zero.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file (will be converted to grayscale for processing).
    *   `output_path` (str): The path to save the thresholded image.
    *   `threshold_value` (float): The pixel intensity value used as the threshold.
    *   `max_value` (float): The value assigned to pixels that exceed the threshold. Typically 255 for white.
*   **Return Value**: (str) A confirmation message indicating the path of the newly created thresholded image.

---

### **Tool: `detect_contours`**

*   **Function Name**: `detect_contours`
*   **Description**: Finds the contours of objects in a binary image and draws them onto a new image.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file.
    *   `output_path` (str): The path to save the image with contours drawn on it.
*   **Return Value**: (dict) A dictionary containing a confirmation message and the number of contours found: `{'message': str, 'contours_found': int}`.

---

### **Tool: `find_shapes`**

*   **Function Name**: `find_shapes`
*   **Description**: A simplified shape detection tool that identifies and counts circles and rectangles in an image. It draws the identified shapes onto the output image.
*   **Parameters**:
    *   `input_path` (str): The path to the source image file.
    *   `output_path` (str): The path to save the image with detected shapes drawn on it.
*   **Return Value**: (dict) A dictionary containing counts of detected shapes: `{'message': str, 'circles_found': int, 'rectangles_found': int}`.