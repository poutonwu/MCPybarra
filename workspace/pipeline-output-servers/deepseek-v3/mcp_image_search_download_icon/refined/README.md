# mcp_image_search_download_icon

## Overview
This MCP server provides tools for searching images from multiple sources (Unsplash, Pexels, Pixabay), downloading images from URLs, and generating simple icons based on text descriptions.

## Installation
Ensure you have Python 3.10+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

The following packages are required:
- `mcp[cli]`
- `httpx`
- `Pillow`

## Running the Server
Run the server using the following command:

```bash
python mcp_image_search_download_icon.py
```

Make sure the script file is named appropriately or adjust the command accordingly.

## Available Tools

### `search_images`
Searches for images based on keywords across supported platforms (Unsplash, Pexels, Pixabay). You can optionally specify a source and the maximum number of results to return.

**Parameters:**
- `keywords` (required): Search query for images.
- `source` (optional): Specify image source ("unsplash", "pexels", "pixabay").
- `max_results` (optional): Maximum number of results to return (default: 5).

---

### `download_image`
Downloads an image from a given URL and saves it to a specified directory.

**Parameters:**
- `image_url` (required): URL of the image to download.
- `filename` (required): Name to save the file as (without extension).
- `save_dir` (optional): Directory path to save the image (default: "./downloads").

---

### `generate_icon`
Generates a basic icon with a background color and centered text based on a description.

**Parameters:**
- `description` (required): Text description of the desired icon.
- `size` (optional): Dimensions of the icon (default: "32x32").
- `save_dir` (optional): Directory path to save the icon (default: "./icons").