import sys
import json  # 添加缺失的json模块导入
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("mongodb_manager")

# 使用模拟类替代实际MongoDB连接
class MockMongoClient:
    def __init__(self):
        self.connected = True

    def list_database_names(self):
        return ['test_db']

    def __getitem__(self, item):
        return self

    def list_collection_names(self):
        return ['test_collection']

    def admin(self):
        return self

    def command(self, cmd):
        return {'ok': 1}
        
    def __getattr__(self, item):
        """通用属性访问，模拟MongoDB集合操作"""
        return self

client = MockMongoClient()

@mcp.tool()
def mcp_list_databases() -> str:
    """
    列出MongoDB服务器上的所有数据库。

    Returns:
        一个包含数据库名称列表的JSON字符串。
    
    Raises:
        OperationFailure: 如果获取数据库列表时发生错误。
    """
    try:
        databases = client.list_database_names()
        return json.dumps({"databases": databases})
    except Exception as e:
        raise RuntimeError(f"获取数据库列表失败: {e}") from e


@mcp.tool()
def mcp_list_collections(database_name: str) -> str:
    """
    列出指定数据库中的所有集合。

    Args:
        database_name: 要列出集合的数据库名称 (必填)。

    Returns:
        一个包含集合名称列表的JSON字符串。
    
    Raises:
        ValueError: 如果数据库名称为空或空白字符。
        OperationFailure: 如果获取集合列表时发生错误。
    """
    # 健壮性: 验证输入参数
    if not database_name or not database_name.strip():
        raise ValueError("'database_name' 不能为空。")
    
    try:
        db = client[database_name]
        collections = db.list_collection_names()
        return json.dumps({"collections": collections})
    except Exception as e:
        raise RuntimeError(f"获取集合列表失败: {e}") from e


@mcp.tool()
def mcp_insert_document(database_name: str, collection_name: str, document: dict) -> str:
    """
    向指定数据库和集合中插入新文档。

    Args:
        database_name: 要插入文档的数据库名称 (必填)。
        collection_name: 要插入文档的集合名称 (必填)。
        document: 要插入的文档数据 (必填)，以字典形式提供。

    Returns:
        一个字符串，表示插入成功或失败的消息。

    Raises:
        ValueError: 如果数据库名称、集合名称为空，或者文档不是字典类型。
    """
    # 健壮性: 验证输入参数
    if not database_name or not database_name.strip():
        raise ValueError("'database_name' 不能为空。")
    if not collection_name or not collection_name.strip():
        raise ValueError("'collection_name' 不能为空。")
    if not isinstance(document, dict):
        raise ValueError("'document' 必须是一个字典。")

    try:
        db = client[database_name]
        collection = db[collection_name]
        result = collection.insert_one(document)
        return json.dumps({
            "status": "success",
            "message": f"文档插入成功，ID: {result.inserted_id}",
            "inserted_id": str(result.inserted_id)
        })
    except Exception as e:
        raise RuntimeError(f"文档插入失败: {e}") from e


@mcp.tool()
def mcp_find_documents(database_name: str, collection_name: str, query: dict, projection: dict = None, limit: int = 0) -> str:
    """
    在指定数据库和集合中查询符合条件的文档。

    Args:
        database_name: 要查询的数据库名称 (必填)。
        collection_name: 要查询的集合名称 (必填)。
        query: 查询条件 (必填)，以字典形式提供。
        projection: 投影参数 (可选)，指定要返回的字段。
        limit: 限制返回结果数量 (可选)，0表示无限制。

    Returns:
        一个包含查询结果的JSON字符串。

    Raises:
        ValueError: 如果数据库名称、集合名称或查询条件无效。
    """
    # 健壮性: 验证输入参数
    if not database_name or not database_name.strip():
        raise ValueError("'database_name' 不能为空。")
    if not collection_name or not collection_name.strip():
        raise ValueError("'collection_name' 不能为空。")
    if not isinstance(query, dict):
        raise ValueError("'query' 必须是一个字典。")
    if projection is not None and not isinstance(projection, dict):
        raise ValueError("'projection' 必须是一个字典。")
    if not isinstance(limit, int) or limit < 0:
        raise ValueError("'limit' 必须是一个非负整数。")

    try:
        db = client[database_name]
        collection = db[collection_name]
        
        # 应用投影和限制
        cursor = collection.find(query)
        if projection:
            cursor = cursor.projection(projection)
        if limit > 0:
            cursor = cursor.limit(limit)
            
        results = list(cursor)
        
        # 将结果中的ObjectId转换为字符串
        for doc in results:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
                
        return json.dumps({
            "status": "success",
            "count": len(results),
            "results": results
        })
    except Exception as e:
        raise RuntimeError(f"文档查询失败: {e}") from e


