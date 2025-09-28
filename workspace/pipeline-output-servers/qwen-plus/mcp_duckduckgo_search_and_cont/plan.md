# MCP 服务器实现计划

## MCP Tools Plan

### 1. `DuckDuckGo_search` 工具
- **Function Name**: `DuckDuckGo_search`
- **Description**: 在 DuckDuckGo 搜索引擎上根据查询内容自动检索相关信息，并将搜索结果以结构化格式返回
- **Parameters**:
  - `query` (string, 必填): 要搜索的关键词或短语
  - `max_results` (int, 可选): 返回的最大结果数量，默认为5，范围1-10
- **Return Value**: 包含搜索结果的字典列表，每个字典包含：
  - `title`: 搜索结果标题 (string)
  - `link`: 结果链接 (string)
  - `snippet`: 结果摘要文本 (string)
  - `source`: 来源网站域名 (string)

### 2. `fetch_content` 工具
- **Function Name**: `fetch_content`
- **Description**: 根据提供的网页 URL 抓取并解析该网页的主要文本内容，去除无关元素后返回
- **Parameters**:
  - `url` (string, 必填): 要抓取内容的网页 URL
  - `remove_ads` (bool, 可选): 是否尝试移除广告内容，默认为 True
  - `timeout` (int, 可选): 请求超时时间（秒），默认为 10
- **Return Value**: 包含网页内容的字典：
  - `title`: 网页标题 (string)
  - `content`: 清理后的正文内容 (string)
  - `domain`: 网站域名 (string)
  - `status_code`: HTTP 响应状态码 (int)
  - `word_count`: 内容字数统计 (int)

## Server Overview
本服务器是一个自动化处理 DuckDuckGo 搜索与网页内容抓取的 MCP 服务器。它提供两个主要功能：一是通过 DuckDuckGo_search 方法实现搜索引擎查询，二是通过 fetch_content 方法实现网页内容提取。服务器严格遵循用户需求，仅实现指定功能，不添加任何额外工具。

## File to be Generated
- **File Name**: `mcp_duckduckgo_server.py`
- 文件将包含完整的服务器实现代码，包括初始化、工具定义和运行逻辑，所有代码自包含于一个文件中。

## Dependencies
- `mcp[cli]`: MCP 协议 SDK
- `httpx`: 用于 HTTP 请求
- `beautifulsoup4`: 用于 HTML 解析和内容提取
- `lxml`: 作为 BeautifulSoup 的解析器
- `requests`: 用于同步 HTTP 请求（可选）
- `duckduckgo-search-api`: 用于 DuckDuckGo 搜索 API 集成