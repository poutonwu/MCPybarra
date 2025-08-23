import base64
import pathlib
import uuid
from mcp.server.fastmcp import FastMCP
from PIL import Image
import io



ROOT_DIR = pathlib.Path.cwd()
CONVERTED_DIR = ROOT_DIR / "converted"
CONVERTED_DIR.mkdir(exist_ok=True)
SUPPORTED_FORMATS = set(Image.registered_extensions().values())
SUPPORTED_FORMATS.add('JPG')  # Add JPG as an alias for JPEG
print(SUPPORTED_FORMATS)

mcp = FastMCP("Image File Converter", dependencies=["Pillow"])

@mcp.tool(
    name="Image File Converter",
    description="Converts an image from one format to another and saves it to the 'converted' directory.",
)
def convert_image(image_path: str, target_format: str) -> str:
    """
    Takes in an image path and and a target format. 
    Converts the image from the image path to target format and saves it to the 'converted' directory.
    Returns the relative path to the converted image.
    """
    if target_format.lower() == "jpg":
        target_format = "JPEG"
    try:
        # Resolve and validate path
        path = image_path

        # Read and convert image
        with open(path, "rb") as f:
            image_bytes = f.read()
        image = Image.open(io.BytesIO(image_bytes))
        target_format_upper = target_format.upper()
        if target_format_upper not in SUPPORTED_FORMATS:
            return f"Error: Unsupported format {target_format}"
        
        # Convert RGBA to RGB if saving as JPEG/JPG
        if target_format_upper in ('JPEG', 'JPG') and image.mode == 'RGBA':
            # Convert to RGB by pasting on white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            image = background

        output_buffer = io.BytesIO()
        image.save(output_buffer, format=target_format_upper)
        converted_image_data = output_buffer.getvalue()

        # Save to file and return path
        file_name = f"{uuid.uuid4().hex}.{target_format.lower()}"
        file_path = CONVERTED_DIR / file_name
        with open(file_path, "wb") as f:
            f.write(converted_image_data)
        return str(file_path)

    except Exception as e:
        return f"Error: {str(e)}"

mcp.add_tool(convert_image)

if __name__ == "__main__":
    mcp.run()
