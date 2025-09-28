import os
import sys
import pyautogui
from PIL import Image
import base64
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("mcp_screenshot_automation")

@mcp.tool()
def take_screenshot() -> dict:
    """
    Capture the current screen content and return it as an image object.

    Returns:
        dict: A dictionary containing the image object serialized for transmission.

    Example:
        result = take_screenshot()
        image = result['image']
    """
    try:
        screenshot = pyautogui.screenshot()
        return {"status": "success", "image": screenshot}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def take_screenshot_image() -> dict:
    """
    Capture the current screen content and return it as a byte stream for direct display.

    Returns:
        dict: A dictionary containing the Base64-encoded byte stream of the image.

    Example:
        result = take_screenshot_image()
        image_bytes = result['image_bytes']
    """
    try:
        screenshot = pyautogui.screenshot()
        byte_stream = base64.b64encode(screenshot.tobytes()).decode('utf-8')  # Encode to Base64 and decode to string
        return {"status": "success", "image_bytes": byte_stream}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def take_screenshot_path(file_path: str) -> dict:
    """
    Capture the current screen content and save it to a specified file path.

    Args:
        file_path (str): The full path where the screenshot will be saved, including file name and extension.

    Returns:
        dict: A dictionary containing the status and saved file path.

    Example:
        result = take_screenshot_path("C:/Users/username/Desktop/screenshot.png")
        if result['status'] == 'success':
            print("Saved to", result['file_path'])
    """
    try:
        if not file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            raise ValueError("Invalid file extension. Supported formats: .png, .jpg, .jpeg, .bmp, .gif")

        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
        return {"status": "success", "file_path": file_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    mcp.run()