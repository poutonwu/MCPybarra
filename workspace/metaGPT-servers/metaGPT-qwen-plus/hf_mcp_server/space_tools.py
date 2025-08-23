from mcp.server.fastmcp import FastMCP
from hf_client import HFClient

class SpaceTools:
    """Spaces相关工具类，提供Spaces搜索和信息获取功能"""
    
    def __init__(self, mcp: FastMCP, hf_client: HFClient):
        self.mcp = mcp
        self.hf_client = hf_client
        self.register_tools()
        
    def register_tools(self):
        """注册Spaces相关工具"""
        @self.mcp.tool()
        async def search_spaces(query: str = "", author: str = "", tags: list[str] = [], sdk: str = "") -> dict:
            """
            根据关键词、作者、标签和SDK类型搜索Hugging Face Spaces。
            
            Args:
                query: 搜索关键词 (可选)。
                author: 作者名称 (可选)。
                tags: 标签列表 (可选)。
                sdk: SDK类型 (可选)。
                
            Returns:
                包含匹配Spaces列表的字典。
                
            示例:
                search_spaces(query="chatbot", author="huggingface", tags=["demo", "NLP"], sdk="gradio")
            """
            try:
                result = await self.hf_client.search_spaces(query, author, tags, sdk)
                # 转换结果格式以符合MCP规范
                return {
                    "spaces": [
                        {
                            "id": space["id"],
                            "name": space.get("id", "").split("/")[-1] if space.get("id") else "",
                            "author": space.get("author", ""),
                            "tags": space.get("tags", []),
                            "sdk": space.get("sdk", ""),
                            "description": space.get("description", ""),
                            "likes": space.get("likes", 0),
                            "downloads": space.get("downloads", 0)
                        } for space in result.get("spaces", [])
                    ]
                }
            except Exception as e:
                raise RuntimeError(f"Error searching spaces: {str(e)}")
    
        @self.mcp.tool()
        async def get_space_info(space_id: str) -> dict:
            """
            获取指定Space的详细信息。
            
            Args:
                space_id: Hugging Face Space ID (例如："bert-base-uncased"或"huggingface/transformers")。
                
            Returns:
                包含Space详细信息的字典。
                
            示例:
                get_space_info(space_id="huggingface/bert-english-françois")
            """
            if not space_id:
                raise ValueError("space_id参数不能为空")
                
            try:
                result = await self.hf_client.get_space_info(space_id)
                # 转换结果格式以符合MCP规范
                return {
                    "space": {
                        "id": result.get("id", ""),
                        "name": result.get("id", "").split("/")[-1] if result.get("id") else "",
                        "author": result.get("author", ""),
                        "tags": result.get("tags", []),
                        "sdk": result.get("sdk", ""),
                        "description": result.get("description", ""),
                        "citation": result.get("citation", ""),
                        "license": result.get("license", ""),
                        "likes": result.get("likes", 0),
                        "downloads": result.get("downloads", 0),
                        "url": result.get("url", "")
                    }
                }
            except Exception as e:
                raise RuntimeError(f"Error getting space info: {str(e)}")