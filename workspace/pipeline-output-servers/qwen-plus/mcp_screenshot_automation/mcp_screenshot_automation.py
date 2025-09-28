import sys
import base64
import os
from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import ImageGrab

# 初始化 FastMCP 服务器
mcp = FastMCP("mcp_screenshot_automation")

@mcp.tool()
def take_screenshot():
    """
    捕获用户当前屏幕内容并以图像对象形式返回。

    Args:
        None

    Returns:
        一个包含图像数据的字典对象，格式为：
        {
            "image": bytes,  # 图像的二进制数据
            "format": str,   # 图像格式（如PNG/JPEG）
            "size": tuple    # 图像尺寸（宽度, 高度）
        }

    Raises:
        RuntimeError: 如果截图捕获失败。
    """
    try:
        # 捕获屏幕截图
        screenshot = ImageGrab.grab()
        
        # 将图像转换为字节数据
        img_byte_arr = BytesIO()
        image_format = screenshot.format if screenshot.format else 'PNG'
        screenshot.save(img_byte_arr, format=image_format)
        
        result = {
            "image": img_byte_arr.getvalue(),
            "format": image_format,
            "size": screenshot.size
        }
        
        return result
    except Exception as e:
        raise RuntimeError(f"截图捕获失败: {str(e)}") from e

@mcp.tool()
def take_screenshot_image():
    """
    捕获屏幕并返回可直接显示的图像内容。

    Args:
        None

    Returns:
        一个包含Base64编码图像数据的字典对象：
        {
            "image_data": str,      # Base64编码的图像数据
            "mime_type": str        # MIME类型（如image/png）
        }

    Raises:
        RuntimeError: 如果截图捕获或编码失败。
    """
    try:
        # 捕获屏幕截图
        screenshot = ImageGrab.grab()
        
        # 将图像转换为Base64编码
        img_byte_arr = BytesIO()
        image_format = screenshot.format if screenshot.format else 'PNG'
        screenshot.save(img_byte_arr, format=image_format)
        
        # 获取MIME类型
        mime_type = f"image/{image_format.lower()}"
        
        result = {
            "image_data": base64.b64encode(img_byte_arr.getvalue()).decode('utf-8'),
            "mime_type": mime_type
        }
        
        return result
    except Exception as e:
        raise RuntimeError(f"截图捕获或编码失败: {str(e)}") from e

@mcp.tool()
def take_screenshot_path(file_path: str):
    """
    将屏幕截图保存到用户指定的本地文件路径，支持自定义文件名。

    Args:
        file_path: str - 文件保存的完整路径（包括文件名和扩展名）

    Returns:
        一个包含文件状态的字典对象：
        {
            "file_path": str,     # 文件保存的实际路径
            "exists": bool,       # 文件是否存在
            "size": int           # 文件大小（字节）
        }

    Raises:
        ValueError: 如果文件路径无效。
        RuntimeError: 如果截图捕获或保存失败。
    """
    try:
        # 验证文件路径
        if not file_path or not isinstance(file_path, str):
            raise ValueError("必须提供有效的文件路径")
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # 捕获屏幕截图
        screenshot = ImageGrab.grab()
        
        # 保存截图到指定路径
        image_format = screenshot.format if screenshot.format else 'PNG'
        save_path = file_path if '.' in os.path.basename(file_path) else f"{file_path}.{image_format.lower()}"
        
        screenshot.save(save_path, format=image_format)
        
        # 获取文件大小
        size = os.path.getsize(save_path)
        
        result = {
            "file_path": save_path,
            "exists": True,
            "size": size
        }
        
        return result
    except Exception as e:
        raise RuntimeError(f"截图保存失败: {str(e)}") from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()