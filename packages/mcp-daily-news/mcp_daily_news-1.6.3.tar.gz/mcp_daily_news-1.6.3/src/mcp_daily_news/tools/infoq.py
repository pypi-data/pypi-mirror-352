"""InfoQ技术资讯工具"""

from ..utils import define_tool_config, get_rss_items
from ..types import ToolConfig


async def get_infoq_news_func(args: dict) -> list:
    """获取InfoQ技术资讯数据"""
    region = args.get("region", "cn")
    
    url_map = {
        "cn": "https://www.infoq.cn/feed",
        "global": "https://feed.infoq.com/",
    }
    
    if region not in url_map:
        raise Exception(f"不支持的地区: {region}")
    
    url = url_map[region]
    items = await get_rss_items(url)
    
    # 中文版description没有实质内容，移除
    if region == "cn":
        for item in items:
            if "description" in item:
                del item["description"]
    
    return items


tool_config = ToolConfig(
    name="get-infoq-news",
    description="获取 InfoQ 技术资讯，包含软件开发、架构设计、云计算、AI等企业级技术内容和前沿开发者动态",
    func=get_infoq_news_func,
    input_schema={
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "enum": ["cn", "global"],
                "default": "cn",
                "description": "地区选择：cn(中文版), global(国际版)"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 