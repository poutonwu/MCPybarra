# 自动化学术文献管理 MCP 服务器实施计划

## MCP Tools Plan

### get_item_metadata 工具
- **Function Name**: `get_item_metadata`
- **Description**: 获取指定 Zotero 条目的详细元数据
- **Parameters**:
  - `item_key` (str): 要获取元数据的 Zotero 条目键值，必须是字符串类型
- **Return Value**: 返回包含条目详细元数据的 JSON 字符串，包括标题、作者、出版年份等信息

### get_item_fulltext 工具
- **Function Name**: `get_item_fulltext`
- **Description**: 提取指定 Zotero 条目的全文内容
- **Parameters**:
  - `item_key` (str): 要提取全文的 Zotero 条目键值，必须是字符串类型
- **Return Value**: 返回包含条目全文内容的字符串，如果条目没有全文内容则返回空字符串

### search_items 工具
- **Function Name**: `search_items`
- **Description**: 在 Zotero 库中执行灵活搜索，支持按标题、创建者、年份或全文搜索
- **Parameters**:
  - `query` (str): 搜索查询字符串，必须是字符串类型
  - `search_type` (str): 搜索类型，可选值为 "title", "creator", "year", "fulltext"，默认为"title"
- **Return Value**: 返回格式化的搜索结果列表，每个结果包含条目键值、标题和匹配度评分

## Server Overview
该服务器旨在实现 Zotero 文献库的自动化访问与操作，提供精确的元数据获取、全文内容提取和灵活的搜索功能。服务器基于 MCP 协议，使用 Python 实现，能够与 Zotero 的本地 API 进行交互。

## File Structure
- zotero_mcp_server.py: 包含服务器主程序和所有工具函数的实现

## Dependencies
- Python 3.10+
- mcp[cli] (MCP SDK)
- httpx (用于处理 HTTP 请求)
- Zotero 7+ (本地安装)