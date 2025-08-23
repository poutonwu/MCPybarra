import sys
import json
from pymongo import MongoClient
from mcp.server.fastmcp import FastMCP

class MongoDBManager:
    def __init__(self, uri):
        """
        Initialize the MongoDB connection using the provided URI.
        """
        self.client = MongoClient(uri)

    def list_databases(self):
        """
        List all available databases in the connected MongoDB instance.
        """
        try:
            return {"databases": self.client.list_database_names()}
        except Exception as e:
            return {"error": str(e)}

    def list_collections(self, database_name):
        """
        List all collections within a specified database.
        """
        try:
            if database_name not in self.client.list_database_names():
                return {"error": f"Database '{database_name}' does not exist."}
            db = self.client[database_name]
            return {"collections": db.list_collection_names()}
        except Exception as e:
            return {"error": str(e)}

    def insert_document(self, database_name, collection_name, document):
        """
        Insert a new document into a specified database and collection.
        """
        try:
            if database_name not in self.client.list_database_names():
                return {"error": f"Database '{database_name}' does not exist."}
            db = self.client[database_name]
            if collection_name not in db.list_collection_names():
                return {"error": f"Collection '{collection_name}' does not exist in database '{database_name}'."}
            collection = db[collection_name]
            result = collection.insert_one(document)
            return {"inserted_id": str(result.inserted_id)}
        except Exception as e:
            return {"error": str(e)}

    def find_documents(self, database_name, collection_name, query, projection=None, limit=None):
        """
        Find documents matching a query within a specified database and collection.
        """
        try:
            if database_name not in self.client.list_database_names():
                return {"error": f"Database '{database_name}' does not exist."}
            db = self.client[database_name]
            if collection_name not in db.list_collection_names():
                return {"error": f"Collection '{collection_name}' does not exist in database '{database_name}'."}
            collection = db[collection_name]
            cursor = collection.find(query, projection)
            if limit:
                cursor = cursor.limit(limit)
            results = list(cursor)
            for doc in results:
                doc['_id'] = str(doc['_id'])
            return {"documents": results}
        except Exception as e:
            return {"error": str(e)}

    def update_document(self, database_name, collection_name, filter_query, update_query, multi=False):
        """
        Update one or more documents within a specified database and collection.
        """
        try:
            if database_name not in self.client.list_database_names():
                return {"error": f"Database '{database_name}' does not exist."}
            db = self.client[database_name]
            if collection_name not in db.list_collection_names():
                return {"error": f"Collection '{collection_name}' does not exist in database '{database_name}'."}
            collection = db[collection_name]
            if multi:
                result = collection.update_many(filter_query, {'$set': update_query})
            else:
                result = collection.update_one(filter_query, {'$set': update_query})
            return {"updated_count": result.modified_count}
        except Exception as e:
            return {"error": str(e)}

    def delete_document(self, database_name, collection_name, filter_query, multi=False):
        """
        Delete one or more documents within a specified database and collection.
        """
        try:
            if database_name not in self.client.list_database_names():
                return {"error": f"Database '{database_name}' does not exist."}
            db = self.client[database_name]
            if collection_name not in db.list_collection_names():
                return {"error": f"Collection '{collection_name}' does not exist in database '{database_name}'."}
            collection = db[collection_name]
            if multi:
                result = collection.delete_many(filter_query)
            else:
                result = collection.delete_one(filter_query)
            return {"deleted_count": result.deleted_count}
        except Exception as e:
            return {"error": str(e)}

# Initialize FastMCP server
mcp = FastMCP("mcp_mongodb_manager")

# MongoDB Manager Instance
uri = "mongodb://localhost:27017"
mongo_manager = MongoDBManager(uri)

@mcp.tool()
def mcp_list_databases() -> str:
    """
    Lists all available databases in the connected MongoDB instance.

    Returns:
        A JSON string containing a list of database names.

    Example:
        mcp_list_databases()
        # Returns: {"databases": ["admin", "config", "local"]}
    """
    result = mongo_manager.list_databases()
    return json.dumps(result)

@mcp.tool()
def mcp_list_collections(database_name: str) -> str:
    """
    Lists all collections within a specified database.

    Args:
        database_name: Name of the database.

    Returns:
        A JSON string containing a list of collection names within the specified database.

    Example:
        mcp_list_collections(database_name="test_db")
        # Returns: {"collections": ["users", "products"]}
    """
    result = mongo_manager.list_collections(database_name)
    return json.dumps(result)

@mcp.tool()
def mcp_insert_document(database_name: str, collection_name: str, document: dict) -> str:
    """
    Inserts a new document into a specified database and collection.

    Args:
        database_name: Name of the database.
        collection_name: Name of the collection.
        document: Document data to insert.

    Returns:
        A JSON string containing the inserted document ID.

    Example:
        mcp_insert_document(database_name="test_db", collection_name="users", document={"name": "John Doe", "age": 30})
        # Returns: {"inserted_id": "60c72b2f54b9a1b4e3d5f8a1"}
    """
    result = mongo_manager.insert_document(database_name, collection_name, document)
    return json.dumps(result)

@mcp.tool()
def mcp_find_documents(database_name: str, collection_name: str, query: dict, projection: dict = None, limit: int = None) -> str:
    """
    Finds documents matching a query within a specified database and collection.

    Args:
        database_name: Name of the database.
        collection_name: Name of the collection.
        query: Query criteria.
        projection: Fields to include or exclude (optional).
        limit: Maximum number of results to return (optional).

    Returns:
        A JSON string containing a list of matching documents.

    Example:
        mcp_find_documents(database_name="test_db", collection_name="users", query={"age": {"$gt": 25}}, projection={"name": 1}, limit=10)
        # Returns: {"documents": [{"_id": "60c72b2f54b9a1b4e3d5f8a1", "name": "John Doe"}]}
    """
    result = mongo_manager.find_documents(database_name, collection_name, query, projection, limit)
    return json.dumps(result)

@mcp.tool()
def mcp_update_document(database_name: str, collection_name: str, filter_query: dict, update_query: dict, multi: bool = False) -> str:
    """
    Updates one or more documents within a specified database and collection.

    Args:
        database_name: Name of the database.
        collection_name: Name of the collection.
        filter_query: Criteria to select documents for update.
        update_query: Update operations.
        multi: If True, updates all matching documents; otherwise, only the first match.

    Returns:
        A JSON string containing the number of documents updated.

    Example:
        mcp_update_document(database_name="test_db", collection_name="users", filter_query={"name": "John Doe"}, update_query={"age": 31}, multi=True)
        # Returns: {"updated_count": 5}
    """
    result = mongo_manager.update_document(database_name, collection_name, filter_query, update_query, multi)
    return json.dumps(result)

@mcp.tool()
def mcp_delete_document(database_name: str, collection_name: str, filter_query: dict, multi: bool = False) -> str:
    """
    Deletes one or more documents within a specified database and collection.

    Args:
        database_name: Name of the database.
        collection_name: Name of the collection.
        filter_query: Criteria to select documents for deletion.
        multi: If True, deletes all matching documents; otherwise, only the first match.

    Returns:
        A JSON string containing the number of documents deleted.

    Example:
        mcp_delete_document(database_name="test_db", collection_name="users", filter_query={"name": "John Doe"}, multi=True)
        # Returns: {"deleted_count": 5}
    """
    result = mongo_manager.delete_document(database_name, collection_name, filter_query, multi)
    return json.dumps(result)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()