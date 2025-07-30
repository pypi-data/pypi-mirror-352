# tools/__init__.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from .command_execute import _execute_server_command, _broadcast_message
from .plugin_search import _search_minecraft_plugins
from .file_download import _download_file
from .web_fetch import _fetch_web_content, Fetch

def register_all_tools(app: Server):
    """统一注册所有工具 - 只能有一个@app.list_tools()和@app.call_tool()入口"""
    
    @app.list_tools()
    async def list_all_tools() -> list[Tool]:
        """列出所有可用工具"""
        return [
            # Minecraft服务器管理工具
            Tool(
                name="send_command",
                description="在 Minecraft 服务器后台执行任意命令",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    },
                    "required": ["command"]
                }
            ),
            Tool(
                name="broadcast_message",
                description="向所有玩家发送一条公告",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"}
                    },
                    "required": ["message"]
                }
            ),
            # 插件搜索工具
            Tool(
                name="search_minecraft_plugins",
                description="搜索插件社区上的 Minecraft 插件",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "搜索关键词，例如：'经济'、'领地'、'权限'等"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回结果数量，默认为5，最大10",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["keyword"]
                }
            ),
            # 文件下载工具
            Tool(
                name="download_file",
                description="从指定URL下载文件到本地路径",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要下载的文件URL链接"
                        },
                        "download_path": {
                            "type": "string",
                            "description": "本地保存路径，包含文件名，例如：'D:/downloads/plugin.jar'"
                        }
                    },
                    "required": ["url", "download_path"]
                }
            ),
            # 网页内容获取工具
            Tool(
                name="fetch_web_content",
                description="从url抓取网站内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "format": "uri",
                            "description": "要抓取的URL"
                        },
                        "max_length": {
                            "type": "integer",
                            "default": 10000,
                            "minimum": 1,
                            "maximum": 999999,
                            "description": "返回的最大字符数"
                        },
                        "start_index": {
                            "type": "integer",
                            "default": 0,
                            "minimum": 0,
                            "description": "从此字符索引开始返回输出，如果之前的获取被截断且需要更多上下文时很有用"
                        },
                        "raw": {
                            "type": "boolean",
                            "default": False,
                            "description": "抓取页面的实际HTML内容，不进行markdown转化"
                        }
                    },
                    "required": ["url"]
                }
            )
        ]
    
    @app.call_tool()
    async def call_tool_unified(name: str, arguments: dict) -> list[TextContent]:
        """统一的工具调用入口"""
        
        # Minecraft服务器管理工具
        if name == "send_command":
            return await _execute_server_command(arguments)
        elif name == "broadcast_message":
            return await _broadcast_message(arguments)
        # 插件搜索工具
        elif name == "search_minecraft_plugins":
            return await _search_minecraft_plugins(arguments)
        # 文件下载工具
        elif name == "download_file":
            return await _download_file(arguments)
        # 网页内容获取工具
        elif name == "fetch_web_content":
            return await _fetch_web_content(arguments)
        else:
            return [TextContent(type="text", text=f"❌ 错误：未知的工具 '{name}'")]