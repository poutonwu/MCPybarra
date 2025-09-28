# mcp_unsplash_photo_searcher

## Overview

`mcp_unsplash_photo_searcher` 是一个 MCP（Model Context Protocol）服务器，它通过 Unsplash API 提供图片搜索功能。该工具允许大语言模型根据关键词、分页、排序方式、颜色和图片方向等条件搜索高质量的图片资源。

## Installation

确保已安装 Python 3.10+，然后运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

你需要在 `requirements.txt` 文件中包含以下基本依赖项：

```
mcp[cli]
httpx
```

## Running the Server

在运行服务器之前，请确保设置好环境变量中的 Unsplash Access Key：

```bash
export UNSPLASH_ACCESS_KEY='your-unsplash-access-key'
```

如果需要代理，请同时设置代理环境变量：

```bash
export HTTP_PROXY='http://127.0.0.1:7890'
export HTTPS_PROXY='http://127.0.0.1:7890'
```

启动服务器：

```bash
python mcp_unsplash_photo_searcher.py
```

## Available Tools

### `search_photos`

在 Unsplash 平台根据关键词、分页、排序、颜色和图片方向等条件搜索图片。

#### Parameters:

- **query** (str): 搜索关键词（必填）
- **page** (int): 分页编号，默认为 1
- **per_page** (int): 每页结果数量，默认为 10，最大不超过 30
- **order_by** (str): 排序方式：latest, oldest, relevant，默认为 relevant
- **color** (str): 图片颜色过滤，如 red, blue, black 等（可选）
- **orientation** (str): 图片方向：landscape, portrait, squarish（可选）

#### Returns:

一个包含以下字段的字典：

- **results**: 包含图片信息的列表，每项包括：
  - id: 图片ID
  - description: 图片描述
  - urls: 包含不同尺寸URL的对象（raw, full, regular, small, thumb）
  - width: 图片宽度
  - height: 图片高度
- **total**: 总结果数
- **page**: 当前页码
- **per_page**: 每页结果数

#### Raises:

- ValueError: 如果必填参数缺失或参数值无效
- httpx.HTTPStatusError: 如果API请求失败