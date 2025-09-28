# mcp_huggingface_hub_manager

## Overview
The `mcp_huggingface_hub_manager` server provides a set of tools to interact with the Hugging Face Hub, allowing users to search and retrieve information about models, datasets, Spaces, papers, and collections. It uses the Model Context Protocol (MCP) to expose these capabilities for integration with LLM-based applications.

## Installation
Make sure you have Python 3.10 or higher installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes:
```
mcp[cli]
huggingface_hub
```

## Running the Server
To start the server, run the following command:

```bash
python mcp_huggingface_hub_manager.py
```

This will launch the MCP server using the default `stdio` transport protocol.

## Available Tools

### `search_models`
Searches for models on Hugging Face Hub by keyword query, author, or tags.

**Example:**
```python
search_models(query="bert", limit=5)
```

---

### `get_model_info`
Retrieves detailed information for a specific model by its repository ID.

**Example:**
```python
get_model_info(model_id="google-bert/bert-base-uncased")
```

---

### `search_datasets`
Searches for datasets on Hugging Face Hub by keyword query, author, or tags.

**Example:**
```python
search_datasets(query="emotion", limit=5)
```

---

### `get_dataset_info`
Retrieves detailed information for a specific dataset by its repository ID.

**Example:**
```python
get_dataset_info(dataset_id="huggingface/datasets-taggers")
```

---

### `search_spaces`
Searches for Spaces on Hugging Face Hub by keyword query, author, or SDK (e.g., Gradio, Streamlit).

**Example:**
```python
search_spaces(query="text generation", sdk="gradio", limit=5)
```

---

### `get_space_info`
Retrieves detailed information for a specific Space by its repository ID.

**Example:**
```python
get_space_info(space_id="huggingface-projects/diffusers-gallery")
```

---

### `get_paper_info`
Retrieves detailed information for a paper by its arXiv ID.

**Example:**
```python
get_paper_info(paper_id="2305.15334")
```

---

### `get_daily_papers`
Retrieves the list of daily trending papers from Hugging Face.

**Example:**
```python
get_daily_papers(limit=5)
```

---

### `search_collections`
Searches for Collections on Hugging Face Hub by keyword query or owner.

**Example:**
```python
search_collections(query="vision", owner="google", limit=5)
```

---

### `get_collection_info`
Retrieves detailed information for a specific Collection by its slug.

**Example:**
```python
get_collection_info(collection_slug="google/bert")
```