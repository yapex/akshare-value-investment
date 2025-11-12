"""
DiskCache 适配器实现
基于验证过的 diskcache 库
"""

from diskcache import Cache
from typing import Any, Optional, Dict
from .base import CacheAdapter


class DiskCacheAdapter(CacheAdapter):
    """DiskCache 适配器"""

    def __init__(self, config):
        self.config = config

        # 构建缓存参数，只传递有效参数
        cache_kwargs = {'directory': config.cache_dir}

        # 只有在size_limit不为None且足够大时才传递
        # 小的size_limit可能导致数据立即被淘汰
        if config.max_size is not None and config.max_size > 10240:  # 至少10KB
            cache_kwargs['size_limit'] = config.max_size

        # eviction_policy可能导致问题，暂时不传递
        # if hasattr(config, 'eviction_policy') and config.eviction_policy:
        #     cache_kwargs['eviction_policy'] = config.eviction_policy

        self._cache = Cache(**cache_kwargs)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            return self._cache.get(key)
        except Exception:
            return None

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            return self._cache.set(key, value, expire=expire)
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            return self._cache.delete(key)
        except Exception:
            return False

    def clear(self) -> bool:
        """清空缓存"""
        try:
            self._cache.clear()
            return True
        except Exception:
            return False

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            return {
                'size': len(self._cache),
                'volume': self._cache.volume()
            }
        except Exception:
            return {'size': 0, 'volume': 0}