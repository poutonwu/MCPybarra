# mcp_mongodb_manager

## Overview

The `mcp_mongodb_manager` is a Model Context Protocol (MCP) server that provides a set of tools for interacting with MongoDB databases. It allows external systems and language models to perform common database operations such as listing databases, inserting documents, querying collections, and updating or deleting records.

This server uses the `FastMCP` interface to expose MongoDB functionality through JSON-RPC, enabling seamless integration between LLMs and MongoDB data sources.

## Installation

1. Ensure you have Python 3.10 or higher installed.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
mcp[cli]
pymongo
```

## Running the Server

To start the server, run the following command in your terminal:

```bash
python mcp_mongodb_manager.py
```

Ensure that MongoDB is running and accessible. You can also set a custom MongoDB connection URI using the `MONGO_URI` environment variable:

```bash
export MONGO_URI="mongodb://user:password@localhost:27017"
python mcp_mongodb_manager.py
```

## Available Tools

Below is a list of available MCP tools provided by the `mcp_mongodb_manager` server:

### `mcp_list_databases`

Lists all available databases in the connected MongoDB instance.

**Returns:**  
A JSON-formatted string containing a list of database names.

---

### `mcp_list_collections`

Lists all collections within a specified database.

**Args:**
- `database_name`: The name of the database to query.

**Returns:**  
A JSON-formatted string containing a list of collection names.

---

### `mcp_insert_document`

Inserts a new document into a specified collection within a specified database.

**Args:**
- `database_name`: Target database name.
- `collection_name`: Target collection name.
- `document`: A dictionary representing the document to insert.

**Returns:**  
A JSON-formatted string containing the ID of the inserted document.

---

### `mcp_find_documents`

Queries documents from a specified collection with optional filters, field projections, and limit.

**Args:**
- `database_name`: Target database name.
- `collection_name`: Target collection name.
- `query`: Optional filter to apply to documents.
- `projection`: Optional fields to include or exclude.
- `limit`: Optional maximum number of documents to return.

**Returns:**  
A JSON-formatted string containing a list of matching documents.

---

### `mcp_update_document`

Updates one or multiple documents in a collection based on a filter.

**Args:**
- `database_name`: Target database name.
- `collection_name`: Target collection name.
- `filter_query`: Filter to identify documents to update.
- `update_data`: Update operations to apply.
- `multi`: Boolean indicating whether to update all matches (`True`) or only the first match (`False`).

**Returns:**  
A JSON-formatted string containing the number of documents modified.

---

### `mcp_delete_document`

Deletes one or multiple documents from a collection based on a filter.

**Args:**
- `database_name`: Target database name.
- `collection_name`: Target collection name.
- `filter_query`: Filter to identify documents to delete.
- `multi`: Boolean indicating whether to delete all matches (`True`) or only the first match (`False`).

**Returns:**  
A JSON-formatted string containing the number of documents deleted.