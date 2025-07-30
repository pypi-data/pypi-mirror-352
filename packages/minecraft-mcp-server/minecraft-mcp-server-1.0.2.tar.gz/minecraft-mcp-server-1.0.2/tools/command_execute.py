# tools/command_execute.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcrcon import MCRcon
from config import get_minecraft_config


# Minecraft工具实现函数 - 不再包含装饰器，由统一入口调用


async def _execute_server_command(arguments: dict) -> list[TextContent]:
    """执行服务器命令"""
    
    cmd = arguments.get("command")
    if not cmd:
        return [TextContent(type="text", text="❌ 错误：命令不能为空")]
    
    try:
        config = get_minecraft_config()
        
        with MCRcon(config["host"], config["password"], port=config["port"]) as mcr:
            result = mcr.command(cmd)
            
            # 处理空返回结果
            if not result or result.strip() == "":
                return [TextContent(type="text",
                                    text=f"✅ 命令执行成功：`{cmd}`\n💡 插件未返回内容，但命令应该已正常执行，也有可能插件未注册该命令")]
            else:
                return [TextContent(type="text", text=f"✅ 执行结果：\n{result}")]
                
    except ConnectionRefusedError:
        return [TextContent(type="text", text="❌ RCON 连接失败：请检查我的世界 server.properties 配置文件中的RCON配置是否正确 若正确则是服务器未启动")]
    except TimeoutError:
        return [TextContent(type="text", text="❌ RCON 连接超时：服务器响应超时，请检查网络连接")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 执行失败：{str(e)}")]


async def _broadcast_message(arguments: dict) -> list[TextContent]:
    """广播消息给所有玩家"""
    
    msg = arguments.get("message")
    if not msg:
        return [TextContent(type="text", text="❌ 错误：消息内容不能为空")]
    
    try:
        config = get_minecraft_config()
        
        with MCRcon(config["host"], config["password"], port=config["port"]) as mcr:
            result = mcr.command(f'say {msg}')
            
            # 广播消息通常没有返回内容
            if not result or result.strip() == "":
                return [TextContent(type="text", text=f"📢 公告已成功发送：{msg}")]
            else:
                return [TextContent(type="text", text=f"📢 公告已发送：{msg}\n📋 服务器响应：{result}")]
                
    except ConnectionRefusedError:
        return [TextContent(type="text", text="❌ RCON 连接失败：请检查我的世界 server.properties 配置文件中的RCON配置是否正确 若正确则是服务器未启动")]
    except TimeoutError:
        return [TextContent(type="text", text="❌ RCON 连接超时：服务器响应超时，请检查网络连接")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 执行失败：{str(e)}")]