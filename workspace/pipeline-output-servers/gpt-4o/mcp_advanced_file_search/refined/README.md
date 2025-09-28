# mcp_advanced_file_search

## Overview

`mcp_advanced_file_search` 是一个基于 Model Context Protocol (MCP) 的 Windows 文件搜索服务器，利用 `everything.dll` 提供快速、高效的本地文件和文件夹检索服务。

该服务器提供了两个主要工具：

- **`search_files`**：根据关键词、正则表达式等条件搜索系统中的文件和文件夹。
- **`get_file_details`**：获取指定文件或文件夹的详细信息（如大小、创建时间、修改时间、属性等）。

适用于需要通过自然语言与本地文件系统交互的应用场景。

## Installation

在运行服务器之前，请确保已安装以下依赖项：

1. Python 3.10 或更高版本
2. MCP SDK 和 CLI 支持

执行以下命令安装所需依赖：

```bash
pip install mcp[cli]
```

此外，还需要将 [Everything](https://www.voidtools.com/) 的动态链接库 (`Everything64.dll`) 安装到系统路径或项目根目录。当前代码中默认路径为：

```
E:\Everything\dll\Everything64.dll
```

请根据实际情况调整路径或复制 DLL 到相应位置。

## Running the Server

要启动服务器，请运行以下命令：

```bash
python mcp_advanced_file_search.py
```

确保脚本文件名与实际保存的 `.py` 文件一致。

服务器默认通过标准输入/输出（stdio）运行，适用于本地开发和测试环境。

## Available Tools

### `search_files`

**Description:**  
使用 Everything 引擎在 Windows 系统上搜索文件和文件夹。

**Parameters:**
- `query` (str): 搜索查询字符串。
- `case_sensitive` (bool, optional): 是否区分大小写，默认 `False`。
- `whole_word_match` (bool, optional): 是否匹配完整单词，默认 `False`。
- `regex` (bool, optional): 是否启用正则表达式，默认 `False`。
- `sort_by` (str, optional): 排序方式，支持 `'name'`, `'size'`, `'date_created'`, `'date_modified'`，默认 `'name'`。
- `limit` (int, optional): 返回结果的最大数量，默认 `100`。

**Returns:**  
JSON 格式的字符串，包含文件列表及其基本信息（名称、路径、大小、创建/修改日期、属性等）。

**Example:**
```python
search_files(query="*.txt", case_sensitive=False, regex=False, sort_by="name", limit=10)
```

---

### `get_file_details`

**Description:**  
获取指定文件或文件夹的详细信息。

**Parameters:**
- `file_path` (str): 要查询的文件或文件夹的完整路径。

**Returns:**  
JSON 格式的字符串，包含文件详细信息（名称、路径、大小、创建/修改日期、属性等）。

**Example:**
```python
get_file_details(file_path="C:\\Path\\To\\example.txt")
```

---