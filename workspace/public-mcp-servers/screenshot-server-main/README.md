# 截图服务器

这个项目是一个截图服务器，使用Python编写。它提供了以下主要功能：

1. **截图功能**：通过调用`take_screenshot_image`工具，可以截取用户屏幕的截图，并将其返回为图像数据。
2. **图像处理**：使用Pillow库对截取的图像进行处理和显示。
3. **MCP服务器**：通过MCP协议与客户端进行通信，提供截图服务。

## 使用方法

1. 确保已安装Python和所需的依赖项。
```
$ uv sync
```
2. 运行`clint.py`文件，启动截图服务器。
```
$ uv run clint.py
```
3. 使用MCP客户端调用`take_screenshot_image`工具，获取屏幕截图。

## 依赖项

- Python 3.x
- Pillow库
- MCP协议相关库

## MCP配置
```
{
  "mcpServers": {
    "mcp-server": {
      "command": "/Users/username/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/username/MCP",
        "run",
        "screenshot.py"
      ]
    }
  }
}
```

## 文件结构

- `screenshot.py`：提供截图功能的MCP服务器。
- `clint.py`：MCP客户端，用于调用截图服务器的工具。
- `README.md`：项目说明文档。