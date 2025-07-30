"""澎湃新闻热榜工具"""

from datetime import datetime
from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_thepaper_trending_func(args: dict) -> list:
    """获取澎湃新闻热榜数据"""
    response = await http_client.get("https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar")
    response.raise_for_status()
    
    data = response.json()
    if data.get("resultCode") != 1 or not isinstance(data.get("data", {}).get("hotNews"), list):
        raise Exception(data.get("resultMsg", "获取澎湃新闻热榜失败"))
    
    results = []
    for item in data["data"]["hotNews"]:
        # 转换发布时间
        publish_time_iso = None
        if item.get("pubTimeLong"):
            try:
                # 假设pubTimeLong是毫秒时间戳
                publish_time_iso = datetime.fromtimestamp(item["pubTimeLong"] / 1000).isoformat()
            except (ValueError, TypeError):
                pass
        
        result_item = {
            "title": item.get("name", ""),
            "cover": item.get("pic", ""),
            "popularity": item.get("praiseTimes", 0),
        }
        
        if publish_time_iso:
            result_item["publish_time"] = publish_time_iso
        
        # 处理标签
        tag_list = item.get("tagList", [])
        if tag_list:
            hashtags = " ".join([f"#{tag.get('tag', '')}" for tag in tag_list if tag.get('tag')])
            if hashtags:
                result_item["hashtags"] = hashtags
        
        # 构建链接
        if item.get("contId"):
            result_item["link"] = f"https://www.thepaper.cn/newsDetail_forward_{item['contId']}"
        
        results.append(result_item)
    
    return results


tool_config = ToolConfig(
    name="get-thepaper-trending",
    description="获取澎湃新闻热榜，包含时政要闻、财经动态、社会事件、文化教育及深度报道的高质量中文新闻资讯",
    func=get_thepaper_trending_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 