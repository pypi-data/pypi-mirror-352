"""自定义RSS工具"""

import os
from ..utils import define_tool_config, parse_rss
from ..types import ToolConfig


async def get_custom_rss_func(args: dict) -> list:
    """获取自定义RSS数据"""
    rss_url = os.environ.get("TRENDS_HUB_CUSTOM_RSS_URL")
    if not rss_url:
        raise Exception("TRENDS_HUB_CUSTOM_RSS_URL 环境变量未设置")
    
    return await parse_rss(rss_url)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    rss_url = os.environ.get("TRENDS_HUB_CUSTOM_RSS_URL")
    if not rss_url:
        raise Exception("TRENDS_HUB_CUSTOM_RSS_URL 环境变量未设置")
    
    # 尝试获取RSS信息来生成描述
    description = "自定义RSS订阅源"
    try:
        # 这里可以添加获取RSS标题和描述的逻辑
        # 为了简化，暂时使用默认描述
        description = f"自定义RSS订阅源: {rss_url}"
    except Exception:
        pass
    
    return await define_tool_config(ToolConfig(
        name="custom-rss",
        description=description,
        func=get_custom_rss_func,
    )) 