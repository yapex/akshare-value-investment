"""
Smart Cache - 生产级缓存装饰器
基于验证成功的原型，为财务数据查询系统提供透明缓存能力

主要组件：
- CacheResult: 缓存结果包装器
- SmartCache: 智能缓存装饰器
- DiskCacheAdapter: diskcache适配器
"""

from .core.cache import SmartCache, smart_cache
from .core.config import CacheConfig
from .core.key_generator import KeyGenerator
from .core.result import CacheResult
from .adapters.diskcache_adapter import DiskCacheAdapter


def get_cache_stats() -> dict:
    """获取默认缓存统计信息"""
    try:
        config = CacheConfig()
        adapter = DiskCacheAdapter(config)
        return adapter.stats()
    except Exception:
        return {'size': 0, 'volume': 0}


__all__ = [
    'CacheResult',
    'SmartCache',
    'smart_cache',
    'CacheConfig',
    'KeyGenerator',
    'DiskCacheAdapter',
    'get_cache_stats'
]