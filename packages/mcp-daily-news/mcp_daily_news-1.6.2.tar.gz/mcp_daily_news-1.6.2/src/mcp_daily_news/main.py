#!/usr/bin/env python3
"""MCP Trends Hub 主程序"""

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .types import ToolConfig
from .utils import handle_error_result, handle_success_result, logger


async def load_tool_configurations() -> Dict[str, ToolConfig]:
    """加载工具配置"""
    tool_config_map = {}
    tools_dir = Path(__file__).parent / "tools"
    
    # 遍历tools目录下的所有Python文件
    for tool_file in tools_dir.glob("*.py"):
        if tool_file.name.startswith("__"):
            continue
            
        module_name = f"mcp_daily_news.tools.{tool_file.stem}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "get_tool_config"):
                tool_config = await module.get_tool_config()
                tool_config_map[tool_config.name] = tool_config
                logger.info(f"已加载工具: {tool_config.name}")
        except Exception as e:
            logger.error(f"加载工具 {module_name} 失败: {str(e)}")
    
    return tool_config_map


async def main():
    """主函数"""
    # 创建MCP服务器
    server = Server("Daily News")
    logger.set_mcp_server(server)
    
    # 加载工具配置
    tool_config_map = await load_tool_configurations()
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """列出所有可用工具"""
        tools = []
        for tool_config in tool_config_map.values():
            tool = Tool(
                name=tool_config.name,
                description=tool_config.description,
                inputSchema=tool_config.input_schema or {"type": "object", "properties": {}}
            )
            tools.append(tool)
        return tools
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[TextContent]:
        """调用工具"""
        try:
            if name not in tool_config_map:
                raise Exception(f"工具不存在: {name}")
            
            tool_config = tool_config_map[name]
            result = await tool_config.func(arguments)
            
            # 处理成功结果
            success_result = handle_success_result(result, name)
            return [TextContent(type="text", text=content["text"]) 
                   for content in success_result["content"]]
            
        except Exception as e:
            logger.error(f"调用工具 {name} 失败: {str(e)}")
            error_result = handle_error_result(e)
            return [TextContent(type="text", text=content["text"]) 
                   for content in error_result["content"]]
    
    # 启动服务器
    logger.info("启动 MCP Trends Hub 服务器...")
    logger.info(f"已加载 {len(tool_config_map)} 个工具")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main_sync():
    """同步主函数入口"""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync() 