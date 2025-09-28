# mcp_screenshot_automation

## Overview

The `mcp_screenshot_automation` server provides a set of tools for capturing screenshots and returning them in various formats. It is built using the Model Context Protocol (MCP) and allows seamless integration with LLM-based applications that require screen capture capabilities.

This server uses the `Pillow` and `pyautogui` libraries to ensure robust screenshot capture across different environments and operating systems.

---

## Installation

Before running the server, make sure to install all required dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, create one with the following dependencies:

```
mcp[cli]
Pillow
pyautogui
```

---

## Running the Server

To start the server, run the Python script from the command line:

```bash
python mcp_screenshot_automation.py
```

Ensure the script file name matches the one used in your project (e.g., `screenshot_server.py` or similar).

---

## Available Tools

Below is a list of available MCP tools provided by this server:

### 1. `take_screenshot()`

Captures the current screen content and returns it as a base64-encoded PNG image string.

**Returns:**  
A base64-encoded string representing the screenshot in the format:  
`data:image/png;base64,<encoded_string>`

**Raises:**  
- Exception if the screenshot capture fails.

---

### 2. `take_screenshot_image()`

Captures the current screen and returns the image content as a base64-encoded string for direct display.

**Returns:**  
A base64-encoded string of the screenshot in PNG format:  
`data:image/png;base64,<encoded_string>`

**Raises:**  
- Exception if the screenshot capture or encoding fails.

---

### 3. `take_screenshot_path(path: str, filename: str = "screenshot.png")`

Captures the current screen and saves the screenshot to a specified local file path.

**Args:**
- `path`: The directory where the screenshot will be saved.
- `filename`: Optional custom filename (default is `"screenshot.png"`).

**Returns:**  
A confirmation string like:  
`Screenshot saved to /path/to/screenshot.png`

**Raises:**  
- Exception if the screenshot capture or file save operation fails.

---