```markdown
# MCP Tools Plan

## Tool 1: `search_images`
- **Function Name**: `search_images`
- **Description**: Searches for images based on user-provided keywords using APIs from Unsplash, Pexels, or Pixabay. Returns structured results containing image links, authors, and other metadata.
- **Parameters**:
  - `keyword` (str): The search term used to find relevant images.
  - `source` (str): The image source to query (`'unsplash'`, `'pexels'`, or `'pixabay'`).
- **Return Value**: A list of dictionaries, where each dictionary contains:
  - `image_url` (str): URL of the image.
  - `author` (str): Name of the image creator.
  - `metadata` (dict): Additional metadata, such as image dimensions and license information.

## Tool 2: `download_image`
- **Function Name**: `download_image`
- **Description**: Downloads an image from a given URL and saves it to a specified file path with a custom filename.
- **Parameters**:
  - `image_url` (str): The URL of the image to be downloaded.
  - `file_name` (str): The desired name for the saved image file, including the extension (e.g., `image.jpg`).
  - `directory` (str): The directory path where the image will be saved.
- **Return Value**: A dictionary containing:
  - `status` (str): The result of the operation (`'success'` or `'failure'`).
  - `file_path` (str): The full path to the saved image file.

## Tool 3: `generate_icon`
- **Function Name**: `generate_icon`
- **Description**: Generates an icon based on a textual description. If a cloud-based generation service is unavailable, it uses a local sample image for simulation.
- **Parameters**:
  - `description` (str): A textual description of the desired icon.
  - `size` (tuple[int, int]): Dimensions of the icon (width, height).
  - `directory` (str): The directory path where the icon will be saved.
- **Return Value**: A dictionary containing:
  - `status` (str): The result of the operation (`'success'` or `'failure'`).
  - `file_path` (str): The full path to the generated icon file.

---

# Server Overview

The MCP server is designed to automate image-related tasks, including searching for images, downloading them, and generating icons based on descriptions. It provides these functionalities via MCP protocol tools, enabling seamless integration with external image sources and local or cloud-based icon generation services.

---

# File to be Generated

The server implementation will be contained within a single Python file named `image_mcp_server.py`.

---

# Dependencies

1. **Python Libraries**:
   - `httpx`: For making HTTP requests to Unsplash, Pexels, and Pixabay APIs.
   - `requests`: For downloading images from URLs.
   - `Pillow (PIL)`: For saving images and handling file formats.
   - `stylecloud`: For generating icons based on textual descriptions.
2. **MCP SDK**:
   - `mcp[cli]`: To implement the MCP protocol for server development.

---
```