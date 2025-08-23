from mcp.server.fastmcp import FastMCP
from hf_client import HFClient

class DatasetTools:
    """数据集相关工具类，提供数据集搜索和信息获取功能"""
    
    def __init__(self, mcp: FastMCP, hf_client: HFClient):
        self.mcp = mcp
        self.hf_client = hf_client
        self.register_tools()
        
    def register_tools(self):
        """注册数据集相关工具"""
        @self.mcp.tool()
        async def search_datasets(query: str = "", author: str = "", tags: list[str] = []) -> dict:
            """
            根据关键词、作者和标签搜索Hugging Face数据集。
            
            Args:
                query: 搜索关键词 (可选)。
                author: 作者名称 (可选)。
                tags: 标签列表 (可选)。
                
            Returns:
                包含匹配数据集列表的字典。
                
            示例:
                search_datasets(query="text classification", author="huggingface", tags=["csv", "text"])
            """
            try:
                result = await self.hf_client.search_datasets(query, author, tags)
                # 转换结果格式以符合MCP规范
                return {
                    "datasets": [
                        {
                            "id": dataset["id"],
                            "name": dataset.get("datasetId", ""),
                            "author": dataset.get("author", ""),
                            "tags": dataset.get("tags", []),
                            "downloads": dataset.get("downloads", 0),
                            "description": dataset.get("description", "")
                        } for dataset in result.get("datasets", [])
                    ]
                }
            except Exception as e:
                raise RuntimeError(f"Error searching datasets: {str(e)}")
    
        @self.mcp.tool()
        async def get_dataset_info(dataset_id: str) -> dict:
            """
            获取指定数据集的详细信息。
            
            Args:
                dataset_id: Hugging Face数据集ID (例如："imdb"或"huggingface/transformers")。
                
            Returns:
                包含数据集详细信息的字典。
                
            示例:
                get_dataset_info(dataset_id="imdb")
            """
            if not dataset_id:
                raise ValueError("dataset_id参数不能为空")
                
            try:
                result = await self.hf_client.get_dataset_info(dataset_id)
                # 转换结果格式以符合MCP规范
                return {
                    "dataset": {
                        "id": result.get("id", ""),
                        "name": result.get("datasetId", ""),
                        "author": result.get("author", ""),
                        "tags": result.get("tags", []),
                        "downloads": result.get("downloads", 0),
                        "description": result.get("description", ""),
                        "citation": result.get("citation", ""),
                        "license": result.get("license", ""),
                        "likes": result.get("likes", 0),
                        "viewer_url": result.get("viewerUrl", "")
                    }
                }
            except Exception as e:
                raise RuntimeError(f"Error getting dataset info: {str(e)}")