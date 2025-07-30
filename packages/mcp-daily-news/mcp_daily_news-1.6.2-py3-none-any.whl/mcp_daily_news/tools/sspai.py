"""少数派热榜工具"""

from datetime import datetime
from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_sspai_rank_func(args: dict) -> list:
    """获取少数派热榜数据"""
    tag = args.get("tag", "热门文章")
    limit = args.get("limit", 40)
    
    # 验证tag参数
    valid_tags = ["热门文章", "应用推荐", "生活方式", "效率技巧", "少数派播客"]
    if tag not in valid_tags:
        raise Exception(f"不支持的分类: {tag}")
    
    response = await http_client.get(
        "https://sspai.com/api/v1/article/tag/page/get",
        params={"tag": tag, "limit": limit}
    )
    response.raise_for_status()
    
    data = response.json()
    if data.get("error") != 0 or not isinstance(data.get("data"), list):
        raise Exception(data.get("msg", "获取少数派热榜失败"))
    
    results = []
    for item in data["data"]:
        # 转换时间戳
        released_time_iso = None
        if item.get("released_time"):
            try:
                released_time_iso = datetime.fromtimestamp(item["released_time"]).isoformat()
            except (ValueError, TypeError):
                pass
        
        result_item = {
            "title": item.get("title", ""),
            "summary": item.get("summary", ""),
            "author": item.get("author", {}).get("nickname", ""),
            "comment_count": item.get("comment_count", 0),
            "like_count": item.get("like_count", 0),
            "view_count": item.get("view_count", 0),
        }
        
        if released_time_iso:
            result_item["released_time"] = released_time_iso
        if item.get("id"):
            result_item["link"] = f"https://sspai.com/post/{item['id']}"
        
        results.append(result_item)
    
    return results


sspai_tool_config = ToolConfig(
    name="get-sspai-rank",
    description="获取少数派热榜，包含数码产品评测、软件应用推荐、生活方式指南及效率工作技巧的优质中文科技生活类内容",
    func=get_sspai_rank_func,
    input_schema={
        "type": "object",
        "properties": {
            "tag": {
                "type": "string",
                "enum": ["热门文章", "应用推荐", "生活方式", "效率技巧", "少数派播客"],
                "default": "热门文章",
                "description": "分类"
            },
            "limit": {
                "type": "integer",
                "default": 40,
                "description": "返回结果数量限制"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(sspai_tool_config) 