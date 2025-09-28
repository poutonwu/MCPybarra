import sys
import os
import re
from typing import List, Dict, Optional, Any
from mcp.server.fastmcp import FastMCP
from huggingface_hub import HfApi, list_models, list_datasets, list_spaces, get_collection
import httpx
import json

# 设置代理支持
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 初始化FastMCP服务器
mcp = FastMCP("huggingface-resource-manager")

# 创建HuggingFace API客户端
hf_api = HfApi()

# 创建HTTP客户端
client = httpx.Client(timeout=30)

def validate_input(params: dict) -> None:
    """验证输入参数是否符合要求"""
    for key, value in params.items():
        if isinstance(value, str) and len(value.strip()) == 0:
            raise ValueError(f"{key} cannot be empty or whitespace only")

def handle_errors(func):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API request failed with status {e.response.status_code}: {e.response.text}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}") from e
    return wrapper

@mcp.tool()
def search_models(keyword: Optional[str] = None, author: Optional[str] = None, tag: Optional[str] = None) -> str:
    """
    搜索Hugging Face上的模型，支持关键词、作者、标签等条件过滤

    Args:
        keyword (str, optional): 搜索关键词
        author (str, optional): 模型作者
        tag (str, optional): 标签（如"pytorch"、"tensorflow"）

    Returns:
        str: JSON字符串，包含模型信息列表，每个条目结构为：
            {
              "id": "bert-base-uncased",
              "name": "BERT Base Uncased",
              "author": "google",
              "tags": ["pytorch", "transformers"],
              "downloads": 123456,
              "url": "https://huggingface.co/bert-base-uncased"
            }

    Raises:
        ValueError: 如果输入参数无效
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        validate_input({k:v for k, v in locals().items() if v is not None})

        # 调用底层实现
        result = _search_models_impl(keyword, author, tag)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in search_models: {str(e)}") from e

def _search_models_impl(keyword: Optional[str] = None, author: Optional[str] = None, tag: Optional[str] = None) -> List[Dict]:
    """搜索模型的底层实现"""
    models = list_models(search=keyword, author=author, filter=tag)
    result = []
    for model in models:
        model_info = {
            "id": model.id,
            "name": getattr(model, 'name', ''),
            "author": model.author or "unknown",
            "tags": list(model.tags),
            "downloads": model.downloads,
            "url": f"https://huggingface.co/{model.id}"
        }
        result.append(model_info)
    return result

@mcp.tool()
def get_model_info(model_id: str) -> str:
    """
    获取指定模型ID的详细信息

    Args:
        model_id (str): 模型ID（格式为[username]/[model-name]）

    Returns:
        str: JSON字符串，包含以下字段：
            {
              "id": "bert-base-uncased",
              "name": "BERT Base Uncased",
              "author": "google",
              "tags": ["pytorch", "transformers"],
              "downloads": 123456,
              "description": "A base-level BERT model...",
              "url": "https://huggingface.co/bert-base-uncased",
              "versions": ["v1.0.0", "v2.0.0"]
            }

    Raises:
        ValueError: 如果model_id为空或格式不正确
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        if not model_id or not isinstance(model_id, str) or '/' not in model_id:
            raise ValueError("model_id must be a non-empty string in the format [username]/[model-name]")

        # 调用底层实现
        result = _get_model_info_impl(model_id)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in get_model_info: {str(e)}") from e

def _get_model_info_impl(model_id: str) -> Dict:
    """获取模型详情的底层实现"""
    model_info = hf_api.model_info(repo_id=model_id)
    
    # 提取版本信息
    versions = []
    if hasattr(model_info, 'siblings') and model_info.siblings:
        for sibling in model_info.siblings:
            if sibling.rfilename.endswith('.bin') and '_' in sibling.rfilename:
                version = sibling.rfilename.split('_')[-1].split('.')[0]
                if version not in versions:
                    versions.append(version)
    
    return {
        "id": model_info.id,
        "name": getattr(model_info, 'name', ''),
        "author": model_info.author or "unknown",
        "tags": list(model_info.tags),
        "downloads": model_info.downloads,
        "description": model_info.description or "",
        "url": f"https://huggingface.co/{model_info.id}",
        "versions": versions
    }

