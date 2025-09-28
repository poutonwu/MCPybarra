# MCP Tools Plan

### Tool 1: `take_screenshot`

*   **Function Name**: `take_screenshot`
*   **Description**: 捕获用户当前全屏内容，并以Base64编码的字符串形式返回PNG图像数据。此字符串可被程序解码和处理。
*   **Parameters**: None
*   **Return Value**:
    *   **Type**: `str`
    *   **Description**: 一个包含PNG图像数据的Base64编码字符串。

### Tool 2: `take_screenshot_image`

*   **Function Name**: `take_screenshot_image`
*   **Description**: 捕获用户当前全屏内容，并返回一个可直接在Web浏览器中显示的Data URI。
*   **Parameters**: None
*   **Return Value**:
    *   **Type**: `str`
    *   **Description**: 一个符合`data:image/png;base64,...`格式的字符串，可直接用于HTML `<img>`标签的`src`属性。

### Tool 3: `take_screenshot_path`

*   **Function Name**: `take_screenshot_path`
*   **Description**: 捕获用户当前全屏内容，并将其保存到用户指定的本地文件路径。如果文件已存在，它将被覆盖。
*   **Parameters**:
    *   `file_path` (`str`): 保存屏幕截图的完整本地文件路径，必须包含文件名和`.png`扩展名 (例如, 'C:/Users/user/Desktop/my_screenshot.png')。
*   **Return Value**:
    *   **Type**: `str`
    *   **Description**: 一条确认消息，指示截图已成功保存到的路径。

# Server Overview

该MCP服务器旨在提供自动化屏幕截图的功能。它允许客户端通过远程调用来捕获用户的屏幕，并根据需求以不同的格式（Base64编码的图像数据、可直接显示的Data URI）返回截图，或者直接将截图保存到本地文件系统中。

# File to be Generated

*   `mcp_screenshot_server.py`

# Dependencies

*   `mcp`
*   `mss`: 用于高效、跨平台地捕获屏幕截图。
*   `Pillow`: 用于处理和保存图像数据。