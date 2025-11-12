"""
缓存工厂
创建和管理缓存系统组件，遵循依赖倒置原则
"""

from typing import Optional, Dict, Any
from ..abstractions import ICacheReader, ICacheWriter, ICacheMonitor
from ..managers.cache_manager import CacheManager
from ..managers.cache_metrics import CacheMetrics
from ..core.enhanced_key_generator import EnhancedKeyGenerator
from ..adapters.combined_adapter import CombinedCacheAdapter
from ..adapters.diskcache_adapter import DiskCacheAdapter
from ..core.config import CacheConfig


class CacheFactory:
    """
    缓存工厂

    职责：
    - 创建缓存组件实例
    - 管理组件依赖关系
    - 提供配置化创建方式
    - 组件生命周期管理
    """

    @staticmethod
    def create_cache_manager(
        config: Optional[CacheConfig] = None,
        custom_adapter: Optional[CombinedCacheAdapter] = None
    ) -> CacheManager:
        """
        创建缓存管理器

        Args:
            config: 缓存配置
            custom_adapter: 自定义适配器

        Returns:
            配置好的缓存管理器
        """
        if config is None:
            config = CacheConfig()

        # 创建适配器
        if custom_adapter is None:
            diskcache_adapter = DiskCacheAdapter(config)
            adapter = CombinedCacheAdapter(diskcache_adapter)
        else:
            adapter = custom_adapter

        # 创建组件
        reader: ICacheReader = adapter
        writer: ICacheWriter = adapter
        monitor: ICacheMonitor = CacheMetrics()
        key_generator = EnhancedKeyGenerator()

        return CacheManager(
            reader=reader,
            writer=writer,
            monitor=monitor,
            key_generator=key_generator,
            default_ttl=config.default_ttl
        )

    @staticmethod
    def create_with_custom_components(
        reader: ICacheReader,
        writer: ICacheWriter,
        monitor: Optional[ICacheMonitor] = None,
        key_generator: Optional[EnhancedKeyGenerator] = None,
        default_ttl: Optional[int] = None
    ) -> CacheManager:
        """
        使用自定义组件创建缓存管理器

        Args:
            reader: 缓存读取器
            writer: 缓存写入器
            monitor: 缓存监控器
            key_generator: 键生成器
            default_ttl: 默认过期时间

        Returns:
            配置好的缓存管理器
        """
        if monitor is None:
            monitor = CacheMetrics()

        if key_generator is None:
            key_generator = EnhancedKeyGenerator()

        return CacheManager(
            reader=reader,
            writer=writer,
            monitor=monitor,
            key_generator=key_generator,
            default_ttl=default_ttl
        )

    @staticmethod
    def create_production_cache(
        cache_dir: Optional[str] = None,
        max_size: Optional[int] = None,
        default_ttl: Optional[int] = None
    ) -> CacheManager:
        """
        创建生产环境缓存

        Args:
            cache_dir: 缓存目录
            max_size: 最大大小
            default_ttl: 默认过期时间

        Returns:
            生产环境缓存管理器
        """
        config = CacheConfig()

        if cache_dir is not None:
            config.cache_dir = cache_dir
        if max_size is not None:
            config.max_size = max_size
        if default_ttl is not None:
            config.default_ttl = default_ttl

        return CacheFactory.create_cache_manager(config)

    @staticmethod
    def create_memory_cache(default_ttl: Optional[int] = None) -> CacheManager:
        """
        创建内存缓存（用于测试）

        Args:
            default_ttl: 默认过期时间

        Returns:
            内存缓存管理器
        """
        # 这里可以实现一个内存适配器
        # 暂时使用磁盘缓存，但设置为临时目录
        import tempfile
        import os

        temp_dir = tempfile.mkdtemp(prefix="smart_cache_test_")
        config = CacheConfig()
        config.cache_dir = temp_dir
        config.default_ttl = default_ttl

        manager = CacheFactory.create_cache_manager(config)

        # 添加清理方法
        def cleanup():
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        manager._cleanup = cleanup
        return manager

    @staticmethod
    def create_from_dict(config_dict: Dict[str, Any]) -> CacheManager:
        """
        从配置字典创建缓存管理器

        Args:
            config_dict: 配置字典

        Returns:
            配置好的缓存管理器
        """
        config = CacheConfig()

        # 应用配置
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return CacheFactory.create_cache_manager(config)