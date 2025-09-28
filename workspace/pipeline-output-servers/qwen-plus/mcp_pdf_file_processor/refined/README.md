# mcp_pdf_file_processor

## Overview
`mcp_pdf_file_processor` 是一个基于 Model Context Protocol (MCP) 的 PDF 文件处理服务器。它提供了一系列工具，用于合并、提取、搜索和查找相关的 PDF 文件。

## Installation
确保你已经安装了 Python 3.10+，然后使用 pip 安装依赖：

```bash
pip install -r requirements.txt
```

你需要的依赖包括：
- `mcp[cli]`
- `PyPDF2`
- `pdfplumber`

## Running the Server
要运行服务器，请执行以下命令：

```bash
python mcp_pdf_file_processor.py
```

这将启动 MCP 服务器，并使其通过标准输入/输出进行通信。

## Available Tools

### `merge_pdfs`
**描述**: 将多个 PDF 文件合并为一个 PDF 文件。  
**参数**:  
- `input_files`: 要合并的 PDF 文件路径列表。
- `output_file`: 合并后的 PDF 输出文件路径。  
**功能**: 验证文件路径后，将所有页面添加到一个新的 PDF 中并保存。

---

### `extract_pages`
**描述**: 从 PDF 文件中提取指定页码的内容，并保存为新的 PDF。  
**参数**:  
- `input_file`: 源 PDF 文件路径。
- `page_numbers`: 要提取的页码列表（从 1 开始计数）。
- `output_file`: 提取后的新 PDF 文件路径。  
**功能**: 读取源 PDF 并仅提取指定页码，创建一个新的 PDF 文件。

---

### `search_pdfs`
**描述**: 在指定目录中搜索符合特定正则表达式模式的 PDF 文件。  
**参数**:  
- `directory`: 要搜索的目录路径。
- `pattern`: 匹配 PDF 文件名的正则表达式。  
**功能**: 返回所有匹配的 PDF 文件路径。

---

### `merge_pdfs_ordered`
**描述**: 根据文件名中的模式按顺序合并 PDF 文件。  
**参数**:  
- `directory`: 包含 PDF 文件的目录路径。
- `order_pattern`: 用于确定合并顺序的文件名模式。
- `output_file`: 合并后的 PDF 输出文件路径。
- `exact_match`: 是否使用精确匹配（默认为 False）。  
**功能**: 查找匹配的 PDF 文件，按字母顺序排序并合并成一个文件。

---

### `find_related_pdfs`
**描述**: 基于文件名和内容相似性查找与目标 PDF 相关的文件。  
**参数**:  
- `target_file`: 目标 PDF 文件路径。
- `search_directory`: 要搜索相关文件的目录路径。  
**功能**: 分析文件名和文本内容，返回与目标文件相关的 PDF 列表。