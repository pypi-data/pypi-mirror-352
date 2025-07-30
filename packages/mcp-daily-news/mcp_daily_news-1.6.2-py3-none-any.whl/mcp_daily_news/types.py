"""类型定义模块"""

from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
from pydantic import BaseModel, Field, ConfigDict


class ToolResult(BaseModel):
    """工具返回结果的数据模型"""
    
    model_config = ConfigDict(extra="allow")
    
    title: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    cover: Optional[str] = None
    popularity: Optional[Union[str, int]] = None
    author: Optional[str] = None
    publish_time: Optional[str] = None


Results = List[Dict[str, Any]]

ToolFunc = Callable[[Dict[str, Any]], Awaitable[Results]]


class ToolConfig(BaseModel):
    """工具配置模型"""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    name: str
    description: str
    func: ToolFunc
    input_schema: Optional[Dict[str, Any]] = Field(default=None, alias="schema") 