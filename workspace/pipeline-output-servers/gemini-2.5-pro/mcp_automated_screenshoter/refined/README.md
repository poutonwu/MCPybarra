# mcp_automated_screenshoter

## Overview

The `mcp_automated_screenshoter` is an MCP (Model Context Protocol) server that enables a large language model (LLM) to programmatically take screenshots of the user's screen. It provides multiple tools for capturing and returning screenshot data in different formats or saving them directly to disk.

This server supports:
- Returning screenshots as Base64-encoded strings.
- Generating Data URIs suitable for direct image display in web interfaces.
- Saving screenshots to local file paths with security checks.

## Installation

Before running the server, install the required dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, create one with the following content:

```
mcp[cli]
mss
Pillow
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_automated_screenshoter.py
```

By default, the server uses the standard input/output (`stdio`) transport protocol.

## Available Tools

The server provides the following MCP tools:

### 1. `take_screenshot()`

Captures a full-screen screenshot and returns the image data as a Base64-encoded string within a JSON object. This is useful for programmatic processing or storage.

**Returns:**  
JSON string containing `"image_base64"` key or `"error"` if failed.

**Example:**
```python
take_screenshot()
```

---

### 2. `take_screenshot_image()`

Captures a full-screen screenshot and returns a Base64-encoded Data URI formatted as `data:image/png;base64,...`. This can be used directly in HTML `<img>` tags for visualization.

**Returns:**  
JSON string containing `"image_data_uri"` key or `"error"` if failed.

**Example:**
```python
take_screenshot_image()
```

---

### 3. `take_screenshot_path(file_path: str)`

Captures a full-screen screenshot and saves it to the specified `.png` file path. Includes validation and security checks to prevent invalid paths or directory traversal attacks.

**Arguments:**
- `file_path`: The absolute file path where the screenshot will be saved. Must end in `.png`.

**Returns:**  
JSON string confirming the save location on success or an error message.

**Example:**
```python
take_screenshot_path(file_path="C:/Users/user/Desktop/screenshot.png")
```