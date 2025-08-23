import sys
import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from PIL import Image, ImageDraw
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("mcp_image_search_download_icon")

# 设置代理（如果需要）
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 创建必要的目录
downloads_dir = Path("downloads")
icons_dir = Path("icons")
downloads_dir.mkdir(exist_ok=True)
icons_dir.mkdir(exist_ok=True)

# 获取 Pexels API 密钥的函数
def get_pexels_api_key() -> Optional[str]:
    """获取 Pexels API 密钥."""
    # 从环境变量获取 API 密钥
    api_key = os.environ.get('PEXELS_API_KEY', "xxx")
    if not api_key:
        print("警告：PEXELS_API_KEY 环境变量未设置，某些功能可能受限")
    return api_key

@mcp.tool()
def search_images(query: str, per_page: int = 5) -> str:
    """
    根据用户输入的关键词，在 Pexels 图像源中自动检索相关图片，并返回包含图片链接、作者等信息的结构化结果。

    Args:
        query: 搜索关键词（例如 "nature landscape"），必填。
        per_page: 每页返回的图片数量，默认为 5，最大值为 10。

    Returns:
        包含以下字段的 JSON 列表：
        - url: 高清图片链接
        - photographer: 摄影师名称
        - source: 图片来源（Pexels 页面链接）

    Raises:
        ValueError: 如果查询参数为空或无效
        requests.exceptions.RequestException: 如果网络请求失败
        json.JSONDecodeError: 如果响应内容无法解析为 JSON

    示例:
        >>> search_images(query="nature landscape", per_page=5)
        [
            {
                "url": "https://images.pexels.com/photos/12345/nature-landscape.jpg",
                "photographer": "John Doe",
                "source": "https://www.pexels.com/photo/12345/"
            },
            ...
        ]
    """
    try:
        # 参数验证
        if not query or not isinstance(query, str):
            raise ValueError("'query' 参数不能为空且必须是字符串类型")
        
        # 限制每页数量不超过 10
        per_page = min(max(per_page, 1), 10)
        
        # 设置请求头
        headers = {}
        api_key = get_pexels_api_key()
        if api_key:
            headers["Authorization"] = api_key
        
        # 构建请求 URL
        base_url = "https://api.pexels.com/v1/search"
        params = {
            "query": query,
            "per_page": per_page
        }
        
        # 发送请求
        response = requests.get(base_url, headers=headers, params=params, timeout=(3.05, 27))
        response.raise_for_status()
        
        # 解析响应
        data = response.json()
        results = []
        
        for photo in data.get("photos", []):
            results.append({
                "url": photo["src"]["large2x"],
                "photographer": photo["photographer"],
                "source": photo["url"]
            })
        
        return json.dumps(results, ensure_ascii=False)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"API 请求失败: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except json.JSONDecodeError as e:
        error_msg = f"响应内容无法解析为 JSON: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        print(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)

@mcp.tool()
def download_image(image_url: str, filename: str, save_dir: str = "downloads") -> str:
    """
    根据用户提供的图片 URL 和文件名，将图片下载并保存到指定目录，返回保存状态和路径信息。

    Args:
        image_url: 要下载的图片 URL，必填。
        filename: 保存的文件名，必填。
        save_dir: 保存图片的目录路径，默认为当前工作目录下的 'downloads/' 文件夹。

    Returns:
        包含以下字段的 JSON 对象：
        - status: 下载是否成功
        - file_path: 图片保存的完整路径（如果失败则为 null）

    Raises:
        ValueError: 如果 URL 或文件名参数无效
        requests.exceptions.RequestException: 如果网络请求失败
        IOError: 如果文件写入失败

    示例:
        >>> download_image(image_url="https://example.com/image.jpg", filename="landscape.jpg")
        {
            "status": true,
            "file_path": "/path/to/downloads/landscape.jpg"
        }
    """
    try:
        # 参数验证
        if not image_url or not isinstance(image_url, str):
            raise ValueError("'image_url' 参数不能为空且必须是字符串类型")
        if not filename or not isinstance(filename, str):
            raise ValueError("'filename' 参数不能为空且必须是字符串类型")
        
        # 创建保存目录
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # 完整文件路径
        file_path = save_path / filename
        
        # 下载图片
        response = requests.get(image_url, stream=True, timeout=(3.05, 27))
        response.raise_for_status()
        
        # 保存图片
        with open(file_path, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)
        
        return json.dumps({
            "status": True,
            "file_path": str(file_path.absolute())
        }, ensure_ascii=False)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"图片下载失败: {str(e)}"
        print(error_msg)
        return json.dumps({
            "status": False,
            "file_path": None,
            "error": error_msg
        }, ensure_ascii=False)
    except IOError as e:
        error_msg = f"文件写入失败: {str(e)}"
        print(error_msg)
        return json.dumps({
            "status": False,
            "file_path": None,
            "error": error_msg
        }, ensure_ascii=False)
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        print(error_msg)
        return json.dumps({
            "status": False,
            "file_path": None,
            "error": error_msg
        }, ensure_ascii=False)

