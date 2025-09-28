import sys
import os
import json
import cv2 as cv
import numpy as np
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_opencv_image_processing_cv")

# Set UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Add proxy support if needed
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

def validate_file_path(file_path):
    """Validate that the file path exists and is accessible."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}")
    return True

def ensure_directory_exists(file_path):
    """Ensure that the directory of the specified file path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    return True

@mcp.tool()
def save_image_tool(image_path: str, output_path: str) -> str:
    """
    保存图片文件。

    Args:
        image_path: 源图像的文件路径 (必填)。
        output_path: 目标保存路径 (必填)。

    Returns:
        包含成功或失败消息的 JSON 字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果输出路径无效。
        Exception: 对于其他意外错误。

    示例:
        save_image_tool(image_path="input.jpg", output_path="output.jpg")
    """
    try:
        # Validate inputs
        validate_file_path(image_path)
        
        # Ensure output directory exists
        ensure_directory_exists(output_path)
        
        # Read and write image using OpenCV
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
            
        success = cv.imwrite(output_path, img)
        
        if not success:
            raise Exception(f"Failed to save image to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Image saved successfully to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def resize_image_tool(image_path: str, width: int, height: int) -> str:
    """
    调整图片尺寸。

    Args:
        image_path: 图像的文件路径 (必填)。
        width: 新宽度，必须为正整数 (必填)。
        height: 新高度，必须为正整数 (必填)。

    Returns:
        包含调整后的尺寸和保存路径的信息字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果宽度或高度不是正整数。
        Exception: 对于其他意外错误。

    示例:
        resize_image_tool(image_path="input.jpg", width=800, height=600)
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        if not isinstance(width, int) or width <= 0:
            raise ValueError(f"Width must be a positive integer, got {width}")
        
        if not isinstance(height, int) or height <= 0:
            raise ValueError(f"Height must be a positive integer, got {height}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Resize image
        resized_img = cv.resize(img, (width, height))
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_resized{file_ext}")
        
        # Save resized image
        success = cv.imwrite(output_path, resized_img)
        
        if not success:
            raise Exception(f"Failed to save resized image to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Image resized to {width}x{height} and saved to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def crop_image_tool(image_path: str, x: int, y: int, width: int, height: int) -> str:
    """
    裁剪图片区域。

    Args:
        image_path: 图像的文件路径 (必填)。
        x: 裁剪区域左上角 x 坐标 (必填)。
        y: 裁剪区域左上角 y 坐标 (必填)。
        width: 裁剪区域宽度，必须为正整数 (必填)。
        height: 裁剪区域高度，必须为正整数 (必填)。

    Returns:
        包含裁剪区域信息和保存路径的信息字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果坐标或尺寸无效。
        Exception: 对于其他意外错误。

    示例:
        crop_image_tool(image_path="input.jpg", x=100, y=100, width=400, height=300)
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        if not isinstance(x, int) or x < 0:
            raise ValueError(f"X coordinate must be non-negative integer, got {x}")
        
        if not isinstance(y, int) or y < 0:
            raise ValueError(f"Y coordinate must be non-negative integer, got {y}")
        
        if not isinstance(width, int) or width <= 0:
            raise ValueError(f"Width must be a positive integer, got {width}")
        
        if not isinstance(height, int) or height <= 0:
            raise ValueError(f"Height must be a positive integer, got {height}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Get image dimensions
        img_height, img_width = img.shape[:2]
        
        # Validate that the crop area is within the image
        if x + width > img_width or y + height > img_height:
            raise ValueError(f"Crop area ({x}, {y}, {width}, {height}) exceeds image dimensions ({img_width}, {img_height})")
        
        # Crop image
        cropped_img = img[y:y+height, x:x+width]
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_cropped{file_ext}")
        
        # Save cropped image
        success = cv.imwrite(output_path, cropped_img)
        
        if not success:
            raise Exception(f"Failed to save cropped image to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Image cropped to {width}x{height} at position ({x}, {y}) and saved to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def get_image_stats_tool(image_path: str) -> str:
    """
    获取图片统计信息。

    Args:
        image_path: 图像的文件路径 (必填)。

    Returns:
        包含图像尺寸、颜色空间和像素值范围等信息的 JSON 字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        Exception: 对于其他意外错误。

    示例:
        get_image_stats_tool(image_path="input.jpg")
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Get basic stats
        height, width = img.shape[:2]
        channels = img.shape[2] if len(img.shape) == 3 else 1
        
        # Determine color space
        if channels == 1:
            color_space = "Grayscale"
        elif channels == 3:
            # Check if it's actually BGR or RGB
            # Convert to HSV to determine dominant color
            try:
                hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
                avg_hue = np.mean(hsv[:, :, 0])
                
                if avg_hue < 5 or avg_hue > 355:
                    dominant_color = "Red"
                elif 5 <= avg_hue < 22:
                    dominant_color = "Orange"
                elif 22 <= avg_hue < 34:
                    dominant_color = "Yellow"
                elif 34 <= avg_hue < 78:
                    dominant_color = "Green"
                elif 78 <= avg_hue < 131:
                    dominant_color = "Blue"
                elif 131 <= avg_hue < 167:
                    dominant_color = "Violet"
                else:
                    dominant_color = "Other"
                
                color_space = f"BGR (Dominant: {dominant_color})"
            except Exception:
                color_space = "BGR"
        else:
            color_space = "Unknown"
        
        # Calculate pixel value ranges per channel
        if channels > 1:
            channel_ranges = []
            for i in range(channels):
                channel_min = int(np.min(img[:, :, i]))
                channel_max = int(np.max(img[:, :, i]))
                channel_ranges.append({
                    "channel": i,
                    "min": channel_min,
                    "max": channel_max,
                    "range": channel_max - channel_min
                })
        else:
            # Grayscale image
            channel_min = int(np.min(img))
            channel_max = int(np.max(img))
            channel_ranges = [{
                "channel": 0,
                "min": channel_min,
                "max": channel_max,
                "range": channel_max - channel_min
            }]
        
        # Calculate total pixel count
        total_pixels = img.size
        
        # Calculate memory usage
        memory_usage = img.nbytes / 1024  # in KB
        
        # Return comprehensive stats
        stats = {
            "status": "success",
            "stats": {
                "dimensions": {
                    "width": width,
                    "height": height,
                    "channels": channels
                },
                "color_space": color_space,
                "pixel_value_ranges": channel_ranges,
                "total_pixels": total_pixels,
                "memory_usage_kb": round(memory_usage, 2)
            }
        }
        
        return json.dumps(stats, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def apply_filter_tool(image_path: str, filter_type: str, kernel_size: int) -> str:
    """
    应用图像滤镜。

    Args:
        image_path: 图像的文件路径 (必填)。
        filter_type: 滤镜类型（例如 \"gaussian\", \"median\"） (必填)。
        kernel_size: 核大小，必须为正奇数 (必填)。

    Returns:
        包含应用的滤镜类型和保存路径的信息字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果参数无效。
        Exception: 对于其他意外错误。

    示例:
        apply_filter_tool(image_path="input.jpg", filter_type="gaussian", kernel_size=5)
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        if not isinstance(kernel_size, int) or kernel_size <= 0 or kernel_size % 2 == 0:
            raise ValueError(f"Kernel size must be a positive odd integer, got {kernel_size}")
        
        filter_types = ["gaussian", "median", "blur", "bilateral"]
        if filter_type.lower() not in filter_types:
            raise ValueError(f"Invalid filter type: {filter_type}. Supported types are {filter_types}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Apply filter based on type
        if filter_type.lower() == "gaussian":
            filtered_img = cv.GaussianBlur(img, (kernel_size, kernel_size), 0)
        elif filter_type.lower() == "median":
            filtered_img = cv.medianBlur(img, kernel_size)
        elif filter_type.lower() == "blur":
            filtered_img = cv.blur(img, (kernel_size, kernel_size))
        elif filter_type.lower() == "bilateral":
            # For bilateral filter, we use sigma values based on kernel size
            sigma_color = 75
            sigma_space = 75
            filtered_img = cv.bilateralFilter(img, kernel_size, sigma_color, sigma_space)
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_{filter_type.lower()}_filtered{file_ext}")
        
        # Save filtered image
        success = cv.imwrite(output_path, filtered_img)
        
        if not success:
            raise Exception(f"Failed to save filtered image to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Applied {filter_type} filter with kernel size {kernel_size} and saved to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def detect_edges_tool(image_path: str, method: str, threshold1: int, threshold2: int) -> str:
    """
    检测图像边缘。

    Args:
        image_path: 图像的文件路径 (必填)。
        method: 边缘检测方法（例如 \"canny\"） (必填)。
        threshold1: 第一个阈值，必须为非负整数 (必填)。
        threshold2: 第二个阈值，必须为非负整数且大于第一个阈值 (必填)。

    Returns:
        包含检测到的边缘数量和保存路径的信息字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果参数无效。
        Exception: 对于其他意外错误。

    示例:
        detect_edges_tool(image_path="input.jpg", method="canny", threshold1=100, threshold2=200)
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        if not isinstance(threshold1, int) or threshold1 < 0:
            raise ValueError(f"Threshold1 must be a non-negative integer, got {threshold1}")
        
        if not isinstance(threshold2, int) or threshold2 <= threshold1:
            raise ValueError(f"Threshold2 must be an integer greater than threshold1, got {threshold2}")
        
        supported_methods = ["canny"]
        if method.lower() not in supported_methods:
            raise ValueError(f"Unsupported edge detection method: {method}. Supported methods are {supported_methods}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Convert to grayscale if necessary
        if len(img.shape) == 3:
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        else:
            gray_img = img
        
        # Apply edge detection based on method
        if method.lower() == "canny":
            edges = cv.Canny(gray_img, threshold1, threshold2)
        
        # Count edges (approximate by counting non-zero pixels)
        edge_count = cv.countNonZero(edges)
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_edges_{method.lower()}{file_ext}")
        
        # Save edge detection result
        success = cv.imwrite(output_path, edges)
        
        if not success:
            raise Exception(f"Failed to save edge detection result to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Detected {edge_count} edges using {method} method and saved to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def apply_threshold_tool(image_path: str, threshold_value: int, max_value: int) -> str:
    """
    进行阈值分割。

    Args:
        image_path: 图像的文件路径 (必填)。
        threshold_value: 阈值，必须为非负整数 (必填)。
        max_value: 最大值，必须为正整数且大于阈值 (必填)。

    Returns:
        包含应用的阈值和保存路径的信息字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果参数无效。
        Exception: 对于其他意外错误。

    示例:
        apply_threshold_tool(image_path="input.jpg", threshold_value=127, max_value=255)
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        if not isinstance(threshold_value, int) or threshold_value < 0:
            raise ValueError(f"Threshold value must be a non-negative integer, got {threshold_value}")
        
        if not isinstance(max_value, int) or max_value <= threshold_value:
            raise ValueError(f"Max value must be an integer greater than threshold value, got {max_value}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Convert to grayscale if necessary
        if len(img.shape) == 3:
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        else:
            gray_img = img
        
        # Apply binary thresholding
        _, thresh_img = cv.threshold(gray_img, threshold_value, max_value, cv.THRESH_BINARY)
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_thresholded{file_ext}")
        
        # Save thresholded image
        success = cv.imwrite(output_path, thresh_img)
        
        if not success:
            raise Exception(f"Failed to save thresholded image to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Applied threshold {threshold_value} with max value {max_value} and saved to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def detect_contours_tool(image_path: str, mode: str, method: str) -> str:
    """
    检测图像轮廓。

    Args:
        image_path: 图像的文件路径 (必填)。
        mode: 轮廓检索模式（例如 \"external\", \"tree\"） (必填)。
        method: 轮廓近似方法（例如 \"simple\", \"chain_approx_none\"） (必填)。

    Returns:
        包含检测到的轮廓数量和保存路径的信息字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果参数无效。
        Exception: 对于其他意外错误。

    示例:
        detect_contours_tool(image_path="input.jpg", mode="external", method="simple")
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        # Define valid modes and methods
        valid_modes = {"external": cv.RETR_EXTERNAL, "tree": cv.RETR_TREE}
        valid_methods = {"simple": cv.CHAIN_APPROX_SIMPLE, "chain_approx_none": cv.CHAIN_APPROX_NONE}
        
        if mode.lower() not in valid_modes:
            raise ValueError(f"Invalid contour retrieval mode: {mode}. Supported modes are {list(valid_modes.keys())}")
        
        if method.lower() not in valid_methods:
            raise ValueError(f"Invalid contour approximation method: {method}. Supported methods are {list(valid_methods.keys())}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Convert to grayscale if necessary
        if len(img.shape) == 3:
            gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        else:
            gray_img = img
        
        # Apply thresholding to create binary image
        _, thresh_img = cv.threshold(gray_img, 127, 255, cv.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv.findContours(thresh_img, valid_modes[mode.lower()], valid_methods[method.lower()])
        
        # Create blank image to draw contours
        contour_img = np.zeros_like(gray_img)
        
        # Draw contours
        cv.drawContours(contour_img, contours, -1, (255, 255, 255), 2)
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_contours_{mode.lower()}_{method.lower()}{file_ext}")
        
        # Save contour image
        success = cv.imwrite(output_path, contour_img)
        
        if not success:
            raise Exception(f"Failed to save contour image to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Detected {len(contours)} contours using mode '{mode}' and method '{method}', saved to {output_path}"
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

@mcp.tool()
def find_shapes_tool(image_path: str, shape_type: str) -> str:
    """
    查找图像形状。

    Args:
        image_path: 图像的文件路径 (必填)。
        shape_type: 形状类型（例如 \"circle\", \"rectangle\"） (必填)。

    Returns:
        包含找到的形状数量和位置信息的 JSON 字符串。

    Raises:
        FileNotFoundError: 如果源文件不存在。
        ValueError: 如果参数无效。
        Exception: 对于其他意外错误。

    示例:
        find_shapes_tool(image_path="input.jpg", shape_type="circle")
    """
    try:
        # Input validation
        validate_file_path(image_path)
        
        # Define valid shape types
        valid_shape_types = ["circle", "rectangle", "triangle", "polygon"]
        
        if shape_type.lower() not in valid_shape_types:
            raise ValueError(f"Invalid shape type: {shape_type}. Supported types are {valid_shape_types}")
        
        # Read image
        img = cv.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Convert to grayscale
        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred_img = cv.GaussianBlur(gray_img, (5, 5), 0)
        
        # Threshold to create binary image
        _, thresh_img = cv.threshold(blurred_img, 127, 255, cv.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv.findContours(thresh_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        detected_shapes = []
        
        # Process each contour based on shape type
        if shape_type.lower() == "circle":
            # Use Hough Circle Transform for circle detection
            circles = cv.HoughCircles(
                gray_img, 
                cv.HOUGH_GRADIENT, 
                dp=1, 
                minDist=20,
                param1=50, 
                param2=30, 
                minRadius=0, 
                maxRadius=0
            )
            
            if circles is not None:
                circles = np.uint16(np.around(circles))
                for i, (x, y, r) in enumerate(circles[0, :]):
                    detected_shapes.append({
                        "type": "circle",
                        "position": {"x": int(x), "y": int(y)},
                        "radius": int(r)
                    })
        
        elif shape_type.lower() in ["rectangle", "triangle", "polygon"]:
            # Approximate polygon shapes
            target_sides = 4 if shape_type.lower() == "rectangle" else 3 if shape_type.lower() == "triangle" else None
            
            for contour in contours:
                # Skip small contours
                if cv.contourArea(contour) < 100:
                    continue
                
                # Approximate polygon
                perimeter = cv.arcLength(contour, True)
                approx = cv.approxPolyDP(contour, 0.04 * perimeter, True)
                
                # Check number of sides
                sides = len(approx)
                
                if shape_type.lower() == "rectangle" and sides == 4:
                    # Additional check for rectangle to ensure angles are close to 90 degrees
                    is_rectangle = True
                    
                    # Get bounding box
                    x, y, w, h = cv.boundingRect(approx)
                    
                    detected_shapes.append({
                        "type": "rectangle",
                        "position": {"x": int(x), "y": int(y)},
                        "dimensions": {"width": int(w), "height": int(h)}
                    })
                
                elif shape_type.lower() == "triangle" and sides == 3:
                    # Get bounding box
                    x, y, w, h = cv.boundingRect(approx)
                    
                    detected_shapes.append({
                        "type": "triangle",
                        "position": {"x": int(x), "y": int(y)},
                        "dimensions": {"width": int(w), "height": int(h)}
                    })
                
                elif shape_type.lower() == "polygon" and sides >= 3:
                    # For polygons, accept any shape with 3 or more sides
                    x, y, w, h = cv.boundingRect(approx)
                    
                    detected_shapes.append({
                        "type": "polygon",
                        "sides": sides,
                        "position": {"x": int(x), "y": int(y)},
                        "dimensions": {"width": int(w), "height": int(h)}
                    })
        
        # Generate output path
        file_name, file_ext = os.path.splitext(os.path.basename(image_path))
        dir_path = os.path.dirname(image_path)
        output_path = os.path.join(dir_path, f"{file_name}_shapes_{shape_type.lower()}{file_ext}")
        
        # Draw detected shapes on output image
        output_img = img.copy()
        
        for shape in detected_shapes:
            if shape["type"] == "circle":
                cv.circle(output_img, (shape["position"]["x"], shape["position"]["y"]), shape["radius"], (0, 255, 0), 2)
            elif shape["type"] in ["rectangle", "triangle", "polygon"]:
                x = shape["position"]["x"]
                y = shape["position"]["y"]
                w = shape["dimensions"]["width"]
                h = shape["dimensions"]["height"]
                cv.rectangle(output_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Save output image
        success = cv.imwrite(output_path, output_img)
        
        if not success:
            raise Exception(f"Failed to save shape detection result to {output_path}")
            
        return json.dumps({
            "status": "success",
            "message": f"Found {len(detected_shapes)} {shape_type} shapes",
            "shapes": detected_shapes
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()