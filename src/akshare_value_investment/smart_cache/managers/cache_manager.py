"""
缓存管理器
遵循单一职责原则，专门负责缓存的核心逻辑管理
"""

import time
from typing import Any, Optional, Callable
from ..abstractions import (
    ICacheReader, ICacheWriter, ICacheMonitor, ICacheKeyGenerator
)
from ..core.result import CacheResult


class CacheManager:
    """
    缓存管理器 - 负责缓存操作的核心逻辑

    职责：
    - 协调读写操作
    - 缓存策略管理
    - 错误处理和恢复
    - 性能监控集成
    """

    def __init__(
        self,
        reader: ICacheReader,
        writer: ICacheWriter,
        monitor: ICacheMonitor,
        key_generator: ICacheKeyGenerator,
        default_ttl: Optional[int] = None
    ):
        self._reader = reader
        self._writer = writer
        self._monitor = monitor
        self._key_generator = key_generator
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值或None
        """
        start_time = time.perf_counter()

        try:
            value = self._reader.get(key)
            read_time = (time.perf_counter() - start_time) * 1000  # 毫秒

            if value is not None:
                self._monitor.record_hit(key, read_time)
                return value
            else:
                self._monitor.record_miss(key, read_time)
                return None

        except Exception:
            # 记录失败但不抛出异常
            self._monitor.record_miss(key, (time.perf_counter() - start_time) * 1000)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）

        Returns:
            设置成功返回True
        """
        start_time = time.perf_counter()

        try:
            ttl = ttl if ttl is not None else self._default_ttl
            success = self._writer.set(key, value, ttl)
            write_time = (time.perf_counter() - start_time) * 1000

            self._monitor.record_write(key, write_time)
            return success

        except Exception:
            return False

    def get_or_compute(
        self,
        key: str,
        compute_func: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> CacheResult:
        """
        获取缓存值或计算新值

        Args:
            key: 缓存键
            compute_func: 计算函数
            ttl: 过期时间（秒）

        Returns:
            缓存结果对象
        """
        # 尝试从缓存获取
        cached_value = self.get(key)
        if cached_value is not None:
            return CacheResult(
                data=cached_value,
                cache_hit=True,
                cache_key=key
            )

        # 缓存未命中，计算新值
        try:
            computed_value = compute_func()
            # 存入缓存
            self.set(key, computed_value, ttl)

            return CacheResult(
                data=computed_value,
                cache_hit=False,
                cache_key=key
            )

        except Exception as e:
            # 计算失败，重新尝试从缓存获取
            cached_value = self.get(key)
            if cached_value is not None:
                return CacheResult(
                    data=cached_value,
                    cache_hit=True,
                    cache_key=key
                )

            # 缓存也没有，抛出原异常
            raise e

    def generate_cache_key(
        self,
        func_name: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        prefix: str = "cache"
    ) -> str:
        """
        生成缓存键

        Args:
            func_name: 函数名称
            args: 位置参数
            kwargs: 关键字参数
            prefix: 键前缀

        Returns:
            缓存键
        """
        return self._key_generator.generate_key(func_name, args, kwargs, prefix)

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            删除成功返回True
        """
        try:
            return self._writer.delete(key)
        except Exception:
            return False

    def clear(self) -> bool:
        """
        清空所有缓存

        Returns:
            清空成功返回True
        """
        try:
            return self._writer.clear()
        except Exception:
            return False

    def get_stats(self) -> dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        stats = self._monitor.get_stats()
        performance = self._monitor.get_performance()

        return {
            'size': stats.size,
            'volume': stats.volume,
            'hit_rate': stats.hit_rate,
            'miss_rate': stats.miss_rate,
            'total_requests': stats.total_requests,
            'avg_read_time': performance.avg_read_time,
            'avg_write_time': performance.avg_write_time,
            'peak_memory_usage': performance.peak_memory_usage
        }

    def create_key_generator_with_prefix(self, prefix: str) -> ICacheKeyGenerator:
        """
        创建带有前缀的键生成器

        Args:
            prefix: 键前缀

        Returns:
            新的键生成器
        """
        return self._key_generator.with_prefix(prefix)