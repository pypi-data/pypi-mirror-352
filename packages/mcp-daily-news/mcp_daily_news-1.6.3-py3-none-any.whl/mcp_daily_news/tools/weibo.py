"""微博热搜工具"""

from urllib.parse import urlencode
from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_weibo_trending_func(args: dict) -> list:
    """获取微博热搜榜数据"""
    response = await http_client.get("https://weibo.com/ajax/side/hotSearch")
    response.raise_for_status()
    
    data = response.json()
    if data.get("ok") != 1 or not isinstance(data.get("data", {}).get("realtime"), list):
        raise Exception("获取微博热搜榜失败")
    
    results = []
    for item in data["data"]["realtime"]:
        if item.get("is_ad") == 1:
            continue
            
        key = item.get("word_scheme") or f"#{item.get('word')}"
        
        # 构建搜索URL
        params = {
            "q": key,
            "band_rank": "1",
            "Refer": "top"
        }
        link = f"https://s.weibo.com/weibo?{urlencode(params)}"
        
        results.append({
            "title": item.get("word", ""),
            "description": item.get("note") or key,
            "popularity": item.get("num", ""),
            "link": link,
        })
    
    return results


weibo_tool_config = ToolConfig(
    name="get-weibo-trending",
    description="获取微博热搜榜，包含时事热点、社会现象、娱乐新闻、明星动态及网络热议话题的实时热门中文资讯",
    func=get_weibo_trending_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(weibo_tool_config) 