"""
缓存适配器工厂
创建不同类型的缓存适配器，遵循开闭原则
"""

from typing import Dict, Any, Type, Optional
from ..abstractions import ICacheReader, ICacheWriter
from ..adapters.diskcache_adapter import DiskCacheAdapter
from ..adapters.combined_adapter import CombinedCacheAdapter
from ..core.config import CacheConfig


class CacheAdapterFactory:
    """
    缓存适配器工厂

    职责：
    - 创建不同类型的适配器
    - 支持配置化适配器创建
    - 适配器类型注册和管理
    - 提供适配器选择策略
    """

    # 注册的适配器类型
    _adapter_registry: Dict[str, Type] = {
        'diskcache': DiskCacheAdapter,
    }

    @classmethod
    def create_adapter(
        self,
        adapter_type: str = 'diskcache',
        config: Optional[CacheConfig] = None
    ) -> CombinedCacheAdapter:
        """
        创建缓存适配器

        Args:
            adapter_type: 适配器类型
            config: 缓存配置

        Returns:
            组合适配器实例
        """
        if config is None:
            config = CacheConfig()

        if adapter_type not in self._adapter_registry:
            raise ValueError(f"Unknown adapter type: {adapter_type}")

        # 创建底层适配器
        adapter_class = self._adapter_registry[adapter_type]
        base_adapter = adapter_class(config)

        # 包装为组合适配器
        return CombinedCacheAdapter(base_adapter)

    @classmethod
    def register_adapter(
        cls,
        name: str,
        adapter_class: Type
    ) -> None:
        """
        注册新的适配器类型

        Args:
            name: 适配器名称
            adapter_class: 适配器类
        """
        cls._adapter_registry[name] = adapter_class

    @classmethod
    def get_available_types(cls) -> list[str]:
        """
        获取可用的适配器类型

        Returns:
            适配器类型列表
        """
        return list(cls._adapter_registry.keys())

    @classmethod
    def create_memory_adapter(cls, config: Optional[CacheConfig] = None) -> CombinedCacheAdapter:
        """
        创建内存适配器（用于测试）

        Args:
            config: 缓存配置

        Returns:
            内存适配器
        """
        if config is None:
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="smart_cache_memory_")
            config = CacheConfig()
            config.cache_dir = temp_dir

        return cls.create_adapter('diskcache', config)

    @classmethod
    def create_production_adapter(
        cls,
        cache_dir: str,
        max_size: Optional[int] = None,
        **kwargs
    ) -> CombinedCacheAdapter:
        """
        创建生产环境适配器

        Args:
            cache_dir: 缓存目录
            max_size: 最大大小
            **kwargs: 其他配置参数

        Returns:
            生产环境适配器
        """
        config = CacheConfig()
        config.cache_dir = cache_dir

        if max_size is not None:
            config.max_size = max_size

        # 应用其他配置
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return cls.create_adapter('diskcache', config)

    @classmethod
    def create_from_config(cls, config_dict: Dict[str, Any]) -> CombinedCacheAdapter:
        """
        从配置字典创建适配器

        Args:
            config_dict: 配置字典

        Returns:
            适配器实例
        """
        adapter_type = config_dict.get('type', 'diskcache')
        config = CacheConfig()

        # 应用配置
        for key, value in config_dict.items():
            if key != 'type' and hasattr(config, key):
                setattr(config, key, value)

        return cls.create_adapter(adapter_type, config)