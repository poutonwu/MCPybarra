import sys
import cv2
import numpy as np
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_opencv_image_processor")

@mcp.tool()
def save_image_tool(image_path: str, image_data: bytes) -> bool:
    """
    Save an image file to a specified path.

    Args:
        image_path: The path where the image will be saved.
        image_data: The image data in bytes.

    Returns:
        True if the image was saved successfully, False otherwise.
    """
    try:
        with open(image_path, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"Error saving image: {e}", file=sys.stderr)
        return False

@mcp.tool()
def resize_image_tool(input_path: str, output_path: str, width: int, height: int) -> bool:
    """
    Resize an image to specified dimensions.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the resized image.
        width: Target width in pixels.
        height: Target height in pixels.

    Returns:
        True if resizing was successful, False otherwise.
    """
    try:
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError("Could not read the input image")
        resized_img = cv2.resize(img, (width, height))
        cv2.imwrite(output_path, resized_img)
        return True
    except Exception as e:
        print(f"Error resizing image: {e}", file=sys.stderr)
        return False

@mcp.tool()
def crop_image_tool(input_path: str, output_path: str, x: int, y: int, width: int, height: int) -> bool:
    """
    Crop a region of an image.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the cropped image.
        x: X-coordinate of the top-left corner of the crop region.
        y: Y-coordinate of the top-left corner of the crop region.
        width: Width of the crop region.
        height: Height of the crop region.

    Returns:
        True if cropping was successful, False otherwise.
    """
    try:
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError("Could not read the input image")
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid crop parameters")
        if x + width > img.shape[1] or y + height > img.shape[0]:
            raise ValueError("Crop region exceeds image dimensions")
        cropped_img = img[y:y+height, x:x+width]
        cv2.imwrite(output_path, cropped_img)
        return True
    except Exception as e:
        print(f"Error cropping image: {e}", file=sys.stderr)
        return False

@mcp.tool()
def get_image_stats_tool(image_path: str) -> dict:
    """
    Retrieve basic statistics (dimensions, channels, etc.) of an image.

    Args:
        image_path: Path to the input image.

    Returns:
        A dictionary containing width, height, channels, and dtype.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read the input image")
        return {
            "width": img.shape[1],
            "height": img.shape[0],
            "channels": img.shape[2] if len(img.shape) > 2 else 1,
            "dtype": str(img.dtype)
        }
    except Exception as e:
        print(f"Error getting image stats: {e}", file=sys.stderr)
        return {}

@mcp.tool()
def apply_filter_tool(input_path: str, output_path: str, filter_type: str, kernel_size: int = 5) -> bool:
    """
    Apply a specified filter (e.g., Gaussian blur, sharpening) to an image.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the filtered image.
        filter_type: Type of filter (blur, sharpen, etc.).
        kernel_size: Kernel size for the filter (if applicable).

    Returns:
        True if filtering was successful, False otherwise.
    """
    try:
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError("Could not read the input image")
        
        if filter_type == "blur":
            if kernel_size % 2 == 0:
                raise ValueError("Kernel size must be odd")
            filtered_img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        elif filter_type == "sharpen":
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            filtered_img = cv2.filter2D(img, -1, kernel)
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")
        
        cv2.imwrite(output_path, filtered_img)
        return True
    except Exception as e:
        print(f"Error applying filter: {e}", file=sys.stderr)
        return False

@mcp.tool()
def detect_edges_tool(input_path: str, output_path: str, threshold1: int = 100, threshold2: int = 200) -> bool:
    """
    Detect edges in an image using Canny edge detection.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the edge-detected image.
        threshold1: First threshold for hysteresis procedure.
        threshold2: Second threshold for hysteresis procedure.

    Returns:
        True if edge detection was successful, False otherwise.
    """
    try:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read the input image")
        edges = cv2.Canny(img, threshold1, threshold2)
        cv2.imwrite(output_path, edges)
        return True
    except Exception as e:
        print(f"Error detecting edges: {e}", file=sys.stderr)
        return False

@mcp.tool()
def apply_threshold_tool(input_path: str, output_path: str, threshold_type: str, threshold_value: int = 127) -> bool:
    """
    Apply binary or adaptive thresholding to an image.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the thresholded image.
        threshold_type: Type of thresholding (binary, adaptive, etc.).
        threshold_value: Threshold value (if applicable).

    Returns:
        True if thresholding was successful, False otherwise.
    """
    try:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read the input image")
        
        if threshold_type == "binary":
            _, thresholded_img = cv2.threshold(img, threshold_value, 255, cv2.THRESH_BINARY)
        elif threshold_type == "adaptive":
            thresholded_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        else:
            raise ValueError(f"Unknown threshold type: {threshold_type}")
        
        cv2.imwrite(output_path, thresholded_img)
        return True
    except Exception as e:
        print(f"Error applying threshold: {e}", file=sys.stderr)
        return False

@mcp.tool()
def detect_contours_tool(input_path: str, output_path: str) -> list:
    """
    Detect contours in an image.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the contour-detected image.

    Returns:
        A list of detected contours.
    """
    try:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read the input image")
        _, thresh = cv2.threshold(img, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        contour_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
        cv2.imwrite(output_path, contour_img)
        
        return [cnt.tolist() for cnt in contours]
    except Exception as e:
        print(f"Error detecting contours: {e}", file=sys.stderr)
        return []

@mcp.tool()
def find_shapes_tool(input_path: str, output_path: str) -> list:
    """
    Identify shapes (e.g., circles, rectangles) in an image.

    Args:
        input_path: Path to the input image.
        output_path: Path to save the shape-detected image.

    Returns:
        A list of detected shapes with their properties.
    """
    try:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Could not read the input image")
        _, thresh = cv2.threshold(img, 127, 255, 0)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes = []
        shape_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        
        for cnt in contours:
            epsilon = 0.01 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            if len(approx) == 3:
                shape = "triangle"
            elif len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h
                if 0.95 <= aspect_ratio <= 1.05:
                    shape = "square"
                else:
                    shape = "rectangle"
            else:
                shape = "circle"
            
            shapes.append({"shape": shape, "contour": cnt.tolist()})
            cv2.drawContours(shape_img, [cnt], -1, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, shape_img)
        return shapes
    except Exception as e:
        print(f"Error finding shapes: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()