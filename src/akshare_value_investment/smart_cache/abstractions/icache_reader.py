"""
缓存读取接口
遵循依赖倒置原则，定义缓存读取操作的抽象
"""

from typing import Any, Optional, Protocol
import asyncio


class ICacheReader(Protocol):
    """缓存读取接口"""

    async def get_async(self, key: str) -> Optional[Any]:
        """
        异步获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在时返回None
        """
        ...

    def get(self, key: str) -> Optional[Any]:
        """
        同步获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在时返回None
        """
        ...

    def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在

        Args:
            key: 缓存键

        Returns:
            存在返回True，否则返回False
        """
        ...

    def get_multiple(self, keys: list[str]) -> dict[str, Any]:
        """
        批量获取缓存值

        Args:
            keys: 缓存键列表

        Returns:
            键值对字典，不存在的键不会出现在结果中
        """
        ...