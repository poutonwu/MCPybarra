# MCPybarra Workspace Directory

## Overview

This workspace contains the experimental results and generated MCP servers from our research. We currently have **25 servers** in total, but are implementing a **phased open-source strategy** to protect research outcomes.

## Open Source Strategy

### Currently Available

- ✅ **Multiple Model-Generated Servers** - 3 eaxmple servers each from different LLM models (Gemini 2.5 Pro, GPT-4o, etc.)
- ✅ **MetaGPT Results** - Servers generated using MetaGPT framework
- ✅ **Public MCP Servers** - Reference implementations from open source community

### Available After Paper Acceptance

- 📊 **Complete Experimental Data** - All 25 servers with full generation details
- 📈 **Detailed Analysis Results** - Comprehensive performance and quality metrics

## Directory Structure

```
workspace/
├── README.md                           # This file
├── pipeline_mapping.json               # Pipeline configuration mapping
├── pipeline-output-servers/            # Model-generated servers
│   ├── gemini-2.5-pro/                # 3 eaxmple servers
│   ├── gpt-4o/
│   ├── deepseek-v3/
│   ├── qwen-max-latest/
│   └── qwen-plus/
├── metaGPT-servers/
│   └── metaGPT-qwen-plus/
└── public-mcp-servers/                 # ✅ Reference implementations (25 servers)
    └── [25 reference MCP servers]
```

## Current Available Content

### Model-Generated Servers

Each model has 3 complete MCP servers generated using our framework:

- **Gemini 2.5 Pro**: Image & Icon Handler, MongoDB Database Manager, Word Document Automation
- **GPT-4o**: 3 servers (same server types)
- **DeepSeek V3**: 3 servers (same server types)
- **Qwen Max**: 3 servers (same server types)
- **Qwen Plus**: 3 servers (same server types)

### MetaGPT Results

Servers generated using the MetaGPT framework for comparison and validation.

### Public MCP Servers

25 reference implementations covering three main categories:

- **Data/Content Retrieval**: Academic search, ArXiv, DuckDuckGo, HuggingFace, Tavily, Financial data, Data exploration, Image search, Unsplash, Everything search, Flights
- **File/Format Processing**: PDF tools, Word automation, Markdown processing, Image conversion, Text editing, OpenCV, Screenshot automation
- **Application/System Integration**: MongoDB, MySQL, Git, SSH, Outlook, Zotero
