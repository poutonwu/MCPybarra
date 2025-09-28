# mcp_web_search_processor

## Overview

`mcp_web_search_processor` 是一个基于 Model Context Protocol (MCP) 的服务器，提供多种网络搜索功能。它通过 Tavily API 支持基础搜索、问答搜索和新闻搜索，能够帮助语言模型获取实时的互联网信息。

该服务器提供了以下工具：

- **tavily_web_search**：执行通用网页搜索。
- **tavily_answer_search**：直接生成问题的答案并附带支持证据。
- **tavily_news_search**：搜索最近的新闻文章。

## Installation

首先确保你已经安装了 Python 3.10 或更高版本。然后运行以下命令安装依赖项：

```bash
pip install -r requirements.txt
```

如果没有 `requirements.txt` 文件，请先创建它，并添加以下内容：

```
mcp[cli]
httpx
tavily
```

## Running the Server

要启动服务器，请运行以下命令：

```bash
python mcp_web_search_processor.py
```

确保你已设置环境变量 `TAVILY_API_KEY`，例如：

```bash
export TAVILY_API_KEY=your_api_key_here
```

如果你需要使用代理，请根据实际情况配置 `HTTP_PROXY` 和 `HTTPS_PROXY` 环境变量。

## Available Tools

### 1. `tavily_web_search`

执行全面的网络搜索，支持基础或高级搜索深度，可通过包含或排除特定域名精确控制搜索范围。

#### 示例参数：
- `query`: 搜索关键词（必填）
- `search_depth`: 搜索深度，可选 "basic" 或 "advanced"（默认为 "basic"）
- `include_domains`: 包含在结果中的域名列表（可选）
- `exclude_domains`: 排除的域名列表（可选）
- `max_results`: 返回的最大结果数（1-5，默认为 5）

---

### 2. `tavily_answer_search`

根据查询内容直接生成回答并附带支持证据，适用于需要具体答案的问题。

#### 示例参数：
- `query`: 要回答的问题（必填）
- `search_depth`: 搜索深度，可选 "basic" 或 "advanced"（默认为 "advanced"）

---

### 3. `tavily_news_search`

专门搜索近期新闻文章，支持限定查询时效性（最多可追溯365天），并可指定包含或排除的新闻源。

#### 示例参数：
- `query`: 新闻搜索关键词（必填）
- `days`: 查询回溯的天数（1-365，默认为 7）
- `include_domains`: 包含的新闻源域名列表（可选）
- `exclude_domains`: 排除的新闻源域名列表（可选）
- `max_results`: 返回的最大结果数（1-5，默认为 5）