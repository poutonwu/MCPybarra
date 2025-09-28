import os
import sys
import json
from typing import Any, Dict, List, Optional, Union
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta

# 设置代理（如果需要）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 初始化 FastMCP 服务器
mcp = FastMCP("web_search_processor")

# 创建异步HTTP客户端
client = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),  # 增加超时时间
    headers={"User-Agent": "mcp-web-search-processor/1.0 (contact@example.com)"}
)

def validate_search_params(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_domains: Optional[Union[str, List[str]]] = None,
    exclude_domains: Optional[Union[str, List[str]]] = None
) -> None:
    """
    验证搜索参数的合法性

    Args:
        query: 搜索查询内容
        search_depth: 搜索深度，可选"basic"或"advanced"
        max_results: 返回结果的最大数量，默认为5，最大20
        include_domains: 需要包含的域名列表
        exclude_domains: 需要排除的域名列表

    Raises:
        ValueError: 参数验证失败时抛出异常
    """
    if not query or not query.strip():
        raise ValueError("搜索查询内容不能为空")
    
    if search_depth not in ["basic", "advanced"]:
        raise ValueError(f'无效的搜索深度: {search_depth}。必须是 "basic" 或 "advanced"')
    
    if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
        raise ValueError(f"max_results必须是1-20之间的整数，当前值: {max_results}")
    
    for domains, param_name in [(include_domains, "include_domains"), (exclude_domains, "exclude_domains")]:
        if domains is not None:
            if isinstance(domains, str):
                if not domains.strip():
                    raise ValueError(f"{param_name}字符串不能为空")
            elif isinstance(domains, list):
                if any(not isinstance(d, str) or not d.strip() for d in domains):
                    raise ValueError(f"{param_name}列表中的域名不能为空且必须为字符串类型")
                if len(set(domains)) != len(domains):
                    raise ValueError(f"{param_name}列表中不能包含重复的域名")

