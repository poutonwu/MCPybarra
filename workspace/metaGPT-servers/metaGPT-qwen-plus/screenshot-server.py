import sys
import asyncio
from mcp.server.fastmcp import FastMCP
from PIL import ImageGrab
import io
import base64
import os

# 初始化 FastMCP 服务器
mcp = FastMCP("screenshot")


# 屏幕截图工具函数
@mcp.tool()
async def take_screenshot() -> dict:
    """
    捕获当前屏幕截图并返回图像对象。

    Returns:
        一个包含屏幕截图数据的字典，格式为 {"image": "base64_encoded_image"}。
    """
    try:
        # 截取当前屏幕
        screenshot = ImageGrab.grab()

        # 将图像转换为Base64编码
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format=screenshot.format)
        img_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return {"image": f"data:image/{screenshot.format.lower()};base64,{img_data}"}
    except Exception as e:
        raise RuntimeError(f"屏幕截图失败: {str(e)}") from e


# 屏幕截图工具函数 - 返回可显示的图像内容
@mcp.tool()
async def take_screenshot_image() -> str:
    """
    捕获当前屏幕截图并返回可直接显示的图像内容。

    Returns:
        一个字符串，包含Base64编码的PNG图像数据。
    """
    try:
        # 截取当前屏幕
        screenshot = ImageGrab.grab()

        # 将图像转换为Base64编码
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

        return f"data:image/png;base64,{img_data}"
    except Exception as e:
        raise RuntimeError(f"屏幕截图失败: {str(e)}") from e


# 屏幕截图工具函数 - 保存到指定路径
@mcp.tool()
async def take_screenshot_path(file_path: str, file_name: str = "screenshot.png") -> dict:
    """
    捕获当前屏幕截图并将其保存到指定路径。

    Args:
        file_path: 图像文件应保存的本地文件系统路径。
        file_name: 要使用的自定义文件名，默认为'screenshot.png'。

    Returns:
        一个包含操作结果信息的字典。
    """
    try:
        # 验证文件路径
        if not file_path or not isinstance(file_path, str):
            raise ValueError("必须提供有效的文件路径")

        # 创建完整的文件路径
        full_path = os.path.join(file_path, file_name)

        # 确保目标目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # 截取当前屏幕
        screenshot = ImageGrab.grab()

        # 保存图像文件
        screenshot.save(full_path)

        return {
            "message": "屏幕截图已成功保存",
            "file_path": full_path,
            "file_size": os.path.getsize(full_path)
        }
    except Exception as e:
        raise RuntimeError(f"屏幕截图保存失败: {str(e)}") from e


async def main():
    """主函数，配置并运行服务器。"""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        print("Starting screenshot MCP server...")
        await mcp.run_stdio_async()
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        raise


if __name__ == "__main__":
    # 在Windows上, asyncio.run() 可能需要这个策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())