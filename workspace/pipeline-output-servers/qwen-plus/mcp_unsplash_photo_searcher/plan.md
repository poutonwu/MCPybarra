# MCP 服务器实现计划 - 自动化图片检索处理

## MCP Tools Plan

### `search_photos` 工具

- **Function Name**: `search_photos`
- **Description**: 在 Unsplash 平台根据关键词、分页、排序、颜色和图片方向等条件搜索图片，并返回包含图片 ID、描述、图片多尺寸 URL、宽度和高度等详细信息的结果列表。
- **Parameters**:

| 参数名 | 类型 | 描述 |
| --- | --- | --- |
| query | string | 搜索关键词（必填） |
| page | integer | 分页编号，默认为 1 |
| per_page | integer | 每页结果数量，默认为 10，最大不超过 30 |
| order_by | string | 排序方式：latest, oldest, relevant，默认为 relevant |
| color | string | 图片颜色过滤，如 red, blue, black 等（可选） |
| orientation | string | 图片方向：landscape, portrait, squarish（可选） |

- **Return Value**:
返回一个 JSON 格式的字符串，包含以下字段：

```json
{
  "results": [
    {
      "id": "string",
      "description": "string",
      "urls": {
        "raw": "string",
        "full": "string",
        "regular": "string",
        "small": "string",
        "thumb": "string"
      },
      "width": integer,
      "height": integer
    }
  ],
  "total": integer,
  "page": integer,
  "per_page": integer
}
```

---

## Server Overview

该 MCP 服务器用于通过 Unsplash API 实现自动化图片检索功能。用户可以使用 `search_photos` 工具，根据关键词、分页、排序、颜色和方向等参数进行图片搜索，并获取包括图片 ID、描述、不同尺寸的 URL、宽度和高度在内的详细信息。

---

## File Structure

该项目将采用单一 Python 文件结构来实现 FastMCP 服务器：

```
unsplash_mcp_server.py
```

该文件将包含以下内容：
- 初始化 FastMCP 服务器
- 定义 `search_photos` 工具函数及其参数
- 使用 `httpx` 发起对 Unsplash API 的请求
- 处理并返回格式化的响应数据

---

## Dependencies

- `mcp[cli]`：用于构建 MCP 服务器的核心 SDK
- `httpx`：用于异步 HTTP 请求
- `python-dotenv`（可选）：用于管理 API 密钥

Unsplash API 要求授权请求头，因此需要注册开发者账号并获取 Access Key。