async def perform_search(
    query: str,
    search_type: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_domains: Optional[Union[str, List[str]]] = None,
    exclude_domains: Optional[Union[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    执行搜索操作

    Args:
        query: 搜索查询内容
        search_type: 搜索类型（web、answer、news）
        search_depth: 搜索深度
        max_results: 返回结果的最大数量
        include_domains: 需要包含的域名
        exclude_domains: 需要排除的域名

    Returns:
        包含搜索结果的字典

    Raises:
        httpx.HTTPStatusError: 如果API请求失败
    """
    url = "https://api.tavily.com/search"
    
    # 处理域名参数
    include_domains_list = []
    if include_domains:
        if isinstance(include_domains, str):
            include_domains_list = [d.strip() for d in include_domains.split(",") if d.strip()]
        else:
            include_domains_list = [d.strip() for d in include_domains if d.strip()]
    
    exclude_domains_list = []
    if exclude_domains:
        if isinstance(exclude_domains, str):
            exclude_domains_list = [d.strip() for d in exclude_domains.split(",") if d.strip()]
        else:
            exclude_domains_list = [d.strip() for d in exclude_domains if d.strip()]
    
    params = {
        "api_key": os.environ.get("TAVILY_API_KEY", "REDACTED_SECRET"),
        "query": query,
        "search_type": search_type,
        "depth": search_depth,
        "max_results": max_results,
        "include_domains": json.dumps(include_domains_list) if include_domains_list else "[]",
        "exclude_domains": json.dumps(exclude_domains_list) if exclude_domains_list else "[]"
    }
    
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.json()

@mcp.tool()
async def tavily_web_search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_domains: Optional[Union[str, List[str]]] = None,
    exclude_domains: Optional[Union[str, List[str]]] = None
) -> str:
    """
    执行全面的网络搜索，支持基础或高级搜索深度，可通过包含或排除特定域名精确控制搜索范围，并返回结构化的网页内容

    Args:
        query: 搜索查询内容 (必填)
        search_depth: 搜索深度，可选"basic"或"advanced"，默认为"basic"
        max_results: 返回结果的最大数量，默认为5，最大20
        include_domains: 需要包含的域名列表或逗号分隔的字符串
        exclude_domains: 需要排除的域名列表或逗号分隔的字符串

    Returns:
        返回包含标题、URL和内容摘要的检索结果列表，格式为JSON字符串：
        [
          {
            "title": "页面标题",
            "url": "https://example.com",
            "content": "页面内容摘要"
          },
          ...
        ]

    Raises:
        ValueError: 参数验证失败时抛出异常
        httpx.HTTPStatusError: 如果API请求失败

    示例:
        >>> tavily_web_search(query="Python编程", search_depth="advanced", max_results=10, include_domains=["python.org", "github.com"])
        '[{"title":"Python官方文档","url":"https://docs.python.org/3/","content":"Python语言的官方文档..."}]'
    """
    try:
        # 验证参数
        validate_search_params(query, search_depth, max_results, include_domains, exclude_domains)
        
        # 执行搜索
        result = await perform_search(
            query=query,
            search_type="web",
            search_depth=search_depth,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        # 返回格式化后的JSON字符串
        return json.dumps(result.get("results", []), ensure_ascii=False, indent=2)
    except Exception as e:
        error_msg = f"tavily_web_search工具发生错误: {str(e)}"
        # 记录错误日志（实际应用中可以添加真正的日志记录）
        print(error_msg, file=sys.stderr)
        # 返回错误信息的结构化数据
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)

@mcp.tool()
async def tavily_answer_search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5
) -> str:
    """
    根据查询内容直接生成回答并附带支持证据，适用于需要具体答案的问题，默认使用高级搜索深度

    Args:
        query: 需要回答的问题 (必填)
        search_depth: 搜索深度，可选"basic"或"advanced"，默认为"advanced"
        max_results: 用于生成答案的源结果数量，默认为5

    Returns:
        返回包含答案和相关证据来源的字典，格式为JSON字符串：
        {
          "answer": "问题的答案",
          "sources": [
            {
              "title": "来源标题",
              "url": "https://example.com"
            },
            ...
          ]
        }

    Raises:
        ValueError: 参数验证失败时抛出异常
        httpx.HTTPStatusError: 如果API请求失败

    示例:
        >>> tavily_answer_search(query="地球的卫星是什么？", search_depth="advanced")
        '{"answer":"地球的卫星是月球","sources":[{"title":"月球 - 维基百科","url":"https://zh.wikipedia.org/wiki/%E6%9C%88%E7%90%83"}]}'
    """
    try:
        # 验证参数
        validate_search_params(query, search_depth, max_results)
        
        # 执行搜索
        result = await perform_search(
            query=query,
            search_type="answer",
            search_depth=search_depth,
            max_results=max_results
        )
        
        # 构建答案响应
        answer_result = {
            "answer": result.get("answer", "未找到明确答案"),
            "sources": result.get("sources", [])
        }
        
        # 返回格式化后的JSON字符串
        return json.dumps(answer_result, ensure_ascii=False, indent=2)
    except Exception as e:
        error_msg = f"tavily_answer_search工具发生错误: {str(e)}"
        # 记录错误日志（实际应用中可以添加真正的日志记录）
        print(error_msg, file=sys.stderr)
        # 返回错误信息的结构化数据
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)

@mcp.tool()
async def tavily_news_search(
    query: str,
    days: int = 3,
    max_results: int = 5,
    include_domains: Optional[Union[str, List[str]]] = None,
    exclude_domains: Optional[Union[str, List[str]]] = None
) -> str:
    """
    专门搜索近期新闻文章，支持限定查询时效性（最多可追溯365天），并可指定包含或排除的新闻源

    Args:
        query: 新闻搜索关键词或主题 (必填)
        days: 要回溯的天数，默认为3，最大365
        max_results: 返回结果的最大数量，默认为5，最大20
        include_domains: 需要包含的新闻源域名列表或逗号分隔的字符串
        exclude_domains: 需要排除的新闻源域名列表或逗号分隔的字符串

    Returns:
        返回包含标题、URL、内容摘要和发布日期的新闻结果列表，格式为JSON字符串：
        [
          {
            "title": "新闻标题",
            "url": "https://example.com",
            "content": "新闻内容摘要",
            "date": "YYYY-MM-DD"
          },
          ...
        ]

    Raises:
        ValueError: 参数验证失败时抛出异常
        httpx.HTTPStatusError: 如果API请求失败

    示例:
        >>> tavily_news_search(query="人工智能发展", days=7, max_results=10, include_domains="techcrunch.com")
        '[{"title":"AI技术最新进展","url":"https://techcrunch.com/ai-developments","content":"关于人工智能发展的最新报道...","date":"2024-03-15"}]'
    """
    try:
        # 验证参数
        if not isinstance(days, int) or days < 1 or days > 365:
            raise ValueError(f"days必须是1-365之间的整数，当前值: {days}")
        
        validate_search_params(query, "basic", max_results, include_domains, exclude_domains)
        
        # 执行搜索
        result = await perform_search(
            query=query,
            search_type="news",
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        # 添加天数过滤
        filtered_results = []
        for item in result.get("results", []):
            if "date" in item:
                try:
                    item_date = datetime.strptime(item["date"], "%Y-%m-%d")
                    if (datetime.now() - item_date).days <= days:
                        filtered_results.append(item)
                except ValueError:
                    continue
        
        # 返回格式化后的JSON字符串
        return json.dumps(filtered_results, ensure_ascii=False, indent=2)
    except Exception as e:
        error_msg = f"tavily_news_search工具发生错误: {str(e)}"
        # 记录错误日志（实际应用中可以添加真正的日志记录）
        print(error_msg, file=sys.stderr)
        # 返回错误信息的结构化数据
        return json.dumps({"error": error_msg}, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()