"""
Smart Cache 核心装饰器实现
基于原型验证，生产级缓存装饰器
"""

from functools import wraps
import time
from typing import Any, Callable, Optional

from .config import CacheConfig
from .key_generator import KeyGenerator
from .result import CacheResult
from ..adapters.diskcache_adapter import DiskCacheAdapter


class SmartCache:
    """智能缓存装饰器类"""

    def __init__(
        self,
        prefix: str = "default",
        ttl: Optional[int] = None,
        config: Optional[CacheConfig] = None
    ):
        self.prefix = prefix
        self.ttl = ttl
        self.config = config or CacheConfig()
        self.key_generator = KeyGenerator(prefix)
        self.adapter = DiskCacheAdapter(self.config)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = None
            cached_data = None

            # 尝试从缓存获取
            try:
                # 生成缓存键
                cache_key = self.key_generator.generate(func.__name__, args, kwargs)
                cached_data = self.adapter.get(cache_key)

                if cached_data is not None:
                    # 缓存命中
                    return CacheResult(cached_data, True, cache_key)
            except Exception:
                # 缓存读取异常，降级处理
                if self.config.fallback_on_error:
                    result = func(*args, **kwargs)
                    return CacheResult(result, False, None)
                else:
                    raise

            # 缓存未命中，执行原函数
            try:
                result = func(*args, **kwargs)

                # 尝试存入缓存
                if cache_key is not None:
                    try:
                        self.adapter.set(cache_key, result, expire=self.ttl)
                    except Exception:
                        # 缓存写入异常，忽略但不影响主流程
                        pass

                return CacheResult(result, False, cache_key)

            except Exception as e:
                # 函数执行异常，降级策略
                if self.config.fallback_on_error:
                    result = func(*args, **kwargs)
                    return CacheResult(result, False, None)
                else:
                    raise

        return wrapper

    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return self.adapter.stats()


def smart_cache(prefix: str = "default", ttl: Optional[int] = None, **kwargs):
    """智能缓存装饰器函数"""
    return SmartCache(prefix, ttl, **kwargs)