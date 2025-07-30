"""贴吧热议榜工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig
from bs4 import BeautifulSoup
import json


async def get_tieba_trending_func(args: dict) -> list:
    """获取贴吧热议榜数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://tieba.baidu.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    try:
        # 贴吧热议榜页面
        response = await http_client.get(
            "https://tieba.baidu.com/hottopic/browse/topicList",
            headers=headers
        )
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        
        # 查找热议话题列表
        topic_list = soup.find_all(['div', 'li'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['topic', 'hot', 'item', 'list']
        ))
        
        if not topic_list:
            # 尝试API接口
            return await get_tieba_trending_api()
        
        rank = 1
        for item in topic_list:
            # 提取话题标题
            title_elem = item.find(['a', 'span', 'div'], string=lambda text: text and len(text.strip()) > 3)
            if not title_elem:
                title_elem = item.find(['a', 'span', 'div'])
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    # 提取链接
                    link_elem = item.find('a', href=True)
                    url = link_elem['href'] if link_elem else ""
                    if url and not url.startswith('http'):
                        url = f"https://tieba.baidu.com{url}"
                    
                    # 提取热度信息
                    hot_elem = item.find(string=lambda text: text and any(
                        char in text for char in ['万', '热度', '讨论', '回复']
                    ))
                    hot_value = hot_elem.strip() if hot_elem else ""
                    
                    results.append({
                        "rank": rank,
                        "title": title,
                        "desc": f"贴吧热议话题 - {title}",
                        "url": url or f"https://tieba.baidu.com/f?kw={title}",
                        "hot_value": hot_value,
                        "source": "百度贴吧",
                        "category": "热议话题"
                    })
                    
                    rank += 1
                    if rank > 50:
                        break
        
        if results:
            return results[:50]
        else:
            return await get_tieba_trending_api()
            
    except Exception as e:
        return await get_tieba_trending_api()


async def get_tieba_trending_api():
    """贴吧热议榜API获取方案"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://tieba.baidu.com/',
        'Accept': 'application/json'
    }
    
    try:
        # 尝试贴吧热门话题API
        response = await http_client.get(
            "https://tieba.baidu.com/mo/q/hotMessage",
            headers=headers
        )
        
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'data' in data and isinstance(data['data'], list):
            hot_topics = data['data']
            
            for idx, topic in enumerate(hot_topics[:50], 1):
                title = topic.get('title', '').strip()
                if title:
                    results.append({
                        "rank": idx,
                        "title": title,
                        "desc": topic.get('desc', f"贴吧热议话题 - {title}"),
                        "url": topic.get('url', f"https://tieba.baidu.com/f?kw={title}"),
                        "hot_value": topic.get('hot_num', 0),
                        "source": "百度贴吧",
                        "category": "热门话题"
                    })
        
        if results:
            return results
            
    except Exception:
        pass
    
    try:
        # 备用方案：贴吧首页热门吧
        response = await http_client.get(
            "https://tieba.baidu.com/",
            headers=headers
        )
        
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找热门贴吧
        hot_bars = soup.find_all('a', href=lambda x: x and '/f?kw=' in x)
        
        results = []
        for idx, bar in enumerate(hot_bars[:50], 1):
            bar_name = bar.get_text(strip=True)
            if bar_name and len(bar_name) > 1:
                results.append({
                    "rank": idx,
                    "title": f"{bar_name}吧",
                    "desc": f"热门贴吧 - {bar_name}吧",
                    "url": f"https://tieba.baidu.com{bar['href']}",
                    "hot_value": "",
                    "source": "百度贴吧",
                    "category": "热门贴吧"
                })
        
        if results:
            return results
            
    except Exception:
        pass
    
    # 最终备用方案
    return [
        {
            "rank": 1,
            "title": "贴吧热议榜数据获取中...",
            "desc": "百度贴吧热门话题和热议内容",
            "url": "https://tieba.baidu.com/",
            "hot_value": "",
            "source": "百度贴吧",
            "category": "系统消息",
            "note": "接口暂时不可用，请稍后重试"
        }
    ]


tieba_tool_config = ToolConfig(
    name="get-tieba-trending",
    description="获取贴吧热议榜，包含百度贴吧的热门话题、热议帖子、热门贴吧及用户关注的热点讨论中文内容",
    func=get_tieba_trending_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tieba_tool_config) 