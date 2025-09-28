# 自动化屏幕截图MCP服务器实现计划

## MCP Tools Plan

### 1. `take_screenshot` 工具
* **Function Name**: `take_screenshot`
* **Description**: 捕获用户当前屏幕内容并以图像对象形式返回
* **Parameters**: 无
* **Return Value**: 返回包含图像数据的字典对象，格式为：
  ```python
  {
    "image": bytes,  # 图像的二进制数据
    "format": str,   # 图像格式（如PNG/JPEG）
    "size": tuple    # 图像尺寸（宽度, 高度）
  }
  ```

### 2. `take_screenshot_image` 工具
* **Function Name**: `take_screenshot_image`
* **Description**: 捕获屏幕并返回可直接显示的图像内容
* **Parameters**: 无
* **Return Value**: 返回包含Base64编码图像数据的字典对象：
  ```python
  {
    "image_data": str,      # Base64编码的图像数据
    "mime_type": str        # MIME类型（如image/png）
  }
  ```

### 3. `take_screenshot_path` 工具
* **Function Name**: `take_screenshot_path`
* **Description**: 将屏幕截图保存到用户指定的本地文件路径，支持自定义文件名
* **Parameters**:
  * `file_path`: str - 文件保存的完整路径（包括文件名和扩展名）
* **Return Value**: 返回包含文件状态的字典对象：
  ```python
  {
    "file_path": str,     # 文件保存的实际路径
    "exists": bool,       # 文件是否存在
    "size": int           # 文件大小（字节）
  }
  ```

## Server Overview
本服务器实现了一个自动化屏幕截图解决方案，通过MCP协议提供三种截图功能：内存中的图像对象、可直接显示的图像数据以及保存到指定路径的截图。所有功能都基于Python实现，使用Pillow库进行屏幕捕获和图像处理。

## File to be Generated
* **File Name**: `screenshot_mcp_server.py`
* 该文件将包含完整的MCP服务器实现，包括必要的导入、服务器初始化、工具函数定义和运行逻辑。

## Dependencies
* **mcp[cli]**: `pip install mcp[cli]` - MCP协议核心库
* **Pillow**: `pip install pillow` - 用于屏幕截图和图像处理
* **Python 3.10+**: 确保支持异步IO和类型提示特性