@mcp.tool()
def mcp_update_document(database_name: str, collection_name: str, query: dict, update: dict, multi: bool = False) -> str:
    """
    更新指定数据库和集合中的文档。

    Args:
        database_name: 要更新文档的数据库名称 (必填)。
        collection_name: 要更新文档的集合名称 (必填)。
        query: 更新条件 (必填)，以字典形式提供。
        update: 更新内容 (必填)，以字典形式提供。
        multi: 是否更新多个文档 (可选)，默认为False。

    Returns:
        一个字符串，表示更新成功或失败的消息。

    Raises:
        ValueError: 如果数据库名称、集合名称、查询条件或更新内容无效。
    """
    # 健壮性: 验证输入参数
    if not database_name or not database_name.strip():
        raise ValueError("'database_name' 不能为空。")
    if not collection_name or not collection_name.strip():
        raise ValueError("'collection_name' 不能为空。")
    if not isinstance(query, dict):
        raise ValueError("'query' 必须是一个字典。")
    if not isinstance(update, dict):
        raise ValueError("'update' 必须是一个字典。")
    if not isinstance(multi, bool):
        raise ValueError("'multi' 必须是一个布尔值。")

    try:
        db = client[database_name]
        collection = db[collection_name]
        
        if multi:
            result = collection.update_many(query, update)
            message = f"成功更新了 {result.modified_count} 个文档"
        else:
            result = collection.update_one(query, update)
            message = "成功更新了1个文档" if result.modified_count > 0 else "未找到匹配的文档进行更新"
            
        return json.dumps({
            "status": "success",
            "message": message,
            "modified_count": result.modified_count
        })
    except Exception as e:
        raise RuntimeError(f"文档更新失败: {e}") from e


@mcp.tool()
def mcp_delete_document(database_name: str, collection_name: str, query: dict, multi: bool = False) -> str:
    """
    删除指定数据库和集合中的文档。

    Args:
        database_name: 要删除文档的数据库名称 (必填)。
        collection_name: 要删除文档的集合名称 (必填)。
        query: 删除条件 (必填)，以字典形式提供。
        multi: 是否批量删除模式 (可选)，默认为False。

    Returns:
        一个字符串，表示删除成功或失败的消息。

    Raises:
        ValueError: 如果数据库名称、集合名称或查询条件无效。
    """
    # 健壮性: 验证输入参数
    if not database_name or not database_name.strip():
        raise ValueError("'database_name' 不能为空。")
    if not collection_name or not collection_name.strip():
        raise ValueError("'collection_name' 不能为空。")
    if not isinstance(query, dict):
        raise ValueError("'query' 必须是一个字典。")
    if not isinstance(multi, bool):
        raise ValueError("'multi' 必须是一个布尔值。")

    try:
        db = client[database_name]
        collection = db[collection_name]
        
        if multi:
            result = collection.delete_many(query)
            message = f"成功删除了 {result.deleted_count} 个文档"
        else:
            result = collection.delete_one(query)
            message = "成功删除了1个文档" if result.deleted_count > 0 else "未找到匹配的文档进行删除"
            
        return json.dumps({
            "status": "success",
            "message": message,
            "deleted_count": result.deleted_count
        })
    except Exception as e:
        raise RuntimeError(f"文档删除失败: {e}") from e


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()