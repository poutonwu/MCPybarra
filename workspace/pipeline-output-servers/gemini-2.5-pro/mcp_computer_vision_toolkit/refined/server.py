import sys
import os
import json
import cv2
import numpy as np
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("mcp_computer_vision_toolkit")

# Dictionary to track outputs from previous steps for dependency resolution
_step_outputs = {}

def _resolve_placeholders(input_path: str) -> str:
    """Resolve placeholders like $outputs.step_name.output_path in input paths."""
    if isinstance(input_path, str) and input_path.startswith("$outputs."):
        # Extract the reference key from the placeholder
        ref_key = input_path.split("$")[1]  # Get everything after $
        
        # Handle nested references (e.g., $outputs.step_name.output_path)
        parts = ref_key.split(".")
        if len(parts) >= 3 and parts[0] == "outputs":
            step_name = parts[1]
            if step_name in _step_outputs:
                output_dict = _step_outputs[step_name]
                # Return the actual output path
                return output_dict.get("output_path")
    return input_path

# --- Helper function for reading and writing images ---
def _read_image(path: str) -> np.ndarray:
    """Reads an image from the specified path and raises an error if it fails."""
    # First try to resolve any placeholders in the path
    resolved_path = _resolve_placeholders(path)
    
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Input file not found at path: {resolved_path}")
    img = cv2.imread(resolved_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"Failed to read or decode the image at path: {resolved_path}")
    return img

def _write_image(path: str, img: np.ndarray):
    """Writes an image to the specified path and raises an error if it fails."""
    try:
        # Create directory if it doesn't exist. Handle case where path is just a filename.
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        cv2.imwrite(path, img)
    except Exception as e:
        raise IOError(f"Failed to write image to path: {path}. Reason: {e}")

