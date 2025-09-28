import sys
from mcp.server.fastmcp import FastMCP
from PIL import Image
import os

# Initialize the FastMCP server
mcp = FastMCP("mcp_image_format_converter")

@mcp.tool()
def convert_image(source_path: str, target_format: str, output_dir: str, preserve_alpha: bool = True, quality: int = 95) -> dict:
    """
    Converts an image file from one format to another, handling transparency and color space conversion.
    
    Args:
        source_path (str): Path to the source image file.
        target_format (str): Desired output format (e.g., "PNG", "JPEG", "BMP", "GIF").
        output_dir (str): Directory where the converted image will be saved.
        preserve_alpha (bool, optional): Whether to preserve transparency (default: True).
        quality (int, optional): Compression quality for lossy formats like JPEG (default: 95).
    
    Returns:
        dict: Contains the following keys:
            - status (str): "success" or "error".
            - message (str): Detailed status or error message.
            - output_path (str): Path to the converted image file (only on success).
    
    Raises:
        ValueError: For invalid input paths or unsupported formats.
    """
    try:
        # Validate input paths and format
        if not os.path.exists(source_path):
            raise ValueError(f"Source file does not exist: {source_path}")
        
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        supported_formats = ["PNG", "JPEG", "BMP", "GIF"]
        target_format_upper = target_format.upper()
        if target_format_upper not in supported_formats:
            raise ValueError(f"Unsupported target format: {target_format}. Supported formats: {supported_formats}")
        
        # Open the image
        with Image.open(source_path) as img:
            # Handle transparency
            if img.mode == 'RGBA' and not preserve_alpha:
                img = img.convert('RGB')
            elif img.mode == 'P' and preserve_alpha:
                img = img.convert('RGBA')
            
            # Determine the output path
            filename = os.path.splitext(os.path.basename(source_path))[0]
            output_path = os.path.join(output_dir, f"{filename}.{target_format.lower()}")
            
            # Save the image with appropriate parameters
            save_kwargs = {'format': target_format_upper, 'quality': quality}
            if target_format_upper == 'JPEG' and img.mode == 'RGBA':
                img = img.convert('RGB')
            
            img.save(output_path, **save_kwargs)
            
            return {
                "status": "success",
                "message": "Image converted successfully",
                "output_path": output_path
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "output_path": None
        }

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()