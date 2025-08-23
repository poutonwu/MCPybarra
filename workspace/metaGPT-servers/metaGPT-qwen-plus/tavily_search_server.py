import sys
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("tavily_search")

# Tavily API 配置
TAVILY_API_BASE = "https://api.tavily.com"
TAVILY_API_KEY = "REDACTED_SECRET"  # 注意：实际使用时应通过安全方式获取API密钥

@mcp.tool()
async def tavily_web_search(query: str, search_depth: str = "advanced", 
                            include_domains: list = None, exclude_domains: list = None,
                            max_results: int = 5) -> str:
    """
    使用Tavily API进行全面的网络搜索，支持基础或高级搜索深度，可通过包含或排除特定域名精确控制搜索范围，
    并返回结构化的网页内容。

    Args:
        query: 搜索查询字符串 (必填)。
        search_depth: 搜索深度，可选值为 "basic" 或 "advanced" (默认值为 "advanced")。
        include_domains: 包含的域名列表 (可选)。
        exclude_domains: 排除的域名列表 (可选)。
        max_results: 返回的最大结果数，必须是1到10之间的整数 (默认值为5)。

    Returns:
        一个包含搜索结果的JSON格式字符串，每个结果包括标题、URL和摘要。

    Raises:
        ValueError: 如果参数无效。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    # 参数验证
    if not query or not query.strip():
        raise ValueError("查询内容不能为空。")
    
    if search_depth not in ["basic", "advanced"]:
        raise ValueError(f"无效的搜索深度: '{search_depth}'。必须是 'basic' 或 'advanced'。")
    
    if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
        raise ValueError(f"无效的结果数量: {max_results}。必须是1到10之间的整数。")
    
    # 构建请求参数
    params = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_domains": include_domains if include_domains else [],
        "exclude_domains": exclude_domains if exclude_domains else []
    }
    
    # 发送API请求
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TAVILY_API_BASE}/search/web", json=params, headers=headers)
        response.raise_for_status()
        
    return response.text

@mcp.tool()
async def tavily_answer_search(query: str, search_depth: str = "advanced", max_results: int = 3) -> str:
    """
    使用Tavily API根据查询内容直接生成回答并附带支持证据，适用于需要具体答案的问题，
    默认使用高级搜索深度。

    Args:
        query: 查询字符串 (必填)。
        search_depth: 搜索深度，可选值为 "basic" 或 "advanced" (默认值为 "advanced")。
        max_results: 返回的最大结果数，必须是1到5之间的整数 (默认值为3)。

    Returns:
        一个包含答案和相关证据的JSON格式字符串。

    Raises:
        ValueError: 如果参数无效。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    # 参数验证
    if not query or not query.strip():
        raise ValueError("查询内容不能为空。")
    
    if search_depth not in ["basic", "advanced"]:
        raise ValueError(f"无效的搜索深度: '{search_depth}'。必须是 'basic' 或 'advanced'。")
    
    if not isinstance(max_results, int) or max_results < 1 or max_results > 5:
        raise ValueError(f"无效的结果数量: {max_results}。必须是1到5之间的整数。")
    
    # 构建请求参数
    params = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results
    }
    
    # 发送API请求
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TAVILY_API_BASE}/search/answer", json=params, headers=headers)
        response.raise_for_status()
        
    return response.text

@mcp.tool()
async def tavily_news_search(query: str, days: int = 7, include_sources: list = None, 
                             exclude_sources: list = None, max_results: int = 5) -> str:
    """
    使用Tavily API专门搜索近期新闻文章，支持限定查询时效性（最多可追溯365天），
    并可指定包含或排除的新闻源。

    Args:
        query: 新闻搜索查询字符串 (必填)。
        days: 查询时效性，必须是1到365之间的整数 (默认值为7)。
        include_sources: 包含的新闻源列表 (可选)。
        exclude_sources: 排除的新闻源列表 (可选)。
        max_results: 返回的最大结果数，必须是1到10之间的整数 (默认值为5)。

    Returns:
        一个包含新闻结果的JSON格式字符串，每个结果包括标题、URL、摘要和来源。

    Raises:
        ValueError: 如果参数无效。
        httpx.HTTPStatusError: 如果API请求失败。
    """
    # 参数验证
    if not query or not query.strip():
        raise ValueError("查询内容不能为空。")
    
    if not isinstance(days, int) or days < 1 or days > 365:
        raise ValueError(f"无效的天数: {days}。必须是1到365之间的整数。")
    
    if not isinstance(max_results, int) or max_results < 1 or max_results > 10:
        raise ValueError(f"无效的结果数量: {max_results}。必须是1到10之间的整数。")
    
    # 构建请求参数
    params = {
        "query": query,
        "days": days,
        "max_results": max_results,
        "include_sources": include_sources if include_sources else [],
        "exclude_sources": exclude_sources if exclude_sources else []
    }
    
    # 发送API请求
    headers = {"Authorization": f"Bearer {TAVILY_API_KEY}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{TAVILY_API_BASE}/search/news", json=params, headers=headers)
        response.raise_for_status()
        
    return response.text

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run("stdio")