import sys
import os
import json
from mcp.server.fastmcp import FastMCP
import pymongo
from bson.objectid import ObjectId
from typing import Dict, Any, List

# Initialize FastMCP server
mcp = FastMCP("mcp_mongodb_database_manager")

# --- Database Connection ---
# It is recommended to use environment variables for sensitive data like connection strings.
# For local development, you can set the MONGODB_URI environment variable.
# Example: export MONGODB_URI="mongodb://user:password@host:port/"
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(MONGODB_URI)

# --- Custom JSON Encoder for MongoDB ---
class MongoJSONEncoder(json.JSONEncoder):
    """
    A custom JSON encoder to handle MongoDB's ObjectId and other BSON types.
    """
    def default(self, o: Any) -> Any:
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

def to_json(data: Any) -> str:
    """
    Serializes Python data to a JSON string, handling MongoDB-specific types.
    """
    return json.dumps(data, cls=MongoJSONEncoder)

# --- Tool Implementations ---

@mcp.tool()
def mcp_list_databases() -> str:
    """
    Lists the names of all available databases on the MongoDB server.

    Returns:
        A JSON string representing a list of database names.
        Example: '["admin", "config", "local", "mydatabase"]'
    """
    try:
        database_names = client.list_database_names()
        return to_json(database_names)
    except pymongo.errors.ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

@mcp.tool()
def mcp_list_collections(database_name: str) -> str:
    """
    Lists the names of all collections within a specified database.

    Args:
        database_name (str): The name of the database to inspect.

    Returns:
        A JSON string representing a list of collection names.
        Example: '["users", "products", "orders"]'
    """
    if not database_name or not isinstance(database_name, str):
        raise ValueError("The 'database_name' parameter must be a non-empty string.")
    try:
        db = client[database_name]
        collection_names = db.list_collection_names()
        return to_json(collection_names)
    except pymongo.errors.ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while listing collections: {e}")

@mcp.tool()
def mcp_insert_document(database_name: str, collection_name: str, document: Dict[str, Any]) -> str:
    """
    Inserts a new document into a specified collection.

    Args:
        database_name (str): The name of the target database.
        collection_name (str): The name of the target collection.
        document (dict): The document to be inserted.

    Returns:
        A JSON string containing the string representation of the newly inserted document's _id.
        Example: '{"inserted_id": "64c9a3e6e7e4a4c4de54d7e1"}'
    """
    if not all(isinstance(arg, str) and arg for arg in [database_name, collection_name]):
        raise ValueError("Parameters 'database_name' and 'collection_name' must be non-empty strings.")
    if not isinstance(document, dict):
        raise ValueError("The 'document' parameter must be a dictionary.")
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.insert_one(document)
        return to_json({"inserted_id": str(result.inserted_id)})
    except pymongo.errors.ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during document insertion: {e}")

@mcp.tool()
def mcp_find_documents(database_name: str, collection_name: str, query: Dict[str, Any], projection: Dict[str, Any] = None, limit: int = 100) -> str:
    """
    Finds documents matching a specific query within a collection.

    Args:
        database_name (str): The name of the database to query.
        collection_name (str): The name of the collection to query.
        query (dict): The MongoDB query filter. Use {} to match all documents.
        projection (dict, optional): The projection specification. Defaults to None.
        limit (int, optional): The maximum number of documents to return. Defaults to 100.

    Returns:
        A JSON string representing a list of documents that match the query.
        Example: '[{"_id": "64c9a3e6e7e4a4c4de54d7e1", "name": "John Doe"}]'
    """
    if not all(isinstance(arg, str) and arg for arg in [database_name, collection_name]):
        raise ValueError("Parameters 'database_name' and 'collection_name' must be non-empty strings.")
    if not isinstance(query, dict):
        raise ValueError("The 'query' parameter must be a dictionary.")
    if projection is not None and not isinstance(projection, dict):
        raise ValueError("The 'projection' parameter must be a dictionary.")
    if not isinstance(limit, int) or limit < 0:
        raise ValueError("The 'limit' parameter must be a non-negative integer.")

    try:
        db = client[database_name]
        collection = db[collection_name]
        cursor = collection.find(query, projection).limit(limit)
        documents = list(cursor)
        return to_json(documents)
    except pymongo.errors.ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred while finding documents: {e}")

@mcp.tool()
def mcp_update_document(database_name: str, collection_name: str, query: Dict[str, Any], update: Dict[str, Any], update_many: bool = False) -> str:
    """
    Updates one or more documents that match a specified filter.

    Args:
        database_name (str): The name of the database for the update.
        collection_name (str): The name of the collection for the update.
        query (dict): The filter to select the document(s) to update.
        update (dict): The update operations to be applied (e.g., using '$set').
        update_many (bool, optional): If True, updates all matching documents. Defaults to False.

    Returns:
        A JSON string with the count of matched and modified documents.
        Example: '{"matched_count": 1, "modified_count": 1}'
    """
    if not all(isinstance(arg, str) and arg for arg in [database_name, collection_name]):
        raise ValueError("Parameters 'database_name' and 'collection_name' must be non-empty strings.")
    if not isinstance(query, dict) or not isinstance(update, dict):
        raise ValueError("Parameters 'query' and 'update' must be dictionaries.")

    try:
        db = client[database_name]
        collection = db[collection_name]
        if update_many:
            result = collection.update_many(query, update)
        else:
            result = collection.update_one(query, update)
        return to_json({"matched_count": result.matched_count, "modified_count": result.modified_count})
    except pymongo.errors.ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during document update: {e}")

@mcp.tool()
def mcp_delete_document(database_name: str, collection_name: str, query: Dict[str, Any], delete_many: bool = False) -> str:
    """
    Deletes one or more documents that match a specified filter.

    Args:
        database_name (str): The name of the database from which to delete.
        collection_name (str): The name of the collection from which to delete.
        query (dict): The filter to select the document(s) for deletion.
        delete_many (bool, optional): If True, deletes all matching documents. Defaults to False.

    Returns:
        A JSON string containing the number of documents deleted.
        Example: '{"deleted_count": 1}'
    """
    if not all(isinstance(arg, str) and arg for arg in [database_name, collection_name]):
        raise ValueError("Parameters 'database_name' and 'collection_name' must be non-empty strings.")
    if not isinstance(query, dict):
        raise ValueError("The 'query' parameter must be a dictionary.")

    try:
        db = client[database_name]
        collection = db[collection_name]
        if delete_many:
            result = collection.delete_many(query)
        else:
            result = collection.delete_one(query)
        return to_json({"deleted_count": result.deleted_count})
    except pymongo.errors.ConnectionFailure as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred during document deletion: {e}")

if __name__ == "__main__":
    # Ensure UTF-8 encoding for stdout
    if sys.stdout.encoding != 'utf-8' and sys.stdout.encoding is not None:
        sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()