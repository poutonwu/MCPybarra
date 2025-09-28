import os
import sys
import json
from mcp.server.fastmcp import FastMCP
from PIL import Image, UnidentifiedImageError

# Version: Pillow 10.4.0
# Version: mcp 0.2.1

# Initialize FastMCP server
mcp = FastMCP("mcp_image_format_converter")

class SecurityException(Exception):
    """Custom exception for security-related errors like path traversal."""
    pass

@mcp.tool()
def convert_image(source_path: str, output_dir: str, target_format: str) -> str:
    """
    Converts an image file from a source format to a specified target format.

    This tool handles various image types, including those with transparency (RGBA),
    by performing necessary color space conversions. It includes robust input
    validation and security checks to prevent common vulnerabilities like path
    traversal attacks.

    Args:
        source_path (str): The absolute or relative path to the source image file
                           (e.g., '/path/to/image.png').
        output_dir (str): The path to the directory where the converted image will
                          be saved. The directory must exist.
        target_format (str): The desired output image format (e.g., 'JPEG', 'PNG',
                             'BMP', 'GIF').

    Returns:
        str: A JSON formatted string indicating success or failure.
             On Success: {"status": "success", "message": "Image converted successfully.", "output_path": "/path/to/output/image.jpeg"}
             On Failure: {"status": "error", "message": "Error details..."}

    Example:
        convert_image(source_path="C:/Users/Test/images/sample.png", output_dir="C:/Users/Test/images/output", target_format="JPEG")
    """
    try:
        # --- Robustness & Security: Input Validation ---
        if not isinstance(source_path, str) or not source_path.strip():
            raise ValueError("Parameter 'source_path' must be a non-empty string.")
        if not isinstance(output_dir, str) or not output_dir.strip():
            raise ValueError("Parameter 'output_dir' must be a non-empty string.")
        if not isinstance(target_format, str) or not target_format.strip():
            raise ValueError("Parameter 'target_format' must be a non-empty string.")

        # --- Security: Path Validation ---
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file not found at '{source_path}'.")
        if not os.path.isdir(output_dir):
            raise FileNotFoundError(f"Output directory not found at '{output_dir}'.")
        
        # Prevent path traversal attacks by ensuring the final path is within the intended directory
        base_name = os.path.basename(source_path)
        file_name, _ = os.path.splitext(base_name)
        
        # Sanitize target_format to prevent using it for path manipulation
        safe_format = "".join(c for c in target_format.lower() if c.isalnum())
        if not safe_format:
            raise ValueError(f"Invalid target format provided: '{target_format}'.")
            
        output_filename = f"{file_name}.{safe_format}"
        output_path = os.path.join(output_dir, output_filename)

        # Final check to ensure the resolved path is within the intended output directory
        if os.path.commonprefix([os.path.realpath(output_path), os.path.realpath(output_dir)]) != os.path.realpath(output_dir):
            raise SecurityException("Attempted path traversal detected.")

        # --- Functionality: Image Conversion Logic ---
        with Image.open(source_path) as img:
            # Handle transparency (RGBA) when converting to formats that don't support it (like JPEG)
            if img.mode in ('RGBA', 'P') and target_format.upper() == 'JPEG':
                # Create a new image with a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Paste the original image onto the background, using the alpha channel as a mask
                # Ensure the image to be pasted has an alpha channel
                img_with_alpha = img.convert('RGBA')
                background.paste(img_with_alpha, (0, 0), img_with_alpha)
                img_to_save = background
            else:
                img_to_save = img.convert('RGB') if target_format.upper() == 'JPEG' else img

            img_to_save.save(output_path, format=target_format)

        # --- Transparency: Success Response ---
        return json.dumps({
            "status": "success",
            "message": "Image converted successfully.",
            "output_path": output_path
        })

    except FileNotFoundError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})
    except UnidentifiedImageError:
        return json.dumps({"status": "error", "message": f"Cannot identify image file. The file at '{source_path}' may be corrupted or not a valid image."})
    except SecurityException as e:
        return json.dumps({"status": "error", "message": str(e)})
    except Exception as e:
        # --- Transparency: Detailed Error Response ---
        return json.dumps({
            "status": "error",
            "message": f"An unexpected error occurred: {type(e).__name__} - {str(e)}"
        })

if __name__ == "__main__":
    # Ensure UTF-8 encoding for cross-platform compatibility
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()