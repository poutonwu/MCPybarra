from mcp.server.fastmcp import FastMCP, Image
import io
import pyautogui
from mcp.types import ImageContent

# Create server
mcp = FastMCP("screenshot server")

@mcp.tool()
def take_screenshot() -> Image:
    """
    Take a screenshot of the user's screen and return it as an image. Use
    this tool anytime the user wants you to look at something they're doing.
    """
    buffer = io.BytesIO()

    # 如果文件大小超过大约1MB，Claude将会拒绝处理。
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    image_data = buffer.getvalue()
    print(f"Image data length: {len(image_data)}")  # 调试输出
    return Image(data=image_data, format="jpeg")

@mcp.tool()
def take_screenshot_image() -> ImageContent:
    """
    Take a screenshot of the user's screen and return it as an image. Use
    """
    buffer = io.BytesIO()

    # 如果文件大小超过大约1MB，Claude将会拒绝处理。
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    image_data = buffer.getvalue()
    print(f"Image data length: {len(image_data)}")  # 调试输出
    return Image(data=image_data, format="jpeg").to_image_content()

@mcp.tool()
def take_screenshot_path(path: str="./", name: str="screenshot.jpg") -> str:
    """
    Take a screenshot of the user's screen and save it to a specified path. Use
    this tool anytime the user wants you to look at something they're doing.
    """
    buffer = io.BytesIO()

    # 如果文件大小超过大约1MB，Claude将会拒绝处理。
    screenshot = pyautogui.screenshot()
    screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
    #  保存到本地, 异常捕获

    try:
        with open(f"{path}{name}", "wb") as f:
            f.write(buffer.getvalue())
        return "success"
    except Exception as e:
        print(f"Error writing to file: {e}")
        return "failed"

def run():
    mcp.run(transport="stdio")

def test_run():
    print(take_screenshot())

if __name__ == "__main__":
    run()
    # test_run()