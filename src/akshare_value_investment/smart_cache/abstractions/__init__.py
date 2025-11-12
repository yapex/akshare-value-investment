"""
Smart Cache 接口抽象层
提供缓存系统的核心接口定义，支持依赖倒置原则
"""

from .icache_reader import ICacheReader
from .icache_writer import ICacheWriter
from .icache_monitor import ICacheMonitor, CacheStats, CachePerformance
from .icache_key_generator import ICacheKeyGenerator

__all__ = [
    'ICacheReader',
    'ICacheWriter',
    'ICacheMonitor',
    'ICacheKeyGenerator',
    'CacheStats',
    'CachePerformance'
]