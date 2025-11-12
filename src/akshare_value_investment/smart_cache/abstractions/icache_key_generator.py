"""
缓存键生成器接口
遵循依赖倒置原则，定义缓存键生成策略的抽象
"""

from typing import Any, Protocol


class ICacheKeyGenerator(Protocol):
    """缓存键生成器接口"""

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
        ...

    def with_prefix(self, prefix: str) -> 'ICacheKeyGenerator':
        """
        创建带有指定前缀的键生成器

        Args:
            prefix: 键前缀

        Returns:
            新的键生成器实例
        """
        ...

    def validate_key(self, key: str) -> bool:
        """
        验证缓存键是否有效

        Args:
            key: 缓存键

        Returns:
            键有效返回True，否则返回False
        """
        ...

    def extract_metadata(self, key: str) -> dict[str, Any]:
        """
        从缓存键中提取元数据

        Args:
            key: 缓存键

        Returns:
            元数据字典
        """
        ...