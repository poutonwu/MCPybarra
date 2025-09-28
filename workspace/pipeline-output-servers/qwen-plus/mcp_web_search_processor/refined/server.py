import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional, Union
import httpx
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient

# 设置代理（如果需要）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 初始化 FastMCP 服务器
mcp = FastMCP("mcp_web_search_processor")

# 获取 API 密钥
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY 环境变量未设置")

# 创建 Tavily 客户端实例
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@mcp.tool()
async def tavily_web_search(
    query: str,
    search_depth: str = "basic",
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> List[Dict[str, str]]:
    """
    执行全面的网络搜索，支持基础或高级搜索深度，可通过包含或排除特定域名精确控制搜索范围。

    Args:
        query: 搜索查询字符串 (必填)。
        search_depth: 搜索深度，可选 "basic" 或 "advanced", 默认 "basic"。
        include_domains: 包含在结果中的域名列表 (可选)。
        exclude_domains: 排除的域名列表 (可选)。
        max_results: 返回的最大结果数 (1-5), 默认 5。

    Returns:
        List[Dict[str, str]]: 包含标题、URL 和内容摘要的搜索结果列表。

    示例:
        >>> tavily_web_search(query="Python 3.10 features", search_depth="advanced", 
                             include_domains=["python.org"], max_results=3)
        [
            {
                "title": "Python 3.10 新特性详解",
                "url": "https://docs.python.org/3.10/whatsnew/3.10.html",
                "content": "Python 3.10 的新特性包括模式匹配、更好的类型提示等..."
            },
            {
                "title": "Python 3.10 发布说明",
                "url": "https://www.python.org/downloads/release/python-3100/",
                "content": "Python 3.10 正式版发布，包含多项性能改进和错误修复..."
            },
            {
                "title": "Python 3.10：面向未来的编程语言",
                "url": "https://realpython.com/python310-new-features/",
                "content": "探索 Python 3.10 中最令人期待的新特性和改进..."
            }
        ]
    """
    try:
        # 验证参数
        if not query or not query.strip():
            raise ValueError("搜索查询不能为空")
        
        if not isinstance(max_results, int) or not (1 <= max_results <= 5):
            raise ValueError("max_results 必须是 1 到 5 之间的整数")
        
        if search_depth not in ["basic", "advanced"]:
            raise ValueError("search_depth 必须是 'basic' 或 'advanced'")

        # 执行搜索
        results = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth=search_depth,
            include_domains=include_domains if include_domains else [],
            exclude_domains=exclude_domains if exclude_domains else [],
            max_results=max_results
        )
        
        # 处理结果
        formatted_results = []
        for result in results.get('results', []):
            formatted_results.append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "content": result.get('content', '')
            })
        
        return formatted_results
    except Exception as e:
        # 记录错误并返回清晰的错误信息
        error_msg = f"tavily_web_search 发生错误: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

@mcp.tool()
async def tavily_answer_search(
    query: str,
    search_depth: str = "advanced"
) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """
    根据查询内容直接生成回答并附带支持证据，适用于需要具体答案的问题。

    Args:
        query: 要回答的问题 (必填)。
        search_depth: 搜索深度，可选 "basic" 或 "advanced", 默认 "advanced".

    Returns:
        Dict[str, Union[str, List[Dict[str, str]]]]: 包含答案和证据的字典.

    示例:
        >>> tavily_answer_search(query="地球的卫星是什么？")
        {
            "answer": "地球的卫星是月球。",
            "evidence": [
                {
                    "title": "月球 - 维基百科",
                    "url": "https://zh.wikipedia.org/wiki/%E6%9C%88%E7%90%83",
                    "content": "月球是地球唯一的天然卫星，也是太阳系中第五大的卫星..."
                }
            ]
        }
    """
    try:
        # 验证参数
        if not query or not query.strip():
            raise ValueError("查询内容不能为空")
        
        if search_depth not in ["basic", "advanced"]:
            raise ValueError("search_depth 必须是 'basic' 或 'advanced'")

        # 执行问答搜索
        response = await asyncio.to_thread(
            tavily_client.qna_search,
            query=query,
            search_depth=search_depth
        )
        
        # 处理结果
        return response
        answer = response.get('answer', '')
        evidence = []
        
        for source in response.get('sources', []):
            evidence.append({
                "title": source.get('title', ''),
                "url": source.get('url', ''),
                "content": source.get('content', '')
            })
        
        return {
            "answer": answer,
            "evidence": evidence
        }
    except Exception as e:
        # 记录错误并返回清晰的错误信息
        error_msg = f"tavily_answer_search 发生错误: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

@mcp.tool()
async def tavily_news_search(
    query: str,
    days: int = 7,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    max_results: int = 5
) -> List[Dict[str, str]]:
    """
    专门搜索近期新闻文章，支持限定查询时效性（最多可追溯365天），并可指定包含或排除的新闻源。

    Args:
        query: 新闻搜索查询 (必填)。
        days: 查询回溯的天数 (1-365), 默认 7。
        include_domains: 包含的新闻源域名列表 (可选)。
        exclude_domains: 排除的新闻源域名列表 (可选)。
        max_results: 返回的最大结果数 (1-5), 默认 5。

    Returns:
        List[Dict[str, str]]: 包含标题、URL 和内容摘要的新闻结果列表.

    示例:
        >>> tavily_news_search(query="人工智能最新进展", days=3, 
                              include_domains=["techcrunch.com"], max_results=2)
        [
            {
                "title": "AI 领域的三大突破：2024 年第一季度",
                "url": "https://techcrunch.com/2024/03/15/ai-breakthroughs-q1-2024/",
                "content": "本文总结了 2024 年第一季度人工智能领域的三项重大突破..."
            },
            {
                "title": "大模型训练成本降低 80%，新技术革新 AI 行业",
                "url": "https://techcrunch.com/2024/03/14/ai-training-cost-reduction/",
                "content": "一项新技术使大模型训练成本大幅降低，为人工智能发展带来新的可能..."
            }
        ]
    """
    try:
        # 验证参数
        if not query or not query.strip():
            raise ValueError("新闻查询不能为空")
        
        if not isinstance(days, int) or not (1 <= days <= 365):
            raise ValueError("days 必须是 1 到 365 之间的整数")
        
        if not isinstance(max_results, int) or not (1 <= max_results <= 5):
            raise ValueError("max_results 必须是 1 到 5 之间的整数")

        # 构建时间范围参数
        time_range_map = {
            1: "d",
            7: "week",
            30: "month",
            365: "year"
        }
        time_range = time_range_map.get(days, None)
        if time_range is None:
            # 如果没有匹配预定义的时间范围，则使用默认值
            time_range = f"d{days}"
        
        # 执行新闻搜索
        results = await asyncio.to_thread(
            tavily_client.search,
            query=query,
            search_depth="basic",
            time_range=time_range,
            include_domains=include_domains if include_domains else [],
            exclude_domains=exclude_domains if exclude_domains else [],
            max_results=max_results
        )
        
        # 处理结果
        formatted_results = []
        for result in results.get('results', []):
            formatted_results.append({
                "title": result.get('title', ''),
                "url": result.get('url', ''),
                "content": result.get('content', '')
            })
        
        return formatted_results
    except Exception as e:
        # 记录错误并返回清晰的错误信息
        error_msg = f"tavily_news_search 发生错误: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()