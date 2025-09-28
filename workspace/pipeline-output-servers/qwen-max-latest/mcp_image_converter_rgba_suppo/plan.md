### MCP Tools Plan

#### Tool: `convert_image`
- **Description**: Converts images from one format to another (e.g., PNG, JPEG, BMP, GIF) while preserving transparency for RGBA images. Automatically handles color space conversion and saves the converted image to a specified directory.
- **Parameters**:
  - `input_path` (str): The file path of the input image to be converted.
  - `output_path` (str): The directory where the converted image will be saved.
  - `output_format` (str): The target image format (e.g., "PNG", "JPEG", "BMP", "GIF").
- **Return Value**: A dictionary containing the status of the conversion (`success` or `failure`) and a message describing the result or any errors encountered.

### Server Overview
The MCP server is designed to automate image format conversion. It allows users to convert images between various formats (such as PNG, JPEG, BMP, and GIF) while maintaining transparency for RGBA images. The server performs appropriate color space conversions and provides comprehensive error handling and status feedback.

### File to be Generated
- `mcp_image_converter.py`: This single Python file will contain all the logic necessary for the image conversion server, including tool definitions, error handling, and server initialization.

### Dependencies
- `Pillow`: A Python Imaging Library (PIL) fork that adds support for opening, manipulating, and saving many different image file formats. It will be used for image processing tasks such as format conversion and color space management.