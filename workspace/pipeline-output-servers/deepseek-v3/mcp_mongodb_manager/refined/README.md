# mcp_mongodb_manager

## Overview

The `mcp_mongodb_manager` is a Model Context Protocol (MCP) server that provides an interface for interacting with MongoDB databases. It allows external tools and LLMs to perform common database operations such as checking the health of the MongoDB connection, listing databases and collections, inserting, querying, updating, and deleting documents, and managing databases and collections.

This server uses the `FastMCP` framework to expose MongoDB functionality through standardized MCP tools.

## Installation

Before running the server, ensure you have Python 3.10+ installed. Then install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure MongoDB is running locally on the default port (`27017`) or update the connection string in the code accordingly.

## Running the Server

To start the server, run the following command:

```bash
python mcp_mongodb_manager.py
```

By default, the server runs using the `stdio` transport protocol. You can modify this behavior by passing a different transport option to the `run()` method if needed.

## Available Tools

Below is a list of available tools exposed by the `mcp_mongodb_manager`. Each tool is described based on its functionality and expected input/output.

### 1. `mcp_health_check`

**Description:** Checks whether the MongoDB server is reachable and responsive.

**Returns:** A string indicating the health status of the MongoDB connection.

---

### 2. `mcp_list_databases`

**Description:** Lists all databases currently available in the MongoDB instance.

**Returns:** A list of database names.

---

### 3. `mcp_list_collections`

**Description:** Lists all collections in a specified database.

**Args:**
- `database_name`: The name of the database to query.

**Returns:** A list of collection names in the specified database.

---

### 4. `mcp_insert_document`

**Description:** Inserts a new document into a specified MongoDB collection.

**Args:**
- `database_name`: Name of the target database.
- `collection_name`: Name of the target collection.
- `document`: A dictionary representing the document to insert.

**Returns:** A message confirming successful insertion and the ID of the inserted document, or an error message.

---

### 5. `mcp_find_documents`

**Description:** Queries documents from a specified MongoDB collection with optional filtering, projection, and limit.

**Args:**
- `database_name`: Name of the target database.
- `collection_name`: Name of the target collection.
- `query`: Optional dictionary specifying the filter criteria.
- `projection`: Optional dictionary specifying which fields to include/exclude.
- `limit`: Optional integer limiting the number of results returned.

**Returns:** A list of matching documents or an error message.

---

### 6. `mcp_update_document`

**Description:** Updates one or more documents in a specified MongoDB collection based on a query.

**Args:**
- `database_name`: Name of the target database.
- `collection_name`: Name of the target collection.
- `query`: Dictionary specifying which documents to update.
- `update`: Dictionary specifying the update operations.
- `multi`: Boolean indicating whether to update multiple documents (default: `False`).

**Returns:** A message indicating how many documents were updated successfully or an error message.

---

### 7. `mcp_delete_document`

**Description:** Deletes one or more documents from a specified MongoDB collection based on a query.

**Args:**
- `database_name`: Name of the target database.
- `collection_name`: Name of the target collection.
- `query`: Dictionary specifying which documents to delete.
- `multi`: Boolean indicating whether to delete multiple documents (default: `False`).

**Returns:** A message indicating how many documents were deleted successfully or an error message.

---

### 8. `mcp_drop_database`

**Description:** Drops (deletes) an entire database.

**Args:**
- `database_name`: Name of the database to drop.

**Returns:** A message indicating whether the database was successfully dropped or an error message.

---

### 9. `mcp_drop_collection`

**Description:** Drops (deletes) a specific collection from a database.

**Args:**
- `database_name`: Name of the target database.
- `collection_name`: Name of the collection to drop.

**Returns:** A message indicating whether the collection was successfully dropped or an error message.