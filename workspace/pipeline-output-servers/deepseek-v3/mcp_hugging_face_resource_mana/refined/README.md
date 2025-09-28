# mcp_hugging_face_resource_mana

## Overview

The `mcp_hugging_face_resource_mana` server is an MCP-compliant tool server that provides access to Hugging Face Hub and arXiv resources. It enables large language models (LLMs) to search and retrieve information about models, datasets, Spaces, papers, and collections hosted on Hugging Face or indexed by arXiv.

This server supports asynchronous operations for efficient data retrieval and includes robust input validation and error handling.

## Installation

Before running the server, ensure you have Python 3.10+ installed and then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure your `requirements.txt` includes the following packages:

```
mcp[cli]
httpx
```

## Running the Server

To start the server, run the following command in your terminal:

```bash
python mcp_hugging_face_resource_mana.py
```

Ensure the script file is named appropriately (e.g., `mcp_hugging_face_resource_mana.py`) and is executable.

## Available Tools

Below is a list of available tools provided by this server:

### `search_models`
Search for models on Hugging Face based on keywords, author, or tags.

**Args:**  
- `keywords`: Search query for model names or descriptions.
- `author`: Filter models by author.
- `tags`: Filter models by tags.

### `get_model_info`
Retrieve detailed information about a specific model by its ID.

**Args:**  
- `model_id`: The unique identifier of the model.

### `search_datasets`
Search for datasets on Hugging Face based on keywords, author, or tags.

**Args:**  
- `keywords`: Search query for dataset names or descriptions.
- `author`: Filter datasets by author.
- `tags`: Filter datasets by tags.

### `get_dataset_info`
Retrieve detailed information about a specific dataset by its ID.

**Args:**  
- `dataset_id`: The unique identifier of the dataset.

### `search_spaces`
Search for Spaces on Hugging Face based on keywords, author, tags, or SDK.

**Args:**  
- `keywords`: Search query for Space names or descriptions.
- `author`: Filter Spaces by author.
- `tags`: Filter Spaces by tags.
- `sdk`: Filter Spaces by SDK (e.g., "gradio", "streamlit").

### `get_space_info`
Retrieve detailed information about a specific Space by its ID.

**Args:**  
- `space_id`: The unique identifier of the Space.

### `get_paper_info`
Retrieve detailed information about an arXiv paper by its ID.

**Args:**  
- `paper_id`: The arXiv ID of the paper.

### `get_daily_papers`
Retrieve a list of daily featured papers from Hugging Face.

### `search_collections`
Search for collections on Hugging Face based on owner, included items, or keywords.

**Args:**  
- `owner`: Filter collections by owner.
- `items`: Filter collections by included items.
- `keywords`: Search query for collection names or descriptions.

### `get_collection_info`
Retrieve detailed information about a specific collection by its namespace and ID.

**Args:**  
- `namespace`: The namespace of the collection.
- `collection_id`: The unique identifier of the collection.