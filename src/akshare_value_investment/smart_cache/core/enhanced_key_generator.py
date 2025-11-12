"""
增强的缓存键生成器
实现ICacheKeyGenerator接口，提供更强大的键生成功能
"""

import hashlib
import json
from typing import Any, Optional
from ..abstractions import ICacheKeyGenerator


class EnhancedKeyGenerator(ICacheKeyGenerator):
    """
    增强的缓存键生成器

    职责：
    - 生成唯一且稳定的缓存键
    - 支持前缀和命名空间
    - 防止键冲突
    - 提供键元数据提取
    """

    def __init__(self, prefix: str = "cache", hash_length: int = 16):
        self.prefix = prefix
        self.hash_length = hash_length
        self._separator = ":"

    def generate_key(
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
            唯一的缓存键
        """
        # 构建可序列化的参数数据
        serializable_data = self._make_serializable({
            'args': args,
            'kwargs': kwargs
        })

        # 生成参数的哈希值
        args_hash = self._generate_hash(serializable_data)

        # 组合键的各个部分
        key_parts = [prefix, func_name, args_hash]

        return self._separator.join(key_parts)

    def with_prefix(self, prefix: str) -> 'EnhancedKeyGenerator':
        """
        创建带有指定前缀的键生成器

        Args:
            prefix: 键前缀

        Returns:
            新的键生成器实例
        """
        return EnhancedKeyGenerator(prefix=prefix, hash_length=self.hash_length)

    def validate_key(self, key: str) -> bool:
        """
        验证缓存键是否有效

        Args:
            key: 缓存键

        Returns:
            键有效返回True，否则返回False
        """
        if not key or not isinstance(key, str):
            return False

        parts = key.split(self._separator)
        return len(parts) >= 3  # prefix:func_name:hash

    def extract_metadata(self, key: str) -> dict[str, Any]:
        """
        从缓存键中提取元数据

        Args:
            key: 缓存键

        Returns:
            元数据字典
        """
        if not self.validate_key(key):
            return {}

        parts = key.split(self._separator)
        return {
            'prefix': parts[0],
            'func_name': parts[1],
            'hash': parts[2],
            'is_valid': True
        }

    def _make_serializable(self, obj: Any) -> Any:
        """
        将对象转换为可序列化的格式

        Args:
            obj: 待转换的对象

        Returns:
            可序列化的对象
        """
        if hasattr(obj, '__dict__'):
            # 对于自定义对象，尝试序列化其属性
            return {
                '__class__': obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                **{k: self._make_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
            }
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return obj

    def _generate_hash(self, data: Any) -> str:
        """
        生成数据的哈希值

        Args:
            data: 待哈希的数据

        Returns:
            哈希字符串
        """
        # 序列化为JSON字符串
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))

        # 生成MD5哈希
        hash_obj = hashlib.md5(json_str.encode('utf-8'))

        # 返回指定长度的哈希值
        return hash_obj.hexdigest()[:self.hash_length]

    def generate_batch_key(
        self,
        operation_id: str,
        items: list[Any],
        prefix: str = "batch"
    ) -> str:
        """
        为批量操作生成缓存键

        Args:
            operation_id: 操作标识
            items: 批量项目列表
            prefix: 键前缀

        Returns:
            批量操作缓存键
        """
        # 生成项目的摘要哈希
        items_summary = self._generate_hash({
            'count': len(items),
            'types': [type(item).__name__ for item in items[:5]]  # 只取前5个类型
        })

        return f"{prefix}{self._separator}{operation_id}{self._separator}{items_summary}"

    def generate_time_based_key(
        self,
        base_key: str,
        time_window: str,  # 'hour', 'day', 'week', 'month'
        timestamp: Optional[float] = None
    ) -> str:
        """
        生成基于时间的缓存键

        Args:
            base_key: 基础键
            time_window: 时间窗口
            timestamp: 时间戳（可选）

        Returns:
            基于时间的缓存键
        """
        import time
        from datetime import datetime

        if timestamp is None:
            timestamp = time.time()

        dt = datetime.fromtimestamp(timestamp)

        if time_window == 'hour':
            time_key = dt.strftime('%Y%m%d%H')
        elif time_window == 'day':
            time_key = dt.strftime('%Y%m%d')
        elif time_window == 'week':
            week_num = dt.isocalendar()[1]
            time_key = f"{dt.strftime('%Y')}_W{week_num:02d}"
        elif time_window == 'month':
            time_key = dt.strftime('%Y%m')
        else:
            raise ValueError(f"Unsupported time window: {time_window}")

        return f"{base_key}{self._separator}{time_window}{self._separator}{time_key}"