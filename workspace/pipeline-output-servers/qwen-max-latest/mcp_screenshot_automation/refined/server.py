import sys
from mcp.server.fastmcp import FastMCP
from PIL import ImageGrab
import os
import json

# Initialize the FastMCP server
mcp = FastMCP("mcp_screenshot_automation")

@mcp.tool()
def take_screenshot() -> str:
    """
    Captures the user's current screen and returns the content as an image object.

    Args:
        None

    Returns:
        A JSON string containing the image data in base64 format.

    Raises:
        Exception: If there is an issue capturing the screen.
    """
    try:
        # Capture the screen
        screenshot = ImageGrab.grab()

        # Convert the image to base64 for JSON serialization
        import base64
        from io import BytesIO

        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return json.dumps({"image": img_str})
    except Exception as e:
        raise Exception(f"Failed to capture screenshot: {str(e)}") from e

@mcp.tool()
def take_screenshot_image() -> str:
    """
    Captures the user's current screen and returns the content as a displayable image.

    Args:
        None

    Returns:
        A JSON string containing the image data in base64 format suitable for direct display.

    Raises:
        Exception: If there is an issue capturing the screen.
    """
    try:
        # Capture the screen
        screenshot = ImageGrab.grab()

        # Convert the image to base64 for JSON serialization
        import base64
        from io import BytesIO

        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Return the image in HTML format for direct display
        return json.dumps({"image": f"data:image/png;base64,{img_str}"})
    except Exception as e:
        raise Exception(f"Failed to capture screenshot: {str(e)}") from e

@mcp.tool()
def take_screenshot_path(file_path: str, file_name: str) -> str:
    """
    Captures the user's current screen and saves it to a specified local file path with a custom filename.

    Args:
        file_path: The local file path where the screenshot will be saved.
        file_name: The custom filename for the saved screenshot.

    Returns:
        A JSON string indicating the success of the operation, including the full path where the file was saved.

    Raises:
        ValueError: If the file_path or file_name is invalid.
        Exception: If there is an issue capturing or saving the screenshot.
    """
    try:
        # Validate inputs
        if not file_path or not isinstance(file_path, str):
            raise ValueError("file_path must be a non-empty string.")
        if not file_name or not isinstance(file_name, str):
            raise ValueError("file_name must be a non-empty string.")

        # Capture the screen
        screenshot = ImageGrab.grab()

        # Construct full file path
        full_path = os.path.join(file_path, file_name)

        # Ensure the directory exists
        os.makedirs(file_path, exist_ok=True)

        # Save the screenshot
        screenshot.save(full_path, format="PNG")

        return json.dumps({"message": "Screenshot saved successfully.", "file_path": full_path})
    except Exception as e:
        raise Exception(f"Failed to capture or save screenshot: {str(e)}") from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()