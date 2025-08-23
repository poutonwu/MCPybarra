import sys
import asyncio
from mcp.server.fastmcp import FastMCP
from hf_client import HFClient
from model_tools import ModelTools
from dataset_tools import DatasetTools
from space_tools import SpaceTools
from paper_tools import PaperTools
from collection_tools import CollectionTools

# 初始化FastMCP服务器
mcp = FastMCP("hf_resource")

# 创建HFClient实例
hf_client = HFClient()

# 注册所有工具
ModelTools(mcp, hf_client)
DatasetTools(mcp, hf_client)
SpaceTools(mcp, hf_client)
PaperTools(mcp, hf_client)
CollectionTools(mcp, hf_client)

async def main():
    """主函数，配置并运行服务器。"""
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        mcp.run()
    finally:
        # 确保优雅关闭资源
        print("Server is shutting down...")

if __name__ == "__main__":
    # 在Windows上, asyncio.run() 可能需要这个策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())