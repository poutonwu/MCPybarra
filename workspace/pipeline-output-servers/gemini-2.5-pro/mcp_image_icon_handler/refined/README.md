# mcp_image_icon_handler

## Overview

The `mcp_image_icon_handler` is a Model Context Protocol (MCP) server that provides tools for searching, downloading, and generating images. It supports image search from Unsplash, Pexels, and Pixabay, allows downloading of images to the local filesystem, and includes functionality to generate simple text-based icons programmatically.

This server is useful in scenarios where an LLM needs to interact with external image sources or create placeholder visual assets.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed and then install the required dependencies:

```bash
pip install -r requirements.txt
```

A sample `requirements.txt` file should include:

```
mcp[cli]
httpx
Pillow
```

---

## Running the Server

To start the server, run the Python script using:

```bash
python mcp_image_icon_handler.py
```

Ensure that environment variables for API keys are set before launching the server:

```bash
export UNSPLASH_API_KEY=your_unsplash_key
export PEXELS_API_KEY=your_pexels_key
export PIXABAY_API_KEY=your_pixabay_key
```

If not provided, default keys are used (not recommended for production).

---

## Available Tools

### 1. `search_images`

**Description:**  
Searches for images based on a keyword from multiple online sources: Unsplash, Pexels, and Pixabay.

**Parameters:**
- `query`: Search term (e.g., "nature", "technology")
- `sources`: List of sources to use (`unsplash`, `pexels`, `pixabay`)
- `per_page`: Number of results per source (default: 10)

**Returns:**  
JSON list of image results including URL, photographer, description, and source.

---

### 2. `download_image`

**Description:**  
Downloads an image from a given URL or local path and saves it to a specified directory.

**Parameters:**
- `image_url`: Direct image URL or local file path
- `filename`: Name to save the image as (e.g., `photo.jpg`)
- `save_dir`: Directory to save the file (default: `./downloads`)

**Returns:**  
JSON object indicating success or error, with absolute path to the saved file if successful.

---

### 3. `generate_icon`

**Description:**  
Generates a simple icon with a solid background and centered text label.

**Parameters:**
- `description`: Text to display on the icon (e.g., "App")
- `size`: Dimensions of the icon (width, height), defaults to `(128, 128)`
- `filename`: Optional custom filename (e.g., `app_icon.png`)
- `save_dir`: Directory to save the icon (default: `./icons`)

**Returns:**  
JSON object indicating success or error, with absolute path to the generated icon PNG file.