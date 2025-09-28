import sys
import httpx
import re
import asyncio
from mcp.server.fastmcp import FastMCP
from typing import List, Optional, Dict, Any

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# Initialize FastMCP server
mcp = FastMCP("huggingface_resource_manager")

# Constants
HUGGING_FACE_API_BASE = "https://huggingface.co/api"
ARXIV_API_BASE = "https://export.arxiv.org/api"
USER_AGENT = "huggingface-mcp-server/1.0 (contact@example.com)"

# Shared AsyncClient for HTTP requests
client = httpx.AsyncClient(
    base_url=HUGGING_FACE_API_BASE,
    headers={"User-Agent": USER_AGENT},
    timeout=30.0
)

@mcp.tool()
async def search_models(
    keywords: Optional[str] = None,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Search for models on Hugging Face Hub based on keywords, author, or tags.

    Args:
        keywords: Search query for model names or descriptions.
        author: Filter models by author.
        tags: Filter models by tags.

    Returns:
        A structured list of models in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    params = {}
    if keywords:
        params["search"] = keywords
    if author:
        params["author"] = author
    if tags:
        params["tags"] = ",".join(tags)

    try:
        response = await client.get("/models", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to search models: {str(e)}")

@mcp.tool()
async def get_model_info(model_id: str) -> str:
    """
    Retrieve detailed information about a specific model by its ID.

    Args:
        model_id: The unique identifier of the model.

    Returns:
        A dictionary containing model details in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    if not model_id or not isinstance(model_id, str):
        raise ValueError("model_id must be a non-empty string")

    try:
        response = await client.get(f"/models/{model_id}")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get model info: {str(e)}")

@mcp.tool()
async def search_datasets(
    keywords: Optional[str] = None,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Search for datasets on Hugging Face Hub based on keywords, author, or tags.

    Args:
        keywords: Search query for dataset names or descriptions.
        author: Filter datasets by author.
        tags: Filter datasets by tags.

    Returns:
        A structured list of datasets in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    params = {}
    if keywords:
        params["search"] = keywords
    if author:
        params["author"] = author
    if tags:
        params["tags"] = ",".join(tags)

    try:
        response = await client.get("/datasets", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to search datasets: {str(e)}")

@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """
    Retrieve detailed information about a specific dataset by its ID.

    Args:
        dataset_id: The unique identifier of the dataset.

    Returns:
        A dictionary containing dataset details in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    if not dataset_id or not isinstance(dataset_id, str):
        raise ValueError("dataset_id must be a non-empty string")

    try:
        response = await client.get(f"/datasets/{dataset_id}")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get dataset info: {str(e)}")

@mcp.tool()
async def search_spaces(
    keywords: Optional[str] = None,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    sdk: Optional[str] = None
) -> str:
    """
    Search for Spaces on Hugging Face Hub based on keywords, author, tags, or SDK.

    Args:
        keywords: Search query for Space names or descriptions.
        author: Filter Spaces by author.
        tags: Filter Spaces by tags.
        sdk: Filter Spaces by SDK (e.g., "gradio", "streamlit").

    Returns:
        A structured list of Spaces in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    params = {}
    if keywords:
        params["search"] = keywords
    if author:
        params["author"] = author
    if tags:
        params["tags"] = ",".join(tags)
    if sdk:
        params["sdk"] = sdk

    try:
        response = await client.get("/spaces", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to search spaces: {str(e)}")

@mcp.tool()
async def get_space_info(space_id: str) -> str:
    """
    Retrieve detailed information about a specific Space by its ID.

    Args:
        space_id: The unique identifier of the Space.

    Returns:
        A dictionary containing Space details in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    if not space_id or not isinstance(space_id, str):
        raise ValueError("space_id must be a non-empty string")

    try:
        response = await client.get(f"/spaces/{space_id}")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get space info: {str(e)}")

@mcp.tool()
async def get_paper_info(paper_id: str) -> str:
    """
    Retrieve detailed information about an arXiv paper by its ID.

    Args:
        paper_id: The arXiv ID of the paper.

    Returns:
        A dictionary containing paper details in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    if not paper_id or not isinstance(paper_id, str):
        raise ValueError("paper_id must be a non-empty string")

    try:
        async with httpx.AsyncClient(base_url=ARXIV_API_BASE, timeout=30.0) as arxiv_client:
            response = await arxiv_client.get(f"/query?id_list={paper_id}")
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get paper info: {str(e)}")

@mcp.tool()
async def get_daily_papers() -> str:
    """
    Retrieve a list of daily featured papers from Hugging Face.

    Returns:
        A structured list of papers in JSON format.

    Raises:
        httpx.HTTPStatusError: If API request fails.
    """
    try:
        response = await client.get("/papers/daily")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get daily papers: {str(e)}")

@mcp.tool()
async def search_collections(
    owner: Optional[str] = None,
    items: Optional[List[str]] = None,
    keywords: Optional[str] = None
) -> str:
    """
    Search for collections on Hugging Face Hub based on owner, items, or keywords.

    Args:
        owner: Filter collections by owner.
        items: Filter collections by included items.
        keywords: Search query for collection names or descriptions.

    Returns:
        A structured list of collections in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    params = {}
    if owner:
        params["owner"] = owner
    if items:
        params["items"] = ",".join(items)
    if keywords:
        params["search"] = keywords

    try:
        response = await client.get("/collections", params=params)
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to search collections: {str(e)}")

@mcp.tool()
async def get_collection_info(namespace: str, collection_id: str) -> str:
    """
    Retrieve detailed information about a specific collection by its namespace and ID.

    Args:
        namespace: The namespace of the collection.
        collection_id: The unique identifier of the collection.

    Returns:
        A dictionary containing collection details in JSON format.

    Raises:
        ValueError: If input validation fails.
        httpx.HTTPStatusError: If API request fails.
    """
    if not namespace or not isinstance(namespace, str) or not collection_id or not isinstance(collection_id, str):
        raise ValueError("namespace and collection_id must be non-empty strings")

    try:
        response = await client.get(f"/collections/{namespace}/{collection_id}")
        response.raise_for_status()
        return response.text
    except httpx.HTTPStatusError as e:
        raise ValueError(f"API request failed with status {e.response.status_code}")
    except Exception as e:
        raise ValueError(f"Failed to get collection info: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()