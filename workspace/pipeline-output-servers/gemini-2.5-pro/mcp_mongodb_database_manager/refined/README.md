# mcp_mongodb_database_manager

A Model Context Protocol (MCP) server that provides MongoDB database management capabilities, allowing tools to interact with a MongoDB instance for common database operations.

## Overview

The `mcp_mongodb_database_manager` server enables integration between LLMs and MongoDB through the MCP protocol. It exposes several tools for managing databases, collections, and documents directly from an LLM-powered interface.

This server supports operations such as listing databases and collections, inserting, querying, updating, and deleting documents in a MongoDB instance.

---

## Installation

Make sure you have Python 3.10 or higher installed.

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

Ensure your `requirements.txt` includes the following:

```
mcp[cli]
pymongo
```

2. Set up the MongoDB connection:

It is recommended to set the `MONGODB_URI` environment variable to point to your MongoDB instance:

```bash
export MONGODB_URI="mongodb://user:password@host:port/"
```

If not set, it defaults to `mongodb://localhost:27017/`.

---

## Running the Server

To run the server, execute the Python script from the command line:

```bash
python mcp_mongodb_database_manager.py
```

This will start the MCP server using the default `stdio` transport.

---

## Available Tools

Each tool is registered using the `@mcp.tool()` decorator and has a complete description visible to the LLM.

### `mcp_list_databases()`

Lists all available databases on the MongoDB server.

**Returns:**  
A JSON array of database names.

---

### `mcp_list_collections(database_name: str)`

Lists all collections in the specified database.

**Args:**  
- `database_name`: The name of the target database.

**Returns:**  
A JSON array of collection names.

---

### `mcp_insert_document(database_name: str, collection_name: str, document: dict)`

Inserts a new document into the specified collection.

**Args:**  
- `database_name`: Target database.
- `collection_name`: Target collection.
- `document`: A dictionary representing the document to insert.

**Returns:**  
A JSON object containing the string representation of the inserted document's `_id`.

---

### `mcp_find_documents(database_name: str, collection_name: str, query: dict, projection: dict = None, limit: int = 100)`

Finds documents matching a given query in the specified collection.

**Args:**  
- `database_name`: Target database.
- `collection_name`: Target collection.
- `query`: A dictionary representing the query filter.
- `projection` *(optional)*: Specifies which fields to return.
- `limit` *(optional)*: Maximum number of documents to return (default: 100).

**Returns:**  
A JSON array of matching documents.

---

### `mcp_update_document(database_name: str, collection_name: str, query: dict, update: dict, update_many: bool = False)`

Updates one or more documents matching the query.

**Args:**  
- `database_name`: Target database.
- `collection_name`: Target collection.
- `query`: Filter to match documents for update.
- `update`: Dictionary specifying update operations (e.g., `$set`).
- `update_many` *(optional)*: If True, updates all matching documents.

**Returns:**  
A JSON object indicating how many documents were matched and modified.

---

### `mcp_delete_document(database_name: str, collection_name: str, query: dict, delete_many: bool = False)`

Deletes one or more documents matching the query.

**Args:**  
- `database_name`: Target database.
- `collection_name`: Target collection.
- `query`: Filter to match documents for deletion.
- `delete_many` *(optional)*: If True, deletes all matching documents.

**Returns:**  
A JSON object indicating how many documents were deleted.