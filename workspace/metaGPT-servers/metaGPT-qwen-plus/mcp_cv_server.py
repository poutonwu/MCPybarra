import sys
import cv2
import numpy as np
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("cv_server")

@mcp.tool()
def save_image_tool(file_path: str, image_data: np.ndarray) -> str:
    """
    保存图片文件。

    Args:
        file_path: 图片保存路径。
        image_data: 要保存的图像数据。

    Returns:
        一个字符串，表示保存成功或失败的消息。
    """
    try:
        cv2.imwrite(file_path, image_data)
        return f"Image saved successfully at {file_path}"
    except Exception as e:
        return f"Failed to save image: {str(e)}"

@mcp.tool()
def resize_image_tool(image_data: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    调整图片尺寸。

    Args:
        image_data: 输入图像数据。
        width: 目标宽度。
        height: 目标高度。

    Returns:
        调整尺寸后的图像数据。
    """
    try:
        resized_image = cv2.resize(image_data, (width, height))
        return resized_image
    except Exception as e:
        raise ValueError(f"Failed to resize image: {str(e)}")

@mcp.tool()
def crop_image_tool(image_data: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    裁剪图片区域。

    Args:
        image_data: 输入图像数据。
        x: 裁剪区域左上角x坐标。
        y: 裁剪区域左上角y坐标。
        width: 裁剪区域宽度。
        height: 裁剪区域高度。

    Returns:
        裁剪后的图像数据。
    """
    try:
        cropped_image = image_data[y:y+height, x:x+width]
        return cropped_image
    except Exception as e:
        raise ValueError(f"Failed to crop image: {str(e)}")

@mcp.tool()
def get_image_stats_tool(image_data: np.ndarray) -> dict:
    """
    获取图片统计信息。

    Args:
        image_data: 输入图像数据。

    Returns:
        包含图像统计信息的字典。
    """
    try:
        mean, std_dev = cv2.meanStdDev(image_data)
        return {
            "mean": mean.tolist(),
            "std_dev": std_dev.tolist(),
            "shape": image_data.shape
        }
    except Exception as e:
        raise ValueError(f"Failed to get image stats: {str(e)}")

@mcp.tool()
def apply_filter_tool(image_data: np.ndarray, filter_type: str) -> np.ndarray:
    """
    应用图像滤镜。

    Args:
        image_data: 输入图像数据。
        filter_type: 滤镜类型 ('blur', 'gaussian_blur', 'median_blur')。

    Returns:
        应用滤镜后的图像数据。
    """
    try:
        if filter_type == 'blur':
            return cv2.blur(image_data, (5,5))
        elif filter_type == 'gaussian_blur':
            return cv2.GaussianBlur(image_data, (5,5), 0)
        elif filter_type == 'median_blur':
            return cv2.medianBlur(image_data, 5)
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")
    except Exception as e:
        raise ValueError(f"Failed to apply filter: {str(e)}")

@mcp.tool()
def detect_edges_tool(image_data: np.ndarray, threshold1: int, threshold2: int) -> np.ndarray:
    """
    检测图像边缘。

    Args:
        image_data: 输入图像数据。
        threshold1: 第一个阈值。
        threshold2: 第二个阈值。

    Returns:
        包含检测到的边缘的图像数据。
    """
    try:
        gray_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY) if len(image_data.shape) > 2 else image_data
        edges = cv2.Canny(gray_image, threshold1, threshold2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)  # 转换为三通道便于显示
    except Exception as e:
        raise ValueError(f"Failed to detect edges: {str(e)}")

@mcp.tool()
def apply_threshold_tool(image_data: np.ndarray, threshold: int, max_value: int) -> np.ndarray:
    """
    进行阈值分割。

    Args:
        image_data: 输入图像数据。
        threshold: 阈值。
        max_value: 最大值。

    Returns:
        应用阈值分割后的图像数据。
    """
    try:
        gray_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY) if len(image_data.shape) > 2 else image_data
        _, thresh_image = cv2.threshold(gray_image, threshold, max_value, cv2.THRESH_BINARY)
        return cv2.cvtColor(thresh_image, cv2.COLOR_GRAY2BGR)  # 转换为三通道便于显示
    except Exception as e:
        raise ValueError(f"Failed to apply threshold: {str(e)}")

@mcp.tool()
def detect_contours_tool(image_data: np.ndarray) -> dict:
    """
    检测图像轮廓。

    Args:
        image_data: 输入图像数据。

    Returns:
        包含轮廓信息的字典。
    """
    try:
        gray_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY) if len(image_data.shape) > 2 else image_data
        _, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # 绘制轮廓
        contour_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 2)
        
        return {
            "contour_image": contour_image.tolist(),
            "num_contours": len(contours),
            "contour_areas": [cv2.contourArea(cnt) for cnt in contours]
        }
    except Exception as e:
        raise ValueError(f"Failed to detect contours: {str(e)}")

@mcp.tool()
def find_shapes_tool(image_data: np.ndarray) -> dict:
    """
    查找图像形状。

    Args:
        image_data: 输入图像数据。

    Returns:
        包含形状信息的字典。
    """
    try:
        gray_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY) if len(image_data.shape) > 2 else image_data
        _, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes_info = []
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            shape = "unknown"
            if len(approx) == 3:
                shape = "triangle"
            elif len(approx) == 4:
                (x, y, w, h) = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                shape = "square" if 0.95 <= aspect_ratio <= 1.05 else "rectangle"
            elif len(approx) == 5:
                shape = "pentagon"
            elif len(approx) > 5:
                shape = "circle"
            
            shapes_info.append({
                "shape": shape,
                "approx_points": len(approx),
                "area": cv2.contourArea(cnt)
            })
        
        return {
            "shapes": shapes_info,
            "total_shapes": len(shapes_info)
        }
    except Exception as e:
        raise ValueError(f"Failed to find shapes: {str(e)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()