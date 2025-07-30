"""缓存存储模块"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional


class CacheStorage:
    """缓存存储类"""
    
    def __init__(self):
        self._cache_dir = Path(tempfile.gettempdir()) / "mcp-daily-news" / "cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path_by_key(self, key: str) -> Path:
        """根据键获取文件路径"""
        # 清理键名中的非法字符
        safe_key = "".join(c for c in key if c.isalnum() or c in "-_.")
        return self._cache_dir / safe_key
    
    def get_item(self, key: str) -> Optional[str]:
        """获取缓存项"""
        item_path = self._get_path_by_key(key)
        if not item_path.exists():
            return None
        
        try:
            return item_path.read_text(encoding="utf-8")
        except Exception:
            return None
    
    def set_item(self, key: str, value: str) -> None:
        """设置缓存项"""
        item_path = self._get_path_by_key(key)
        try:
            item_path.write_text(value, encoding="utf-8")
        except Exception:
            pass  # 静默忽略写入错误
    
    def remove_item(self, key: str) -> None:
        """删除缓存项"""
        item_path = self._get_path_by_key(key)
        if item_path.exists():
            try:
                item_path.unlink()
            except Exception:
                pass  # 静默忽略删除错误
    
    def clear(self) -> None:
        """清空所有缓存"""
        if self._cache_dir.exists():
            try:
                shutil.rmtree(self._cache_dir)
                self._cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass  # 静默忽略清空错误


# 全局缓存存储实例
cache_storage = CacheStorage() 