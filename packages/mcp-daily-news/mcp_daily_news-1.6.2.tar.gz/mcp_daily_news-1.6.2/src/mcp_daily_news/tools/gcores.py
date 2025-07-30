"""机核网新闻工具"""

from ..utils import define_tool_config, get_rss_items
from ..types import ToolConfig


async def get_gcores_new_func(args: dict) -> list:
    """获取机核网新闻数据"""
    return await get_rss_items("https://www.gcores.com/rss")


tool_config = ToolConfig(
    name="get-gcores-new",
    description="获取机核网游戏相关资讯，包含电子游戏评测、玩家文化、游戏开发和游戏周边产品的深度内容",
    func=get_gcores_new_func,
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 