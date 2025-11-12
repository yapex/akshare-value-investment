"""
Smart Cache 适配器模块
"""

from .base import CacheAdapter
from .diskcache_adapter import DiskCacheAdapter

__all__ = [
    'CacheAdapter',
    'DiskCacheAdapter'
]