# mcp_hugging_face_hub_manager

## Overview

`mcp_hugging_face_hub_manager` is an MCP (Model Context Protocol) server that provides seamless integration with the Hugging Face Hub. It enables large language models (LLMs) to search and retrieve information about models, datasets, Spaces, papers, and collections hosted on Hugging Face.

This server supports multiple tools for querying Hugging Face resources and retrieving detailed metadata, making it ideal for use in AI development environments where real-time access to model and dataset information is essential.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
huggingface_hub
fastapi
uvicorn
```

## Running the Server

To start the server, run the following command:

```bash
python mcp_hugging_face_hub_manager.py
```

By default, the server will run using the `stdio` transport protocol. You can modify the `.run()` method in the code to specify a different transport such as `"sse"` or `"http"` if needed.

## Available Tools

The following tools are available via the MCP interface:

### **search_models**
Search for Hugging Face models based on a query string, author, and/or tags.

**Example:**
```python
search_models(query="transformers", author="google", tags=["text-classification"])
```

---

### **get_model_info**
Get detailed information about a specific Hugging Face model by its ID.

**Example:**
```python
get_model_info(model_id="google/bert-base-uncased")
```

---

### **search_datasets**
Search for Hugging Face datasets based on a query string, author, and/or tags.

**Example:**
```python
search_datasets(query="text classification", author="huggingface", tags=["text"])
```

---

### **get_dataset_info**
Get detailed information about a specific Hugging Face dataset by its ID.

**Example:**
```python
get_dataset_info(dataset_id="huggingface/common_voice")
```

---

### **search_spaces**
Search for Hugging Face Spaces based on a query string, author, tags, and SDK.

**Example:**
```python
search_spaces(query="gradio app", author="gradio", tags=["app"], sdk="gradio")
```

---

### **get_space_info**
Get detailed information about a specific Hugging Face Space by its ID.

**Example:**
```python
get_space_info(space_id="gradio/calculator")
```

---

### **get_daily_papers**
Retrieve a list of featured research papers from Hugging Face.

**Example:**
```python
get_daily_papers()
```

---

### **get_paper_info**
Retrieve detailed information about a specific arXiv paper using its ID (not yet implemented).

**Example:**
```python
get_paper_info(paper_id="2305.12345")
```

---

### **search_collections**
Search for Hugging Face collections based on owner, entry, or query string (not yet implemented).

**Example:**
```python
search_collections(owner="huggingface", entry="transformers", query="NLP")
```

---

### **get_collection_info**
Retrieve detailed information about a specific Hugging Face collection (not yet implemented).

**Example:**
```python
get_collection_info(namespace="huggingface", collection_id="transformers-collection")
```