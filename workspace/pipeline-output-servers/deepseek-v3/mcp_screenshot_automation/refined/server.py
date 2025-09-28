import sys
from io import BytesIO
from mcp.server.fastmcp import FastMCP
from PIL import ImageGrab
import pyautogui
import base64
import os

# Initialize FastMCP server
mcp = FastMCP("mcp_screenshot_automation")

@mcp.tool()
def take_screenshot() -> str:
    """
    Captures the current screen content and returns it as a PIL.Image object.

    Returns:
        A base64-encoded string representing the screenshot as a PIL.Image object.

    Raises:
        Exception: If screenshot capture fails.
    """
    try:
        # Try using Pillow first
        screenshot = ImageGrab.grab()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        # Fallback to pyautogui if Pillow fails
        try:
            screenshot = pyautogui.screenshot()
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            raise Exception(f"Failed to capture screenshot: {e}")

@mcp.tool()
def take_screenshot_image() -> str:
    """
    Captures the current screen and returns the image content as a base64-encoded string for direct display.

    Returns:
        A base64-encoded string of the screenshot in PNG format (e.g., "data:image/png;base64,...").

    Raises:
        Exception: If screenshot capture or encoding fails.
    """
    try:
        # Try using Pillow first
        screenshot = ImageGrab.grab()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        # Fallback to pyautogui if Pillow fails
        try:
            screenshot = pyautogui.screenshot()
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            raise Exception(f"Failed to capture or encode screenshot: {e}")

@mcp.tool()
def take_screenshot_path(path: str, filename: str = "screenshot.png") -> str:
    """
    Captures the current screen and saves the screenshot to a user-specified local file path.

    Args:
        path: The directory path where the screenshot will be saved.
        filename: The custom filename (e.g., "custom.png"). Defaults to "screenshot.png".

    Returns:
        A confirmation string (e.g., "Screenshot saved to /path/to/custom.png").

    Raises:
        Exception: If screenshot capture or file save fails.
    """
    try:
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, filename)
        
        # Try using Pillow first
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(file_path)
            return f"Screenshot saved to {file_path}"
        except Exception as e:
            # Fallback to pyautogui if Pillow fails
            try:
                screenshot = pyautogui.screenshot()
                screenshot.save(file_path)
                return f"Screenshot saved to {file_path} (fallback)"
            except Exception as e:
                raise Exception(f"Failed to capture or save screenshot: {e}")
    except Exception as e:
        raise Exception(f"Failed to create directory or save screenshot: {e}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()