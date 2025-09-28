# MCP Server Implementation Plan: OpenCV Image Processor

This document outlines the implementation plan for an MCP server that provides image processing and computer vision functionalities using the OpenCV library.

## 1. Server Overview

The MCP server, named `opencv_image_processor`, will provide a suite of tools for image manipulation and analysis. It is designed to be integrated with systems that require computer vision capabilities. The server will offer basic functionalities such as saving, resizing, and cropping images, as well as advanced features including applying filters, edge and contour detection, thresholding, and shape recognition. All image data will be handled as Base64 encoded strings to ensure compatibility with the JSON-based MCP protocol.

## 2. File to be Generated

All the server logic, including tool definitions and dependencies, will be contained within a single Python file:
`mcp_opencv_server.py`

## 3. Dependencies

The following third-party Python libraries are required for this implementation:
- `mcp-sdk`: For building the core MCP server.
- `opencv-python`: The core library for all image processing functions.
- `numpy`: A dependency of OpenCV, used for handling image data as numerical arrays.

## 4. MCP Tools Plan

### Basic Image Operations

---

#### **Tool 1: `save_image_tool`**

*   **Function Name**: `save_image`
*   **Description**: Decodes a Base64 encoded image string and saves it as a file to a specified path on the server.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the image to be saved.
    *   `file_path` (str): The full path, including the filename and extension (e.g., `/path/to/save/image.png`), where the image will be saved.
*   **Return Value**:
    *   (dict): A dictionary containing a `status` key with a success or failure message. Example: `{"status": "Image saved successfully to /path/to/save/image.png"}`.

---

#### **Tool 2: `resize_image_tool`**

*   **Function Name**: `resize_image`
*   **Description**: Resizes an image to a specified width and height.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source image.
    *   `width` (int): The target width for the resized image in pixels.
    *   `height` (int): The target height for the resized image in pixels.
*   **Return Value**:
    *   (dict): A dictionary containing the `image_data` key with the Base64 encoded string of the resized image. Example: `{"image_data": "iVBORw0KGgoAAAANSUhEUgA..."}`.

---

#### **Tool 3: `crop_image_tool`**

*   **Function Name**: `crop_image`
*   **Description**: Crops a rectangular region from an image based on specified coordinates.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source image.
    *   `x` (int): The x-coordinate of the top-left corner of the crop area.
    *   `y` (int): The y-coordinate of the top-left corner of the crop area.
    *   `width` (int): The width of the crop area.
    *   `height` (int): The height of the crop area.
*   **Return Value**:
    *   (dict): A dictionary containing the `image_data` key with the Base64 encoded string of the cropped image.

---

#### **Tool 4: `get_image_stats_tool`**

*   **Function Name**: `get_image_stats`
*   **Description**: Retrieves basic statistics from an image, such as dimensions, number of channels, and mean pixel values.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source image.
*   **Return Value**:
    *   (dict): A dictionary containing image statistics. Example: `{"height": 480, "width": 640, "channels": 3, "mean_pixel_value": [120.5, 130.2, 145.8]}`.

### Advanced Image Processing

---

#### **Tool 5: `apply_filter_tool`**

*   **Function Name**: `apply_filter`
*   **Description**: Applies a specified filter to an image.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source image.
    *   `filter_type` (str): The type of filter to apply. Supported values: `'blur'`, `'grayscale'`, `'sharpen'`.
*   **Return Value**:
    *   (dict): A dictionary containing the `image_data` key with the Base64 encoded string of the filtered image.

---

#### **Tool 6: `detect_edges_tool`**

*   **Function Name**: `detect_edges`
*   **Description**: Performs Canny edge detection on an image.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source image.
    *   `low_threshold` (int): The lower threshold for the Canny edge detector.
    *   `high_threshold` (int): The upper threshold for the Canny edge detector.
*   **Return Value**:
    *   (dict): A dictionary containing the `image_data` key with the Base64 encoded string of the resulting edge map (a binary image).

---

#### **Tool 7: `apply_threshold_tool`**

*   **Function Name**: `apply_threshold`
*   **Description**: Applies a fixed-level threshold to a grayscale image, converting it to a binary image.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source grayscale image.
    *   `threshold_value` (int): The pixel value used as the threshold (0-255).
    *   `max_value` (int): The value assigned to pixels exceeding the threshold (typically 255).
*   **Return Value**:
    *   (dict): A dictionary containing the `image_data` key with the Base64 encoded string of the binary thresholded image.

---

#### **Tool 8: `detect_contours_tool`**

*   **Function Name**: `detect_contours`
*   **Description**: Detects contours in a binary image.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source binary image (e.g., from edge detection or thresholding).
*   **Return Value**:
    *   (dict): A dictionary containing `count` (the number of contours found) and `contours` (a list of contours, where each contour is a list of points). Example: `{"count": 5, "contours": [[[10,10]], [[20,20]], ...]}`.

---

#### **Tool 9: `find_shapes_tool`**

*   **Function Name**: `find_shapes`
*   **Description**: Detects and identifies simple geometric shapes (triangles, rectangles, circles) in an image.
*   **Parameters**:
    *   `image_data` (str): The Base64 encoded string of the source image.
*   **Return Value**:
    *   (dict): A dictionary containing a `shapes` key. The value is a list of dictionaries, each describing a found shape, its type, and its center coordinates. Example: `{"shapes": [{"type": "rectangle", "center": [150, 200]}, {"type": "circle", "center": [300, 250]}]}`.