# main.py

import asyncio
from mcp.server.stdio import stdio_server
from mcp.server import Server
# 移除对不存在的resources模块的引用
from tools import register_all_tools

app = Server("我的世界mcp")

# 定义一个空的register_all_resources函数
def register_all_resources(server):
    """注册所有资源"""
    pass

# 注册资源和工具
register_all_resources(app)
register_all_tools(app)

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def run_main():
    """作为PyPI包的入口点"""
    asyncio.run(main())

if __name__ == "__main__":
    run_main()