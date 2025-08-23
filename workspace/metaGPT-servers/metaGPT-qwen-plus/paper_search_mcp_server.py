import sys
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("paper_search")

# 常量定义
SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
CROSSREF_SEARCH_URL = "https://api.crossref.org/works"
SEMANTIC_SCHOLAR_PAPER_DETAILS_URL = "https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
USER_AGENT = "paper-search-app/1.0 (contact@example.com)"

# 定义支持的论文来源
PAPER_SOURCE_TYPES = ["semantic_scholar", "crossref"]

@mcp.tool()
async def search_papers(query: str, limit: int = 5) -> dict:
    """
    根据关键词搜索学术论文，返回来自 Semantic Scholar 和 Crossref 的格式化论文列表。
    
    Args:
        query: 搜索关键词 (必填)。
        limit: 返回结果数量限制，默认为5，最大不超过10。
    
    Returns:
        包含来自 Semantic Scholar 和 Crossref 的格式化论文列表，每个条目包含标题、作者、年份和 DOI。
        
    Raises:
        ValueError: 如果查询为空或无效。
        httpx.HTTPStatusError: 如果 API 请求失败。
    """
    # 输入验证
    if not query or not query.strip():
        raise ValueError("搜索查询不能为空。")
    
    if not isinstance(limit, int) or limit < 1 or limit > 10:
        raise ValueError("结果数量限制必须是1到10之间的整数。")
    
    # 创建异步客户端
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        # 并发执行两个API请求
        semantic_scholar_task = _search_semantic_scholar(client, query, limit)
        crossref_task = _search_crossref(client, query, limit)
        
        semantic_scholar_results, crossref_results = await asyncio.gather(
            semantic_scholar_task, crossref_task
        )
        
        return {
            "semantic_scholar": semantic_scholar_results,
            "crossref": crossref_results
        }

async def _search_semantic_scholar(client, query, limit):
    """内部方法：使用 Semantic Scholar API 执行搜索"""
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,doi"
    }
    
    response = await client.get(SEMANTIC_SCHOLAR_SEARCH_URL, params=params)
    response.raise_for_status()
    
    data = response.json()
    results = []
    
    for paper in data.get("data", []):
        results.append({
            "title": paper.get("title"),
            "authors": [author.get("name") for author in paper.get("authors", [])],
            "year": paper.get("year"),
            "doi": paper.get("doi")
        })
    
    return results

async def _search_crossref(client, query, limit):
    """内部方法：使用 Crossref API 执行搜索"""
    params = {
        "query": query,
        "rows": limit,
        "select": "title,author,created,DOI"
    }
    
    response = await client.get(CROSSREF_SEARCH_URL, params=params)
    response.raise_for_status()
    
    data = response.json().get("message", {})
    results = []
    
    for paper in data.get("items", []):
        title = paper.get("title", [""])[0] if isinstance(paper.get("title"), list) else paper.get("title")
        authors = []
        
        if "author" in paper:
            for author in paper["author"]:
                given = author.get("given", "")
                family = author.get("family", "")
                if given or family:
                    authors.append(f"{given} {family}".strip())
        
        year = None
        if "created" in paper and "date-parts" in paper["created"]:
            date_parts = paper["created"]["date-parts"]
            if date_parts and len(date_parts) > 0:
                year = date_parts[0][0]
        
        doi = paper.get("DOI")
        
        results.append({
            "title": title,
            "authors": authors,
            "year": year,
            "doi": doi
        })
    
    return results

@mcp.tool()
async def fetch_paper_details(paper_id: str, source: str = "semantic_scholar") -> dict:
    """
    根据论文ID（DOI或Semantic Scholar ID）和指定来源获取详细信息。
    
    Args:
        paper_id: 论文的唯一标识符 (必填)。
        source: 论文来源，可选值为 "semantic_scholar" 或 "crossref"，默认为 "semantic_scholar"。
    
    Returns:
        包含论文详细信息的字典，包括标题、作者、摘要和出版场所。
    
    Raises:
        ValueError: 如果参数无效。
        httpx.HTTPStatusError: 如果 API 请求失败。
    """
    # 输入验证
    if not paper_id or not paper_id.strip():
        raise ValueError("论文ID不能为空。")
    
    if source not in PAPER_SOURCE_TYPES:
        raise ValueError(f"论文来源必须是以下之一: {', '.join(PAPER_SOURCE_TYPES)}")
    
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        if source == "semantic_scholar":
            return await _fetch_semantic_scholar_details(client, paper_id)
        elif source == "crossref":
            return await _fetch_crossref_details(client, paper_id)
    
    raise ValueError(f"无法从源 '{source}' 获取论文详情。")

