# mcp_screenshot_automation

## Overview

`mcp_screenshot_automation` 是一个 Model Context Protocol (MCP) 服务器，用于通过程序化方式捕获屏幕截图。它提供多个工具接口，允许客户端以不同格式获取或保存当前屏幕内容。

## Installation

在运行服务器之前，请确保已安装以下依赖项：

```bash
pip install -r requirements.txt
```

`requirements.txt` 文件应包含以下内容：

```
mcp[cli]
Pillow
```

## Running the Server

要启动 MCP 服务器，请使用以下命令：

```bash
python mcp_screenshot_automation.py
```

确保脚本文件名与你的 Python 文件一致（例如 `mcp_screenshot_automation.py`）。

## Available Tools

该服务器提供了以下 MCP 工具：

### 1. `take_screenshot`

- **功能描述**: 捕获用户当前屏幕内容并返回图像的二进制数据。
- **参数**: 无
- **返回值**:
  ```json
  {
    "image": "bytes",         // 图像的原始字节数据
    "format": "str",          // 图像格式（如 PNG）
    "size": [width, height]   // 图像尺寸
  }
  ```
- **异常**：如果截图失败，抛出 `RuntimeError`

---

### 2. `take_screenshot_image`

- **功能描述**: 捕获屏幕并返回 Base64 编码的图像数据和 MIME 类型。
- **参数**: 无
- **返回值**:
  ```json
  {
    "image_data": "str",      // Base64 编码的图像字符串
    "mime_type": "str"        // MIME 类型（如 image/png）
  }
  ```
- **异常**：如果截图或编码失败，抛出 `RuntimeError`

---

### 3. `take_screenshot_path`

- **功能描述**: 将屏幕截图保存到指定路径，并返回文件状态信息。
- **参数**:
  - `file_path: str` - 文件保存的完整路径（包括文件名和扩展名）
- **返回值**:
  ```json
  {
    "file_path": "str",       // 实际保存路径
    "exists": true,           // 是否成功创建
    "size": 12345             // 文件大小（字节）
  }
  ```
- **异常**：
  - 如果路径无效，抛出 `ValueError`
  - 如果截图或保存失败，抛出 `RuntimeError`

---