"""知乎热榜工具"""

from datetime import datetime
from ..utils import define_tool_config, http_client
from ..types import ToolConfig


async def get_zhihu_trending_func(args: dict) -> list:
    """获取知乎热榜数据"""
    limit = args.get("limit", 50)
    
    headers = {
        'User-Agent': 'osee2unifiedRelease/22916 osee2unifiedReleaseVersion/10.49.0 Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
        'x-app-versioncode': '22916',
        'x-app-bundleid': 'com.zhihu.ios',
        'x-app-build': 'release',
        'x-package-ytpe': 'appstore',  # 知乎的typo
        'x-app-za': 'OS=iOS&Release=18.5&Model=iPhone17,2&VersionName=10.49.0&VersionCode=22916&Width=1290&Height=2796&DeviceType=Phone&Brand=Apple&OperatorType=6553565535'
    }
    
    response = await http_client.get(
        "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total",
        params={"limit": limit},
        headers=headers
    )
    response.raise_for_status()
    
    data = response.json()
    if not isinstance(data.get("data"), list):
        raise Exception("获取知乎热榜失败")
    
    results = []
    for item in data["data"]:
        target = item.get("target", {})
        url = target.get("url", "")
        question_id = url.split("/")[-1] if url else None
        
        # 转换时间戳
        created_timestamp = target.get("created")
        created_iso = None
        if created_timestamp:
            try:
                created_iso = datetime.fromtimestamp(created_timestamp).isoformat()
            except (ValueError, TypeError):
                pass
        
        # 获取封面图片
        cover = None
        children = item.get("children", [])
        if children and len(children) > 0:
            cover = children[0].get("thumbnail")
        
        result_item = {
            "title": target.get("title", ""),
            "description": target.get("excerpt", ""),
            "popularity": item.get("detail_text", ""),
        }
        
        if cover:
            result_item["cover"] = cover
        if created_iso:
            result_item["created"] = created_iso
        if question_id:
            result_item["link"] = f"https://www.zhihu.com/question/{question_id}"
        
        results.append(result_item)
    
    return results


zhihu_tool_config = ToolConfig(
    name="get-zhihu-trending",
    description="获取知乎热榜，包含时事热点、社会话题、科技动态、娱乐八卦等多领域的热门问答和讨论的中文资讯",
    func=get_zhihu_trending_func,
    input_schema={
        "type": "object",
        "properties": {
            "limit": {
                "type": "number",
                "description": "返回结果数量限制",
                "default": 50
            }
        }
    }
)


async def get_tool_config() -> ToolConfig:
    """获取工具配置"""
    return await define_tool_config(zhihu_tool_config) 