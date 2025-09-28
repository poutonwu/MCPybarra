import sys
import os
import json
import cv2
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("mcp_opencv_image_processing")

@mcp.tool()
def save_image_tool(image_path: str, output_path: str) -> bool:
    """
    Saves an image to the file system in the desired format.

    Args:
        image_path (str): Path to the input image file.
        output_path (str): Path to save the output image file.

    Returns:
        bool: True if the image is successfully saved, otherwise False.

    Example:
        save_image_tool("input.jpg", "output.png")
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        result = cv2.imwrite(output_path, image)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def resize_image_tool(image_path: str, width: int, height: int) -> str:
    """
    Resizes the image to specific dimensions.

    Args:
        image_path (str): Path to the input image file.
        width (int): The new width of the image.
        height (int): The new height of the image.

    Returns:
        str: Path to the resized image file.

    Example:
        resize_image_tool("input.jpg", 800, 600)
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        resized_image = cv2.resize(image, (width, height))
        output_path = "resized_image.jpg"
        cv2.imwrite(output_path, resized_image)
        return output_path
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def crop_image_tool(image_path: str, x: int, y: int, width: int, height: int) -> str:
    """
    Crops a specific rectangular region from the image.

    Args:
        image_path (str): Path to the input image file.
        x (int): The x-coordinate of the top-left corner of the crop box.
        y (int): The y-coordinate of the top-left corner of the crop box.
        width (int): The width of the crop box.
        height (int): The height of the crop box.

    Returns:
        str: Path to the cropped image file.

    Example:
        crop_image_tool("input.jpg", 10, 10, 100, 100)
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        cropped_image = image[y:y+height, x:x+width]
        output_path = "cropped_image.jpg"
        cv2.imwrite(output_path, cropped_image)
        return output_path
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_image_stats_tool(image_path: str) -> str:
    """
    Retrieves basic statistics about the image, including dimensions and pixel intensity histograms.

    Args:
        image_path (str): Path to the input image file.

    Returns:
        str: JSON string containing dimensions and histogram data.

    Example:
        get_image_stats_tool("input.jpg")
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        dimensions = image.shape
        histogram = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten().tolist()
        return json.dumps({"dimensions": dimensions, "histogram": histogram})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def apply_filter_tool(image_path: str, filter_type: str, kernel_size: int) -> str:
    """
    Applies a specified filter to the image (e.g., Gaussian blur, median blur).

    Args:
        image_path (str): Path to the input image file.
        filter_type (str): The type of filter to apply ("gaussian", "median", etc.).
        kernel_size (int): The size of the kernel used for filtering.

    Returns:
        str: Path to the filtered image file.

    Example:
        apply_filter_tool("input.jpg", "gaussian", 5)
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        if filter_type == "gaussian":
            filtered_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        elif filter_type == "median":
            filtered_image = cv2.medianBlur(image, kernel_size)
        else:
            raise ValueError("Unsupported filter type.")
        output_path = "filtered_image.jpg"
        cv2.imwrite(output_path, filtered_image)
        return output_path
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def detect_edges_tool(image_path: str, threshold1: float, threshold2: float) -> str:
    """
    Detects edges in the image using OpenCV's Canny edge detection algorithm.

    Args:
        image_path (str): Path to the input image file.
        threshold1 (float): The first threshold for the hysteresis procedure.
        threshold2 (float): The second threshold for the hysteresis procedure.

    Returns:
        str: Path to the edge-detected image file.

    Example:
        detect_edges_tool("input.jpg", 50.0, 150.0)
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        edges = cv2.Canny(image, threshold1, threshold2)
        output_path = "edges_image.jpg"
        cv2.imwrite(output_path, edges)
        return output_path
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def apply_threshold_tool(image_path: str, threshold_value: float, max_value: float) -> str:
    """
    Applies a thresholding operation to the image.

    Args:
        image_path (str): Path to the input grayscale image file.
        threshold_value (float): The threshold value.
        max_value (float): The maximum value to assign to pixels exceeding the threshold.

    Returns:
        str: Path to the thresholded binary image file.

    Example:
        apply_threshold_tool("input.jpg", 127.0, 255.0)
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        _, thresholded_image = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_BINARY)
        output_path = "thresholded_image.jpg"
        cv2.imwrite(output_path, thresholded_image)
        return output_path
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def detect_contours_tool(image_path: str) -> str:
    """
    Detects contours in the image.

    Args:
        image_path (str): Path to the input binary image file.

    Returns:
        str: JSON string containing a list of contours.

    Example:
        detect_contours_tool("thresholded_image.jpg")
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_list = [contour.tolist() for contour in contours]
        return json.dumps({"contours": contours_list})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def find_shapes_tool(image_path: str) -> str:
    """
    Identifies and classifies simple geometric shapes (e.g., circles, squares) in the image.

    Args:
        image_path (str): Path to the input binary image file.

    Returns:
        str: JSON string containing a list of detected shapes.

    Example:
        find_shapes_tool("thresholded_image.jpg")
    """
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Image could not be loaded from the provided path.")
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        shapes = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
            if len(approx) == 3:
                shape = "triangle"
            elif len(approx) == 4:
                shape = "rectangle"
            elif len(approx) > 4:
                shape = "circle"
            else:
                shape = "unknown"
            shapes.append({"shape": shape, "contour": contour.tolist()})
        return json.dumps({"shapes": shapes})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    mcp.run()