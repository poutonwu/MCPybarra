import os
import json
from typing import List, Dict, Optional, Any
from mcp.server.fastmcp import FastMCP
from huggingface_hub import HfApi

# Initialize the MCP server
mcp = FastMCP("hugging_face_hub_manager")

# Configure proxy settings if necessary
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# Initialize the Hugging Face API client
hf_api = HfApi()

@mcp.tool()
def search_models(
    query: str,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Search for models on the Hugging Face Hub based on user-provided criteria.

    Args:
        query: A string containing keywords or a search string (e.g., 'transformers').
        author: Optional; The model's author name (e.g., 'google').
        tags: Optional; A list of tags to filter models (e.g., ['text-classification', 'en']).

    Returns:
        A JSON-formatted string containing a list of matching models, each with its name, author, download count, tags, and description.

    Example:
        search_models(query="transformers", author="google", tags=["text-classification"])
    """
    try:
        models = hf_api.list_models(
            filter=tags,
            author=author,
            search=query
        )
        result = [
            {
                "model_name": model.modelId,
                "author": model.author,
                "downloads": model.downloads,
                "tags": model.tags,
                "description": getattr(model, 'description', '')
            }
            for model in models
        ]
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to search models: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_model_info(model_id: str) -> str:
    """
    Retrieve detailed information about a specific model from the Hugging Face Hub.

    Args:
        model_id: The unique identifier of the model (e.g., 'google/bert-base-uncased').

    Returns:
        A JSON-formatted string containing the model's details such as author, tags, downloads, and description.

    Example:
        get_model_info(model_id="google/bert-base-uncased")
    """
    try:
        model_info = hf_api.model_info(repo_id=model_id)
        result = {
            "model_name": model_info.modelId,
            "author": model_info.author,
            "downloads": model_info.downloads,
            "tags": model_info.tags,
            "description": getattr(model_info, 'description', '')
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve model info: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def search_datasets(
    query: str,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Search for datasets on the Hugging Face Hub based on user-provided criteria.

    Args:
        query: A string containing keywords or a search string (e.g., 'text classification').
        author: Optional; The dataset's author name (e.g., 'huggingface').
        tags: Optional; A list of tags to filter datasets (e.g., ['text', 'classification']).

    Returns:
        A JSON-formatted string containing a list of matching datasets, each with its name, author, download count, tags, and description.

    Example:
        search_datasets(query="text classification", author="huggingface", tags=["text"])
    """
    try:
        datasets = hf_api.list_datasets(
            filter=tags,
            author=author,
            search=query
        )
        result = [
            {
                "dataset_name": dataset.id,
                "author": dataset.author,
                "downloads": dataset.downloads,
                "tags": dataset.tags,
                "description": getattr(dataset, 'description', '')
            }
            for dataset in datasets
        ]
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to search datasets: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_dataset_info(dataset_id: str) -> str:
    """
    Retrieve detailed information about a specific dataset from the Hugging Face Hub.

    Args:
        dataset_id: The unique identifier of the dataset (e.g., 'huggingface/common_voice').

    Returns:
        A JSON-formatted string containing the dataset's details such as author, tags, downloads, and description.

    Example:
        get_dataset_info(dataset_id="huggingface/common_voice")
    """
    try:
        dataset_info = hf_api.dataset_info(repo_id=dataset_id)
        result = {
            "dataset_name": dataset_info.id,
            "author": dataset_info.author,
            "downloads": dataset_info.downloads,
            "tags": dataset_info.tags,
            "description": getattr(dataset_info, 'description', '')
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve dataset info: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def search_spaces(
    query: str,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    sdk: Optional[str] = None
) -> str:
    """
    Search for Spaces on the Hugging Face Hub based on user-provided criteria.

    Args:
        query: A string containing keywords or a search string (e.g., 'gradio app').
        author: Optional; The Space's author name (e.g., 'gradio').
        tags: Optional; A list of tags to filter Spaces (e.g., ['app', 'demo']).
        sdk: Optional; The SDK used to create the Space (e.g., 'gradio').

    Returns:
        A JSON-formatted string containing a list of matching Spaces, each with its name, author, SDK, tags, and description.

    Example:
        search_spaces(query="gradio app", author="gradio", tags=["app"], sdk="gradio")
    """
    try:
        spaces = hf_api.list_spaces(
            filter=tags,
            author=author,
            search=query
        )
        result = [
            {
                "space_name": space.id,
                "author": space.author,
                "sdk": space.sdk,
                "tags": space.tags,
                "description": getattr(space, 'description', '')
            }
            for space in spaces
        ]
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to search spaces: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_space_info(space_id: str) -> str:
    """
    Retrieve detailed information about a specific Space from the Hugging Face Hub.

    Args:
        space_id: The unique identifier of the Space (e.g., 'gradio/calculator').

    Returns:
        A JSON-formatted string containing the Space's details such as author, SDK, tags, and description.

    Example:
        get_space_info(space_id="gradio/calculator")
    """
    try:
        space_info = hf_api.space_info(repo_id=space_id)
        result = {
            "space_name": space_info.id,
            "author": space_info.author,
            "sdk": space_info.sdk,
            "tags": space_info.tags,
            "description": getattr(space_info, 'description', '')
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve space info: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_paper_info(paper_id: str) -> str:
    """
    Retrieve detailed information about a specific arXiv paper using its ID.

    Args:
        paper_id: The unique identifier of the arXiv paper (e.g., '2305.12345').

    Returns:
        A JSON-formatted string containing the paper's details such as title, authors, abstract, and related implementations.

    Example:
        get_paper_info(paper_id="2305.12345")
    """
    try:
        # Placeholder for future implementation
        raise NotImplementedError("This feature is not yet implemented.")
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve paper info: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_daily_papers() -> str:
    """
    Retrieve a list of daily featured papers from Hugging Face.

    Returns:
        A JSON-formatted string containing a list of featured papers, each with its title, authors, and abstract.

    Example:
        get_daily_papers()
    """
    try:
        # Placeholder for future implementation
        raise NotImplementedError("This feature is not yet implemented.")
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve daily papers: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def search_collections(
    owner: Optional[str] = None,
    entry: Optional[str] = None,
    query: str = ""
) -> str:
    """
    Search for collections on the Hugging Face Hub based on user-provided criteria.

    Args:
        owner: Optional; The owner of the collection (e.g., 'huggingface').
        entry: Optional; A specific entry within the collection (e.g., 'transformers').
        query: A string containing keywords or a search string (e.g., 'NLP').

    Returns:
        A JSON-formatted string containing a list of matching collections, each with its title, owner, description, and entries.

    Example:
        search_collections(owner="huggingface", entry="transformers", query="NLP")
    """
    try:
        # Placeholder for future implementation
        raise NotImplementedError("This feature is not yet implemented.")
    except Exception as e:
        return json.dumps({"error": f"Failed to search collections: {str(e)}"}, ensure_ascii=False)

@mcp.tool()
def get_collection_info(namespace: str, collection_id: str) -> str:
    """
    Retrieve detailed information about a specific collection from the Hugging Face Hub.

    Args:
        namespace: The namespace of the collection (e.g., 'huggingface').
        collection_id: The unique identifier of the collection (e.g., 'transformers-collection').

    Returns:
        A JSON-formatted string containing the collection's details such as title, owner, description, and entries.

    Example:
        get_collection_info(namespace="huggingface", collection_id="transformers-collection")
    """
    try:
        # Placeholder for future implementation
        raise NotImplementedError("This feature is not yet implemented.")
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve collection info: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()