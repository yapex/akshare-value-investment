"""
Smart Cache 核心装饰器实现
基于原型验证，生产级缓存装饰器
"""

import logging
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
        self.logger = logging.getLogger("investment.cache")

    def _generate_friendly_params(self, args: tuple, kwargs: dict) -> str:
        """生成友好的参数描述用于日志"""
        params = []

        # 过滤self参数
        filtered_args = args[1:] if args and hasattr(args[0], '__class__') else args

        # 处理位置参数
        for i, arg in enumerate(filtered_args):
            if isinstance(arg, str):
                params.append(f'"{arg}"')
            else:
                params.append(str(arg))

        # 处理关键字参数
        for key, value in kwargs.items():
            if isinstance(value, str):
                params.append(f'{key}="{value}"')
            else:
                params.append(f'{key}={value}')

        return ', '.join(params)

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
                    return cached_data  # 返回原始数据，而不是CacheResult对象
            except Exception:
                # 缓存读取异常，降级处理
                if self.config.fallback_on_error:
                    result = func(*args, **kwargs)
                    return result  # 返回原始数据，而不是CacheResult对象
                else:
                    raise

            # 缓存未命中，执行原函数
            try:
                result = func(*args, **kwargs)

                # 尝试存入缓存并记录日志
                if cache_key is not None:
                    try:
                        self.adapter.set(cache_key, result, expire=self.ttl)
                        # 生成友好的参数描述用于日志
                        friendly_params = self._generate_friendly_params(args, kwargs)
                        self.logger.info(f"缓存未命中并写入: {func.__name__}({friendly_params})")
                    except Exception:
                        # 缓存写入异常，静默处理
                        pass

                return result  # 返回原始数据，而不是CacheResult对象

            except Exception as e:
                # 函数执行异常，降级策略
                if self.config.fallback_on_error:
                    result = func(*args, **kwargs)
                    return result  # 返回原始数据，而不是CacheResult对象
                else:
                    raise

        return wrapper

    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return self.adapter.stats()


def smart_cache(prefix: str = "default", ttl: Optional[int] = None, **kwargs):
    """智能缓存装饰器函数"""
    return SmartCache(prefix, ttl, **kwargs)