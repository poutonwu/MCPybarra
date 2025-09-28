# mcp_arxiv_paper_manager

## Overview

`mcp_arxiv_paper_manager` 是一个基于 MCP 协议的服务器，用于与 arXiv 学术论文进行交互。它提供了一组工具来搜索、下载、列出和读取 arXiv 上发布的论文内容。

## Installation

首先确保你已安装 Python 3.10 或更高版本。然后使用 pip 安装项目依赖：

```bash
pip install mcp[cli]
pip install PyPDF2
pip install arxiv
```

将以上依赖保存到 `requirements.txt` 文件中以方便部署：

```
mcp[cli]
PyPDF2
arxiv
```

## Running the Server

运行服务器的命令如下：

```bash
python mcp_arxiv_paper_manager.py
```

确保你的 Python 脚本文件名为 `mcp_arxiv_paper_manager.py` 或根据实际文件名调整命令。

## Available Tools

以下是该 MCP 服务器提供的可用工具及其功能描述：

### 1. `search_papers`

**功能：** 根据用户输入的关键词在 arXiv 上搜索学术论文。

**参数：**
- `query`: 搜索关键词（必填）。
- `max_results`: 返回的最大结果数，默认为 10。
- `sort_by`: 排序方式，支持 `"relevance"`（相关性）或 `"lastUpdatedDate"`（更新时间）。
- `sort_order`: 排序顺序，支持 `"ascending"`（升序）或 `"descending"`（降序），默认为 `"descending"`。

**示例：**
```python
search_papers(query="quantum computing", max_results=5, sort_by="relevance", sort_order="descending")
```

---

### 2. `download_paper`

**功能：** 下载指定 ID 的 arXiv 论文 PDF 并本地存储。

**参数：**
- `paper_id`: 论文的唯一标识符（例如 `"arXiv:1234.56789"`）。

**示例：**
```python
download_paper(paper_id="arXiv:1234.56789")
```

---

### 3. `list_papers`

**功能：** 列出所有本地存储的论文文件，可选过滤和排序。

**参数：**
- `filter_by`: 过滤条件（目前未实现具体过滤逻辑）。
- `sort_by`: 排序字段，如 `"title"` 或 `"download_date"`。

**示例：**
```python
list_papers(filter_by="author:John Doe", sort_by="title")
```

---

### 4. `read_paper`

**功能：** 读取并返回本地存储的 PDF 文件文本内容。

**参数：**
- `file_path`: 本地 PDF 文件路径。

**示例：**
```python
read_paper(file_path="./downloaded_papers/arXiv_1234_56789.pdf")
```

---