"""
Smart Cache 配置管理
"""

import os
from typing import Optional


class CacheConfig:
    """缓存配置类"""

    def __init__(self):
        # 基础配置 - 使用相对路径，符合Unix隐藏目录惯例
        default_cache_dir = os.path.join(os.getcwd(), ".cache")
        self.cache_dir = default_cache_dir
        self.max_size = None  # 设为None避免diskcache问题
        self.eviction_policy = "least-recently-used"

        # 功能开关
        self.enable_metrics = True
        self.fallback_on_error = True
        self.compression_enabled = False

        # 默认TTL（秒）
        self.default_ttl = 3600  # 1小时

        # 加载环境变量配置
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置"""
        self.cache_dir = os.getenv("CACHE_DIR", self.cache_dir)

        # 只有当环境变量存在时才覆盖max_size
        cache_max_size_env = os.getenv("CACHE_MAX_SIZE")
        if cache_max_size_env is not None:
            self.max_size = int(cache_max_size_env)

        self.default_ttl = int(os.getenv("CACHE_TTL", str(self.default_ttl)))
        self.enable_metrics = os.getenv("CACHE_ENABLE_METRICS", "true").lower() == "true"
        self.fallback_on_error = os.getenv("CACHE_FALLBACK_ON_ERROR", "true").lower() == "true"