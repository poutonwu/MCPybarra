# mcp_screenshot_automation

## Overview

The `mcp_screenshot_automation` server is a Model Context Protocol (MCP) service that enables taking screenshots of the current screen and returning or saving them in various formats. It provides tools for capturing screenshots as base64-encoded image data, HTML-ready image URLs, or saving them to a specified file path.

## Installation

Before running the server, ensure you have Python 3.10+ installed and install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include the following packages:

```
mcp[cli]
pillow
```

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_screenshot_automation.py
```

This will launch the MCP server using the default `stdio` transport protocol.

## Available Tools

The server exposes the following tools via the MCP protocol:

### `take_screenshot`

Captures the user's current screen and returns the content as an image object.

- **Returns:** A JSON string containing the image data in base64 format.
- **Raises:** Exception if there is an issue capturing the screen.

---

### `take_screenshot_image`

Captures the user's current screen and returns the content as a displayable image.

- **Returns:** A JSON string containing the image data in base64 format suitable for direct display in HTML.
- **Raises:** Exception if there is an issue capturing the screen.

---

### `take_screenshot_path(file_path: str, file_name: str)`

Captures the user's current screen and saves it to a specified local file path with a custom filename.

- **Args:**
  - `file_path`: The local file path where the screenshot will be saved.
  - `file_name`: The custom filename for the saved screenshot.
- **Returns:** A JSON string indicating the success of the operation, including the full path where the file was saved.
- **Raises:**
  - `ValueError`: If the file_path or file_name is invalid.
  - `Exception`: If there is an issue capturing or saving the screenshot.