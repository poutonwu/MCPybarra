import sys
import base64
import json
import cv2
import numpy as np
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("opencv_image_processor")

# --- Helper Functions ---

def decode_image(image_data: str) -> np.ndarray:
    """Decodes a Base64 string to an OpenCV image (NumPy array)."""
    try:
        # Add padding if missing
        missing_padding = len(image_data) % 4
        if missing_padding:
            image_data += '=' * (4 - missing_padding)

        decoded_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image. The image data may be corrupt or in an unsupported format.")
        return img
    except (base64.binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base64 string or image format: {e}")

def encode_image(image: np.ndarray, extension: str = ".png") -> str:
    """Encodes an OpenCV image (NumPy array) to a Base64 string."""
    try:
        is_success, buffer = cv2.imencode(extension, image)
        if not is_success:
            raise ValueError("Failed to encode image.")
        return base64.b64encode(buffer).decode("utf-8")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during image encoding: {e}")

# --- MCP Tools ---

@mcp.tool()
def save_image(image_data: str, file_path: str) -> dict:
    """
    Decodes a Base64 encoded image string and saves it as a file.

    Args:
        image_data (str): The Base64 encoded string of the image to be saved.
        file_path (str): The path where the image will be saved (e.g., 'output/image.png').

    Returns:
        dict: A dictionary with a status message.
    """
    try:
        img = decode_image(image_data)
        cv2.imwrite(file_path, img)
        return {"status": f"Image saved successfully to {file_path}"}
    except Exception as e:
        return {"error": f"Failed to save image: {str(e)}"}

@mcp.tool()
def resize_image(image_data: str, width: int, height: int) -> dict:
    """
    Resizes an image to a specified width and height.

    Args:
        image_data (str): The Base64 encoded string of the source image.
        width (int): The target width for the resized image in pixels.
        height (int): The target height for the resized image in pixels.

    Returns:
        dict: A dictionary containing the Base64 encoded string of the resized image.
    """
    try:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        img = decode_image(image_data)
        resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
        encoded_img = encode_image(resized_img)
        return {"image_data": encoded_img}
    except Exception as e:
        return {"error": f"Failed to resize image: {str(e)}"}

@mcp.tool()
def crop_image(image_data: str, x: int, y: int, width: int, height: int) -> dict:
    """
    Crops a rectangular region from an image.

    Args:
        image_data (str): The Base64 encoded string of the source image.
        x (int): The x-coordinate of the top-left corner of the crop area.
        y (int): The y-coordinate of the top-left corner of the crop area.
        width (int): The width of the crop area.
        height (int): The height of the crop area.

    Returns:
        dict: A dictionary containing the Base64 encoded string of the cropped image.
    """
    try:
        img = decode_image(image_data)
        img_height, img_width = img.shape[:2]
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Coordinates and dimensions for cropping must be positive.")
        if x + width > img_width or y + height > img_height:
            raise ValueError("Crop area exceeds image dimensions.")

        cropped_img = img[y:y+height, x:x+width]
        encoded_img = encode_image(cropped_img)
        return {"image_data": encoded_img}
    except Exception as e:
        return {"error": f"Failed to crop image: {str(e)}"}

@mcp.tool()
def get_image_stats(image_data: str) -> dict:
    """
    Retrieves basic statistics from an image.

    Args:
        image_data (str): The Base64 encoded string of the source image.

    Returns:
        dict: A dictionary containing image statistics.
    """
    try:
        img = decode_image(image_data)
        height, width, channels = img.shape
        mean_pixel_value = np.mean(img, axis=(0, 1)).tolist()

        stats = {
            "height": height,
            "width": width,
            "channels": channels,
            "mean_pixel_value": mean_pixel_value
        }
        return stats
    except Exception as e:
        return {"error": f"Failed to get image stats: {str(e)}"}

@mcp.tool()
def apply_filter(image_data: str, filter_type: str) -> dict:
    """
    Applies a specified filter to an image.

    Args:
        image_data (str): The Base64 encoded string of the source image.
        filter_type (str): The filter to apply. Supported: 'blur', 'grayscale', 'sharpen'.

    Returns:
        dict: A dictionary containing the Base64 encoded string of the filtered image.
    """
    try:
        img = decode_image(image_data)
        if filter_type == 'grayscale':
            filtered_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif filter_type == 'blur':
            filtered_img = cv2.GaussianBlur(img, (15, 15), 0)
        elif filter_type == 'sharpen':
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            filtered_img = cv2.filter2D(img, -1, kernel)
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}. Supported types are 'blur', 'grayscale', 'sharpen'.")

        encoded_img = encode_image(filtered_img)
        return {"image_data": encoded_img}
    except Exception as e:
        return {"error": f"Failed to apply filter: {str(e)}"}

