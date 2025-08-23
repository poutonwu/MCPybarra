### MCP Tools Plan

1. **Function Name**: `mcp_list_databases`  
   - **Description**: Lists all available databases in the MongoDB instance.  
   - **Parameters**: None  
   - **Return Value**: A list of strings, where each string represents a database name.  

2. **Function Name**: `mcp_list_collections`  
   - **Description**: Lists all collections in a specified MongoDB database.  
   - **Parameters**:  
     - `database_name` (str): The name of the database to query.  
   - **Return Value**: A list of strings, where each string represents a collection name in the specified database.  

3. **Function Name**: `mcp_insert_document`  
   - **Description**: Inserts a new document into a specified MongoDB collection.  
   - **Parameters**:  
     - `database_name` (str): The name of the database.  
     - `collection_name` (str): The name of the collection.  
     - `document` (dict): The document to insert.  
   - **Return Value**: A string indicating the success or failure of the insertion, including the inserted document's ID if successful.  

4. **Function Name**: `mcp_find_documents`  
   - **Description**: Queries documents in a specified MongoDB collection, with support for projection and result limiting.  
   - **Parameters**:  
     - `database_name` (str): The name of the database.  
     - `collection_name` (str): The name of the collection.  
     - `query` (dict, optional): The query criteria. Defaults to `{}` (all documents).  
     - `projection` (dict, optional): The fields to include/exclude in the results. Defaults to `None` (all fields).  
     - `limit` (int, optional): The maximum number of documents to return. Defaults to `0` (no limit).  
   - **Return Value**: A list of dictionaries, where each dictionary represents a matching document.  

5. **Function Name**: `mcp_update_document`  
   - **Description**: Updates documents in a specified MongoDB collection, supporting single or multiple updates.  
   - **Parameters**:  
     - `database_name` (str): The name of the database.  
     - `collection_name` (str): The name of the collection.  
     - `query` (dict): The query criteria to select documents to update.  
     - `update` (dict): The update operations to apply.  
     - `multi` (bool, optional): Whether to update multiple documents. Defaults to `False`.  
   - **Return Value**: A string indicating the success or failure of the update, including the number of documents modified.  

6. **Function Name**: `mcp_delete_document`  
   - **Description**: Deletes documents from a specified MongoDB collection, supporting single or batch deletion.  
   - **Parameters**:  
     - `database_name` (str): The name of the database.  
     - `collection_name` (str): The name of the collection.  
     - `query` (dict): The query criteria to select documents to delete.  
     - `multi` (bool, optional): Whether to delete multiple documents. Defaults to `False`.  
   - **Return Value**: A string indicating the success or failure of the deletion, including the number of documents deleted.  

---

### Server Overview  
The MCP server will automate MongoDB database management, providing tools to list databases and collections, insert, query, update, and delete documents. All functionalities are exposed via JSON-RPC 2.0, ensuring seamless integration with LLMs or other clients.  

---

### File to be Generated  
- **Filename**: `mcp_mongodb_server.py`  

---

### Dependencies  
- **Python 3.10+**  
- **MCP SDK**: `pip install mcp[cli]`  
- **PyMongo**: `pip install pymongo` (for MongoDB interactions)  
- **httpx**: `pip install httpx` (for optional HTTP-based features)