import sys
import os
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_image_format_converter")


@mcp.tool()
def convert_image(input_path: str, output_format: str, output_dir: str) -> dict:
    """
    Convert an image file to a different format.

    Args:
        input_path: The path to the input image file. Must be a string and a valid path to an existing file.
        output_format: The desired output format (e.g., 'PNG', 'JPEG', 'BMP', 'GIF'). Must be a string.
        output_dir: The directory where the converted image will be saved. Must be a string and a valid directory path.

    Returns:
        A dictionary with keys 'success' (boolean), 'output_path' (string), and 'error' (string or None).

    Raises:
        ValueError: If any of the input parameters are invalid or if the input file does not exist.
        OSError: If there is an issue reading the input file or writing the output file.
        Exception: For any other unexpected errors during the conversion process.
    
    Example:
        >>> convert_image(input_path="image.jpg", output_format="PNG", output_dir="converted_images")
        {'success': True, 'output_path': 'converted_images/image.png', 'error': None}
    """
    try:
        # Validate input parameters
        if not isinstance(input_path, str):
            raise ValueError("'input_path' must be a string.")
        if not os.path.isfile(input_path):
            raise ValueError(f"Input file does not exist: {input_path}")
        
        if not isinstance(output_format, str) or not output_format.strip():
            raise ValueError("'output_format' must be a non-empty string.")
        
        if not isinstance(output_dir, str):
            raise ValueError("'output_dir' must be a string.")
        if not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Output directory does not exist and could not be created: {output_dir}") from e
        
        # Get the base filename and stem
        input_path_obj = Path(input_path)
        base_name = input_path_obj.stem
        
        # Construct the output path
        output_path = os.path.join(output_dir, f"{base_name}.{output_format.lower()}")
        
        # Open the image
        try:
            with Image.open(input_path) as img:
                # Handle RGBA to RGB conversion if necessary
                if output_format.upper() in ['JPEG', 'BMP', 'WEBP'] and img.mode in ['RGBA', 'LA']:
                    background = Image.new('RGB', img.size, (255, 255, 255))  # White background
                    background.paste(img, mask=img.split()[-1])  # Paste using alpha channel
                    img = background
                
                # Save the image in the new format
                img.save(output_path, format=output_format)
        except UnidentifiedImageError as e:
            raise OSError(f"Cannot identify image file: {input_path}") from e
        except Exception as e:
            raise OSError(f"Error processing the image: {e}") from e
        
        return {
            "success": True,
            "output_path": output_path,
            "error": None
        }
    
    except Exception as e:
        return {
            "success": False,
            "output_path": None,
            "error": str(e)
        }

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()