"""爱范儿科技快讯工具"""

from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_ifanr_news_func(args: dict) -> list:
    """获取爱范儿科技快讯数据"""
    limit = args.get("limit", 20)
    offset = args.get("offset", 0)
    
    response = await http_client.get(
        "https://sso.ifanr.com/api/v5/wp/buzz",
        params={"limit": limit, "offset": offset}
    )
    response.raise_for_status()
    
    data = response.json()
    if not isinstance(data.get("objects"), list):
        raise Exception("获取爱范儿快讯失败")
    
    results = []
    for item in data["objects"]:
        result_item = {
            "title": item.get("post_title", ""),
            "description": item.get("post_content", ""),
        }
        
        # 构建链接
        if item.get("buzz_original_url"):
            result_item["link"] = item["buzz_original_url"]
        elif item.get("post_id"):
            result_item["link"] = f"https://www.ifanr.com/{item['post_id']}"
        
        results.append(result_item)
    
    return results


tool_config = ToolConfig(
    name="get-ifanr-news",
    description="获取爱范儿科技快讯，包含最新的科技产品、数码设备、互联网动态等前沿科技资讯",
    func=get_ifanr_news_func,
    input_schema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "default": 20,
                "description": "返回结果数量限制"
            },
            "offset": {
                "type": "integer",
                "default": 0,
                "description": "偏移量"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(tool_config) 