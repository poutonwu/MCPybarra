from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["image_converter_server.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("convert_image",{'image_path':"test.png",'target_format':"jpg"})
            # result = await session.convert_image(image_path="test.png",target_format="jpg")
            # result = await session.tools["convert_image"].call(
            #             image_path="test.png",
            #             target_format="jpg"
            #         )
            print(result.content)

if __name__ == "__main__":
    asyncio.run(main())