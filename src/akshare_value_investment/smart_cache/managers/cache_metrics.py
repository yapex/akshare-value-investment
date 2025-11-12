"""
缓存指标收集器
遵循单一职责原则，专门负责缓存性能指标和统计数据收集
"""

import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
from ..abstractions import ICacheMonitor, CacheStats, CachePerformance


class CacheMetrics(ICacheMonitor):
    """
    缓存指标收集器

    职责：
    - 性能指标收集
    - 命中率统计
    - 监控数据聚合
    - 实时性能追踪
    """

    def __init__(self):
        self._hits = 0
        self._misses = 0
        self._total_requests = 0
        self._read_times: List[float] = []
        self._write_times: List[float] = []
        self._key_access_times: Dict[str, datetime] = {}
        self._eviction_count = 0
        self._start_time = datetime.now()

    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0.0
        miss_rate = (self._misses / total) if total > 0 else 0.0

        last_access = None
        if self._key_access_times:
            last_access = max(self._key_access_times.values())

        return CacheStats(
            size=0,  # 需要从适配器获取
            volume=0,  # 需要从适配器获取
            hit_rate=hit_rate,
            miss_rate=miss_rate,
            total_requests=self._total_requests,
            last_access=last_access
        )

    def get_performance(self) -> CachePerformance:
        """获取缓存性能指标"""
        avg_read_time = sum(self._read_times) / len(self._read_times) if self._read_times else 0.0
        avg_write_time = sum(self._write_times) / len(self._write_times) if self._write_times else 0.0

        # 简化的内存使用计算（实际应该从系统获取）
        peak_memory_usage = len(self._key_access_times) * 100  # 估算值

        return CachePerformance(
            avg_read_time=avg_read_time,
            avg_write_time=avg_write_time,
            peak_memory_usage=peak_memory_usage,
            eviction_count=self._eviction_count
        )

    def record_hit(self, key: str, read_time: float) -> None:
        """记录缓存命中"""
        self._hits += 1
        self._total_requests += 1
        self._read_times.append(read_time)
        self._key_access_times[key] = datetime.now()

        # 保持最近1000次记录
        if len(self._read_times) > 1000:
            self._read_times = self._read_times[-1000:]

    def record_miss(self, key: str, read_time: float) -> None:
        """记录缓存未命中"""
        self._misses += 1
        self._total_requests += 1
        self._read_times.append(read_time)

        # 保持最近1000次记录
        if len(self._read_times) > 1000:
            self._read_times = self._read_times[-1000:]

    def record_write(self, key: str, write_time: float) -> None:
        """记录缓存写入"""
        self._write_times.append(write_time)
        self._key_access_times[key] = datetime.now()

        # 保持最近1000次记录
        if len(self._write_times) > 1000:
            self._write_times = self._write_times[-1000:]

    def record_eviction(self, key: str) -> None:
        """记录缓存淘汰"""
        self._eviction_count += 1
        self._key_access_times.pop(key, None)

    def reset_metrics(self) -> None:
        """重置监控指标"""
        self._hits = 0
        self._misses = 0
        self._total_requests = 0
        self._read_times.clear()
        self._write_times.clear()
        self._key_access_times.clear()
        self._eviction_count = 0
        self._start_time = datetime.now()

    def get_hot_keys(self, top_n: int = 10) -> List[tuple[str, int]]:
        """
        获取热点键（访问次数最多的键）

        Args:
            top_n: 返回前N个热点键

        Returns:
            (键, 访问次数) 的列表
        """
        # 简化实现，实际应该记录访问次数
        key_counts = defaultdict(int)
        for key in self._key_access_times:
            key_counts[key] += 1

        return sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_uptime(self) -> float:
        """
        获取运行时间（秒）

        Returns:
            运行时间
        """
        return (datetime.now() - self._start_time).total_seconds()

    def get_detailed_stats(self) -> Dict[str, any]:
        """
        获取详细的统计信息

        Returns:
            详细统计信息字典
        """
        stats = self.get_stats()
        performance = self.get_performance()

        return {
            'basic_stats': {
                'hits': self._hits,
                'misses': self._misses,
                'total_requests': self._total_requests,
                'hit_rate': stats.hit_rate,
                'miss_rate': stats.miss_rate
            },
            'performance': {
                'avg_read_time': performance.avg_read_time,
                'avg_write_time': performance.avg_write_time,
                'read_operations': len(self._read_times),
                'write_operations': len(self._write_times)
            },
            'memory': {
                'tracked_keys': len(self._key_access_times),
                'peak_memory_usage': performance.peak_memory_usage,
                'eviction_count': performance.eviction_count
            },
            'time': {
                'uptime': self.get_uptime(),
                'start_time': self._start_time.isoformat(),
                'last_access': stats.last_access.isoformat() if stats.last_access else None
            },
            'hot_keys': self.get_hot_keys()
        }