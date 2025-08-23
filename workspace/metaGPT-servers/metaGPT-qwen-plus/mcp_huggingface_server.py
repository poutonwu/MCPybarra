import asyncio
from http import client
import sys
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("huggingface")

# 定义常量
HUGGINGFACE_API_BASE = "https://huggingface.co/api"
USER_AGENT = "huggingface-mcp-server/1.0 (contact@example.com)"

@mcp.tool()
async def search_models(keyword: str = "", author: str = "", tag: str = "") -> str:
    """
    根据关键词、作者和标签搜索Hugging Face模型。

    Args:
        keyword: 搜索关键词 (可选)。
        author: 模型作者名称 (可选)。
        tag: 模型标签 (可选)。

    Returns:
        一个字符串，包含匹配的模型列表信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    params = {}
    if keyword:
        params["search"] = keyword
    if author:
        params["author"] = author
    if tag:
        params["tag"] = tag

    url = f"{HUGGINGFACE_API_BASE}/models"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_model_info(model_id: str) -> str:
    """
    根据模型ID获取Hugging Face模型的详细信息。

    Args:
        model_id: Hugging Face上的模型标识符。

    Returns:
        一个字符串，包含模型的详细信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    url = f"{HUGGINGFACE_API_BASE}/models/{model_id}"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def search_datasets(keyword: str = "", author: str = "", tag: str = "") -> str:
    """
    根据关键词、作者和标签搜索Hugging Face数据集。

    Args:
        keyword: 搜索关键词 (可选)。
        author: 数据集作者名称 (可选)。
        tag: 数据集标签 (可选)。

    Returns:
        一个字符串，包含匹配的数据集列表信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    params = {}
    if keyword:
        params["search"] = keyword
    if author:
        params["author"] = author
    if tag:
        params["tag"] = tag

    url = f"{HUGGINGFACE_API_BASE}/datasets"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """
    根据数据集ID获取Hugging Face数据集的详细信息。

    Args:
        dataset_id: Hugging Face上的数据集标识符。

    Returns:
        一个字符串，包含数据集的详细信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    url = f"{HUGGINGFACE_API_BASE}/datasets/{dataset_id}"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def search_spaces(keyword: str = "", author: str = "", tag: str = "", sdk: str = "") -> str:
    """
    根据关键词、作者、标签和SDK搜索Hugging Face Spaces。

    Args:
        keyword: 搜索关键词 (可选)。
        author: Space作者名称 (可选)。
        tag: Space标签 (可选)。
        sdk: 使用的SDK名称 (可选)。

    Returns:
        一个字符串，包含匹配的Space列表信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    params = {}
    if keyword:
        params["search"] = keyword
    if author:
        params["author"] = author
    if tag:
        params["tag"] = tag
    if sdk:
        params["sdk"] = sdk

    url = f"{HUGGINGFACE_API_BASE}/spaces"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_space_info(space_id: str) -> str:
    """
    根据Space ID获取Hugging Face Space的详细信息。

    Args:
        space_id: Hugging Face上的Space标识符。

    Returns:
        一个字符串，包含Space的详细信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    url = f"{HUGGINGFACE_API_BASE}/spaces/{space_id}"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_paper_info(arxiv_id: str) -> str:
    """
    根据arXiv ID获取论文的详细信息。

    Args:
        arxiv_id: arXiv上的论文标识符。

    Returns:
        一个字符串，包含论文的详细信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    url = f"{HUGGINGFACE_API_BASE}/papers/{arxiv_id}"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_daily_papers() -> str:
    """
    获取Hugging Face每日精选论文列表。

    Returns:
        一个字符串，包含每日精选论文列表信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    url = f"{HUGGINGFACE_API_BASE}/daily-papers"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def search_collections(owner: str = "", entry: str = "", keyword: str = "") -> str:
    """
    根据拥有者、条目和关键词搜索Hugging Face集合。

    Args:
        owner: 集合的拥有者名称 (可选)。
        entry: 集合中的条目 (可选)。
        keyword: 搜索关键词 (可选)。

    Returns:
        一个字符串，包含匹配的集合列表信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    params = {}
    if owner:
        params["owner"] = owner
    if entry:
        params["entry"] = entry
    if keyword:
        params["search"] = keyword

    url = f"{HUGGINGFACE_API_BASE}/collections"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text

@mcp.tool()
async def get_collection_info(namespace: str, collection_id: str) -> str:
    """
    根据集合命名空间和ID获取Hugging Face集合的详细信息。

    Args:
        namespace: 集合的命名空间。
        collection_id: Hugging Face上的集合标识符。

    Returns:
        一个字符串，包含集合的详细信息。

    Raises:
        httpx.HTTPStatusError: 如果API请求失败。
    """
    url = f"{HUGGINGFACE_API_BASE}/collections/{namespace}/{collection_id}"
    headers = {"User-Agent": USER_AGENT}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()