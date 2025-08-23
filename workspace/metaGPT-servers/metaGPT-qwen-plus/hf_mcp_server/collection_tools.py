from mcp.server.fastmcp import FastMCP
from hf_client import HFClient

class CollectionTools:
    """集合相关工具类，提供集合搜索和信息获取功能"""
    
    def __init__(self, mcp: FastMCP, hf_client: HFClient):
        self.mcp = mcp
        self.hf_client = hf_client
        self.register_tools()
        
    def register_tools(self):
        """注册集合相关工具"""
        @self.mcp.tool()
        async def search_collections(owner: str = "", entry: str = "", query: str = "") -> dict:
            """
            根据拥有者、条目和关键词搜索Hugging Face集合。
            
            Args:
                owner: 集合拥有者 (可选)。
                entry: 集合条目 (可选)。
                query: 搜索关键词 (可选)。
                
            Returns:
                包含匹配集合列表的字典。
                
            示例:
                search_collections(owner="huggingface", entry="bert-base-uncased", query="nlp models")
            """
            try:
                result = await self.hf_client.search_collections(owner, entry, query)
                # 转换结果格式以符合MCP规范
                return {
                    "collections": [
                        {
                            "id": collection["id"],
                            "name": collection.get("modelId", ""),
                            "author": collection.get("author", ""),
                            "description": collection.get("description", ""),
                            "entry_count": len(collection.get("entries", [])),
                            "tags": collection.get("tags", [])
                        } for collection in result.get("models", [])  # 使用"models"作为临时占位符
                    ]
                }
            except Exception as e:
                raise RuntimeError(f"Error searching collections: {str(e)}")
    
        @self.mcp.tool()
        async def get_collection_info(namespace: str, id: str) -> dict:
            """
            获取指定集合的详细信息。
            
            Args:
                namespace: 集合命名空间。
                id: 集合ID。
                
            Returns:
                包含集合详细信息的字典。
                
            示例:
                get_collection_info(namespace="huggingface", id="bert-collection")
            """
            if not namespace or not id:
                raise ValueError("namespace和id参数都不能为空")
                
            try:
                result = await self.hf_client.get_collection_info(namespace, id)
                # 转换结果格式以符合MCP规范
                entries = result.get("entries", [])
                
                return {
                    "collection": {
                        "id": result.get("id", ""),
                        "name": result.get("modelId", ""),
                        "namespace": namespace,
                        "author": result.get("author", ""),
                        "description": result.get("description", ""),
                        "tags": result.get("tags", []),
                        "downloads": result.get("downloads", 0),
                        "likes": result.get("likes", 0),
                        "entries": [
                            {
                                "id": entry.get("id", ""),
                                "type": entry.get("type", ""),
                                "title": entry.get("title", ""),
                                "description": entry.get("description", "")
                            } for entry in entries
                        ],
                        "entry_count": len(entries)
                    }
                }
            except Exception as e:
                raise RuntimeError(f"Error getting collection info: {str(e)}")