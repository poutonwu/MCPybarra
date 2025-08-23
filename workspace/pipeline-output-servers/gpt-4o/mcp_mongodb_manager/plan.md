```markdown
# MCP Server Implementation Plan

## MCP Tools Plan

### Tool: `mcp_list_databases`
- **Description**: Lists all available databases in the MongoDB server.
- **Parameters**:
  - None.
- **Return Value**:
  - A list of database names (e.g., `["admin", "local", "my_database"]`).

### Tool: `mcp_list_collections`
- **Description**: Lists all collections within a specified database.
- **Parameters**:
  - `database_name` (string): The name of the database to query.
- **Return Value**:
  - A list of collection names within the specified database (e.g., `["users", "orders", "products"]`).

### Tool: `mcp_insert_document`
- **Description**: Inserts a new document into a specified MongoDB database and collection.
- **Parameters**:
  - `database_name` (string): The name of the database.
  - `collection_name` (string): The name of the collection.
  - `document` (object): The document to insert (e.g., `{"name": "John", "age": 30}`).
- **Return Value**:
  - The ID of the inserted document (e.g., `{"_id": "63a1b2c3d4e5f67890"}`).

### Tool: `mcp_find_documents`
- **Description**: Queries documents in a specified MongoDB database and collection, with support for filtering, projection, and limiting the number of results.
- **Parameters**:
  - `database_name` (string): The name of the database.
  - `collection_name` (string): The name of the collection.
  - `filter` (object, optional): The filter criteria for the query (e.g., `{"age": {"$gte": 25}}`).
  - `projection` (object, optional): The fields to include or exclude (e.g., `{"name": 1, "_id": 0}`).
  - `limit` (integer, optional): The maximum number of documents to return.
- **Return Value**:
  - A list of documents matching the query criteria.

### Tool: `mcp_update_document`
- **Description**: Updates documents in a specified MongoDB database and collection, with support for single or multiple document updates.
- **Parameters**:
  - `database_name` (string): The name of the database.
  - `collection_name` (string): The name of the collection.
  - `filter` (object): The filter criteria to match documents for updating (e.g., `{"name": "John"}`).
  - `update` (object): The update operations to apply (e.g., `{"$set": {"age": 35}}`).
  - `multi` (boolean, optional): If true, updates all matching documents; otherwise, updates only the first match.
- **Return Value**:
  - The count of documents updated.

### Tool: `mcp_delete_document`
- **Description**: Deletes documents in a specified MongoDB database and collection, with support for single or multiple document deletions.
- **Parameters**:
  - `database_name` (string): The name of the database.
  - `collection_name` (string): The name of the collection.
  - `filter` (object): The filter criteria to match documents for deletion (e.g., `{"age": {"$lt": 20}}`).
  - `multi` (boolean, optional): If true, deletes all matching documents; otherwise, deletes only the first match.
- **Return Value**:
  - The count of documents deleted.

## Server Overview
The MCP server is an automation tool for managing MongoDB databases. It provides functionalities to list databases and collections, insert documents, query documents with filter and projection, update documents, and delete documents. Each functionality is exposed as an MCP tool, enabling seamless integration with applications.

## File to be Generated
The server implementation will be contained in a single Python file named `mcp_mongodb_server.py`.

## Dependencies
- **pymongo**: A Python library for interacting with MongoDB.
- **mcp**: The MCP SDK for creating MCP servers.
- **httpx**: For potential asynchronous operations, though not required for the current implementation.
```