"""
Smart Cache 缓存键生成器
"""

import hashlib
import json
from typing import Any


class KeyGenerator:
    """缓存键生成器"""

    def __init__(self, prefix: str = "default"):
        self.prefix = prefix

    def generate(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        # 过滤self参数
        filtered_args = args[1:] if args and hasattr(args[0], '__class__') else args

        # 创建参数签名
        param_data = {
            'args': filtered_args,
            'kwargs': sorted(kwargs.items())
        }

        # 生成哈希
        param_hash = hashlib.md5(
            json.dumps(param_data, sort_keys=True, default=str).encode('utf-8')
        ).hexdigest()[:16]

        return f"{self.prefix}_{func_name}_{param_hash}"

    def with_prefix(self, prefix: str) -> 'KeyGenerator':
        """创建带指定前缀的新生成器"""
        return KeyGenerator(prefix)

    @staticmethod
    def generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
        """静态方法：生成缓存键"""
        # 过滤self参数
        filtered_args = args[1:] if args and hasattr(args[0], '__class__') else args

        # 创建参数签名
        param_data = {
            'args': filtered_args,
            'kwargs': sorted(kwargs.items())
        }

        # 生成哈希
        param_hash = hashlib.md5(
            json.dumps(param_data, sort_keys=True, default=str).encode('utf-8')
        ).hexdigest()[:16]

        return f"{prefix}_{func_name}_{param_hash}"