async def _fetch_semantic_scholar_details(client, paper_id):
    """内部方法：从 Semantic Scholar 获取论文详细信息"""
    url = SEMANTIC_SCHOLAR_PAPER_DETAILS_URL.format(paper_id=paper_id)
    params = {"fields": "title,authors,abstract,venue"}
    
    response = await client.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    
    return {
        "title": data.get("title"),
        "authors": [author.get("name") for author in data.get("authors", [])],
        "abstract": data.get("abstract"),
        "venue": data.get("venue")
    }

async def _fetch_crossref_details(client, paper_id):
    """内部方法：从 Crossref 获取论文详细信息"""
    params = {
        "query": paper_id,
        "select": "title,author,abstract,container-title"
    }
    
    response = await client.get(CROSSREF_SEARCH_URL, params=params)
    response.raise_for_status()
    
    data = response.json().get("message", {})
    
    if not data.get("items"):
        return {}
    
    paper = data["items"][0]
    
    title = paper.get("title", [""])[0] if isinstance(paper.get("title"), list) else paper.get("title")
    abstract = paper.get("abstract", "")
    
    authors = []
    if "author" in paper:
        for author in paper["author"]:
            given = author.get("given", "")
            family = author.get("family", "")
            if given or family:
                authors.append(f"{given} {family}".strip())
    
    venue = ""
    if "container-title" in paper and isinstance(paper["container-title"], list) and paper["container-title"]:
        venue = paper["container-title"][0]
    
    return {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "venue": venue
    }

@mcp.tool()
async def search_by_topic(topic: str, limit: int = 5, min_year: int = None, max_year: int = None) -> dict:
    """
    根据主题关键词搜索论文，优先使用 Semantic Scholar 并支持回退到通用搜索。
    
    Args:
        topic: 主题关键词 (必填)。
        limit: 结果数量限制，默认为5，最大不超过10。
        min_year: 可选的最小年份。
        max_year: 可选的最大年份。
    
    Returns:
        包含来自 Semantic Scholar 的格式化论文列表，如果失败则回退到 Crossref。
    
    Raises:
        ValueError: 如果参数无效。
        httpx.HTTPStatusError: 如果 API 请求失败。
    """
    # 输入验证
    if not topic or not topic.strip():
        raise ValueError("主题关键词不能为空。")
    
    if not isinstance(limit, int) or limit < 1 or limit > 10:
        raise ValueError("结果数量限制必须是1到10之间的整数。")
    
    # 尝试使用 Semantic Scholar 搜索
    try:
        return await _search_semantic_scholar_by_topic(topic, limit, min_year, max_year)
    except Exception as e:
        print(f"Semantic Scholar 搜索失败: {str(e)}，正在回退到通用搜索...")
        # 回退到通用搜索
        return await _search_crossref_by_topic(topic, limit, min_year, max_year)

async def _search_semantic_scholar_by_topic(topic, limit, min_year, max_year):
    """内部方法：使用 Semantic Scholar 按主题搜索"""
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        params = {
            "query": topic,
            "limit": limit,
            "fields": "title,authors,year,doi"
        }
        
        if min_year is not None:
            params["year"] = f">{min_year - 1}" if min_year > 0 else None
        if max_year is not None:
            params["year"] = f"{params.get('year', '')}<={max_year}" if "year" in params else f"<={max_year}"
        
        response = await client.get(SEMANTIC_SCHOLAR_SEARCH_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for paper in data.get("data", []):
            results.append({
                "title": paper.get("title"),
                "authors": [author.get("name") for author in paper.get("authors", [])],
                "year": paper.get("year"),
                "doi": paper.get("doi")
            })
        
        return {"papers": results}

async def _search_crossref_by_topic(topic, limit, min_year, max_year):
    """内部方法：使用 Crossref 按主题搜索"""
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
        params = {
            "query": topic,
            "rows": limit,
            "select": "title,author,created,DOI"
        }
        
        if min_year is not None and min_year > 0:
            params[f"filter"] = f"from-pub-date:{min_year}-01-01"
        if max_year is not None and max_year > 0:
            params[f"filter"] = f"{params.get('filter', '')},until-pub-date:{max_year}-12-31"
        
        response = await client.get(CROSSREF_SEARCH_URL, params=params)
        response.raise_for_status()
        
        data = response.json().get("message", {})
        results = []
        
        for paper in data.get("items", []):
            title = paper.get("title", [""])[0] if isinstance(paper.get("title"), list) else paper.get("title")
            authors = []
            
            if "author" in paper:
                for author in paper["author"]:
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if given or family:
                        authors.append(f"{given} {family}".strip())
            
            year = None
            if "created" in paper and "date-parts" in paper["created"]:
                date_parts = paper["created"]["date-parts"]
                if date_parts and len(date_parts) > 0:
                    year = date_parts[0][0]
            
            doi = paper.get("DOI")
            
            results.append({
                "title": title,
                "authors": authors,
                "year": year,
                "doi": doi
            })
        
        return {"papers": results}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()