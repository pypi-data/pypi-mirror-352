"""36氪热榜工具"""

import time
from datetime import datetime
from ..utils import define_tool_config, http_client
from ..types import ToolConfig


LIST_TYPE_MAP = {
    "hot": "hotRankList",
    "video": "videoList", 
    "comment": "remarkList",
    "collect": "collectList",
}


async def get_36kr_trending_func(args: dict) -> list:
    """获取36氪热榜数据"""
    list_type = args.get("type", "hot")
    
    if list_type not in LIST_TYPE_MAP:
        raise Exception(f"不支持的类型: {list_type}")
    
    payload = {
        "partner_id": "wap",
        "param": {
            "siteId": 1,
            "platformId": 2,
        },
        "timestamp": int(time.time() * 1000),
    }
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }
    
    response = await http_client.post(
        f"https://gateway.36kr.com/api/mis/nav/home/nav/rank/{list_type}",
        json=payload,
        headers=headers
    )
    response.raise_for_status()
    
    data = response.json()
    if not isinstance(data.get("data"), dict):
        raise Exception("获取36氪热榜失败")
    
    list_key = LIST_TYPE_MAP[list_type]
    items = data["data"].get(list_key, [])
    
    results = []
    for item in items:
        template_material = item.get("templateMaterial", {})
        
        # 转换发布时间
        publish_time_str = template_material.get("publishTime")
        publish_time_iso = None
        if publish_time_str:
            try:
                # 假设时间格式为时间戳（毫秒）
                if isinstance(publish_time_str, (int, float)):
                    publish_time_iso = datetime.fromtimestamp(publish_time_str / 1000).isoformat()
                elif isinstance(publish_time_str, str):
                    # 尝试解析字符串时间
                    publish_time_iso = publish_time_str
            except (ValueError, TypeError):
                pass
        
        result_item = {
            "title": template_material.get("widgetTitle", ""),
            "author": template_material.get("authorName", ""),
            "read_count": template_material.get("statRead", 0),
            "collect_count": template_material.get("statCollect", 0),
            "comment_count": template_material.get("statComment", 0),
            "praise_count": template_material.get("statPraise", 0),
        }
        
        # 添加可选字段
        if template_material.get("widgetImage"):
            result_item["cover"] = template_material["widgetImage"]
        if publish_time_iso:
            result_item["publish_time"] = publish_time_iso
        if template_material.get("itemId"):
            result_item["link"] = f"https://www.36kr.com/p/{template_material['itemId']}"
        
        results.append(result_item)
    
    return results


kr36_tool_config = ToolConfig(
    name="get-36kr-trending",
    description="获取 36 氪热榜，提供创业、商业、科技领域的热门资讯，包含投融资动态、新兴产业分析和商业模式创新信息",
    func=get_36kr_trending_func,
    input_schema={
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["hot", "video", "comment", "collect"],
                "default": "hot",
                "description": "分类：hot(人气榜), video(视频榜), comment(热议榜), collect(收藏榜)"
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(kr36_tool_config) 