@mcp.tool()
def search_datasets(keyword: Optional[str] = None, author: Optional[str] = None, tag: Optional[str] = None) -> str:
    """
    搜索Hugging Face上的数据集，支持关键词、作者、标签等条件过滤

    Args:
        keyword (str, optional): 搜索关键词
        author (str, optional): 数据集作者
        tag (str, optional): 标签（如"text"、"image"）

    Returns:
        str: JSON字符串，包含数据集信息列表，每个条目结构为：
            {
              "id": "imdb",
              "name": "IMDB Movie Reviews",
              "author": "stanford",
              "tags": ["text", "classification"],
              "downloads": 78901,
              "url": "https://huggingface.co/datasets/imdb"
            }

    Raises:
        ValueError: 如果输入参数无效
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        validate_input({k:v for k, v in locals().items() if v is not None})

        # 调用底层实现
        result = _search_datasets_impl(keyword, author, tag)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in search_datasets: {str(e)}") from e

def _search_datasets_impl(keyword: Optional[str] = None, author: Optional[str] = None, tag: Optional[str] = None) -> List[Dict]:
    """搜索数据集的底层实现"""
    datasets = list_datasets(search=keyword, author=author, filter=tag)
    result = []
    for dataset in datasets:
        dataset_info = {
            "id": dataset.id,
            "name": getattr(dataset, 'name', ''),
            "author": dataset.author or "unknown",
            "tags": list(dataset.tags),
            "downloads": dataset.downloads,
            "url": f"https://huggingface.co/datasets/{dataset.id}"
        }
        result.append(dataset_info)
    return result

@mcp.tool()
def get_dataset_info(dataset_id: str) -> str:
    """
    获取指定数据集ID的详细信息

    Args:
        dataset_id (str): 数据集ID（格式为[username]/[dataset-name]）

    Returns:
        str: JSON字符串，包含以下字段：
            {
              "id": "imdb",
              "name": "IMDB Movie Reviews",
              "author": "stanford",
              "tags": ["text", "classification"],
              "downloads": 78901,
              "description": "A large collection of movie reviews...",
              "url": "https://huggingface.co/datasets/imdb",
              "configurations": ["plain_text", "with_ratings"]
            }

    Raises:
        ValueError: 如果dataset_id为空或格式不正确
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        if not dataset_id or not isinstance(dataset_id, str) or '/' not in dataset_id:
            raise ValueError("dataset_id must be a non-empty string in the format [username]/[dataset-name]")

        # 调用底层实现
        result = _get_dataset_info_impl(dataset_id)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in get_dataset_info: {str(e)}") from e

def _get_dataset_info_impl(dataset_id: str) -> Dict:
    """获取数据集详情的底层实现"""
    dataset_info = hf_api.dataset_info(repo_id=dataset_id)
    
    # 提取配置信息
    configurations = []
    if hasattr(dataset_info, 'card_data') and hasattr(dataset_info.card_data, 'evaluates'):
        configurations = dataset_info.card_data.evaluates
    
    return {
        "id": dataset_info.id,
        "name": getattr(dataset_info, 'name', ''),
        "author": dataset_info.author or "unknown",
        "tags": list(dataset_info.tags),
        "downloads": dataset_info.downloads,
        "description": dataset_info.description or "",
        "url": f"https://huggingface.co/datasets/{dataset_info.id}",
        "configurations": configurations
    }

