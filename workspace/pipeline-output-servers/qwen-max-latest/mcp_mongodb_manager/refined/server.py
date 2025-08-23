import sys
import pymongo
from pymongo import MongoClient
from mcp.server.fastmcp import FastMCP
import json
import os

# Initialize FastMCP server
mcp = FastMCP("mcp_mongodb_manager")

# MongoDB connection setup
mongo_uri = os.environ.get('MONGO_URI', "mongodb://localhost:27017")
client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)  # Add timeout for robustness

def validate_database_name(database_name: str):
    if not database_name or not isinstance(database_name, str):
        raise ValueError(f"Invalid database name: '{database_name}'. Must be a non-empty string.")

def validate_collection_name(collection_name: str):
    if not collection_name or not isinstance(collection_name, str):
        raise ValueError(f"Invalid collection name: '{collection_name}'. Must be a non-empty string.")

def validate_document(document: dict):
    if not document or not isinstance(document, dict):
        raise ValueError("The document must be a non-empty dictionary.")

def validate_query(query: dict):
    if query is not None and not isinstance(query, dict):
        raise ValueError("Query must be a dictionary or None.")

def validate_projection(projection: dict):
    if projection is not None and not isinstance(projection, dict):
        raise ValueError("Projection must be a dictionary or None.")

def validate_limit(limit: int):
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise ValueError("Limit must be a positive integer or None.")

def validate_filter_query(filter_query: dict):
    if not filter_query or not isinstance(filter_query, dict):
        raise ValueError("Filter query must be a non-empty dictionary.")

def validate_update_data(update_data: dict):
    if not update_data or not isinstance(update_data, dict):
        raise ValueError("Update data must be a non-empty dictionary.")

def validate_multi(multi: bool):
    if not isinstance(multi, bool):
        raise ValueError("Multi must be a boolean value.")

@mcp.tool()
def mcp_list_databases() -> str:
    """
    Lists all available databases in the MongoDB instance.

    Returns:
        A JSON-formatted string containing a list of database names.

    Example:
        mcp_list_databases()
        => '["admin", "config", "local"]'
    """
    try:
        databases = client.list_database_names()
        return json.dumps(databases)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to list databases: {str(e)}")

@mcp.tool()
def mcp_list_collections(database_name: str) -> str:
    """
    Lists all collections within a specified database in the MongoDB instance.

    Args:
        database_name: The name of the database whose collections need to be listed.

    Returns:
        A JSON-formatted string containing a list of collection names.

    Raises:
        ValueError: If the database name is invalid.
        RuntimeError: If an error occurs while listing collections.

    Example:
        mcp_list_collections(database_name="test_db")
        => '["users", "products"]'
    """
    validate_database_name(database_name)

    try:
        collections = client[database_name].list_collection_names()
        return json.dumps(collections)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to list collections: {str(e)}")

@mcp.tool()
def mcp_insert_document(database_name: str, collection_name: str, document: dict) -> str:
    """
    Inserts a new document into a specified collection within a specified database.

    Args:
        database_name: The name of the target database.
        collection_name: The name of the target collection.
        document: The document to insert, represented as a Python dictionary.

    Returns:
        A JSON-formatted string containing the ID of the newly inserted document.

    Raises:
        ValueError: If any argument is invalid.
        RuntimeError: If an error occurs during document insertion.

    Example:
        mcp_insert_document(
            database_name="test_db",
            collection_name="users",
            document={"name": "Alice", "age": 30}
        )
        => '"65a4f8b9d3c5f2e4d8e9f0a1"'
    """
    validate_database_name(database_name)
    validate_collection_name(collection_name)
    validate_document(document)

    try:
        result = client[database_name][collection_name].insert_one(document)
        return json.dumps(str(result.inserted_id))
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to insert document: {str(e)}")

@mcp.tool()
def mcp_find_documents(
    database_name: str,
    collection_name: str,
    query: dict = None,
    projection: dict = None,
    limit: int = None
) -> str:
    """
    Queries documents from a specified collection within a specified database, with optional projection and result limit.

    Args:
        database_name: The name of the target database.
        collection_name: The name of the target collection.
        query: A query filter represented as a Python dictionary. Defaults to None.
        projection: Specifies fields to include or exclude in the returned documents. Defaults to None.
        limit: Limits the number of documents returned. Defaults to None.

    Returns:
        A JSON-formatted string containing a list of matching documents.

    Raises:
        ValueError: If any argument is invalid.
        RuntimeError: If an error occurs during querying.

    Example:
        mcp_find_documents(
            database_name="test_db",
            collection_name="users",
            query={"age": {"$gt": 25}},
            projection={"_id": 0, "name": 1},
            limit=2
        )
        => '[{"name": "Alice"}, {"name": "Bob"}]'
    """
    validate_database_name(database_name)
    validate_collection_name(collection_name)
    validate_query(query)
    validate_projection(projection)
    validate_limit(limit)

    try:
        cursor = client[database_name][collection_name].find(query, projection)
        if limit:
            cursor = cursor.limit(limit)
        documents = list(cursor)
        return json.dumps(documents, default=str)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to find documents: {str(e)}")

@mcp.tool()
def mcp_update_document(
    database_name: str,
    collection_name: str,
    filter_query: dict,
    update_data: dict,
    multi: bool
) -> str:
    """
    Updates one or multiple documents in a specified collection within a specified database.

    Args:
        database_name: The name of the target database.
        collection_name: The name of the target collection.
        filter_query: A filter to identify the documents to update.
        update_data: The update operations to apply, represented as a Python dictionary.
        multi: If True, updates all matching documents; otherwise, updates only the first match.

    Returns:
        A JSON-formatted string containing the number of documents modified.

    Raises:
        ValueError: If any argument is invalid.
        RuntimeError: If an error occurs during updating.

    Example:
        mcp_update_document(
            database_name="test_db",
            collection_name="users",
            filter_query={"age": {"$lt": 30}},
            update_data={"$set": {"status": "inactive"}},
            multi=True
        )
        => '3'
    """
    validate_database_name(database_name)
    validate_collection_name(collection_name)
    validate_filter_query(filter_query)
    validate_update_data(update_data)
    validate_multi(multi)

    try:
        if multi:
            result = client[database_name][collection_name].update_many(filter_query, update_data)
        else:
            result = client[database_name][collection_name].update_one(filter_query, update_data)
        return json.dumps(result.modified_count)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to update documents: {str(e)}")

@mcp.tool()
def mcp_delete_document(
    database_name: str,
    collection_name: str,
    filter_query: dict,
    multi: bool
) -> str:
    """
    Deletes one or multiple documents from a specified collection within a specified database.

    Args:
        database_name: The name of the target database.
        collection_name: The name of the target collection.
        filter_query: A filter to identify the documents to delete.
        multi: If True, deletes all matching documents; otherwise, deletes only the first match.

    Returns:
        A JSON-formatted string containing the number of documents deleted.

    Raises:
        ValueError: If any argument is invalid.
        RuntimeError: If an error occurs during deletion.

    Example:
        mcp_delete_document(
            database_name="test_db",
            collection_name="users",
            filter_query={"status": "inactive"},
            multi=True
        )
        => '2'
    """
    validate_database_name(database_name)
    validate_collection_name(collection_name)
    validate_filter_query(filter_query)
    validate_multi(multi)

    try:
        if multi:
            result = client[database_name][collection_name].delete_many(filter_query)
        else:
            result = client[database_name][collection_name].delete_one(filter_query)
        return json.dumps(result.deleted_count)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise RuntimeError(f"Failed to connect to MongoDB: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Failed to delete documents: {str(e)}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()