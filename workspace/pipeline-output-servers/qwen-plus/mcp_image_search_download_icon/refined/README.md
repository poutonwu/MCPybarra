# mcp_image_search_download_icon

## Overview

The `mcp_image_search_download_icon` server provides a set of tools for searching images via the Pexels API, downloading them to local storage, and generating simple icons based on textual descriptions. It is built using the Model Context Protocol (MCP) and allows seamless integration with LLMs for image-related tasks.

This server supports:
- Searching for high-quality images from Pexels.
- Downloading images to a local directory.
- Generating simple icon graphics locally if no cloud service is available.

---

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes at least the following packages:

```
mcp[cli]
requests
Pillow
```

---

## Running the Server

To start the server, run the following command:

```bash
python mcp_image_search_download_icon.py
```

By default, the server will use the `stdio` transport protocol as specified in the `mcp.run()` call.

---

## Available Tools

### 1. `search_images`

**Description:**  
Searches for images on Pexels based on a keyword query and returns structured results including URLs, photographer names, and source links.

**Parameters:**
- `query`: Search keywords (e.g., "nature landscape") — **required**.
- `per_page`: Number of results to return (default: 5, max: 10).

**Returns:**
A JSON list containing:
- `url`: High-resolution image URL.
- `photographer`: Name of the photographer.
- `source`: Link to the image page on Pexels.

---

### 2. `download_image`

**Description:**  
Downloads an image from a given URL and saves it to a local directory (`downloads/` by default).

**Parameters:**
- `image_url`: URL of the image to download — **required**.
- `filename`: Name to save the file as — **required**.
- `save_dir`: Directory to save the image (default: `downloads`).

**Returns:**
A JSON object indicating success or failure, and the full path where the image was saved.

---

### 3. `generate_icon`

**Description:**  
Generates a simple icon based on a description (e.g., "settings icon blue color"). If no cloud generation is enabled, it creates a basic icon locally using Pillow.

**Parameters:**
- `description`: Description of the icon (e.g., "settings icon red color") — **required**.
- `size`: Icon dimensions (default: `(64, 64)`).
- `use_cloud`: Whether to use a cloud-based icon generator (currently not implemented).

**Returns:**
A JSON object indicating success or failure, and the full path where the icon was saved (in the `icons/` directory).