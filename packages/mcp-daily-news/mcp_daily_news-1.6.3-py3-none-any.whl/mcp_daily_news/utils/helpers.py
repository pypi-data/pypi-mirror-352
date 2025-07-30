"""辅助函数模块"""

import json
import os
from typing import Any, Dict, List, Optional, TypeVar, Callable, Awaitable, Union
from pydantic import ValidationError

from ..types import ToolConfig, Results

T = TypeVar('T')


async def define_tool_config(
    config: Union[ToolConfig, Callable[[], Union[ToolConfig, Awaitable[ToolConfig]]]]
) -> ToolConfig:
    """定义工具配置"""
    if callable(config):
        result = config()
        if hasattr(result, '__await__'):
            return await result
        return result
    return config


def handle_error_result(error: Exception) -> Dict[str, Any]:
    """处理错误结果"""
    error_message = ""
    
    if isinstance(error, ValidationError):
        error_message = str(error)
    elif isinstance(error, Exception):
        error_message = str(error)
    else:
        error_message = json.dumps(str(error))
    
    return {
        "content": [
            {
                "type": "text",
                "text": error_message,
            }
        ],
        "isError": True,
    }


def handle_success_result(results: Results, tool_name: str) -> Dict[str, Any]:
    """处理成功结果"""
    hidden_fields_env = os.environ.get("DAILY_NEWS_HIDDEN_FIELDS", "")
    hidden_fields = []
    
    if hidden_fields_env:
        configs = [config.strip() for config in hidden_fields_env.split(",") if config.strip()]
        for config in configs:
            if ":" in config:
                tool, key = config.split(":", 1)
                if tool == tool_name:
                    hidden_fields.append(key)
            else:
                hidden_fields.append(config)
    
    content = []
    for item in results:
        if not isinstance(item, dict):
            continue
            
        filtered_entries = []
        for key, value in item.items():
            if (key not in hidden_fields and 
                value is not None and 
                value != "" and 
                value != 0):
                filtered_entries.append(f"<{key}>{str(value)}</{key}>")
        
        if filtered_entries:
            content.append({
                "type": "text",
                "text": "\n".join(filtered_entries),
            })
    
    return {
        "content": content,
    }


def safe_json_parse(json_str: str) -> Optional[Any]:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def pick(obj: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """从字典中选择指定的键"""
    return {key: obj[key] for key in keys if key in obj}


def omit(obj: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """从字典中排除指定的键"""
    return {key: value for key, value in obj.items() if key not in keys} 