"""
Smart Cache 核心模块
"""

from .cache import SmartCache, smart_cache
from .result import CacheResult
from .config import CacheConfig
from .key_generator import KeyGenerator

__all__ = [
    'CacheResult',
    'SmartCache',
    'smart_cache',
    'CacheConfig',
    'KeyGenerator'
]