# --- MCP Tools Implementation ---
@mcp.tool()
def save_image(source_path: str, destination_path: str) -> str:
    """Saves an image from a source path to a destination path.
    This function is useful for creating copies or changing the format of an image file.

    Args:
        source_path (str): The full path to the existing image file.
        destination_path (str): The full path where the new image file will be saved.

    Returns:
        str: A JSON string with a confirmation message indicating the path where the image was successfully saved, or an error message.

    Example:
        save_image(source_path="input/logo.png", destination_path="output/logo_copy.jpg")
    """
    try:
        img = _read_image(source_path)
        _write_image(destination_path, img)
        result = {"message": f"Image successfully saved to {destination_path}"}
        # Store output for potential future dependencies
        _step_outputs['save_image'] = {'output_path': destination_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def resize_image(input_path: str, output_path: str, width: int, height: int) -> str:
    """Changes the dimensions of an image to a specified width and height.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the resized image file.
        width (int): The target width for the resized image in pixels.
        height (int): The target height for the resized image in pixels.

    Returns:
        str: A JSON string with a confirmation message indicating the path of the newly created resized image, or an error message.

    Example:
        resize_image(input_path="input/photo.jpg", output_path="output/photo_resized.jpg", width=800, height=600)
    """
    try:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        img = _read_image(input_path)
        resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        _write_image(output_path, resized_img)
        result = {"message": f"Image resized and saved to {output_path}"}
        # Store output for potential future dependencies
        _step_outputs['resize_image'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def crop_image(input_path: str, output_path: str, x: int, y: int, width: int, height: int) -> str:
    """Extracts a rectangular region from an image.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the cropped image file.
        x (int): The x-coordinate of the top-left corner of the crop area.
        y (int): The y-coordinate of the top-left corner of the crop area.
        width (int): The width of the crop rectangle.
        height (int): The height of the crop rectangle.

    Returns:
        str: A JSON string with a confirmation message indicating the path of the newly created cropped image, or an error message.

    Example:
        crop_image(input_path="input/scenery.png", output_path="output/scenery_cropped.png", x=100, y=150, width=300, height=200)
    """
    try:
        img = _read_image(input_path)
        img_h, img_w = img.shape[:2]
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Coordinates (x, y) and dimensions (width, height) must be positive.")
        if x + width > img_w or y + height > img_h:
            raise ValueError("Crop area is outside the image boundaries.")

        cropped_img = img[y:y+height, x:x+width]
        _write_image(output_path, cropped_img)
        result = {"message": f"Image cropped and saved to {output_path}"}
        # Store output for potential future dependencies
        _step_outputs['crop_image'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_image_stats(input_path: str) -> str:
    """Retrieves basic statistical information about an image, such as its
    dimensions and number of color channels.

    Args:
        input_path (str): The path to the image file to be analyzed.

    Returns:
        str: A JSON string containing the image's statistics: {'width': int, 'height': int, 'channels': int}, or an error message.

    Example:
        get_image_stats(input_path="input/image.jpg")
    """
    try:
        img = _read_image(input_path)
        height, width = img.shape[:2]
        channels = img.shape[2] if len(img.shape) == 3 else 1
        stats = {
            "width": width,
            "height": height,
            "channels": channels
        }
        # Store output for potential future dependencies
        _step_outputs['get_image_stats'] = {'stats': stats}
        return json.dumps(stats)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def apply_filter(input_path: str, output_path: str, filter_type: str) -> str:
    """Applies a pre-defined filter to an image. Supported filters are 'blur',
    'grayscale', and 'sharpen'.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the filtered image file.
        filter_type (str): The type of filter to apply. Must be one of 'blur', 'grayscale', or 'sharpen'.

    Returns:
        str: A JSON string with a confirmation message indicating the path of the newly created filtered image, or an error message.

    Example:
        apply_filter(input_path="input/portrait.jpg", output_path="output/portrait_blurred.jpg", filter_type="blur")
    """
    try:
        img = _read_image(input_path)

        if filter_type == 'grayscale':
            if len(img.shape) == 3:
                filtered_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                filtered_img = img # Already grayscale
        elif filter_type == 'blur':
            filtered_img = cv2.GaussianBlur(img, (15, 15), 0)
        elif filter_type == 'sharpen':
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            filtered_img = cv2.filter2D(img, -1, kernel)
        else:
            raise ValueError("Invalid filter_type. Supported filters are 'blur', 'grayscale', 'sharpen'.")

        _write_image(output_path, filtered_img)
        result = {"message": f"Filter '{filter_type}' applied and image saved to {output_path}"}
        # Store output for potential future dependencies
        _step_outputs['apply_filter'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def detect_edges(input_path: str, output_path: str, threshold1: float, threshold2: float) -> str:
    """Detects and highlights edges in an image using the Canny edge detection algorithm.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the resulting edge-detected image.
        threshold1 (float): The first (lower) threshold for the hysteresis procedure.
        threshold2 (float): The second (higher) threshold for the hysteresis procedure.

    Returns:
        str: A JSON string with a confirmation message indicating the path of the newly created edge-map image, or an error message.

    Example:
        detect_edges(input_path="input/building.jpg", output_path="output/building_edges.jpg", threshold1=100.0, threshold2=200.0)
    """
    try:
        # Validate thresholds are within acceptable range for image intensity (0-255)
        if threshold1 < 0 or threshold1 > 255 or threshold2 < 0 or threshold2 > 255:
            raise ValueError("Threshold values must be between 0 and 255.")
        
        img = _read_image(input_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        edges = cv2.Canny(gray_img, int(threshold1), int(threshold2))
        _write_image(output_path, edges)
        result = {"message": f"Edge detection complete. Image saved to {output_path}"}
        # Store output for potential future dependencies
        _step_outputs['detect_edges'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def apply_threshold(input_path: str, output_path: str, threshold_value: float, max_value: float) -> str:
    """Applies a fixed-level binary threshold to a grayscale image.

    Args:
        input_path (str): The path to the source image file (will be converted to grayscale).
        output_path (str): The path to save the thresholded image.
        threshold_value (float): The pixel intensity value used as the threshold.
        max_value (float): The value assigned to pixels that exceed the threshold (e.g., 255 for white).

    Returns:
        str: A JSON string with a confirmation message indicating the path of the newly created thresholded image, or an error message.

    Example:
        apply_threshold(input_path="input/text.png", output_path="output/text_binary.png", threshold_value=127.0, max_value=255.0)
    """
    try:
        # Validate thresholds are within acceptable range for image intensity (0-255)
        if threshold_value < 0 or threshold_value > 255 or max_value < 0 or max_value > 255:
            raise ValueError("Threshold and max values must be between 0 and 255.")
        
        img = _read_image(input_path)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        _, thresholded_img = cv2.threshold(gray_img, threshold_value, max_value, cv2.THRESH_BINARY)
        _write_image(output_path, thresholded_img)
        result = {"message": f"Threshold applied. Image saved to {output_path}"}
        # Store output for potential future dependencies
        _step_outputs['apply_threshold'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def detect_contours(input_path: str, output_path: str) -> str:
    """Finds the contours of objects in a binary image and draws them onto a new image.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the image with contours drawn on it.

    Returns:
        str: A JSON string with a confirmation message and the number of contours found, or an error message.

    Example:
        detect_contours(input_path="input/shapes.png", output_path="output/shapes_contours.png")
    """
    try:
        img = _read_image(input_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # Apply threshold to get a binary image
        _, binary_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on the original image
        output_img = img.copy()
        cv2.drawContours(output_img, contours, -1, (0, 255, 0), 3)
        _write_image(output_path, output_img)

        result = {
            "message": f"Contours detected and drawn. Image saved to {output_path}",
            "contours_found": len(contours)
        }
        # Store output for potential future dependencies
        _step_outputs['detect_contours'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def find_shapes(input_path: str, output_path: str) -> str:
    """A simplified shape detection tool that identifies and counts circles and rectangles in an image.

    Args:
        input_path (str): The path to the source image file.
        output_path (str): The path to save the image with detected shapes drawn on it.

    Returns:
        str: A JSON string with a message and counts of detected circles and rectangles, or an error message.

    Example:
        find_shapes(input_path="input/geometry.jpg", output_path="output/geometry_detected.jpg")
    """
    try:
        img = _read_image(input_path)
        output_img = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        circles_found = 0
        rectangles_found = 0

        # Detect circles using Hough Circle Transform
        rows = gray.shape[0]
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, rows / 8,
                                   param1=100, param2=30,
                                   minRadius=1, maxRadius=300) # Adjust maxRadius based on expected circle sizes
        if circles is not None:
            circles = np.uint16(np.around(circles))
            circles_found = len(circles[0, :])
            for i in circles[0, :]:
                # Draw circle center
                cv2.circle(output_img, (i[0], i[1]), 1, (0, 100, 100), 3)
                # Draw circle outline
                cv2.circle(output_img, (i[0], i[1]), i[2], (255, 0, 255), 3)

        # Detect rectangles
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                if h == 0: continue # Avoid division by zero
                aspect_ratio = float(w)/h
                # A simple check to filter out non-rectangular shapes
                if 0.8 <= aspect_ratio <= 1.25:
                    rectangles_found += 1
                    cv2.drawContours(output_img, [approx], 0, (0, 0, 255), 3)

        _write_image(output_path, output_img)

        result = {
            "message": f"Shape detection complete. Image saved to {output_path}",
            "circles_found": circles_found,
            "rectangles_found": rectangles_found
        }
        # Store output for potential future dependencies
        _step_outputs['find_shapes'] = {'output_path': output_path}
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()