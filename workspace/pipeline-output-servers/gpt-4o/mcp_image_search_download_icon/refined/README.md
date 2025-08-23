# mcp_image_search_download_icon

## Overview

This MCP server provides tools for searching images from Unsplash, Pexels, or Pixabay, downloading them to a specified directory, and generating simple icons based on textual descriptions.

---

## Installation

To install the required dependencies:

1. Ensure you have Python 3.10+ installed.
2. Install the MCP SDK and `httpx`:
   ```bash
   pip install mcp[cli] httpx
   ```
3. Additionally, install Pillow for image generation:
   ```bash
   pip install pillow
   ```

You may also use a `requirements.txt` file containing:
```
mcp[cli]
httpx
Pillow
```

Then install via:
```bash
pip install -r requirements.txt
```

---

## Running the Server

To start the server, run the following command in your terminal:
```bash
python mcp_image_search_download_icon.py
```

Make sure to replace `mcp_image_search_download_icon.py` with the actual filename where the server code is saved.

---

## Available Tools

### 1. `search_images`

**Description:**  
Searches for images based on a keyword using APIs from Unsplash, Pexels, or Pixabay.

**Arguments:**
- `keyword`: The search term (e.g., `"sunset"`).
- `source`: The image source (`"unsplash"`, `"pexels"`, or `"pixabay"`).

**Returns:**  
A JSON list of dictionaries containing:
- `image_url`: URL of the image.
- `author`: Name of the image creator.
- `metadata`: Additional info like dimensions and license.

---

### 2. `download_image`

**Description:**  
Downloads an image from a given URL and saves it to a specified directory with a custom filename.

**Arguments:**
- `image_url`: The URL of the image to download.
- `file_name`: The desired name for the saved image (including extension).
- `directory`: The path to the directory where the image will be saved.

**Returns:**  
A JSON object indicating success or failure, including the `file_path`.

---

### 3. `generate_icon`

**Description:**  
Generates a simple icon based on a textual description and saves it as a PNG file.

**Arguments:**
- `description`: A brief text describing the icon (e.g., `"sun and clouds"`).
- `size`: A tuple specifying width and height (e.g., `(128, 128)`).
- `directory`: The directory to save the generated icon.

**Returns:**  
A JSON object indicating success or failure, including the `file_path`.