"""虎扑热榜工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig
from bs4 import BeautifulSoup
import json


async def get_hupu_trending_func(args: dict) -> list:
    """获取虎扑热榜数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.hupu.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    try:
        # 虎扑步行街热帖
        response = await http_client.get(
            "https://bbs.hupu.com/bxj",
            headers=headers
        )
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 查找帖子列表
        thread_list = soup.find_all(['tr', 'li', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['thread', 'post', 'topic', 'item']
        ))
        
        if not thread_list:
            # 尝试从虎扑首页获取热门内容
            return await get_hupu_trending_homepage()
        
        rank = 1
        for item in thread_list:
            # 提取帖子标题
            title_elem = item.find('a', href=True)
            if not title_elem:
                title_elem = item.find(['span', 'div'], string=lambda text: text and len(text.strip()) > 5)
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 5 and not any(skip in title for skip in ['登录', '注册', '首页']):
                    # 提取链接
                    url = title_elem.get('href', '') if title_elem.name == 'a' else ""
                    if url and not url.startswith('http'):
                        url = f"https://bbs.hupu.com{url}"
                    
                    # 提取回复数、浏览数等信息
                    reply_elem = item.find(string=lambda text: text and any(
                        char in text for char in ['回复', '浏览', '万', '热度']
                    ))
                    reply_count = reply_elem.strip() if reply_elem else ""
                    
                    results.append({
                        "rank": rank,
                        "title": title,
                        "desc": f"虎扑步行街热帖 - {title}",
                        "url": url or f"https://www.hupu.com/search?q={title}",
                        "reply_count": reply_count,
                        "source": "虎扑",
                        "category": "步行街热帖"
                    })
                    
                    rank += 1
                    if rank > 50:
                        break
        
        if results:
            return results[:50]
        else:
            return await get_hupu_trending_homepage()
            
    except Exception as e:
        return await get_hupu_trending_homepage()


async def get_hupu_trending_homepage():
    """从虎扑首页获取热门内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.hupu.com/'
    }
    
    try:
        # 虎扑首页
        response = await http_client.get(
            "https://www.hupu.com/",
            headers=headers
        )
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 查找热门新闻和帖子
        hot_items = soup.find_all(['a', 'div'], href=True) + soup.find_all(['div', 'span'], class_=lambda x: x and 'hot' in x.lower())
        
        rank = 1
        for item in hot_items:
            if item.name == 'a':
                title = item.get_text(strip=True)
                url = item.get('href', '')
            else:
                link_elem = item.find('a', href=True)
                if link_elem:
                    title = link_elem.get_text(strip=True)
                    url = link_elem.get('href', '')
                else:
                    title = item.get_text(strip=True)
                    url = ""
            
            if title and len(title) > 5 and not any(skip in title for skip in ['登录', '注册', '首页', '下载']):
                if url and not url.startswith('http'):
                    url = f"https://www.hupu.com{url}"
                
                results.append({
                    "rank": rank,
                    "title": title,
                    "desc": f"虎扑热门内容 - {title}",
                    "url": url or f"https://www.hupu.com/search?q={title}",
                    "reply_count": "",
                    "source": "虎扑",
                    "category": "热门内容"
                })
                
                rank += 1
                if rank > 50:
                    break
        
        if results:
            return results[:50]
            
    except Exception:
        pass
    
    # 尝试API接口
    try:
        response = await http_client.get(
            "https://www.hupu.com/api/list",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            if 'data' in data:
                items = data['data'][:50]
                for idx, item in enumerate(items, 1):
                    results.append({
                        "rank": idx,
                        "title": item.get('title', '').strip(),
                        "desc": item.get('summary', f"虎扑内容 - {item.get('title', '')}"),
                        "url": item.get('url', ''),
                        "reply_count": item.get('reply_count', ''),
                        "source": "虎扑",
                        "category": "热门话题"
                    })
            
            if results:
                return results
                
    except Exception:
        pass
    
    # 最终备用方案
    return [
        {
            "rank": 1,
            "title": "虎扑热榜数据获取中...",
            "desc": "虎扑体育、步行街热门话题和热议内容",
            "url": "https://www.hupu.com/",
            "reply_count": "",
            "source": "虎扑",
            "category": "系统消息",
            "note": "接口暂时不可用，请稍后重试"
        }
    ]


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    hupu_tool_config = ToolConfig(
        name="get-hupu-trending",
        description="获取虎扑热榜，包含虎扑体育赛事、步行街热帖、篮球足球话题及男性生活兴趣的热门中文讨论内容",
        func=get_hupu_trending_func,
    )
    return await define_tool_config(hupu_tool_config) 