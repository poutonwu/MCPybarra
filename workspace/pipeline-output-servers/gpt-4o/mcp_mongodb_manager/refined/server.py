import os
import sys
import json
from pymongo import MongoClient
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("mcp_mongodb_manager")

# MongoDB connection setup
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

@mcp.tool()
def mcp_list_databases():
    """
    Lists all available databases in the MongoDB server.

    Returns:
        str: A JSON string containing a list of database names.

    Example:
        >>> mcp_list_databases()
        '["admin", "local", "my_database"]'
    """
    try:
        databases = client.list_database_names()
        return json.dumps(databases)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def mcp_list_collections(database_name: str):
    """
    Lists all collections within a specified database.

    Args:
        database_name (str): The name of the database to query.

    Returns:
        str: A JSON string containing a list of collection names.

    Example:
        >>> mcp_list_collections("my_database")
        '["users", "orders", "products"]'
    """
    try:
        db = client[database_name]
        collections = db.list_collection_names()
        return json.dumps(collections)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def mcp_insert_document(database_name: str, collection_name: str, document: dict):
    """
    Inserts a new document into a specified MongoDB database and collection.

    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection.
        document (dict): The document to insert.

    Returns:
        str: A JSON string containing the ID of the inserted document.

    Example:
        >>> mcp_insert_document("my_database", "users", {"name": "John", "age": 30})
        '{"_id": "63a1b2c3d4e5f67890"}'
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.insert_one(document)
        return json.dumps({"_id": str(result.inserted_id)})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def mcp_find_documents(database_name: str, collection_name: str, filter: dict = None, projection: dict = None, limit: int = 0):
    """
    Queries documents in a specified MongoDB database and collection, with support for filtering, projection, and limiting the number of results.

    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection.
        filter (dict, optional): The filter criteria for the query.
        projection (dict, optional): The fields to include or exclude.
        limit (int, optional): The maximum number of documents to return.

    Returns:
        str: A JSON string containing a list of documents matching the query criteria.

    Example:
        >>> mcp_find_documents("my_database", "users", {"age": {"$gte": 25}}, {"name": 1, "_id": 0}, 10)
        '[{"name": "John"}, {"name": "Jane"}]'
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        cursor = collection.find(filter or {}, projection).limit(limit)
        documents = list(cursor)
        return json.dumps(documents, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def mcp_update_document(database_name: str, collection_name: str, filter: dict, update: dict, multi: bool = False):
    """
    Updates documents in a specified MongoDB database and collection, with support for single or multiple document updates.

    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection.
        filter (dict): The filter criteria to match documents for updating.
        update (dict): The update operations to apply.
        multi (bool, optional): If true, updates all matching documents; otherwise, updates only the first match.

    Returns:
        str: A JSON string containing the count of documents updated.

    Example:
        >>> mcp_update_document("my_database", "users", {"name": "John"}, {"$set": {"age": 35}}, True)
        '{"updated_count": 1}'
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        if multi:
            result = collection.update_many(filter, update)
        else:
            result = collection.update_one(filter, update)
        return json.dumps({"updated_count": result.modified_count})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def mcp_delete_document(database_name: str, collection_name: str, filter: dict, multi: bool = False):
    """
    Deletes documents in a specified MongoDB database and collection, with support for single or multiple document deletions.

    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection.
        filter (dict): The filter criteria to match documents for deletion.
        multi (bool, optional): If true, deletes all matching documents; otherwise, deletes only the first match.

    Returns:
        str: A JSON string containing the count of documents deleted.

    Example:
        >>> mcp_delete_document("my_database", "users", {"age": {"$lt": 20}}, True)
        '{"deleted_count": 2}'
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        if multi:
            result = collection.delete_many(filter)
        else:
            result = collection.delete_one(filter)
        return json.dumps({"deleted_count": result.deleted_count})
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Reconfigure stdout to handle UTF-8 encoding
    sys.stdout.reconfigure(encoding="utf-8")
    # Run the MCP server
    mcp.run()