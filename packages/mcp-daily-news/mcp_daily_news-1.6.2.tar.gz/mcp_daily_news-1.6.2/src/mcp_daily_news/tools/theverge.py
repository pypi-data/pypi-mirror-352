"""The Verge新闻工具"""

from urllib.parse import urlparse, parse_qs
from ..utils import define_tool_config, get_rss
from ..types import ToolConfig


async def get_theverge_news_func(args: dict) -> list:
    """获取The Verge新闻数据"""
    rss_data = await get_rss("https://www.theverge.com/rss/index.xml")
    
    if not isinstance(rss_data.get("feed", {}).get("entry"), list):
        raise Exception("获取 The Verge 新闻失败")
    
    results = []
    for item in rss_data["feed"]["entry"]:
        link = item.get("link")
        if not link and item.get("id"):
            link = item["id"]
        
        # 处理链接参数
        if link:
            try:
                parsed = urlparse(link)
                query_params = parse_qs(parsed.query)
                if "p" in query_params:
                    # 重构URL
                    link = f"{parsed.scheme}://{parsed.netloc}{query_params['p'][0]}"
            except Exception:
                pass
        
        result_item = {
            "title": item.get("title", ""),
            "description": item.get("summary", ""),
            "publish_time": item.get("published", ""),
            "link": link or "",
        }
        results.append(result_item)
    
    return results


tool_config = ToolConfig(
    name="get-theverge-news",
    description="获取 The Verge 新闻，包含科技创新、数码产品评测、互联网趋势及科技公司动态的英文科技资讯",
    func=get_theverge_news_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 