@mcp.tool()
def generate_icon(description: str, size: Tuple[int, int] = (64, 64), use_cloud: bool = False) -> str:
    """
    根据用户输入的图标描述词，自动生成指定尺寸的图标图片，并保存到指定目录；如未配置云端生成服务，则用本地样例图标模拟生成。

    Args:
        description: 图标描述词（例如 "settings icon blue color"），必填。
        size: 图标的宽度和高度，默认为 (64, 64)。
        use_cloud: 是否使用云端图标生成服务，默认为 False。

    Returns:
        包含以下字段的 JSON 对象：
        - status: 生成是否成功
        - file_path: 图标保存的完整路径（如果失败则为 null）

    Raises:
        ValueError: 如果描述词参数无效
        IOError: 如果文件写入失败
        Exception: 其他未知错误

    示例:
        >>> generate_icon(description="settings icon blue color", size=(64, 64))
        {
            "status": true,
            "file_path": "/path/to/icons/settings_icon_blue_color.png"
        }
    """
    try:
        # 参数验证
        if not description or not isinstance(description, str):
            raise ValueError("'description' 参数不能为空且必须是字符串类型")
        
        # 确保尺寸是元组类型且包含两个正整数
        if not isinstance(size, tuple) or len(size) != 2:
            size = (64, 64)
        width, height = size
        width = max(1, int(width))
        height = max(1, int(height))
        size = (width, height)
        
        # 构建文件路径
        icons_dir = Path("icons")
        icons_dir.mkdir(exist_ok=True)
        
        # 清理描述词以创建合法文件名
        safe_description = "_".join(filter(str.isalnum, description.split()))
        filename = f"{safe_description}_{width}x{height}.png"
        file_path = icons_dir / filename
        
        # 如果启用云端服务（目前未实现）
        if use_cloud:
            # 这里可以添加实际的云端生成逻辑
            # 由于没有现成的云端服务，我们暂时使用本地示例图标
            print("警告：云端图标生成服务尚未实现，使用本地示例图标代替")
            
        # 使用本地示例图标
        # 这里我们创建一个简单的蓝色圆角矩形作为示例图标
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 解析描述词中的颜色
        color = (0, 122, 255)  # 默认蓝色
        if "red" in description.lower():
            color = (255, 0, 0)
        elif "green" in description.lower():
            color = (0, 255, 0)
        elif "yellow" in description.lower():
            color = (255, 255, 0)
        elif "black" in description.lower():
            color = (0, 0, 0)
        elif "white" in description.lower():
            color = (255, 255, 255)
        
        # 绘制圆角矩形
        radius = min(size) // 10
        draw.rounded_rectangle([0, 0, width, height], radius=radius, fill=color)
        
        # 添加简单的图标细节
        draw.line([(width//4, height//2), (width*3//4, height//2)], fill=(255, 255, 255), width=3)
        draw.line([(width//2, height//4), (width//2, height*3//4)], fill=(255, 255, 255), width=3)
        
        # 保存图标
        img.save(file_path, format='PNG')
        
        return json.dumps({
            "status": True,
            "file_path": str(file_path.absolute())
        }, ensure_ascii=False)
    
    except IOError as e:
        error_msg = f"文件写入失败: {str(e)}"
        print(error_msg)
        return json.dumps({
            "status": False,
            "file_path": None,
            "error": error_msg
        }, ensure_ascii=False)
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"
        print(error_msg)
        return json.dumps({
            "status": False,
            "file_path": None,
            "error": error_msg
        }, ensure_ascii=False)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mcp.run()