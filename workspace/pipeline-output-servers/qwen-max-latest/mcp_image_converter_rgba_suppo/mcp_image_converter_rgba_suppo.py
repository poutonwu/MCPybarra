import os
import json
import sys
from PIL import Image
from mcp.server.fastmcp import FastMCP


# Initialize the FastMCP server
mcp = FastMCP("image_converter")

def save_content_to_file(func):
    """Decorator to ensure output directory exists before saving content."""
    def wrapper(*args, **kwargs):
        output_path = kwargs.get('output_path') or args[1]
        os.makedirs(output_path, exist_ok=True)
        return func(*args, **kwargs)
    return wrapper

@save_content_to_file
@mcp.tool()
def convert_image(input_path: str, output_path: str, output_format: str) -> dict:
    """
    Converts images from one format to another (e.g., PNG, JPEG, BMP, GIF) while preserving transparency for RGBA images.
    Automatically handles color space conversion and saves the converted image to a specified directory.

    Args:
        input_path: The file path of the input image to be converted (str).
        output_path: The directory where the converted image will be saved (str).
        output_format: The target image format (e.g., "PNG", "JPEG", "BMP", "GIF") (str).

    Returns:
        A dictionary containing the status of the conversion ('success' or 'failure') and a message describing the result or any errors encountered.

    Example:
        convert_image(
            input_path="/path/to/input/image.png",
            output_path="/path/to/output/",
            output_format="JPEG"
        )
    """
    try:
        # Validate input parameters
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file does not exist: {input_path}")

        if not output_format.upper() in {"PNG", "JPEG", "BMP", "GIF"}:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Open the image using Pillow
        with Image.open(input_path) as img:
            # Handle transparency for RGBA images
            if img.mode == "RGBA" and output_format.upper() not in {"PNG", "GIF"}:
                img = img.convert("RGB")

            # Save the converted image to the specified output path
            output_file = os.path.join(output_path, f"converted_image.{output_format.lower()}")
            img.save(output_file, format=output_format.upper())

        return {"status": "success", "message": f"Image successfully converted and saved to {output_file}"}

    except Exception as e:
        return {"status": "failure", "message": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8-sig')
    mcp.run()