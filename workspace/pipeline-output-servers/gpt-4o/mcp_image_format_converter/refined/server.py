import os
import sys
import json
from PIL import Image
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("mcp_image_format_converter")

@mcp.tool()
def convert_image(source_path: str, target_format: str, output_directory: str) -> str:
    """
    Converts an input image from one format to another (e.g., PNG, JPEG, BMP, GIF).
    Preserves transparency (RGBA) and performs appropriate color space conversion.

    Args:
        source_path (str): The file path of the source image to be converted.
            Example: "input/image.png"
        target_format (str): The desired format for the output image (e.g., "JPEG", "PNG").
            Supported formats include: 'JPEG', 'PNG', 'BMP', 'GIF'.
        output_directory (str): The directory where the converted image will be saved.
            Example: "output/"

    Returns:
        str: JSON string containing:
            - status (str): Conversion status ("success" or "failure").
            - message (str): A detailed message about the conversion process or error encountered.
            - output_path (str, optional): The file path of the converted image (if successful).

    Example:
        >>> convert_image("input/image.png", "JPEG", "output/")
    """
    try:
        # Validate input parameters
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        if target_format.upper() not in ["JPEG", "PNG", "BMP", "GIF"]:
            raise ValueError(f"Unsupported target format: {target_format}")

        if not os.path.isdir(output_directory):
            raise NotADirectoryError(f"Output directory not found: {output_directory}")

        # Open the source image
        with Image.open(source_path) as img:
            # Convert to RGB if the format requires it
            if target_format.upper() == "JPEG" and img.mode != "RGB":
                img = img.convert("RGB")

            # Define the output file path
            base_name = os.path.splitext(os.path.basename(source_path))[0]
            output_path = os.path.join(output_directory, f"{base_name}.{target_format.lower()}")

            # Save the image in the target format
            img.save(output_path, target_format.upper())

        return json.dumps({
            "status": "success",
            "message": f"Image successfully converted to {target_format}.",
            "output_path": output_path
        })

    except FileNotFoundError as e:
        return json.dumps({
            "status": "failure",
            "message": str(e)
        })

    except ValueError as e:
        return json.dumps({
            "status": "failure",
            "message": str(e)
        })

    except NotADirectoryError as e:
        return json.dumps({
            "status": "failure",
            "message": str(e)
        })

    except Exception as e:
        return json.dumps({
            "status": "failure",
            "message": f"An unexpected error occurred: {str(e)}"
        })

if __name__ == "__main__":
    # Ensure UTF-8 encoding for standard output
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Run the MCP server
    mcp.run()