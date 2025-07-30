"""雪球财经热榜工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig
from bs4 import BeautifulSoup
import json


async def get_xueqiu_trending_func(args: dict) -> list:
    """获取雪球财经热榜数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://xueqiu.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    try:
        # 雪球热榜API
        response = await http_client.get(
            "https://xueqiu.com/v4/statuses/hot_list",
            headers=headers
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                results = []
                
                if 'list' in data:
                    items = data['list'][:50]
                    for idx, item in enumerate(items, 1):
                        status = item.get('status', {})
                        user = item.get('user', {})
                        
                        results.append({
                            "rank": idx,
                            "title": status.get('text', '').strip()[:100],
                            "desc": status.get('description', f"雪球财经热议 - {status.get('text', '')[:50]}"),
                            "url": f"https://xueqiu.com{status.get('target', '')}" if status.get('target') else f"https://xueqiu.com/statuses/show/{status.get('id', '')}",
                            "author": user.get('screen_name', ''),
                            "comment_count": status.get('reply_count', 0),
                            "like_count": status.get('like_count', 0),
                            "created_at": status.get('created_at', ''),
                            "source": "雪球",
                            "category": "财经投资"
                        })
                
                if results:
                    return results
                    
            except json.JSONDecodeError:
                pass
                
    except Exception:
        pass
    
    # 尝试从雪球首页获取热门内容
    try:
        response = await http_client.get(
            "https://xueqiu.com/",
            headers=headers
        )
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 查找热门股票和话题
        hot_items = soup.find_all(['a', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['hot', 'trend', 'topic', 'stock']
        ))
        
        rank = 1
        seen_titles = set()
        
        for item in hot_items:
            try:
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
                
                if title and len(title) > 3 and title not in seen_titles:
                    # 过滤无效内容
                    if any(skip in title for skip in ['登录', '注册', '下载', '首页']):
                        continue
                    
                    seen_titles.add(title)
                    
                    if url and not url.startswith('http'):
                        url = f"https://xueqiu.com{url}"
                    
                    # 尝试获取其他信息
                    desc = ""
                    parent = item.parent if item else None
                    if parent:
                        desc_elem = parent.find('p') or parent.find('span', class_='desc')
                        if desc_elem:
                            desc = desc_elem.get_text(strip=True)[:150]
                    
                    if not desc:
                        desc = f"雪球财经热议 - {title}"
                    
                    results.append({
                        "rank": rank,
                        "title": title,
                        "desc": desc,
                        "url": url or f"https://xueqiu.com/search?q={title}",
                        "author": "",
                        "comment_count": "",
                        "like_count": "",
                        "created_at": "",
                        "source": "雪球",
                        "category": "财经投资"
                    })
                    
                    rank += 1
                    if rank > 50:
                        break
                        
            except Exception:
                continue
        
        if results:
            return results[:50]
            
    except Exception:
        pass
    
    # 最终备用方案
    return [
        {
            "rank": 1,
            "title": "雪球财经热榜数据获取中...",
            "desc": "雪球财经投资热门话题和股市讨论",
            "url": "https://xueqiu.com/",
            "author": "",
            "comment_count": "",
            "like_count": "",
            "created_at": "",
            "source": "雪球",
            "category": "财经投资",
            "note": "接口暂时不可用，请稍后重试"
        }
    ]


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    xueqiu_tool_config = ToolConfig(
        name="get-xueqiu-trending",
        description="获取雪球财经热榜，包含股票投资、财经新闻、投资策略、市场分析及投资者热议的财经投资类中文资讯",
        func=get_xueqiu_trending_func,
    )
    return await define_tool_config(xueqiu_tool_config) 