"""
缓存写入接口
遵循依赖倒置原则，定义缓存写入操作的抽象
"""

from typing import Any, Optional, Protocol


class ICacheWriter(Protocol):
    """缓存写入接口"""

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None表示永不过期

        Returns:
            设置成功返回True，失败返回False
        """
        ...

    def set_multiple(self, items: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存值

        Args:
            items: 键值对字典
            ttl: 过期时间（秒），None表示永不过期

        Returns:
            全部设置成功返回True，部分失败返回False
        """
        ...

    def delete(self, key: str) -> bool:
        """
        删除缓存值

        Args:
            key: 缓存键

        Returns:
            删除成功返回True，失败返回False
        """
        ...

    def delete_multiple(self, keys: list[str]) -> bool:
        """
        批量删除缓存值

        Args:
            keys: 缓存键列表

        Returns:
            全部删除成功返回True，部分失败返回False
        """
        ...

    def clear(self) -> bool:
        """
        清空所有缓存

        Returns:
            清空成功返回True，失败返回False
        """
        ...