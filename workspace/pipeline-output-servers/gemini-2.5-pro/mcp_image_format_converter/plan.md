<thought>
The user wants me to create a detailed implementation plan for an MCP server that automates image format conversion.

Here's my plan of action:

1.  **Deconstruct the Request**: I'll break down the user's request into the core functionalities.
    *   **Functionality**: Convert an image from a source format to a target format.
    *   **Inputs**:
        *   `source_path`: The full path to the input image file.
        *   `output_dir`: The directory where the converted image will be saved.
        *   `target_format`: The desired output format (e.g., 'JPEG', 'PNG', 'BMP').
    *   **Outputs**:
        *   A success message with the path to the newly created file.
        *   A detailed error message if the conversion fails.
    *   **Key Features**:
        *   Support for various formats (PNG, JPEG, BMP, GIF).
        *   Handle RGBA (transparency).
        *   Automatic color space conversion.
        *   Robust error handling.
        *   Status feedback.

2.  **Formulate a Research Strategy**: The core of this task is image manipulation. The best library for this in Python is `Pillow` (a fork of PIL). I need to confirm the best practice for handling transparency, especially when converting from a format that supports it (like PNG) to one that doesn't (like JPEG). The Tavily search confirmed my initial thought process. The key is using `image.convert('RGB')` before saving to a format like JPEG. This will handle the alpha channel by blending it against a default black background, or I can implement a more sophisticated approach by creating a new image with a white background and pasting the RGBA image onto it. The search results confirm that a simple `.convert("RGB")` is the most direct method.

3.  **Execute Research**: I have already executed the search. The key takeaway is the method `image.convert('RGB').save('output.jpg')`. This is a clean and effective way to handle the transparency layer when converting to JPEG. This confirms that the `Pillow` library is sufficient and no other external libraries are needed for the core conversion logic.

4.  **Generate the Final Plan**: Now I will structure the final plan according to the user's specified format. I will create a single MCP tool, `convert_image`, and detail its parameters and return values. I will also outline the server overview, the single file to be generated, and the necessary dependencies (`mcp` and `Pillow`). The plan will be entirely self-contained within a single Python file as requested.# MCP Tools Plan

This section details the design of the MCP tool required for the image format conversion server.

### Tool 1: `convert_image`

*   **Function Name**: `convert_image`
*   **Description**: Converts an image file from a source format to a specified target format. The tool handles various image types, including those with transparency (RGBA). It performs necessary color space conversions and saves the resulting image to a designated output directory. It provides clear feedback on success or failure.
*   **Parameters**:
    *   `source_path` (str): The absolute or relative path to the source image file (e.g., `/path/to/image.png`). This parameter is required.
    *   `output_dir` (str): The path to the directory where the converted image will be saved. The directory must exist. This parameter is required.
    *   `target_format` (str): The desired output image format (e.g., 'JPEG', 'PNG', 'BMP', 'GIF'). This parameter is required.
*   **Return Value**:
    *   **On Success** (str): A success message indicating the path of the newly created image, for example: `{"status": "success", "message": "Image converted successfully.", "output_path": "/path/to/output/image.jpeg"}`.
    *   **On Failure** (str): A JSON formatted string containing an error message detailing the cause of failure, such as file not found, invalid format, or permission errors. For example: `{"status": "error", "message": "Source file not found at /path/to/nonexistent/image.png"}`.

# Server Overview

The MCP server will provide a single tool, `convert_image`, to automate the conversion of image files between various formats like PNG, JPEG, BMP, and GIF. The server is designed to correctly handle images with transparency (RGBA color mode) by automatically managing color space transformations during the conversion process. It will save the converted files to a user-specified directory and provide comprehensive status feedback, including detailed error messages for any issues encountered during the process.

# File to be Generated

All the server logic, including the MCP tool definition and dependencies, will be contained within a single Python file.

*   **Filename**: `mcp_image_converter.py`

# Dependencies

The following third-party Python libraries are required for the server's functionality. They should be installed via pip.

*   `mcp`: The core library for creating the MCP server.
*   `Pillow`: A powerful image processing library used for opening, converting, and saving images.