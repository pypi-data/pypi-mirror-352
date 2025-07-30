"""豆瓣实时热门榜工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig


URL_MAP = {
    "subject": "https://m.douban.com/rexxar/api/v2/subject_collection/subject_real_time_hotest/items",
    "movie": "https://m.douban.com/rexxar/api/v2/subject_collection/movie_real_time_hotest/items",
    "tv": "https://m.douban.com/rexxar/api/v2/subject_collection/tv_real_time_hotest/items",
}


async def get_douban_rank_func(args: dict) -> list:
    """获取豆瓣实时热门榜数据"""
    rank_type = args.get("type", "subject")
    start = args.get("start", 0)
    count = args.get("count", 10)
    
    if rank_type not in URL_MAP:
        raise Exception(f"不支持的类型: {rank_type}")
    
    response = await http_client.get(
        URL_MAP[rank_type],
        params={
            "type": rank_type,
            "start": start,
            "count": count,
            "for_mobile": 1,
        },
        headers={
            "Referer": "https://m.douban.com/subject_collection/movie_real_time_hotest",
        }
    )
    response.raise_for_status()
    
    data = response.json()
    if not isinstance(data.get("subject_collection_items"), list):
        raise Exception("获取豆瓣实时热门榜失败")
    
    results = []
    for item in data["subject_collection_items"]:
        rating = item.get("rating", {})
        rating_count = rating.get("count", 0)
        
        result_item = {
            "type_name": item.get("type_name", ""),
            "title": item.get("title", ""),
            "info": item.get("info", ""),
            "cover": item.get("cover", {}).get("url", ""),
            "year": item.get("year", ""),
            "release_date": item.get("release_date", ""),
            "link": item.get("url", ""),
            "popularity": item.get("score", 0),
            "rating_count": rating_count,
        }
        
        # 只有评分人数大于0时才显示评分值
        if rating_count > 0:
            result_item["rating_value"] = rating.get("value")
        
        # 处理标签
        related_terms = item.get("related_search_terms", [])
        if related_terms:
            hashtags = " ".join([f"#{term.get('name', '')}" for term in related_terms if term.get('name')])
            if hashtags:
                result_item["hashtags"] = hashtags
        
        results.append(result_item)
    
    return results


tool_config = ToolConfig(
    name="get-douban-rank",
    description="获取豆瓣实时热门榜单，提供当前热门的图书、电影、电视剧、综艺等作品信息，包含评分和热度数据",
    func=get_douban_rank_func,
    input_schema={
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["subject", "movie", "tv"],
                "default": "subject",
                "description": "榜单类型：subject(图书、电影、电视剧、综艺等), movie(电影), tv(电视剧)"
            },
            "start": {
                "type": "integer",
                "default": 0,
                "description": "起始位置"
            },
            "count": {
                "type": "integer",
                "default": 10,
                "description": "返回结果数量"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 