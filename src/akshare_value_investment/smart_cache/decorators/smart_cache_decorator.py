"""
智能缓存装饰器（重构版）
遵循单一职责原则，轻量级装饰器实现
"""

import functools
from typing import Any, Callable, Optional, Union
from ..managers.cache_manager import CacheManager
from ..core.result import CacheResult


class SmartCacheDecorator:
    """
    智能缓存装饰器（重构版）

    职责：
    - 函数装饰逻辑
    - 参数解析和传递
    - 依赖注入管理器
    - 结果包装
    """

    def __init__(
        self,
        cache_manager: CacheManager,
        prefix: str = "cache",
        ttl: Optional[int] = None
    ):
        self._cache_manager = cache_manager
        self._prefix = prefix
        self._ttl = ttl

    def __call__(
        self,
        func_or_prefix: Union[Callable, str],
        ttl: Optional[int] = None
    ) -> Callable:
        """
        装饰器调用逻辑

        Args:
            func_or_prefix: 函数或前缀字符串
            ttl: 过期时间（秒）

        Returns:
            装饰后的函数
        """
        if callable(func_or_prefix):
            # 直接作为装饰器使用：@cache
            func = func_or_prefix
            return self._decorate_function(func, self._prefix, self._ttl)
        else:
            # 带参数使用：@cache("prefix") 或 @cache(ttl=3600)
            prefix = func_or_prefix
            actual_ttl = ttl if ttl is not None else self._ttl

            def decorator(func: Callable) -> Callable:
                return self._decorate_function(func, prefix, actual_ttl)

            return decorator

    def _decorate_function(
        self,
        func: Callable,
        prefix: str,
        ttl: Optional[int]
    ) -> Callable:
        """
        装饰函数

        Args:
            func: 待装饰的函数
            prefix: 缓存键前缀
            ttl: 过期时间（秒）

        Returns:
            装饰后的函数
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self._cache_manager.generate_cache_key(
                func.__name__,
                args,
                kwargs,
                prefix
            )

            # 定义计算函数
            def compute_func():
                return func(*args, **kwargs)

            # 使用缓存管理器获取或计算结果
            cache_result = self._cache_manager.get_or_compute(
                cache_key,
                compute_func,
                ttl
            )

            # 返回原始数据，保持向后兼容
            return cache_result.data

        return wrapper

    def invalidate(self, func: Callable, *args, **kwargs) -> bool:
        """
        使指定函数调用的缓存失效

        Args:
            func: 函数
            args: 参数
            kwargs: 关键字参数

        Returns:
            失功成功返回True
        """
        cache_key = self._cache_manager.generate_cache_key(
            func.__name__,
            args,
            kwargs,
            self._prefix
        )

        return self._cache_manager.delete(cache_key)

    def get_with_metadata(self, func: Callable, *args, **kwargs):
        """
        获取带有缓存元数据的结果

        Args:
            func: 函数
            args: 参数
            kwargs: 关键字参数

        Returns:
            CacheResult对象，包含缓存命中信息
        """
        cache_key = self._cache_manager.generate_cache_key(
            func.__name__,
            args,
            kwargs,
            self._prefix
        )

        cached_value = self._cache_manager.get(cache_key)
        if cached_value is not None:
            from ..core.result import CacheResult
            return CacheResult(
                data=cached_value,
                cache_hit=True,
                cache_key=cache_key
            )

        # 缓存未命中，计算新值
        computed_value = func(*args, **kwargs)
        self._cache_manager.set(cache_key, computed_value)

        from ..core.result import CacheResult
        return CacheResult(
            data=computed_value,
            cache_hit=False,
            cache_key=cache_key
        )


def smart_cache_decorator(
    cache_manager: CacheManager,
    prefix: str = "cache",
    ttl: Optional[int] = None
) -> SmartCacheDecorator:
    """
    创建智能缓存装饰器的工厂函数

    Args:
        cache_manager: 缓存管理器实例
        prefix: 默认缓存键前缀
        ttl: 默认过期时间（秒）

    Returns:
        装饰器实例
    """
    return SmartCacheDecorator(cache_manager, prefix, ttl)