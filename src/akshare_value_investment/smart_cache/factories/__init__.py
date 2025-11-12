"""
Smart Cache 工厂层
提供对象创建和配置的工厂组件，遵循依赖倒置原则
"""

from .cache_factory import CacheFactory
from .adapter_factory import CacheAdapterFactory

__all__ = [
    'CacheFactory',
    'CacheAdapterFactory'
]