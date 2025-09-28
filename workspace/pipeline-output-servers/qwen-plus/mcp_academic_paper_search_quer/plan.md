# MCP 服务器实现计划：学术论文搜索与查询

## MCP 工具计划

### 1. `search_papers` 工具

- **功能**：根据关键词和结果数量限制搜索学术论文，返回来自 Semantic Scholar 和 Crossref 的格式化论文列表
- **参数**：
  - `keywords` (str, 必填)：用于搜索的关键词
  - `limit` (int, 可选，默认为 5)：返回结果的最大数量
- **返回值**：
  - 返回包含以下字段的 JSON 数组：
    - `title` (str)：论文标题
    - `authors` (List[str])：作者列表
    - `year` (int)：发表年份
    - `doi` (str)：论文的 DOI 编号
    - `source` (str)：来源（"Semantic Scholar" 或 "Crossref"）

### 2. `fetch_paper_details` 工具

- **功能**：根据论文 ID（如 DOI 或 Semantic Scholar ID）和指定来源获取论文详细信息
- **参数**：
  - `paper_id` (str, 必填)：论文的唯一标识符（DOI 或 Semantic Scholar ID）
  - `source` (str, 必填)：指定数据源（"Semantic Scholar" 或 "Crossref"）
- **返回值**：
  - 包含以下字段的 JSON 对象：
    - `title` (str)：论文标题
    - `authors` (List[str])：作者列表
    - `abstract` (str)：论文摘要
    - `publication_venue` (str)：出版场所（期刊/会议名称）

### 3. `search_by_topic` 工具

- **功能**：根据主题关键词、可选的年份范围和结果数量限制搜索论文，优先使用 Semantic Scholar 并支持回退到通用搜索
- **参数**：
  - `topic` (str, 必填)：主题关键词
  - `year_range` (str, 可选)：年份范围（格式："YYYY-YYYY"）
  - `limit` (int, 可选，默认为 5)：返回结果的最大数量
- **返回值**：
  - 返回包含以下字段的 JSON 数组：
    - `title` (str)：论文标题
    - `authors` (List[str])：作者列表
    - `year` (int)：发表年份
    - `doi` (str)：论文的 DOI 编号
    - `source` (str)：来源（"Semantic Scholar" 或 "Crossref"）

## 服务器概述

该 MCP 服务器专门用于自动化处理学术论文的搜索与查询任务。它提供三个主要工具：`search_papers` 根据关键词搜索论文，`fetch_paper_details` 获取特定论文的详细信息，以及 `search_by_topic` 根据主题搜索论文。服务器优先使用 Semantic Scholar API，并在需要时回退到 Crossref API。

## 文件结构

```
academic_paper_search_server.py  # 主要实现文件
```

## 依赖项

- `mcp[cli]`：MCP 协议 SDK
- `httpx`：用于发送 HTTP 请求
- `python-dotenv`：用于管理环境变量（如果需要 API 密钥）