@mcp.tool()
def search_spaces(keyword: Optional[str] = None, author: Optional[str] = None, tag: Optional[str] = None, sdk: Optional[str] = None) -> str:
    """
    搜索Hugging Face上的Spaces，支持关键词、作者、标签、SDK等条件过滤

    Args:
        keyword (str, optional): 搜索关键词
        author (str, optional): Spaces作者
        tag (str, optional): 标签（如"gradio"、"streamlit"）
        sdk (str, optional): SDK类型（如"gradio"、"streamlit"）

    Returns:
        str: JSON字符串，包含Spaces信息列表，每个条目结构为：
            {
              "id": "spaces/gradio-chatbot",
              "name": "Chatbot Demo",
              "author": "hf",
              "tags": ["chat", "demo"],
              "sdk": "gradio",
              "url": "https://huggingface.co/spaces/gradio-chatbot"
            }

    Raises:
        ValueError: 如果输入参数无效
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        validate_input({k:v for k, v in locals().items() if v is not None})

        # 调用底层实现
        result = _search_spaces_impl(keyword, author, tag, sdk)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in search_spaces: {str(e)}") from e

def _search_spaces_impl(keyword: Optional[str] = None, author: Optional[str] = None, tag: Optional[str] = None, sdk: Optional[str] = None) -> List[Dict]:
    """搜索Spaces的底层实现"""
    spaces = list_spaces(search=keyword, author=author, filter=tag)
    result = []
    for space in spaces:
        # 只返回匹配SDK类型的Spaces
        if sdk and space.sdk != sdk:
            continue
            
        space_info = {
            "id": space.id,
            "name": getattr(space, 'name', ''),
            "author": space.author or "unknown",
            "tags": list(space.tags),
            "sdk": space.sdk or "unknown",
            "url": f"https://huggingface.co/{space.id}"
        }
        result.append(space_info)
    return result

@mcp.tool()
def get_space_info(space_id: str) -> str:
    """
    获取指定Space ID的详细信息

    Args:
        space_id (str): Space ID（格式为[username]/[space-name]）

    Returns:
        str: JSON字符串，包含以下字段：
            {
              "id": "spaces/gradio-chatbot",
              "name": "Chatbot Demo",
              "author": "hf",
              "tags": ["chat", "demo"],
              "sdk": "gradio",
              "description": "An interactive chatbot demo...",
              "url": "https://huggingface.co/spaces/gradio-chatbot",
              "status": "active"
            }

    Raises:
        ValueError: 如果space_id为空或格式不正确
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        if not space_id or not isinstance(space_id, str) or '/' not in space_id:
            raise ValueError("space_id must be a non-empty string in the format [username]/[space-name]")

        # 调用底层实现
        result = _get_space_info_impl(space_id)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in get_space_info: {str(e)}") from e

def _get_space_info_impl(space_id: str) -> Dict:
    """获取Space详情的底层实现"""
    space_info = hf_api.space_info(repo_id=space_id)
    
    return {
        "id": space_info.id,
        "name": getattr(space_info, 'name', ''),
        "author": space_info.author or "unknown",
        "tags": list(space_info.tags),
        "sdk": space_info.sdk or "unknown",
        "description": space_info.description or "",
        "url": f"https://huggingface.co/{space_info.id}",
        "status": space_info.hosted_inference.get('status', 'unknown') if hasattr(space_info, 'hosted_inference') else 'unknown'
    }

@mcp.tool()
def get_paper_info(paper_id: str) -> str:
    """
    获取指定arXiv论文的详细信息

    Args:
        paper_id (str): arXiv论文ID（如"2106.16155v1"）

    Returns:
        str: JSON字符串，包含以下字段：
            {
              "id": "2106.16155v1",
              "title": "Language Models are Few-Shot Learners",
              "authors": ["Benjamin Burch", "David Smith"],
              "abstract": "This paper demonstrates that language models...",
              "published": "2021-06-16",
              "updated": "2021-06-16",
              "related_models": ["gpt-3", "gpt-4"],
              "url": "https://arxiv.org/abs/2106.16155"
            }

    Raises:
        ValueError: 如果paper_id为空或格式不正确
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        if not paper_id or not isinstance(paper_id, str) or not re.match(r'^\d{4}\.\d{5}(v\d+)?$', paper_id):
            raise ValueError("paper_id must be a non-empty string in the format like '2106.16155v1'")

        # 调用底层实现
        result = _get_paper_info_impl(paper_id)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in get_paper_info: {str(e)}") from e

def _get_paper_info_impl(paper_id: str) -> Dict:
    """获取论文详情的底层实现"""
    # 实现论文信息获取逻辑
    url = f"https://api.arxiv.org/papers/{paper_id}.json"
    response = client.get(url)
    response.raise_for_status()
    data = response.json()
    
    # 解析响应数据
    paper_data = data.get('paper', {})
    
    return {
        "id": paper_id,
        "title": paper_data.get('title', ''),
        "authors": paper_data.get('authors', []),
        "abstract": paper_data.get('abstract', ''),
        "published": paper_data.get('published_date', ''),
        "updated": paper_data.get('updated_date', ''),
        "related_models": [],  # 这个字段需要从其他来源获取
        "url": f"https://arxiv.org/abs/{paper_id}"
    }

@mcp.tool()
def get_daily_papers() -> str:
    """
    获取Hugging Face每日精选论文列表

    Returns:
        str: JSON字符串，包含每日论文信息列表，每个条目结构为：
            {
              "id": "2106.16155v1",
              "title": "Language Models are Few-Shot Learners",
              "authors": ["Benjamin Burch", "David Smith"],
              "abstract": "This paper demonstrates that language models...",
              "url": "https://arxiv.org/abs/2106.16155"
            }

    Raises:
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 调用底层实现
        result = _get_daily_papers_impl()
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in get_daily_papers: {str(e)}") from e

