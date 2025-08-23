import httpx
from typing import List, Dict, Any, Optional

class HFClient:
    """Hugging Face API客户端，提供对Hugging Face Hub资源的访问"""
    
    def __init__(self, base_url: str = "https://huggingface.co", api_base_url: str = "https://api.huggingface.co"):
        """
        初始化HFClient
        
        Args:
            base_url: Hugging Face基础URL
            api_base_url: Hugging Face API基础URL
        """
        self.base_url = base_url
        self.api_base_url = api_base_url
        self.headers = {
            "User-Agent": "hf-mcp-server/1.0 (contact@example.com)"
        }
        
    async def search_models(self, query: str = "", author: str = "", tags: List[str] = []) -> Dict[str, Any]:
        """
        根据条件搜索Hugging Face模型
        
        Args:
            query: 搜索关键词
            author: 作者名称
            tags: 标签列表
            
        Returns:
            包含搜索结果的字典
        """
        search_url = f"{self.api_base_url}/v1/models"
        
        params = {}
        if query:
            params["search"] = query
        if author:
            params["author"] = author
        if tags:
            params["tags"] = ",".join(tags)
            
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        获取模型详细信息
        
        Args:
            model_id: 模型ID
            
        Returns:
            包含模型详细信息的字典
        """
        info_url = f"{self.api_base_url}/v1/models/{model_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(info_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def search_datasets(self, query: str = "", author: str = "", tags: List[str] = []) -> Dict[str, Any]:
        """
        根据条件搜索Hugging Face数据集
        
        Args:
            query: 搜索关键词
            author: 作者名称
            tags: 标签列表
            
        Returns:
            包含搜索结果的字典
        """
        search_url = f"{self.api_base_url}/v1/datasets"
        
        params = {}
        if query:
            params["search"] = query
        if author:
            params["author"] = author
        if tags:
            params["tags"] = ",".join(tags)
            
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """
        获取数据集详细信息
        
        Args:
            dataset_id: 数据集ID
            
        Returns:
            包含数据集详细信息的字典
        """
        info_url = f"{self.api_base_url}/v1/datasets/{dataset_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(info_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def search_spaces(self, query: str = "", author: str = "", tags: List[str] = [], sdk: str = "") -> Dict[str, Any]:
        """
        根据条件搜索Hugging Face Spaces
        
        Args:
            query: 搜索关键词
            author: 作者名称
            tags: 标签列表
            sdk: SDK类型
            
        Returns:
            包含搜索结果的字典
        """
        search_url = f"{self.api_base_url}/v1/spaces"
        
        params = {}
        if query:
            params["search"] = query
        if author:
            params["author"] = author
        if tags:
            params["tags"] = ",".join(tags)
        if sdk:
            params["sdk"] = sdk
            
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_space_info(self, space_id: str) -> Dict[str, Any]:
        """
        获取Space详细信息
        
        Args:
            space_id: Space ID
            
        Returns:
            包含Space详细信息的字典
        """
        info_url = f"{self.api_base_url}/v1/spaces/{space_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(info_url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
    async def get_paper_info(self, arxiv_id: str) -> Dict[str, Any]:
        """
        获取arXiv论文详细信息
        
        Args:
            arxiv_id: arXiv论文ID
            
        Returns:
            包含论文详细信息的字典
        """
        # Hugging Face并没有直接提供通过arXiv ID查询的API
        # 这里我们使用标准的arXiv API进行查询
        search_url = f"https://export.arxiv.org/api/query"
        
        params = {
            "id_list": arxiv_id,
            "max_results": 1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 将返回结果转换为更标准的JSON格式
            # 实际开发中应该使用专门的XML解析器来处理arXiv的响应
            return {
                "raw_response": response.text,
                "note": "The server returns raw XML data. In a real implementation, you should parse this XML data into structured JSON format."
            }
            
    async def get_daily_papers(self) -> Dict[str, Any]:
        """
        获取Hugging Face每日精选论文
        
        Returns:
            包含每日论文列表的字典
        """
        # Hugging Face目前没有官方的"每日精选论文"API
        # 我们可以搜索"huggingface.co/paper"相关的资源或使用社区提供的API
        search_url = f"{self.api_base_url}/v1/models"
        
        params = {
            "tags": "paper"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 注意：这只是一个示例实现，实际的每日论文API可能需要不同的端点和处理逻辑
            return {
                "papers": response.json().get("models", []),
                "note": "This is an example implementation using the model search API with 'paper' tag. The actual daily papers API might be different."
            }
            
    async def search_collections(self, owner: str = "", entry: str = "", query: str = "") -> Dict[str, Any]:
        """
        搜索Hugging Face集合
        
        Args:
            owner: 集合拥有者
            entry: 集合条目
            query: 搜索关键词
            
        Returns:
            包含搜索结果的字典
        """
        # Hugging Face目前没有明确公开的集合搜索API
        # 我们假设可以通过模型搜索API添加额外参数来实现
        search_url = f"{self.api_base_url}/v1/models"
        
        params = {}
        if query:
            params["search"] = query
        if owner:
            params["author"] = owner
        # 对于entry，我们将其作为额外的标签添加
        if entry:
            params["tags"] = entry
            
        async with httpx.AsyncClient() as client:
            response = await client.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # 在实际应用中，可能需要进一步处理结果以符合集合的特定需求
            return response.json()
            
    async def get_collection_info(self, namespace: str, id: str) -> Dict[str, Any]:
        """
        获取集合详细信息
        
        Args:
            namespace: 集合命名空间
            id: 集合ID
            
        Returns:
            包含集合详细信息的字典
        """
        # 假设集合详情可以通过模型详情API获取
        info_url = f"{self.api_base_url}/v1/models/{namespace}/{id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(info_url, headers=self.headers)
            response.raise_for_status()
            return response.json()