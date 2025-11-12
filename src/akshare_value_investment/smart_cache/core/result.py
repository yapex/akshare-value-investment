"""
Smart Cache 结果包装器
包装缓存结果，包含缓存命中状态信息
"""

import time
from typing import Any


class CacheResult:
    """缓存结果包装器"""

    def __init__(self, data: Any, cache_hit: bool, cache_key: str, timestamp: float = None):
        """
        初始化缓存结果

        Args:
            data: 原始数据
            cache_hit: 缓存命中状态
            cache_key: 缓存键
            timestamp: 时间戳（可选）
        """
        self.data = data
        self.cache_hit = cache_hit
        self.cache_key = cache_key
        self.timestamp = timestamp or time.time()

    def __repr__(self) -> str:
        return f"CacheResult(data={type(self.data).__name__}, cache_hit={self.cache_hit}, cache_key='{self.cache_key}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, CacheResult):
            return False
        return (
            self.data == other.data and
            self.cache_hit == other.cache_hit and
            self.cache_key == other.cache_key
        )

    def is_hit(self) -> bool:
        """检查是否缓存命中"""
        return self.cache_hit

    def get_data(self) -> Any:
        """获取原始数据"""
        return self.data

    def get_cache_key(self) -> str:
        """获取缓存键"""
        return self.cache_key

    def get_timestamp(self) -> float:
        """获取时间戳"""
        return self.timestamp