# tools/plugin_search.py

import requests
from bs4 import BeautifulSoup
import urllib.parse
from mcp.server import Server
from mcp.types import Tool, TextContent


# 插件搜索工具实现函数 - 不再包含装饰器，由统一入口调用


async def _search_minecraft_plugins(arguments: dict) -> list[TextContent]:
    """执行Minecraft插件搜索"""
    
    keyword = arguments.get("keyword")
    limit = arguments.get("limit", 5)
    
    if not keyword:
        return [TextContent(type="text", text="❌ 错误：搜索关键词不能为空")]
    
    try:
        # 构建搜索URL
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = f"https://www.minebbs.com/search/15498982/?q={encoded_keyword}&t=resource&c[categories][0]=63&c[categories][1]=70&c[categories][2]=75&c[child_categories]=1&o=relevance"
        base_url = "https://www.minebbs.com"
        
        # 添加请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送GET请求
        response = requests.get(search_url, headers=headers, allow_redirects=True, timeout=10)
        
        if response.status_code != 200:
            return [TextContent(type="text", text=f"❌ 请求失败，状态码: {response.status_code}")]
        
        soup = BeautifulSoup(response.text, 'html.parser')
        all_results = soup.find_all('li', class_='block-row block-row--separated js-inlineModContainer')
        
        if not all_results:
            return [TextContent(type="text", text=f"🔍 没有找到关于 '{keyword}' 的插件搜索结果")]
        
        # 解析搜索结果
        parsed_data = _parse_search_results(all_results[:limit], base_url)
        
        # 格式化输出结果
        result_text = _format_search_results(keyword, len(all_results), parsed_data)
        
        return [TextContent(type="text", text=result_text)]
        
    except requests.RequestException as e:
        return [TextContent(type="text", text=f"❌ 网络请求错误: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ 解析错误: {str(e)}")]


def _parse_search_results(results, base_url: str) -> list[dict]:
    """解析搜索结果"""
    
    parsed_data = []
    
    for item_index, item in enumerate(results):
        # 1. 标题和资源链接
        title_tag = item.find('h3', class_='contentRow-title')
        resource_link_tag = title_tag.find('a') if title_tag else None
        
        title = "N/A"
        resource_url = "N/A"
        
        if resource_link_tag and resource_link_tag.has_attr('href'):
            title = resource_link_tag.get_text(strip=True).replace('\n', ' ')
            resource_url = urllib.parse.urljoin(base_url, resource_link_tag['href'])
        
        # 2. 简介
        snippet_tag = item.find('div', class_='contentRow-snippet')
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else "N/A"
        
        # 3. 作者、发布日期、标签、分类
        minor_info_tag = item.find('div', class_='contentRow-minor')
        author = "N/A"
        publish_date = "N/A"
        tags_list = []
        category = "N/A"
        
        if minor_info_tag:
            author_tag = minor_info_tag.find('a', class_='username')
            author = author_tag.get_text(strip=True) if author_tag else "N/A"
            
            time_tag = minor_info_tag.find('time', class_='u-dt')
            publish_date = time_tag.get_text(strip=True) if time_tag else "N/A"
            
            # 标签
            tags_list = [tag.get_text(strip=True) for tag in minor_info_tag.find_all('span', class_='tagItem')]
            
            category_link_tag = minor_info_tag.find('a', href=lambda href: href and "/resources/categories/" in href)
            if category_link_tag:
                category = category_link_tag.get_text(strip=True)
        
        plugin_info = {
            "序号": item_index + 1,
            "标题": title,
            "插件链接": resource_url,
            "简介": snippet[:200] + "..." if len(snippet) > 200 else snippet,
            "作者": author,
            "发布日期": publish_date,
            "标签": ", ".join(tags_list) if tags_list else "N/A",
            "分类": category
        }
        parsed_data.append(plugin_info)
    
    return parsed_data


def _format_search_results(keyword: str, total_count: int, parsed_data: list[dict]) -> str:
    """格式化搜索结果输出"""
    
    result_text = f"🔍 搜索关键词: {keyword}\n"
    result_text += f"📊 找到 {total_count} 个结果，显示前 {len(parsed_data)} 个:\n\n"
    
    for plugin in parsed_data:
        result_text += f"【{plugin['序号']}】{plugin['标题']}\n"
        result_text += f"👤 作者: {plugin['作者']}\n"
        result_text += f"📅 发布日期: {plugin['发布日期']}\n"
        result_text += f"🏷️ 标签: {plugin['标签']}\n"
        result_text += f"📂 分类: {plugin['分类']}\n"
        result_text += f"📝 简介: {plugin['简介']}\n"
        result_text += f"🔗 链接: {plugin['插件链接']}\n"
        result_text += "-" * 50 + "\n\n"
    
    return result_text