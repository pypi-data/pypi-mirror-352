"""纽约时报新闻工具"""

from ..utils import define_tool_config, get_rss_items
from ..types import ToolConfig


async def get_nytimes_news_func(args: dict) -> list:
    """获取纽约时报新闻数据"""
    region = args.get("region", "cn")
    section = args.get("section", "HomePage")
    
    if region == "cn":
        url = "https://cn.nytimes.com/rss/"
    else:
        url = f"https://rss.nytimes.com/services/xml/rss/nyt/{section}.xml"
    
    return await get_rss_items(url)


tool_config = ToolConfig(
    name="get-nytimes-news",
    description="获取纽约时报新闻，包含国际政治、经济金融、社会文化、科学技术及艺术评论的高质量英文或中文国际新闻资讯",
    func=get_nytimes_news_func,
    input_schema={
        "type": "object",
        "properties": {
            "region": {
                "type": "string",
                "enum": ["cn", "global"],
                "default": "cn",
                "description": "地区选择：cn(中文), global(全球)"
            },
            "section": {
                "type": "string",
                "default": "HomePage",
                "description": "分类，当region为cn时无效。可选值: Africa, Americas, ArtandDesign, Arts, AsiaPacific, Automobiles, Baseball, Books/Review, Business, Climate, CollegeBasketball, CollegeFootball, Dance, Dealbook, DiningandWine, Economy, Education, EnergyEnvironment, Europe, FashionandStyle, Golf, Health, Hockey, HomePage, Jobs, Lens, MediaandAdvertising, MiddleEast, MostEmailed, MostShared, MostViewed, Movies, Music, NYRegion, Obituaries, PersonalTech, Politics, ProBasketball, ProFootball, RealEstate, Science, SmallBusiness, Soccer, Space, Sports, SundayBookReview, Sunday-Review, Technology, Television, Tennis, Theater, TMagazine, Travel, Upshot, US, Weddings, Well, World, YourMoney"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 