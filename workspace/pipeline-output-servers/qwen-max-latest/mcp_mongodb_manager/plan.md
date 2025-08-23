### **MCP Tools Plan**

#### Tool 1: `mcp_list_databases`
- **Description**: Lists all available databases in the MongoDB instance.
- **Parameters**:
  - None
- **Return Value**: A list of strings, where each string represents the name of a database.

#### Tool 2: `mcp_list_collections`
- **Description**: Lists all collections within a specified database in the MongoDB instance.
- **Parameters**:
  - `database_name` (str): The name of the database whose collections need to be listed.
- **Return Value**: A list of strings, where each string represents the name of a collection within the specified database.

#### Tool 3: `mcp_insert_document`
- **Description**: Inserts a new document into a specified collection within a specified database.
- **Parameters**:
  - `database_name` (str): The name of the target database.
  - `collection_name` (str): The name of the target collection.
  - `document` (dict): The document to insert, represented as a Python dictionary.
- **Return Value**: A string containing the ID of the newly inserted document.

#### Tool 4: `mcp_find_documents`
- **Description**: Queries documents from a specified collection within a specified database, with optional projection and result limit.
- **Parameters**:
  - `database_name` (str): The name of the target database.
  - `collection_name` (str): The name of the target collection.
  - `query` (dict): A query filter represented as a Python dictionary.
  - `projection` (dict, optional): Specifies fields to include or exclude in the returned documents.
  - `limit` (int, optional): Limits the number of documents returned.
- **Return Value**: A list of dictionaries, where each dictionary represents a matching document.

#### Tool 5: `mcp_update_document`
- **Description**: Updates one or multiple documents in a specified collection within a specified database.
- **Parameters**:
  - `database_name` (str): The name of the target database.
  - `collection_name` (str): The name of the target collection.
  - `filter_query` (dict): A filter to identify the documents to update.
  - `update_data` (dict): The update operations to apply, represented as a Python dictionary.
  - `multi` (bool): If True, updates all matching documents; otherwise, updates only the first match.
- **Return Value**: An integer indicating the number of documents modified.

#### Tool 6: `mcp_delete_document`
- **Description**: Deletes one or multiple documents from a specified collection within a specified database.
- **Parameters**:
  - `database_name` (str): The name of the target database.
  - `collection_name` (str): The name of the target collection.
  - `filter_query` (dict): A filter to identify the documents to delete.
  - `multi` (bool): If True, deletes all matching documents; otherwise, deletes only the first match.
- **Return Value**: An integer indicating the number of documents deleted.

---

### **Server Overview**
The MCP server will provide an interface for automating MongoDB database management. It will support listing databases and collections, inserting documents, querying documents with projection and limits, updating single or multiple documents, and deleting documents either individually or in bulk.

---

### **File to be Generated**
- **File Name**: `mcp_mongodb_server.py`

---

### **Dependencies**
- `pymongo`: A Python driver for interacting with MongoDB.
- `mcp[cli]`: The MCP SDK required for building the server.