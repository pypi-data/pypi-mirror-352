"""9to5Mac新闻工具"""

from ..utils import define_tool_config, get_rss_items
from ..types import ToolConfig


async def get_9to5mac_news_func(args: dict) -> list:
    """获取9to5Mac新闻数据"""
    return await get_rss_items("https://9to5mac.com/feed/")


tool_config = ToolConfig(
    name="get-9to5mac-news",
    description="获取 9to5Mac 苹果相关新闻，包含苹果产品发布、iOS 更新、Mac 硬件、应用推荐及苹果公司动态的英文资讯",
    func=get_9to5mac_news_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 