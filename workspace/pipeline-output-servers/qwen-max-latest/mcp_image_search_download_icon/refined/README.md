# mcp_image_search_download_icon

## Overview
This server provides image search, download, and icon generation capabilities via the Model Context Protocol (MCP). It allows integration with LLMs to perform tasks such as searching for images from Unsplash, downloading them to a specified directory, and generating simple icons based on textual descriptions.

## Installation
Before running the server, ensure you have Python 3.10+ installed, then install dependencies using:

```bash
pip install -r requirements.txt
```

Make sure to set the `IMAGE_API_KEY` environment variable with your Unsplash API access key.

## Running the Server
To start the server, run the following command in your terminal:

```bash
python mcp_image_search_download_icon.py
```

By default, the server will communicate over standard input/output (stdio).

## Available Tools

### `search_images`
**Description:**  
Searches for images based on provided keywords using the Unsplash API.

**Parameters:**
- `keywords`: A string of space-separated keywords used to find relevant images.

**Returns:**
A JSON-formatted list of dictionaries containing:
- `image_url`: URL of the found image.
- `author`: Name of the image author/photographer.

**Raises:**
- `ValueError` if keywords are empty or invalid.
- `httpx.HTTPStatusError` if the API request fails.

---

### `download_image`
**Description:**  
Downloads an image from a given URL and saves it to a specified directory.

**Parameters:**
- `image_url`: The URL of the image to download.
- `file_name`: The desired filename for the downloaded image.
- `save_directory`: The directory where the image should be saved.

**Returns:**
A JSON object indicating success or failure, including:
- `status`: `"success"` or `"failure"`.
- `file_path`: Path to the saved image (if successful).
- `error_message`: Error description (if failed).

**Raises:**
- `ValueError` if any parameter is empty or the directory is invalid.
- `httpx.HTTPStatusError` if the image download fails.

---

### `generate_icon`
**Description:**  
Generates a simple icon based on a textual description and saves it to a specified directory.

**Parameters:**
- `description`: A short textual description of the icon content.
- `icon_size`: The size of the icon in pixels (e.g., 64 for a 64x64 icon).
- `save_directory`: The directory where the icon should be saved.

**Returns:**
A JSON object indicating success or failure, including:
- `status`: `"success"` or `"failure"`.
- `file_path`: Path to the generated icon (if successful).
- `error_message`: Error description (if failed).

**Raises:**
- `ValueError` if description is empty or icon size is not positive.
- Any exceptions during image generation.