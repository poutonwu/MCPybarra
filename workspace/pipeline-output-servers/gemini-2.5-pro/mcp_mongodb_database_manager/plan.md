# MCP Server Implementation Plan: MongoDB Management

This document outlines the implementation plan for an MCP server designed to manage MongoDB databases.

## 1. Server Overview

The server will provide a set of tools to automate the management of MongoDB databases. It will expose functionalities to list databases and collections, as well as perform CRUD (Create, Read, Update, Delete) operations on documents within those collections. This enables programmatic interaction with the database through the MCP protocol.

## 2. File to be Generated

All the server logic will be contained within a single Python file:
*   `mcp_mongodb_server.py`

## 3. Dependencies

The following third-party Python library is required:
*   `pymongo`: The official Python driver for MongoDB, used for all database interactions.

## 4. MCP Tools Plan

The server will implement the following tools. A single `pymongo.MongoClient` instance will be initialized and reused across all tools for efficient connection management.

---

### **Tool 1: `mcp_list_databases`**

*   **Function Name**: `mcp_list_databases`
*   **Description**: Lists the names of all available databases on the MongoDB server.
*   **Parameters**: None.
*   **Return Value**:
    *   **Type**: `list[str]`
    *   **Description**: A list containing the names of the databases as strings.
    *   **Example**: `["admin", "config", "local", "mydatabase"]`

---

### **Tool 2: `mcp_list_collections`**

*   **Function Name**: `mcp_list_collections`
*   **Description**: Lists the names of all collections within a specified database.
*   **Parameters**:
    *   `database_name` (`str`): The name of the database to inspect.
*   **Return Value**:
    *   **Type**: `list[str]`
    *   **Description**: A list containing the names of the collections as strings.
    *   **Example**: `["users", "products", "orders"]`

---

### **Tool 3: `mcp_insert_document`**

*   **Function Name**: `mcp_insert_document`
*   **Description**: Inserts a new document into a specified collection.
*   **Parameters**:
    *   `database_name` (`str`): The name of the target database.
    *   `collection_name` (`str`): The name of the target collection.
    *   `document` (`dict`): The document to be inserted, represented as a Python dictionary.
*   **Return Value**:
    *   **Type**: `dict`
    *   **Description**: A dictionary containing the string representation of the newly inserted document's `_id`.
    *   **Example**: `{"inserted_id": "64c9a3e6e7e4a4c4de54d7e1"}`

---

### **Tool 4: `mcp_find_documents`**

*   **Function Name**: `mcp_find_documents`
*   **Description**: Finds documents matching a specific query within a collection. Supports projection to shape the output and a limit on the number of results.
*   **Parameters**:
    *   `database_name` (`str`): The name of the database to query.
    *   `collection_name` (`str`): The name of the collection to query.
    *   `query` (`dict`): The MongoDB query filter. Use an empty dictionary `{}` to match all documents.
    *   `projection` (`dict`, optional): The projection specification to determine which fields to include or exclude. Defaults to `None` (all fields included). Example: `{"name": 1, "_id": 0}`.
    *   `limit` (`int`, optional): The maximum number of documents to return. Defaults to `100`.
*   **Return Value**:
    *   **Type**: `list[dict]`
    *   **Description**: A list of documents that match the query. The `_id` field of each document is converted to a string for JSON compatibility.
    *   **Example**: `[{"_id": "64c9a3e6e7e4a4c4de54d7e1", "name": "John Doe", "age": 30}]`

---

### **Tool 5: `mcp_update_document`**

*   **Function Name**: `mcp_update_document`
*   **Description**: Updates one or more documents that match a specified filter.
*   **Parameters**:
    *   `database_name` (`str`): The name of the database where the update will occur.
    *   `collection_name` (`str`): The name of the collection where the update will occur.
    *   `query` (`dict`): The filter to select the document(s) to update.
    *   `update` (`dict`): The update operations to be applied (e.g., using `$set`).
    *   `update_many` (`bool`, optional): If `True`, updates all documents matching the query. If `False` (default), updates only the first matching document.
*   **Return Value**:
    *   **Type**: `dict`
    *   **Description**: A dictionary containing the count of documents matched and the count of documents modified.
    *   **Example**: `{"matched_count": 1, "modified_count": 1}`

---

### **Tool 6: `mcp_delete_document`**

*   **Function Name**: `mcp_delete_document`
*   **Description**: Deletes one or more documents that match a specified filter.
*   **Parameters**:
    *   `database_name` (`str`): The name of the database from which to delete.
    *   `collection_name` (`str`): The name of the collection from which to delete.
    *   `query` (`dict`): The filter to select the document(s) for deletion.
    *   `delete_many` (`bool`, optional): If `True`, deletes all documents matching the query. If `False` (default), deletes only the first matching document.
*   **Return Value**:
    *   **Type**: `dict`
    *   **Description**: A dictionary containing the number of documents deleted.
    *   **Example**: `{"deleted_count": 1}`