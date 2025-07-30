"""腾讯新闻热点榜工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_tencent_news_trending_func(args: dict) -> list:
    """获取腾讯新闻热点榜数据"""
    page_size = args.get("page_size", 20)
    
    response = await http_client.get(
        "https://r.inews.qq.com/gw/event/hot_ranking_list",
        params={"page_size": page_size}
    )
    response.raise_for_status()
    
    data = response.json()
    if data.get("ret") != 0 or not isinstance(data.get("idlist", [{}])[0].get("newslist"), list):
        raise Exception("获取腾讯新闻热点榜失败")
    
    newslist = data["idlist"][0]["newslist"]
    # 过滤掉第一个元素（通常是标题）
    filtered_newslist = newslist[1:] if len(newslist) > 1 else newslist
    
    results = []
    for item in filtered_newslist:
        result_item = {
            "title": item.get("title", ""),
            "description": item.get("abstract", ""),
            "source": item.get("source", ""),
            "publish_time": item.get("time", ""),
            "link": item.get("url", ""),
        }
        
        # 获取封面图片
        thumbnails = item.get("thumbnails", [])
        if thumbnails:
            result_item["cover"] = thumbnails[0]
        
        # 获取热度分数
        hot_event = item.get("hotEvent", {})
        if hot_event.get("hotScore"):
            result_item["popularity"] = hot_event["hotScore"]
        
        results.append(result_item)
    
    return results


tool_config = ToolConfig(
    name="get-tencent-news-trending",
    description="获取腾讯新闻热点榜，包含国内外时事、社会热点、财经资讯、娱乐动态及体育赛事的综合性中文新闻资讯",
    func=get_tencent_news_trending_func,
    input_schema={
        "type": "object",
        "properties": {
            "page_size": {
                "type": "integer",
                "default": 20,
                "description": "返回结果数量"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 