def _get_daily_papers_impl() -> List[Dict]:
    """获取每日论文列表的底层实现"""
    # Hugging Face没有直接提供每日论文的API，这里使用模拟数据
    # 在实际应用中，可以访问Hugging Face Hub的每日论文页面并解析内容
    url = "https://huggingface.co/papers?sort=published&direction=-1"
    response = client.get(url)
    response.raise_for_status()
    
    # 这里应该解析HTML页面来获取论文信息
    # 由于简化实现，我们返回一个空列表
    return []

@mcp.tool()
def search_collections(owner: Optional[str] = None, keyword: Optional[str] = None) -> str:
    """
    搜索Hugging Face上的集合，支持拥有者、关键词等条件过滤

    Args:
        owner (str, optional): 集合拥有者
        keyword (str, optional): 搜索关键词

    Returns:
        str: JSON字符串，包含集合信息列表，每个条目结构为：
            {
              "id": "collection-nlp-benchmarks",
              "title": "NLP Benchmarks Collection",
              "owner": "hf",
              "entry_count": 15,
              "url": "https://huggingface.co/collections/nlp-benchmarks"
            }

    Raises:
        ValueError: 如果输入参数无效
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        validate_input({k:v for k, v in locals().items() if v is not None})

        # 调用底层实现
        result = _search_collections_impl(owner, keyword)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in search_collections: {str(e)}") from e

def _search_collections_impl(owner: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict]:
    """搜索集合的底层实现"""
    collections = hf_api.list_collections(owner=owner)
    result = []
    for collection in collections:
        # 如果有关键词，只返回匹配的集合
        if keyword and (keyword.lower() not in collection.title.lower() and keyword.lower() not in collection.description.lower()):
            continue
            
        collection_info = {
            "id": collection.slug,
            "title": collection.title,
            "owner": collection.namespace,
            "entry_count": len(collection.items) if hasattr(collection, 'items') else 0,
            "url": f"https://huggingface.co/collections/{collection.namespace}/{collection.slug}-{collection.id}"
        }
        result.append(collection_info)
    return result

@mcp.tool()
def get_collection_info(namespace: str, collection_id: str) -> str:
    """
    获取指定集合命名空间和ID的详细信息

    Args:
        namespace (str): 集合命名空间（如"user"或"organization"）
        collection_id (str): 集合ID

    Returns:
        str: JSON字符串，包含以下字段：
            {
              "id": "collection-nlp-benchmarks",
              "title": "NLP Benchmarks Collection",
              "owner": "hf",
              "description": "A collection of NLP benchmark datasets and models...",
              "entries": [
                {
                  "type": "model",
                  "id": "bert-base-uncased"
                },
                {
                  "type": "dataset",
                  "id": "imdb"
                }
              ],
              "url": "https://huggingface.co/collections/nlp-benchmarks"
            }

    Raises:
        ValueError: 如果namespace或collection_id为空
        RuntimeError: 如果API请求失败或发生意外错误
    """
    try:
        # 验证输入参数
        if not namespace or not isinstance(namespace, str) or not namespace.strip():
            raise ValueError("namespace must be a non-empty string")
        if not collection_id or not isinstance(collection_id, str) or not collection_id.strip():
            raise ValueError("collection_id must be a non-empty string")

        # 调用底层实现
        result = _get_collection_info_impl(namespace, collection_id)
        
        # 序列化结果
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Error in get_collection_info: {str(e)}") from e

def _get_collection_info_impl(namespace: str, collection_id: str) -> Dict:
    """获取集合详情的底层实现"""
    collection = get_collection(namespace=namespace, id=collection_id)
    
    entries = []
    if hasattr(collection, 'items') and collection.items:
        for item in collection.items:
            if hasattr(item, 'item') and item.item:
                entries.append({
                    "type": item.item.type,
                    "id": item.item.id
                })
    
    return {
        "id": collection.slug,
        "title": collection.title,
        "owner": collection.namespace,
        "description": collection.description or "",
        "entries": entries,
        "url": f"https://huggingface.co/collections/{collection.namespace}/{collection.slug}-{collection.id}"
    }

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()