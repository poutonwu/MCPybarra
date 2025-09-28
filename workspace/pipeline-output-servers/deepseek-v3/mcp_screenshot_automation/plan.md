### MCP Tools Plan (Final)

#### 1. `take_screenshot`
- **Description**: Captures the current screen content and returns it as a `PIL.Image` object.
- **Parameters**: None.
- **Return Value**: A `PIL.Image` object representing the screenshot.

#### 2. `take_screenshot_image`
- **Description**: Captures the current screen and returns the image content as a base64-encoded string for direct display.
- **Parameters**: None.
- **Return Value**: A base64-encoded string (e.g., `"data:image/png;base64,..."`) of the screenshot in PNG format.

#### 3. `take_screenshot_path`
- **Description**: Captures the current screen and saves the screenshot to a user-specified local file path with an optional custom filename.
- **Parameters**:
  - `path` (str): The directory path where the screenshot will be saved.
  - `filename` (str, optional): The custom filename (e.g., `"custom.png"`). Defaults to `"screenshot.png"`.
- **Return Value**: A confirmation string (e.g., `"Screenshot saved to /path/to/custom.png"`).

---

### Server Overview
The MCP server will automate screenshot capture, providing three methods to retrieve screenshots: as an image object, a displayable base64 string, or a saved file. This server is designed for cross-platform compatibility (Windows, Linux, macOS).

---

### File to be Generated
- **Filename**: `mcp_screenshot_server.py`

---

### Dependencies
- **Required Libraries**:
  - `mcp[cli]`: For MCP server functionality.
  - `Pillow` (PIL): For image capture and manipulation (supports `ImageGrab` on Windows, Linux, and macOS).
  - `pyautogui`: For cross-platform screenshot capture (fallback if `Pillow` lacks OS support).
  - `base64` (built-in): For encoding images to base64 strings.

---

### Implementation Notes
1. **Primary Library**: `Pillow` (`ImageGrab.grab()`) will be the first choice for screenshot capture due to its simplicity and direct support for `PIL.Image` objects.
2. **Fallback Library**: If `Pillow` fails on certain platforms (e.g., Linux), `pyautogui.screenshot()` will be used as a backup.
3. **Base64 Encoding**: The `base64` module will encode `PIL.Image` objects to strings for `take_screenshot_image`.
4. **Error Handling**: Input validation (e.g., path existence) and platform-specific exceptions will be handled explicitly. 

No further research is needed. The plan is ready for implementation.