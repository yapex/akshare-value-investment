"""
Smart Cache 管理层
提供缓存系统的核心管理组件，遵循单一职责原则
"""

from .cache_manager import CacheManager
from .cache_metrics import CacheMetrics

__all__ = [
    'CacheManager',
    'CacheMetrics'
]