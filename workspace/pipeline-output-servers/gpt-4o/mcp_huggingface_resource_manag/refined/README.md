# mcp_huggingface_resource_manag

## Overview
The `mcp_huggingface_resource_manag` server provides a set of tools to interact with Hugging Face Hub and arXiv for searching and retrieving information about models, datasets, Spaces, collections, and academic papers. It acts as an interface between the Model Context Protocol (MCP) and external resources, allowing large language models (LLMs) to access up-to-date information from Hugging Face and arXiv programmatically.

## Installation
To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

Ensure your environment includes Python 3.10 or higher.

## Running the Server
To start the server, execute the Python script from the command line:

```bash
python mcp_huggingface_resource_manag.py
```

This will launch the MCP server using the default `stdio` transport protocol.

## Available Tools

### `search_models`
Searches Hugging Face Hub for models based on keywords, author, or tags.

**Parameters:**
- `keywords`: Search keywords.
- `author`: Optional filter by author.
- `tags`: Optional list of tags to filter results.

**Returns:** JSON string containing matching model data.

---

### `get_model_info`
Retrieves detailed information about a specific model using its ID.

**Parameters:**
- `model_id`: The unique identifier of the model on Hugging Face Hub.

**Returns:** JSON string containing model metadata.

---

### `search_datasets`
Searches Hugging Face Hub for datasets based on keywords, author, or tags.

**Parameters:**
- `keywords`: Search keywords.
- `author`: Optional filter by author.
- `tags`: Optional list of tags to filter results.

**Returns:** JSON string containing matching dataset data.

---

### `get_dataset_info`
Retrieves detailed information about a specific dataset using its ID.

**Parameters:**
- `dataset_id`: The unique identifier of the dataset on Hugging Face Hub.

**Returns:** JSON string containing dataset metadata.

---

### `search_spaces`
Searches Hugging Face Hub for Spaces based on keywords, author, tags, or SDK type.

**Parameters:**
- `keywords`: Search keywords.
- `author`: Optional filter by author.
- `tags`: Optional list of tags to filter results.
- `sdk`: Optional SDK type used in the Space (e.g., "gradio", "streamlit").

**Returns:** JSON string containing matching Space data.

---

### `get_space_info`
Retrieves detailed information about a specific Space using its ID.

**Parameters:**
- `space_id`: The unique identifier of the Space on Hugging Face Hub.

**Returns:** JSON string containing Space metadata.

---

### `get_paper_info`
Fetches detailed information about a paper from arXiv using its ID.

**Parameters:**
- `arxiv_id`: The unique identifier of the paper on arXiv.

**Returns:** JSON string containing title, authors, abstract, and PDF URL.

---

### `get_daily_papers`
Retrieves a list of selected daily papers from Hugging Face.

**Parameters:** None  
**Returns:** JSON string containing daily paper details.

---

### `search_collections`
Searches Hugging Face Hub for collections based on keywords, owner, or entries.

**Parameters:**
- `keywords`: Search keywords.
- `owner`: Optional filter by collection owner.
- `entries`: Optional list of entries to refine the search.

**Returns:** JSON string containing matching collection data.

---

### `get_collection_info`
Retrieves detailed information about a specific collection using its namespace and ID.

**Parameters:**
- `namespace`: Owner or organization name.
- `collection_id`: Unique identifier of the collection.

**Returns:** JSON string containing collection metadata.