import json
import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from huggingface_hub import (
    list_models,
    model_info,
    list_datasets,
    dataset_info,
    list_spaces,
    space_info,
    paper_info,
    list_papers,
    list_collections,
    get_collection,
)
from huggingface_hub.utils import HfHubHTTPError

# Initialize FastMCP server
mcp = FastMCP("mcp_huggingface_hub_manager")

def format_return(data):
    """Helper function to convert data to a JSON string."""
    if isinstance(data, list):
        return json.dumps([item.dict() for item in data], indent=2)
    elif hasattr(data, "dict"):
        return json.dumps(data.dict(), indent=2)
    if isinstance(data, dict) or isinstance(data, list):
        return json.dumps(data, indent=2)
    return str(data)

@mcp.tool()
async def search_models(
    query: Optional[str] = None,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: Optional[int] = 10,
) -> str:
    """
    Searches for models on the Hugging Face Hub based on specified criteria.

    Args:
        query (str, optional): Keyword search string to filter models. Defaults to None.
        author (str, optional): A user or organization name to filter by. Defaults to None.
        tags (list[str], optional): A list of library or framework tags to filter by (e.g., ['pytorch', 'text-classification']). Defaults to None.
        limit (int, optional): The maximum number of models to return. Defaults to 10.

    Returns:
        A JSON string representing a list of found models.

    Example:
        search_models(query="bert", limit=5)
    """
    try:
        models = list_models(search=query, author=author, tags=tags, limit=limit)
        return format_return(list(models))
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to search models on Hugging Face Hub: {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def get_model_info(model_id: str) -> str:
    """
    Retrieves detailed information for a specific model from the Hugging Face Hub.

    Args:
        model_id (str): The repository ID of the model (e.g., 'google-bert/bert-base-uncased').

    Returns:
        A JSON string containing detailed information about the model.

    Example:
        get_model_info(model_id="google-bert/bert-base-uncased")
    """
    try:
        info = model_info(model_id)
        return format_return(info)
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to retrieve model info for '{model_id}': {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def search_datasets(
    query: Optional[str] = None,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: Optional[int] = 10,
) -> str:
    """
    Searches for datasets on the Hugging Face Hub based on specified criteria.

    Args:
        query (str, optional): Keyword search string to filter datasets. Defaults to None.
        author (str, optional): A user or organization name to filter by. Defaults to None.
        tags (list[str], optional): A list of tags to filter by (e.g., ['text-classification']). Defaults to None.
        limit (int, optional): The maximum number of datasets to return. Defaults to 10.

    Returns:
        A JSON string representing a list of found datasets.

    Example:
        search_datasets(query="emotion", limit=5)
    """
    try:
        datasets = list_datasets(search=query, author=author, tags=tags, limit=limit)
        return format_return(list(datasets))
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to search datasets on Hugging Face Hub: {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def get_dataset_info(dataset_id: str) -> str:
    """
    Retrieves detailed information for a specific dataset from the Hugging Face Hub.

    Args:
        dataset_id (str): The repository ID of the dataset (e.g., 'huggingface/datasets-taggers').

    Returns:
        A JSON string containing detailed information about the dataset.

    Example:
        get_dataset_info(dataset_id="huggingface/datasets-taggers")
    """
    try:
        info = dataset_info(dataset_id)
        return format_return(info)
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to retrieve dataset info for '{dataset_id}': {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def search_spaces(
    query: Optional[str] = None,
    author: Optional[str] = None,
    sdk: Optional[str] = None,
    limit: Optional[int] = 10,
) -> str:
    """
    Searches for Spaces on the Hugging Face Hub based on specified criteria.

    Args:
        query (str, optional): Keyword search string to filter Spaces. Defaults to None.
        author (str, optional): A user or organization name to filter by. Defaults to None.
        sdk (str, optional): The SDK used by the Space (e.g., 'gradio', 'streamlit'). Defaults to None.
        limit (int, optional): The maximum number of Spaces to return. Defaults to 10.

    Returns:
        A JSON string representing a list of found Spaces.

    Example:
        search_spaces(query="text generation", sdk="gradio", limit=5)
    """
    try:
        # Filter spaces by SDK manually since it's not supported by the API directly
        spaces = list_spaces(search=query, author=author, limit=limit)
        if sdk:
            filtered_spaces = [space for space in spaces if getattr(space, 'sdk', None) == sdk]
            return format_return(filtered_spaces)
        return format_return(list(spaces))
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to search spaces on Hugging Face Hub: {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def get_space_info(space_id: str) -> str:
    """
    Retrieves detailed information for a specific Space from the Hugging Face Hub.

    Args:
        space_id (str): The repository ID of the Space (e.g., 'huggingface-projects/diffusers-gallery').

    Returns:
        A JSON string containing detailed information about the Space.

    Example:
        get_space_info(space_id="huggingface-projects/diffusers-gallery")
    """
    try:
        info = space_info(space_id)
        return format_return(info)
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to retrieve space info for '{space_id}': {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def get_paper_info(paper_id: str) -> str:
    """
    Retrieves detailed information for a specific paper from Hugging Face, using its arXiv ID.

    Args:
        paper_id (str): The arXiv ID of the paper (e.g., '2305.15334').

    Returns:
        A JSON string containing the paper's details.

    Example:
        get_paper_info(paper_id="2305.15334")
    """
    try:
        info = paper_info(paper_id)
        return format_return(info)
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to retrieve paper info for '{paper_id}': {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def get_daily_papers(limit: Optional[int] = 10) -> str:
    """
    Retrieves the list of daily trending papers from the Hugging Face Hub.

    Args:
        limit (int, optional): The maximum number of papers to return. Defaults to 10.

    Returns:
        A JSON string representing a list of the most recent papers.

    Example:
        get_daily_papers(limit=5)
    """
    try:
        papers = list_papers()
        # Manually apply the limit since it's not supported by the API directly
        return format_return(list(papers)[:limit])
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to retrieve daily papers: {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def search_collections(
    query: Optional[str] = None,
    owner: Optional[str] = None,
    limit: Optional[int] = 10,
) -> str:
    """
    Searches for Collections on the Hugging Face Hub.

    Args:
        query (str, optional): Keyword search string to filter collections. Defaults to None.
        owner (str, optional): A user or organization name who owns the collection. Defaults to None.
        limit (int, optional): The maximum number of collections to return. Defaults to 10.

    Returns:
        A JSON string representing a list of found Collections.

    Example:
        search_collections(query="vision", owner="google", limit=5)
    """
    try:
        collections = list_collections(owner=owner)
        # Manually apply query filtering since it's not supported by the API directly
        if query:
            filtered_collections = [col for col in collections if query.lower() in col.name.lower() or 
                                      any(query.lower() in tag.lower() for tag in getattr(col, 'tags', []))]
            return format_return(list(filtered_collections)[:limit])
        return format_return(list(collections)[:limit])
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to search collections on Hugging Face Hub: {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

@mcp.tool()
async def get_collection_info(collection_slug: str) -> str:
    """
    Retrieves detailed information for a specific Collection from the Hugging Face Hub.

    Args:
        collection_slug (str): The unique slug for the collection (e.g., 'google/bert').

    Returns:
        A JSON string containing detailed information about the Collection.

    Example:
        get_collection_info(collection_slug="google/bert")
    """
    try:
        info = get_collection(collection_slug)
        return format_return(info)
    except HfHubHTTPError as e:
        return json.dumps({"error": f"Failed to retrieve collection info for '{collection_slug}': {e}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})

if __name__ == "__main__":
    # The following line is for development on Windows to prevent encoding errors.
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()