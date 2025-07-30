"""日志模块"""

import logging
import sys
from typing import Any, Optional


class Logger:
    """自定义日志器"""
    
    def __init__(self):
        self._logger = logging.getLogger("mcp-daily-news")
        self._logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.INFO)
        
        # 创建格式器
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        
        # 添加处理器
        if not self._logger.handlers:
            self._logger.addHandler(handler)
        
        self._mcp_server: Optional[Any] = None
    
    def set_mcp_server(self, server: Any) -> None:
        """设置MCP服务器实例"""
        self._mcp_server = server
    
    def info(self, message: str) -> None:
        """记录信息日志"""
        self._logger.info(message)
        if self._mcp_server:
            try:
                # 发送到MCP服务器
                pass  # TODO: 实现MCP日志发送
            except Exception:
                pass
    
    def error(self, message: str) -> None:
        """记录错误日志"""
        self._logger.error(message)
        if self._mcp_server:
            try:
                # 发送到MCP服务器
                pass  # TODO: 实现MCP日志发送
            except Exception:
                pass
    
    def warning(self, message: str) -> None:
        """记录警告日志"""
        self._logger.warning(message)
        if self._mcp_server:
            try:
                # 发送到MCP服务器
                pass  # TODO: 实现MCP日志发送
            except Exception:
                pass
    
    def debug(self, message: str) -> None:
        """记录调试日志"""
        self._logger.debug(message)


# 全局日志器实例
logger = Logger() 