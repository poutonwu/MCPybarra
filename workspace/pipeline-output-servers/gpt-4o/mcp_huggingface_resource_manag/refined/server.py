import os
import json
import asyncio
from mcp.server.fastmcp import FastMCP
from huggingface_hub import HfApi
import arxiv
from datetime import datetime

def default_serializer(obj):
    """Custom serializer to handle non-serializable objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, '__dict__'):
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Initialize MCP Server
mcp = FastMCP("huggingface_resource_manager")

# Constants for HTTP proxy (optional)
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

@mcp.tool()
async def search_models(keywords: str, author: str = None, tags: list = None) -> str:
    """
    Searches Hugging Face Hub for models based on user-provided keywords, authors, or tags.

    Args:
        keywords (str): Keywords to filter the models.
        author (str, optional): Name of the author to narrow the search.
        tags (list[str], optional): Tags to refine the search further.

    Returns:
        str: A JSON string containing structured model data.

    Example:
        search_models(keywords="transformer", author="huggingface", tags=["text-generation"])

    Raises:
        ValueError: If keywords are empty.
        RuntimeError: If the API request fails.
    """
    if not keywords.strip():
        raise ValueError("Keywords cannot be empty.")

    api = HfApi()
    try:
        results = api.list_models(search=keywords, author=author, tags=tags)
        return json.dumps([model for model in results], default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to search models: {str(e)}")

@mcp.tool()
async def get_model_info(model_id: str) -> str:
    """
    Retrieves detailed information about a specific model by its ID from Hugging Face Hub.

    Args:
        model_id (str): The unique identifier for the model.

    Returns:
        str: A JSON string containing model details.

    Example:
        get_model_info(model_id="distilbert/distilgpt2")

    Raises:
        ValueError: If model_id is empty.
        RuntimeError: If the API request fails.
    """
    if not model_id.strip():
        raise ValueError("Model ID cannot be empty.")

    api = HfApi()
    try:
        model_info = api.model_info(model_id)
        return json.dumps(model_info, default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve model info: {str(e)}")

@mcp.tool()
async def search_datasets(keywords: str, author: str = None, tags: list = None) -> str:
    """
    Searches Hugging Face Hub for datasets based on user-provided keywords, authors, or tags.

    Args:
        keywords (str): Keywords to filter the datasets.
        author (str, optional): Name of the author to narrow the search.
        tags (list[str], optional): Tags to refine the search further.

    Returns:
        str: A JSON string containing structured dataset data.

    Example:
        search_datasets(keywords="image-classification", author="huggingface", tags=["computer-vision"])

    Raises:
        ValueError: If keywords are empty.
        RuntimeError: If the API request fails.
    """
    if not keywords.strip():
        raise ValueError("Keywords cannot be empty.")

    api = HfApi()
    try:
        results = api.list_datasets(search=keywords, author=author, tags=tags)
        return json.dumps([dataset for dataset in results], default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to search datasets: {str(e)}")

@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """
    Retrieves detailed information about a specific dataset by its ID from Hugging Face Hub.

    Args:
        dataset_id (str): The unique identifier for the dataset.

    Returns:
        str: A JSON string containing dataset details.

    Example:
        get_dataset_info(dataset_id="huggingface/datasets")

    Raises:
        ValueError: If dataset_id is empty.
        RuntimeError: If the API request fails.
    """
    if not dataset_id.strip():
        raise ValueError("Dataset ID cannot be empty.")

    api = HfApi()
    try:
        dataset_info = api.dataset_info(dataset_id)
        return json.dumps(dataset_info, default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve dataset info: {str(e)}")

@mcp.tool()
async def search_spaces(keywords: str, author: str = None, tags: list = None, sdk: str = None) -> str:
    """
    Searches Hugging Face Hub for Spaces based on user-provided keywords, authors, tags, or SDKs.

    Args:
        keywords (str): Keywords to filter the Spaces.
        author (str, optional): Name of the author to narrow the search.
        tags (list[str], optional): Tags to refine the search further.
        sdk (str, optional): SDK type to filter the Spaces.

    Returns:
        str: A JSON string containing structured Space data.

    Example:
        search_spaces(keywords="demo", author="huggingface", tags=["interactive"], sdk="gradio")

    Raises:
        ValueError: If keywords are empty.
        RuntimeError: If the API request fails.
    """
    if not keywords.strip():
        raise ValueError("Keywords cannot be empty.")

    api = HfApi()
    try:
        results = api.list_spaces(search=keywords, author=author, space_sdk=sdk)
        return json.dumps([space for space in results], default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to search Spaces: {str(e)}")

@mcp.tool()
async def get_space_info(space_id: str) -> str:
    """
    Retrieves detailed information about a specific Space by its ID from Hugging Face Hub.

    Args:
        space_id (str): The unique identifier for the Space.

    Returns:
        str: A JSON string containing Space details.

    Example:
        get_space_info(space_id="huggingface/space_demo")

    Raises:
        ValueError: If space_id is empty.
        RuntimeError: If the API request fails.
    """
    if not space_id.strip():
        raise ValueError("Space ID cannot be empty.")

    api = HfApi()
    try:
        space_info = api.space_info(space_id)
        return json.dumps(space_info, default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve Space info: {str(e)}")

@mcp.tool()
async def get_paper_info(arxiv_id: str) -> str:
    """
    Fetches detailed information about a specific paper using its arXiv ID.

    Args:
        arxiv_id (str): The unique identifier for the paper on arXiv.

    Returns:
        str: A JSON string containing paper details.

    Example:
        get_paper_info(arxiv_id="1605.08386v1")

    Raises:
        ValueError: If arxiv_id is empty.
        RuntimeError: If the API request fails.
    """
    if not arxiv_id.strip():
        raise ValueError("arXiv ID cannot be empty.")

    try:
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
        return json.dumps({
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "abstract": paper.summary,
            "url": paper.pdf_url
        })
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve paper info: {str(e)}")

@mcp.tool()
async def get_daily_papers() -> str:
    """
    Retrieves the daily list of selected papers from Hugging Face.

    Args:
        None.

    Returns:
        str: A JSON string containing daily paper details.

    Example:
        get_daily_papers()

    Raises:
        RuntimeError: If the API request fails.
    """
    try:
        # Placeholder for Hugging Face API interaction
        papers = []  # Replace with actual API call
        return json.dumps(papers)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve daily papers: {str(e)}")

@mcp.tool()
async def search_collections(keywords: str, owner: str = None, entries: list = None) -> str:
    """
    Searches Hugging Face Hub for collections based on user-provided keywords, owners, or entries.

    Args:
        keywords (str): Keywords to filter the collections.
        owner (str, optional): Name of the owner to narrow the search.
        entries (list[str], optional): Specific entries to refine the search further.

    Returns:
        str: A JSON string containing structured collection data.

    Example:
        search_collections(keywords="vision", owner="huggingface", entries=["dataset1", "model1"])

    Raises:
        ValueError: If keywords are empty.
        RuntimeError: If the API request fails.
    """
    if not keywords.strip():
        raise ValueError("Keywords cannot be empty.")

    api = HfApi()
    try:
        results = api.list_collections(keyword=keywords, owner=owner, entries=entries)
        return json.dumps([collection for collection in results], default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to search collections: {str(e)}")

@mcp.tool()
async def get_collection_info(namespace: str, collection_id: str) -> str:
    """
    Retrieves detailed information about a specific collection using its namespace and ID.

    Args:
        namespace (str): The namespace of the collection.
        collection_id (str): The unique identifier for the collection.

    Returns:
        str: A JSON string containing collection details.

    Example:
        get_collection_info(namespace="huggingface", collection_id="vision_collection")

    Raises:
        ValueError: If namespace or collection_id is empty.
        RuntimeError: If the API request fails.
    """
    if not namespace.strip() or not collection_id.strip():
        raise ValueError("Namespace and Collection ID cannot be empty.")

    api = HfApi()
    try:
        collection_info = api.collection_info(namespace, collection_id)
        return json.dumps(collection_info, default=default_serializer)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve collection info: {str(e)}")

if __name__ == "__main__":
    asyncio.run(mcp.run())