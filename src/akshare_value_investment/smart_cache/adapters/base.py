"""
缓存适配器基类
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class CacheAdapter(ABC):
    """缓存适配器基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清空缓存"""
        pass

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        pass