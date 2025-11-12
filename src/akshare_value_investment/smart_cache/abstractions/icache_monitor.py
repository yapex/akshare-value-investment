"""
缓存监控接口
遵循依赖倒置原则，定义缓存监控操作的抽象
"""

from typing import Dict, Any, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CacheStats:
    """缓存统计数据"""
    size: int = 0
    volume: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    total_requests: int = 0
    last_access: Optional[datetime] = None


@dataclass
class CachePerformance:
    """缓存性能指标"""
    avg_read_time: float = 0.0
    avg_write_time: float = 0.0
    peak_memory_usage: int = 0
    eviction_count: int = 0


class ICacheMonitor(Protocol):
    """缓存监控接口"""

    def get_stats(self) -> CacheStats:
        """
        获取缓存统计信息

        Returns:
            缓存统计数据
        """
        ...

    def get_performance(self) -> CachePerformance:
        """
        获取缓存性能指标

        Returns:
            缓存性能数据
        """
        ...

    def record_hit(self, key: str, read_time: float) -> None:
        """
        记录缓存命中

        Args:
            key: 缓存键
            read_time: 读取时间（毫秒）
        """
        ...

    def record_miss(self, key: str, read_time: float) -> None:
        """
        记录缓存未命中

        Args:
            key: 缓存键
            read_time: 读取时间（毫秒）
        """
        ...

    def record_write(self, key: str, write_time: float) -> None:
        """
        记录缓存写入

        Args:
            key: 缓存键
            write_time: 写入时间（毫秒）
        """
        ...

    def reset_metrics(self) -> None:
        """重置监控指标"""
        ...