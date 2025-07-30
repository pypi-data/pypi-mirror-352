"""网易新闻热点榜工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_netease_news_trending_func(args: dict) -> list:
    """获取网易新闻热点榜数据"""
    response = await http_client.get("https://m.163.com/fe/api/hot/news/flow")
    response.raise_for_status()
    
    data = response.json()
    if data.get("code") != 200 or not isinstance(data.get("data", {}).get("list"), list):
        raise Exception("获取网易新闻热点榜失败")
    
    results = []
    for item in data["data"]["list"]:
        result_item = {
            "title": item.get("title", ""),
            "cover": item.get("imgsrc", ""),
            "source": item.get("source", ""),
            "publish_time": item.get("ptime", ""),
            "link": item.get("url", ""),
        }
        results.append(result_item)
    
    return results


tool_config = ToolConfig(
    name="get-netease-news-trending",
    description="获取网易新闻热点榜，包含时政要闻、社会事件、财经资讯、科技动态及娱乐体育的全方位中文新闻资讯",
    func=get_netease_news_trending_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 