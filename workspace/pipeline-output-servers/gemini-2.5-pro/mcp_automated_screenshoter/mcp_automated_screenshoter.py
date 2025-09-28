import sys
import base64
import io
import os
import json
from mcp.server.fastmcp import FastMCP
import mss
from PIL import Image

# Initialize FastMCP server
mcp = FastMCP("mcp_automated_screenshoter")

def _capture_screenshot_as_pil_image():
    """
    Helper function to capture the screen and return a Pillow Image object.
    """
    with mss.mss() as sct:
        # Get a screenshot of the primary monitor
        sct_img = sct.grab(sct.monitors[1])
        # Convert the mss screenshot to a Pillow Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img

@mcp.tool()
def take_screenshot() -> str:
    """
    Captures the user's current full screen and returns the PNG image data as a Base64 encoded string.

    This function is useful for scenarios where the image data needs to be processed or stored programmatically
    without being displayed directly. The output is a JSON string containing the Base64 data.

    Returns:
        str: A JSON string containing the key "image_base64" with the Base64 encoded PNG image data as its value.
             On failure, returns a JSON string with an "error" key.

    Example:
        take_screenshot()
    """
    try:
        pil_image = _capture_screenshot_as_pil_image()

        # Save the image to an in-memory buffer
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")

        # Get the bytes and encode to Base64
        img_bytes = buffered.getvalue()
        base64_encoded_string = base64.b64encode(img_bytes).decode('utf-8')

        return json.dumps({"image_base64": base64_encoded_string})
    except Exception as e:
        error_message = f"Failed to take screenshot: {str(e)}"
        return json.dumps({"error": error_message})

@mcp.tool()
def take_screenshot_image() -> str:
    """
    Captures the user's current full screen and returns a Data URI that can be displayed directly in a web browser.

    The returned string is formatted as `data:image/png;base64,...` and can be used directly in the `src`
    attribute of an HTML `<img>` tag to render the screenshot.

    Returns:
        str: A JSON string containing the key "image_data_uri" with the Data URI as its value.
             On failure, returns a JSON string with an "error" key.

    Example:
        take_screenshot_image()
    """
    try:
        pil_image = _capture_screenshot_as_pil_image()

        # Save the image to an in-memory buffer
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")

        # Get the bytes and encode to Base64
        img_bytes = buffered.getvalue()
        base64_encoded_string = base64.b64encode(img_bytes).decode('utf-8')

        # Format as a Data URI
        data_uri = f"data:image/png;base64,{base64_encoded_string}"

        return json.dumps({"image_data_uri": data_uri})
    except Exception as e:
        error_message = f"Failed to create screenshot image URI: {str(e)}"
        return json.dumps({"error": error_message})

@mcp.tool()
def take_screenshot_path(file_path: str) -> str:
    """
    Captures the user's current full screen and saves it to a specified local file path.

    This function will overwrite the file if it already exists. It includes security checks to prevent
    path traversal attacks and ensures the destination directory exists before saving.

    Args:
        file_path (str): The full local file path to save the screenshot to. The path must include
                         the filename and a `.png` extension (e.g., 'C:/Users/user/Desktop/my_screenshot.png').

    Returns:
        str: A JSON string confirming the successful save path or an error message. On success, it includes
             the status, absolute path, and a confirmation message.

    Example:
        take_screenshot_path(file_path="C:/Users/user/Desktop/my_screenshot.png")
    """
    # Security: Basic input validation
    if not isinstance(file_path, str) or not file_path.lower().endswith('.png'):
        error_message = "Invalid input: 'file_path' must be a string ending with '.png'."
        return json.dumps({"error": error_message})

    # Security: Prevent path traversal attacks
    # Normalize the path to resolve '..' and check if it's still absolute as intended.
    # This helps ensure the final path is the one intended by the user, without escaping a base directory.
    normalized_path = os.path.normpath(os.path.abspath(file_path))
    if ".." in file_path.split(os.path.sep):
        error_message = "Invalid file path: Path traversal using '..' is not allowed."
        return json.dumps({"error": error_message})

    try:
        # Robustness: Ensure the directory exists before saving
        directory = os.path.dirname(normalized_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with mss.mss() as sct:
            # The simplest way to save to a file with mss
            sct.shot(mon=-1, output=normalized_path)

        # Transparency: Return a clear success message
        success_message = f"Screenshot saved successfully to: {normalized_path}"
        return json.dumps({"status": "success", "path": normalized_path, "message": success_message})
    except (mss.exception.ScreenShotError, IOError, OSError, PermissionError) as e:
        # Transparency: Provide a specific error message for file-related issues
        error_message = f"Failed to save screenshot to path '{file_path}': {str(e)}"
        return json.dumps({"error": error_message})
    except Exception as e:
        # Catch any other unexpected errors
        error_message = f"An unexpected error occurred: {str(e)}"
        return json.dumps({"error": error_message})

if __name__ == "__main__":
    # Ensure stdout handles UTF-8 for cross-platform compatibility
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()