import os
import sys
import json
import cv2
import numpy as np
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_opencv_image_processor")

@mcp.tool()
def save_image_tool(source_path: str, destination_path: str) -> str:
    """
    Saves an image file from the given source path to a new destination path.

    Args:
        source_path (str): The file path of the image to be saved.
        destination_path (str): The file path where the image will be saved.

    Returns:
        str: The file path of the newly saved image.

    Raises:
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the image to the destination path
        cv2.imwrite(destination_path, image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while saving the image: {e}")

@mcp.tool()
def resize_image_tool(source_path: str, destination_path: str, width: int, height: int) -> str:
    """
    Resizes an image located at the source path and saves it to a new destination path.

    Args:
        source_path (str): The file path of the image to resize.
        destination_path (str): The file path where the resized image will be saved.
        width (int): The desired width for the resized image.
        height (int): The desired height for the resized image.

    Returns:
        str: The file path of the resized image.

    Raises:
        ValueError: If width or height are not positive integers.
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Validate dimensions
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")

        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Resize the image
        resized_image = cv2.resize(image, (width, height))

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the resized image to the destination path
        cv2.imwrite(destination_path, resized_image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while resizing the image: {e}")

@mcp.tool()
def crop_image_tool(source_path: str, destination_path: str, x: int, y: int, width: int, height: int) -> str:
    """
    Crops an image located at the source path and saves it to a new destination path.

    Args:
        source_path (str): The file path of the image to crop.
        destination_path (str): The file path where the cropped image will be saved.
        x (int): The x-coordinate of the top-left corner of the cropping rectangle.
        y (int): The y-coordinate of the top-left corner of the cropping rectangle.
        width (int): The width of the cropping rectangle.
        height (int): The height of the cropping rectangle.

    Returns:
        str: The file path of the cropped image.

    Raises:
        ValueError: If width or height are not positive integers or coordinates are invalid.
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Validate dimensions and coordinates
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        if x < 0 or y < 0:
            raise ValueError("Coordinates x and y must be non-negative integers.")

        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Validate crop boundaries
        if x + width > image.shape[1] or y + height > image.shape[0]:
            raise ValueError("Crop rectangle exceeds image boundaries.")

        # Crop the image
        cropped_image = image[y:y + height, x:x + width]

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the cropped image to the destination path
        cv2.imwrite(destination_path, cropped_image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while cropping the image: {e}")

@mcp.tool()
def get_image_stats_tool(source_path: str) -> str:
    """
    Retrieves statistical information about an image and returns the result as a string.

    Args:
        source_path (str): The file path of the image to analyze.

    Returns:
        str: A string containing the statistical information about the image.

    Raises:
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading the image.
    """
    try:
        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Calculate statistics
        stats = {
            'shape': image.shape,
            'mean': np.mean(image, axis=(0, 1)).tolist(),
            'std_dev': np.std(image, axis=(0, 1)).tolist()
        }

        # Convert stats to JSON string
        return json.dumps(stats)

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while retrieving image statistics: {e}")

@mcp.tool()
def apply_filter_tool(source_path: str, destination_path: str, filter_type: str) -> str:
    """
    Applies a specified filter to an image and saves the filtered image to a new destination path.

    Args:
        source_path (str): The file path of the image to apply the filter on.
        destination_path (str): The file path where the filtered image will be saved.
        filter_type (str): The type of filter to apply (e.g., 'blur', 'sharpen').

    Returns:
        str: The file path of the filtered image.

    Raises:
        ValueError: If the filter type is not supported.
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Apply the specified filter
        if filter_type == 'blur':
            filtered_image = cv2.GaussianBlur(image, (5, 5), 0)
        elif filter_type == 'sharpen':
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            filtered_image = cv2.filter2D(image, -1, kernel)
        else:
            raise ValueError(f"Unsupported filter type: '{filter_type}'. Supported types are 'blur' and 'sharpen'.")

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the filtered image to the destination path
        cv2.imwrite(destination_path, filtered_image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while applying the filter: {e}")

@mcp.tool()
def detect_edges_tool(source_path: str, destination_path: str) -> str:
    """
    Detects edges in an image using edge detection algorithms and saves the result to a new destination path.

    Args:
        source_path (str): The file path of the image to detect edges.
        destination_path (str): The file path where the edge-detected image will be saved.

    Returns:
        str: The file path of the edge-detected image.

    Raises:
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Detect edges using Canny algorithm
        edges = cv2.Canny(image, 100, 200)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the edge-detected image to the destination path
        cv2.imwrite(destination_path, edges)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while detecting edges: {e}")

@mcp.tool()
def apply_threshold_tool(source_path: str, destination_path: str, threshold_value: int) -> str:
    """
    Applies a threshold to an image, converting it to a binary image, and saves the result to a new destination path.

    Args:
        source_path (str): The file path of the image to apply the threshold on.
        destination_path (str): The file path where the thresholded image will be saved.
        threshold_value (int): The threshold value for binarization.

    Returns:
        str: The file path of the thresholded image.

    Raises:
        ValueError: If the threshold value is out of valid range.
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Validate threshold value
        if not 0 <= threshold_value <= 255:
            raise ValueError("Threshold value must be between 0 and 255.")

        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Apply thresholding
        _, thresholded_image = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the thresholded image to the destination path
        cv2.imwrite(destination_path, thresholded_image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while applying the threshold: {e}")

@mcp.tool()
def detect_contours_tool(source_path: str, destination_path: str) -> str:
    """
    Detects contours in an image and saves the contour-detected image to a new destination path.

    Args:
        source_path (str): The file path of the image to detect contours.
        destination_path (str): The file path where the contour-detected image will be saved.

    Returns:
        str: The file path of the contour-detected image.

    Raises:
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Find contours
        _, thresh = cv2.threshold(image, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on the original image
        color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(color_image, contours, -1, (0, 255, 0), 3)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the contour-detected image to the destination path
        cv2.imwrite(destination_path, color_image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while detecting contours: {e}")

@mcp.tool()
def find_shapes_tool(source_path: str, destination_path: str) -> str:
    """
    Finds shapes in an image using contour detection and saves the shape-detected image to a new destination path.

    Args:
        source_path (str): The file path of the image to find shapes.
        destination_path (str): The file path where the shape-detected image will be saved.

    Returns:
        str: The file path of the shape-detected image.

    Raises:
        FileNotFoundError: If the source file does not exist.
        IOError: If there is an issue reading or writing the image.
    """
    try:
        # Check if the source file exists
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file '{source_path}' does not exist.")

        # Read the image from the source path
        image = cv2.imread(source_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise IOError(f"Failed to read image from '{source_path}'.")

        # Find contours
        _, thresh = cv2.threshold(image, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Draw rectangles around detected shapes
        color_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(color_image, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        # Save the shape-detected image to the destination path
        cv2.imwrite(destination_path, color_image)
        return destination_path

    except Exception as e:
        # Handle any exceptions and raise them with a clear message
        raise RuntimeError(f"An error occurred while finding shapes: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()