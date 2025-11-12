"""
组合缓存适配器
实现读写和监控接口的完整适配器
"""

from typing import Any, Optional, Dict, List
from ..abstractions import ICacheReader, ICacheWriter
from .diskcache_adapter import DiskCacheAdapter


class CombinedCacheAdapter(ICacheReader, ICacheWriter):
    """
    组合缓存适配器

    整合现有的DiskCacheAdapter以符合新的接口规范
    遵循适配器模式，保持向后兼容性
    """

    def __init__(self, diskcache_adapter: DiskCacheAdapter):
        self._adapter = diskcache_adapter

    # ICacheReader 接口实现
    async def get_async(self, key: str) -> Optional[Any]:
        """异步获取缓存值"""
        # 简单的异步包装
        return self.get(key)

    def get(self, key: str) -> Optional[Any]:
        """同步获取缓存值"""
        return self._adapter.get(key)

    def exists(self, key: str) -> bool:
        """检查缓存键是否存在"""
        return self.get(key) is not None

    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值"""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    # ICacheWriter 接口实现
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        return self._adapter.set(key, value, expire=ttl)

    def set_multiple(self, items: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存值"""
        success = True
        for key, value in items.items():
            if not self.set(key, value, ttl):
                success = False
        return success

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        return self._adapter.delete(key)

    def delete_multiple(self, keys: List[str]) -> bool:
        """批量删除缓存值"""
        success = True
        for key in keys:
            if not self.delete(key):
                success = False
        return success

    def clear(self) -> bool:
        """清空所有缓存"""
        return self._adapter.clear()

    # 额外方法 - 代理原有适配器的功能
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return self._adapter.stats()