import sys
from mcp.server.fastmcp import FastMCP
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Optional, Union
import json

# Initialize FastMCP server
mcp = FastMCP("mcp_mongodb_manager")

# MongoDB connection setup
client = MongoClient("mongodb://localhost:27017/")

@mcp.tool()
def mcp_list_databases() -> List[str]:
    """
    Lists all available databases in the MongoDB instance.

    Returns:
        A list of strings, where each string represents a database name.
    """
    try:
        return client.list_database_names()
    except pymongo.errors.PyMongoError as e:
        return [f"Error listing databases: {str(e)}"]

@mcp.tool()
def mcp_list_collections(database_name: str) -> List[str]:
    """
    Lists all collections in a specified MongoDB database.

    Args:
        database_name: The name of the database to query.

    Returns:
        A list of strings, where each string represents a collection name in the specified database.
    """
    try:
        db = client[database_name]
        return db.list_collection_names()
    except pymongo.errors.PyMongoError as e:
        return [f"Error listing collections: {str(e)}"]

@mcp.tool()
def mcp_insert_document(database_name: str, collection_name: str, document: Dict) -> str:
    """
    Inserts a new document into a specified MongoDB collection.

    Args:
        database_name: The name of the database.
        collection_name: The name of the collection.
        document: The document to insert.

    Returns:
        A string indicating the success or failure of the insertion, including the inserted document's ID if successful.
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.insert_one(document)
        return f"Document inserted successfully with ID: {result.inserted_id}"
    except pymongo.errors.PyMongoError as e:
        return f"Error inserting document: {str(e)}"

@mcp.tool()
def mcp_find_documents(database_name: str, collection_name: str, query: Optional[Dict] = None, projection: Optional[Dict] = None, limit: int = 0) -> List[Dict]:
    """
    Queries documents in a specified MongoDB collection, with support for projection and result limiting.

    Args:
        database_name: The name of the database.
        collection_name: The name of the collection.
        query: The query criteria. Defaults to {} (all documents).
        projection: The fields to include/exclude in the results. Defaults to None (all fields).
        limit: The maximum number of documents to return. Defaults to 0 (no limit).

    Returns:
        A list of dictionaries, where each dictionary represents a matching document.
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        cursor = collection.find(query or {}, projection or {})
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
    except pymongo.errors.PyMongoError as e:
        return [{"error": f"Error finding documents: {str(e)}"}]

@mcp.tool()
def mcp_update_document(database_name: str, collection_name: str, query: Dict, update: Dict, multi: bool = False) -> str:
    """
    Updates documents in a specified MongoDB collection, supporting single or multiple updates.

    Args:
        database_name: The name of the database.
        collection_name: The name of the collection.
        query: The query criteria to select documents to update.
        update: The update operations to apply.
        multi: Whether to update multiple documents. Defaults to False.

    Returns:
        A string indicating the success or failure of the update, including the number of documents modified.
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.update_many(query, update) if multi else collection.update_one(query, update)
        return f"Successfully updated {result.modified_count} document(s)"
    except pymongo.errors.PyMongoError as e:
        return f"Error updating document: {str(e)}"

@mcp.tool()
def mcp_delete_document(database_name: str, collection_name: str, query: Dict, multi: bool = False) -> str:
    """
    Deletes documents from a specified MongoDB collection, supporting single or batch deletion.

    Args:
        database_name: The name of the database.
        collection_name: The name of the collection.
        query: The query criteria to select documents to delete.
        multi: Whether to delete multiple documents. Defaults to False.

    Returns:
        A string indicating the success or failure of the deletion, including the number of documents deleted.
    """
    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.delete_many(query) if multi else collection.delete_one(query)
        return f"Successfully deleted {result.deleted_count} document(s)"
    except pymongo.errors.PyMongoError as e:
        return f"Error deleting document: {str(e)}"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()