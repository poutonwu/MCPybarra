## MCP Tools Plan

### 1. **Function Name**: `search_images`
- **Description**: Searches for images based on user-provided keywords across popular image sources like Unsplash, Pexels, or Pixabay. Returns structured results including image URLs, author information, and other metadata.
- **Parameters**:
  - `keywords` (string, required): The search query for images.
  - `source` (string, optional): Specify the image source (e.g., "unsplash", "pexels", "pixabay"). Defaults to searching all sources.
  - `max_results` (integer, optional): Maximum number of results to return. Defaults to 5.
- **Return Value**: A list of dictionaries, each containing:
  - `url` (string): Direct link to the image.
  - `author` (string): Name of the image author.
  - `source` (string): The platform where the image was found.
  - `license` (string, optional): License type of the image.

### 2. **Function Name**: `download_image`
- **Description**: Downloads an image from a given URL and saves it to a specified directory. Returns the save status and path information.
- **Parameters**:
  - `image_url` (string, required): URL of the image to download.
  - `filename` (string, required): Name to save the file as (excluding extension).
  - `save_dir` (string, optional): Directory path to save the image. Defaults to "./downloads".
- **Return Value**: A dictionary containing:
  - `status` (string): Success or error message.
  - `path` (string): Full path to the saved image file.

### 3. **Function Name**: `generate_icon`
- **Description**: Generates an icon based on a user-provided description and saves it to a specified directory. If no cloud-based service is configured, uses a local sample icon for simulation.
- **Parameters**:
  - `description` (string, required): Text description of the desired icon.
  - `size` (string, optional): Dimensions of the icon (e.g., "64x64"). Defaults to "32x32".
  - `save_dir` (string, optional): Directory path to save the icon. Defaults to "./icons".
- **Return Value**: A dictionary containing:
  - `status` (string): Success or error message.
  - `path` (string): Full path to the saved icon file.

## Server Overview

The MCP server will automate image search, download, and icon generation tasks. It will provide three main functionalities:
1. **Image Search**: Retrieve images from Unsplash, Pexels, or Pixabay based on keywords.
2. **Image Download**: Download and save images from URLs.
3. **Icon Generation**: Generate icons from descriptions, with fallback to local samples if cloud services are unavailable.

## File to be Generated

All server logic will be contained in a single Python file named:
- `mcp_image_server.py`

## Dependencies

The following Python libraries will be required:
- `httpx`: For making HTTP requests to image APIs.
- `Pillow`: For image processing and icon generation (if local simulation is needed).
- `requests`: For downloading images (alternative to `httpx` if preferred).
- `python-dotenv`: For managing environment variables (e.g., API keys).

This plan ensures the server meets the user's requirements while adhering to MCP protocol standards. No additional functionalities beyond those specified are included.