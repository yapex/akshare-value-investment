"""
废弃警告工具模块

用于标记和警告已废弃的类和方法。
"""

import warnings
from typing import Any


def deprecated(reason: str, replacement: str = None):
    """
    废弃装饰器

    Args:
        reason: 废弃原因
        replacement: 推荐的替代方案
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            message = f"{func.__name__} is deprecated: {reason}"
            if replacement:
                message += f". Use {replacement} instead."
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated_class(reason: str, replacement: str = None):
    """
    废弃类装饰器

    Args:
        reason: 废弃原因
        replacement: 推荐的替代类
    """
    def decorator(cls):
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            message = f"{cls.__name__} is deprecated: {reason}"
            if replacement:
                message += f". Use {replacement} instead."
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return decorator