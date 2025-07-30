"""BBC新闻工具"""

from ..utils import define_tool_config, parse_rss
from ..types import ToolConfig


def build_bbc_url(category: str = "", edition: str = "") -> str:
    """构建BBC RSS URL"""
    url = "https://feeds.bbci.co.uk/news/"
    
    if category:
        url += f"{category}/"
    
    url += "rss.xml"
    
    if edition:
        url += f"?edition={edition}"
    
    return url


async def get_bbc_news_func(args: dict) -> list:
    """获取BBC新闻数据"""
    category = args.get("category", "")
    edition = args.get("edition", "")
    
    # 验证category参数
    valid_categories = [
        "", "world", "uk", "business", "politics", "health", 
        "education", "science_and_environment", "technology", 
        "entertainment_and_arts"
    ]
    
    if category not in valid_categories:
        raise Exception(f"不支持的分类: {category}")
    
    # 验证edition参数
    valid_editions = ["", "uk", "us", "int"]
    if edition not in valid_editions:
        raise Exception(f"不支持的版本: {edition}")
    
    url = build_bbc_url(category, edition)
    return await parse_rss(url)


bbc_tool_config = ToolConfig(
    name="get-bbc-news",
    description="获取 BBC 新闻，提供全球新闻、英国新闻、商业、政治、健康、教育、科技、娱乐等资讯",
    func=get_bbc_news_func,
    input_schema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": [
                    "", "world", "uk", "business", "politics", "health",
                    "education", "science_and_environment", "technology",
                    "entertainment_and_arts"
                ],
                "default": "",
                "description": "新闻分类：''(热门), world(国际), uk(英国), business(商业), politics(政治), health(健康), education(教育), science_and_environment(科学与环境), technology(科技), entertainment_and_arts(娱乐与艺术)"
            },
            "edition": {
                "type": "string",
                "enum": ["", "uk", "us", "int"],
                "default": "",
                "description": "版本：''(默认), uk(英国), us(美国和加拿大), int(世界其他地区)，仅对category为空时有效"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(bbc_tool_config) 