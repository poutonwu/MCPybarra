from mcp.server.fastmcp import FastMCP
from hf_client import HFClient

# 假设mcp已经在main.py中初始化，这里需要的话可以单独测试
# mcp = FastMCP("hf_model")

class ModelTools:
    """模型相关工具类，提供模型搜索和信息获取功能"""
    
    def __init__(self, mcp: FastMCP, hf_client: HFClient):
        self.mcp = mcp
        self.hf_client = hf_client
        self.register_tools()
        
    def register_tools(self):
        """注册模型相关工具"""
        @self.mcp.tool()
        async def search_models(query: str = "", author: str = "", tags: list[str] = []) -> dict:
            """
            根据关键词、作者和标签搜索Hugging Face模型。
            
            Args:
                query: 搜索关键词 (可选)。
                author: 作者名称 (可选)。
                tags: 标签列表 (可选)。
                
            Returns:
                包含匹配模型列表的字典。
                
            示例:
                search_models(query="text generation", author="google", tags=["tensorflow", "t5"])
            """
            try:
                result = await self.hf_client.search_models(query, author, tags)
                # 转换结果格式以符合MCP规范
                return {
                    "models": [
                        {
                            "id": model["id"],
                            "name": model.get("modelId", ""),
                            "author": model.get("author", ""),
                            "tags": model.get("tags", []),
                            "downloads": model.get("downloads", 0),
                            "description": model.get("description", "")
                        } for model in result.get("models", [])
                    ]
                }
            except Exception as e:
                raise RuntimeError(f"Error searching models: {str(e)}")
    
        @self.mcp.tool()
        async def get_model_info(model_id: str) -> dict:
            """
            获取指定模型的详细信息。
            
            Args:
                model_id: Hugging Face模型ID (例如："bert-base-uncased")。
                
            Returns:
                包含模型详细信息的字典。
                
            示例:
                get_model_info(model_id="bert-base-uncased")
            """
            if not model_id:
                raise ValueError("model_id参数不能为空")
                
            try:
                result = await self.hf_client.get_model_info(model_id)
                # 转换结果格式以符合MCP规范
                return {
                    "model": {
                        "id": result.get("id", ""),
                        "name": result.get("modelId", ""),
                        "author": result.get("author", ""),
                        "tags": result.get("tags", []),
                        "downloads": result.get("downloads", 0),
                        "description": result.get("description", ""),
                        "library_name": result.get("libraryName", ""),
                        "pipeline_tag": result.get("pipelineTag", ""),
                        "license": result.get("license", ""),
                        "likes": result.get("likes", 0)
                    }
                }
            except Exception as e:
                raise RuntimeError(f"Error getting model info: {str(e)}")