@mcp.tool()
def detect_edges(image_data: str, low_threshold: int, high_threshold: int) -> dict:
    """
    Performs Canny edge detection on an image.

    Args:
        image_data (str): The Base64 encoded string of the source image.
        low_threshold (int): The lower threshold for the Canny edge detector.
        high_threshold (int): The upper threshold for the Canny edge detector.

    Returns:
        dict: A dictionary containing the Base64 encoded string of the edge map.
    """
    try:
        img = decode_image(image_data)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_img, low_threshold, high_threshold)
        encoded_img = encode_image(edges)
        return {"image_data": encoded_img}
    except Exception as e:
        return {"error": f"Failed to detect edges: {str(e)}"}

@mcp.tool()
def apply_threshold(image_data: str, threshold_value: int, max_value: int) -> dict:
    """
    Applies a fixed-level threshold to a grayscale image.

    Args:
        image_data (str): The Base64 encoded string of the source grayscale image.
        threshold_value (int): The pixel value used as the threshold (0-255).
        max_value (int): The value assigned to pixels exceeding the threshold (typically 255).

    Returns:
        dict: A dictionary containing the Base64 encoded string of the binary image.
    """
    try:
        img = decode_image(image_data)
        if len(img.shape) > 2 and img.shape[2] > 1:
             img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, thresholded_img = cv2.threshold(img, threshold_value, max_value, cv2.THRESH_BINARY)
        encoded_img = encode_image(thresholded_img)
        return {"image_data": encoded_img}
    except Exception as e:
        return {"error": f"Failed to apply threshold: {str(e)}"}

@mcp.tool()
def detect_contours(image_data: str) -> dict:
    """
    Detects contours in a binary image.

    Args:
        image_data (str): The Base64 encoded string of the source binary image.

    Returns:
        dict: A dictionary containing the count of contours and the contours themselves.
    """
    try:
        img = decode_image(image_data)
        if len(img.shape) > 2:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Convert contours to a JSON-serializable format
        serializable_contours = [c.tolist() for c in contours]

        return {
            "count": len(contours),
            "contours": serializable_contours
        }
    except Exception as e:
        return {"error": f"Failed to detect contours: {str(e)}"}

@mcp.tool()
def find_shapes(image_data: str) -> dict:
    """
    Detects and identifies simple geometric shapes in an image.

    Args:
        image_data (str): The Base64 encoded string of the source image.

    Returns:
        dict: A list of found shapes with their type and center coordinates.
    """
    try:
        img = decode_image(image_data)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        found_shapes = []
        for contour in contours:
            if cv2.contourArea(contour) < 100:  # Skip small artifacts
                continue

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue

            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

            shape_type = "unidentified"
            if len(approx) == 3:
                shape_type = "triangle"
            elif len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                ar = w / float(h)
                shape_type = "square" if 0.95 <= ar <= 1.05 else "rectangle"
            else:
                # Check for circle
                area = cv2.contourArea(contour)
                (x, y), radius = cv2.minEnclosingCircle(contour)
                if radius > 0:
                    circle_area = np.pi * (radius**2)
                    if 0.85 < (area / circle_area) < 1.15:
                        shape_type = "circle"

            if shape_type != "unidentified":
                found_shapes.append({"type": shape_type, "center": [cX, cY]})

        return {"shapes": found_shapes}
    except Exception as e:
        return {"error": f"Failed to find shapes: {str(e)}"}


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()