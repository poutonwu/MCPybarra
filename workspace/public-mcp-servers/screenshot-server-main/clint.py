import base64
from io import BytesIO
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from PIL import Image as PILImage

# 为 stdio 连接创建服务器参数
server_params = StdioServerParameters(
    command="uv", # Executable
    args=["run","screenshot.py"], # Optional command line arguments
    env=None # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            result = await session.call_tool("take_screenshot_image")
            # 报存码
            for content in result.content:
                image_data = content.data
                # 解码Base64图像数据
                image_data = base64.b64decode(image_data)
                try:
                    # 将解码后的数据转换为BytesIO对象
                    image_stream = BytesIO(image_data)
                    # 使用Pillow打开图像
                    image = PILImage.open(image_stream)
                    # 展示图像
                    image.show()
                except Exception as e:
                    print("Error:", e)
                    # 可选：保存数据到文件以便检查
                    with open("debug_image_data.png", "wb") as f:
                        f.write(image_data)
                    raise

if __name__ == "__main__":
    asyncio.run(run())