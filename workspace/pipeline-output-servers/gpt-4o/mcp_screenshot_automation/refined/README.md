# mcp_screenshot_automation

## Overview

The `mcp_screenshot_automation` server provides a set of tools to capture and manage screenshots via the MCP protocol. It allows for capturing the current screen content and returning it in various formats or saving it directly to a file.

## Installation

To install dependencies, run:

```bash
pip install -r requirements.txt
```

Ensure you have Python 3.10+ installed before proceeding.

## Running the Server

To start the server, execute the script from the command line:

```bash
python mcp_screenshot_automation.py
```

## Available Tools

### `take_screenshot`

Captures the current screen content and returns it as an image object. This is useful when direct access to the image data is needed within the application logic.

**Returns:**  
- `status`: "success" or "error"
- `image`: The captured screenshot as an image object (on success)

---

### `take_screenshot_image`

Captures the current screen content and encodes it into a Base64 string for easy transmission or display in web interfaces.

**Returns:**  
- `status`: "success" or "error"
- `image_bytes`: Base64-encoded string of the screenshot (on success)

---

### `take_screenshot_path`

Captures the current screen and saves it to the specified file path. Only `.png`, `.jpg`, `.jpeg`, `.bmp`, and `.gif` formats are supported.

**Arguments:**
- `file_path`: Full path including filename and extension where the screenshot will be saved.

**Returns:**  
- `status`: "success" or "error"
- `file_path`: The path where the screenshot was saved (on success)
- `message`: Error message (on failure)