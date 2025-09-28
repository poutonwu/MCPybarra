# mcp_word_document_processor

## Overview

`mcp_word_document_processor` 是一个 Model Context Protocol (MCP) 服务器，提供了一组用于创建、编辑和操作 Word 文档的工具。它允许通过 JSON-RPC 接口与外部系统集成，实现文档自动化处理功能。

该服务器支持创建新文档、打开现有文档、添加段落/标题/表格、搜索替换文本、修改页面边距等常见文档操作。

## Installation

1. 确保安装了 Python 3.10 或更高版本
2. 安装依赖项：

```bash
pip install -r requirements.txt
```

requirements.txt 应包含以下内容：

```
mcp[cli]
python-docx
```

## Running the Server

要启动服务器，请运行以下命令：

```bash
python mcp_word_document_processor.py
```

确保将服务器代码保存为 `mcp_word_document_processor.py` 或相应地调整命令。

## Available Tools

### Document Management
- **create_document**：创建一个新的 Word 文档并返回其句柄
- **open_document(file_path: str)**：打开一个现有的 Word 文档进行编辑
- **save_document(document_handle: str)**：保存当前文档到原始文件路径
- **save_as_document(document_handle: str, file_path: str)**：将文档另存为指定的文件路径
- **create_document_copy(document_handle: str)**：创建文档的一个副本并返回新的句柄

### Content Manipulation
- **add_paragraph(document_handle: str, text: str)**：在文档中添加一个段落
- **add_heading(document_handle: str, text: str, level: int)**：在文档中添加一个指定级别的标题
- **add_table(document_handle: str, rows: int, cols: int)**：在文档中添加一个指定行列数的表格
- **add_page_break(document_handle: str)**：在文档中添加一个分页符

### Search and Replace
- **search_text(document_handle: str, search_term: str)**：在文档中搜索指定的文本
- **find_and_replace(document_handle: str, search_term: str, replace_term: str)**：查找并替换文档中的文本
- **search_and_replace(document_handle: str, search_term: str, replace_term: str)**：查找并替换文档中的文本（与 find_and_replace 相同）

### Deletion Operations
- **delete_paragraph(document_handle: str, paragraph_index: int)**：删除指定索引处的段落
- **delete_text(document_handle: str, text_to_delete: str)**：删除文档中指定的文本

### Table Operations
- **add_table_row(document_handle: str, table_index: int, row_data: list)**：向指定表格添加一行数据
- **delete_table_row(document_handle: str, table_index: int, row_index: int)**：删除指定表格中的指定行
- **edit_table_cell(document_handle: str, table_index: int, row_index: int, col_index: int, new_content: str)**：编辑表格中的单元格内容
- **merge_table_cells(document_handle: str, table_index: int, start_row: int, start_col: int, end_row: int, end_col: int)**：合并表格中的多个单元格
- **split_table(document_handle: str, table_index: int, row_index: int)**：在指定行处分割表格为两个表格

### Document Formatting
- **set_page_margins(document_handle: str, top: float, bottom: float, left: float, right: float)**：设置文档的页面边距（单位：英寸）

### Section Management
- **replace_section(document_handle: str, heading: str, new_content: str)**：根据标题替换章节内容
- **edit_section_by_keyword(document_handle: str, keyword: str, new_content: str)**：根据关键字编辑章节内容