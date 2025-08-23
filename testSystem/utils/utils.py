import os
from typing import Dict

PIPELINE_MODELS = ["gpt-4o", "gemini-2.5-pro", "qwen-plus", "qwen-max-latest", 'deepseek-v3']

def _simplify_public_name(name: str) -> str:
    """Simplifies the public server name for better readability on charts using a specific mapping."""
    name = name.lower()
    # This explicit mapping is more robust than generic string replacement.
    mapping = {
        "academic-search-mcp-server-master": "academic search",
        "arxiv-mcp-server-main": "arxiv",
        "duckduckgo-mcp-server-main": "duckduckgo",
        "flights-mcp-main": "flights",
        "huggingface-mcp-server-main": "huggingface",
        "image-file-converter-mcp-server-main": "image converter",
        "markitdown-main": "markdown",
        "mcp-doc-main": "word automation (doc)",
        "office-word-mcp-server-main": "word processor (office)",
        "mcp-everything-search-main": "everything search",
        "mcp-official-git": "git",
        "mcp-pdf-tools": "pdf tools",
        "mcp-server-data-exploration-main": "data exploration",
        "mcp-server-main": "financial data",
        "mcp-tavily-main": "tavily",
        "mcp-text-editor-main": "text editor",
        "mcp_search_images-main": "image search",
        "mongo-mcp-main": "mongodb",
        "my-mcp-ssh-master": "ssh",
        "mysql_mcp_server-main": "mysql",
        "opencv-mcp-server-main": "opencv",
        "outlook-mcp-server-main": "outlook",
        "screenshot-server-main": "screenshot",
        "unsplash-mcp-server-main": "unsplash",
        "zotero-mcp-main": "zotero",
    }
    return mapping.get(name, name).title()

def load_server_mapping(mapping_file: str) -> Dict[str, str]:
    """加载服务器名称映射文件"""
    if not os.path.exists(mapping_file):
        print(f"警告: 映射文件 {mapping_file} 不存在。")
        return {}
    
    mapping = {}
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # 支持两种格式: "A -> B" 或 "A - B"
                if '->' in line:
                    public_name, refinement_name = line.split('->')
                elif ' - ' in line:
                    public_name, refinement_name = line.split(' - ')
                else:
                    print(f"警告: 无法解析映射行: {line}")
                    continue
                    
                mapping[public_name.strip()] = refinement_name.strip()
        
        if mapping:
            print(f"成功从 {mapping_file} 加载了 {len(mapping)} 条映射关系")
        else:
            print(f"警告: 映射文件 {mapping_file} 中未找到有效的映射关系")
    except Exception as e:
        print(f"读取映射文件 {mapping_file} 时出错: {e}")
    
    return mapping 