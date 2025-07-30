# tools/file_download.py

import requests
import os
from mcp.types import TextContent
from pathlib import Path


# 文件下载工具实现函数 - 不再包含装饰器，由统一入口调用


def download(url, local_filepath): 
    """下载文件的核心函数"""
    headers = { 
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " 
                      "Chrome/111.0.0.0 Safari/537.36" 
    } 
    try: 
        with requests.get(url, stream=True, headers=headers, allow_redirects=True) as r: 
            r.raise_for_status() 
            chunk_size = 8192 
            
            with open(local_filepath, "wb") as f: 
                for chunk in r.iter_content(chunk_size=chunk_size): 
                    f.write(chunk)
                
    except Exception as e: 
        print(f"下载错误:{e}") 
        raise e


async def _download_file(arguments: dict) -> list[TextContent]:
    """下载文件工具的MCP接口"""
    
    url = arguments.get("url")
    download_path = arguments.get("download_path")
    
    if not url:
        return [TextContent(type="text", text="❌ 错误：下载链接不能为空")]
    
    if not download_path:
        return [TextContent(type="text", text="❌ 错误：下载路径不能为空")]
    
    try:
        # 确保下载目录存在
        download_dir = Path(download_path).parent
        download_dir.mkdir(parents=True, exist_ok=True)
        
        # 执行下载
        download(url, download_path)
        
        # 检查文件是否下载成功
        if os.path.exists(download_path):
            file_size = os.path.getsize(download_path)
            return [TextContent(type="text", text=f"✅ 文件下载成功！\n📁 保存位置: {download_path}\n📊 文件大小: {file_size} 字节")]
        else:
            return [TextContent(type="text", text="❌ 下载失败：文件未能成功保存")]
            
    except requests.RequestException as e:
        return [TextContent(type="text", text=f"❌ 网络请求错误: {str(e)}")]
    except PermissionError:
        return [TextContent(type="text", text="❌ 权限错误：无法写入指定路径，请检查文件夹权限")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 下载失败: {str(e)}")]