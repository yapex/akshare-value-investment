"""
依赖注入容器配置 - 重构版本

使用 dependency-injector 框架管理依赖关系，支持新的服务层架构。
"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from dependency_injector import containers, providers

from .core.models import MarketType
from .core.stock_identifier import StockIdentifier
from .datasource.adapters import AdapterManager
from .smart_cache import CacheConfig

# 导入业务层组件
from .business.processing.response_formatter import ResponseFormatter
from .business.processing.time_range_processor import TimeRangeProcessor
from .business.processing.data_processor import DataStructureProcessor

# 导入服务层组件
from .services.financial_query_service import FinancialIndicatorQueryService
from .services.field_discovery_service import FieldDiscoveryService

# 导入智能字段映射系统
from .business.mapping.field_mapper import FinancialFieldMapper

# 导入重构后的Smart Cache组件
from .smart_cache.factories.cache_factory import CacheFactory
from .smart_cache.factories.adapter_factory import CacheAdapterFactory
from .smart_cache.managers.cache_manager import CacheManager
from .smart_cache.managers.cache_metrics import CacheMetrics
from .smart_cache.core.enhanced_key_generator import EnhancedKeyGenerator
from .smart_cache.decorators import smart_cache_decorator
from .smart_cache.decorators.smart_cache_decorator import SmartCacheDecorator
from .smart_cache.adapters.combined_adapter import CombinedCacheAdapter

# 导入MCP相关组件
from .mcp.formatters import ResponseFormatter
from .mcp_server import AkshareMCPServerV2
from .mcp.data_processors import SmartQueryDataProcessor, QueryDataProcessor, FieldMatcher


class ProductionContainer(containers.DeclarativeContainer):
    """生产环境容器 - 重构版本"""

    # 配置
    config = providers.Configuration()

    # 日志配置
    logger = providers.Singleton(
        logging.getLogger,
        "investment.container"
    )

    @staticmethod
    def _setup_logging():
        """设置系统日志配置 - 单日轮换"""
        # 获取根logger，让所有子logger都能使用相同的handler
        root_logger = logging.getLogger("investment")

        if not root_logger.handlers:
            # 避免重复配置
            root_logger.setLevel(logging.INFO)

            # 创建日志目录
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            # 创建单日轮换文件处理器
            log_file = log_dir / "akshare_value_investment.log"
            file_handler = TimedRotatingFileHandler(
                log_file,
                when='midnight',  # 每天午夜轮换
                interval=1,       # 每天一次
                backupCount=30,   # 保留30天的日志
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)

            # 设置轮换文件名格式
            file_handler.suffix = "%Y-%m-%d"

            # 创建格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            # 添加处理器到根logger
            root_logger.addHandler(file_handler)
            root_logger.propagate = False

    def __init__(self):
        """初始化容器并设置日志"""
        super().__init__()
        self._setup_logging()

    # Smart Cache配置 - 重构版本
    cache_config = providers.Singleton(CacheConfig)

    # 重构后的Smart Cache组件 - 遵循SOLID原则
    # 1. 适配器层
    cache_adapter = providers.Factory(
        CacheAdapterFactory.create_adapter,
        config=cache_config
    )

    # 2. 监控组件
    cache_metrics = providers.Singleton(CacheMetrics)

    # 3. 键生成器
    cache_key_generator = providers.Singleton(
        EnhancedKeyGenerator,
        prefix="akshare_cache"
    )

    # 4. 缓存管理器 - 核心组件，依赖注入所有抽象接口
    cache_manager = providers.Singleton(
        CacheFactory.create_cache_manager,
        config=cache_config
    )

    # 5. 装饰器工厂 - 轻量级装饰器
    cache_decorator = providers.Factory(
        SmartCacheDecorator,
        cache_manager=cache_manager,
        prefix="akshare",
        ttl=cache_config.provided.default_ttl
    )

    # 核心组件
    stock_identifier = providers.Singleton(StockIdentifier)
    adapter_manager = providers.Singleton(AdapterManager)


  # 服务层组件 - 使用新的智能字段映射系统
    field_mapper = providers.Singleton(FinancialFieldMapper)  # 使用新的智能字段映射器
    response_formatter = providers.Singleton(ResponseFormatter)
    time_processor = providers.Singleton(TimeRangeProcessor)
    data_processor = providers.Singleton(DataStructureProcessor)
    field_discovery_service = providers.Singleton(
        FieldDiscoveryService,
        query_service=adapter_manager  # 使用适配器管理器作为查询服务
    )

    # 核心财务指标查询服务 - 新架构
    financial_query_service = providers.Singleton(
        FinancialIndicatorQueryService,
        query_service=adapter_manager,  # 适配器管理器实现IQueryService接口
        field_mapper=field_mapper,
        formatter=response_formatter,
        time_processor=time_processor,
        data_processor=data_processor
    )

    # 向后兼容的查询服务别名
    query_service = financial_query_service

      # MCP数据处理器 - 遵循单一职责原则
    mcp_field_matcher = providers.Singleton(FieldMatcher)
    mcp_data_processor = providers.Singleton(QueryDataProcessor)
    mcp_smart_data_processor = providers.Singleton(
        SmartQueryDataProcessor,
        data_processor=mcp_data_processor,
        field_matcher=mcp_field_matcher
    )

    # MCP格式化器 - 只负责格式化，依赖注入数据处理器
    mcp_response_formatter = providers.Singleton(
        ResponseFormatter,
        data_processor=mcp_smart_data_processor
    )

    # MCP服务器 - 使用依赖注入，避免直接依赖
    mcp_server = providers.Singleton(
        AkshareMCPServerV2,
        financial_service=financial_query_service,
        field_discovery_service=field_discovery_service,
        response_formatter=mcp_response_formatter
    )

    # 新增：缓存服务访问接口
    def get_cache_manager(self) -> CacheManager:
        """获取缓存管理器实例"""
        return self.cache_manager()

    def get_cache_decorator(self, prefix: str = "default", ttl: int = None) -> SmartCacheDecorator:
        """获取缓存装饰器实例"""
        return SmartCacheDecorator(
            cache_manager=self.cache_manager(),
            prefix=prefix,
            ttl=ttl
        )

    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        return self.cache_manager().get_stats()


def create_production_service() -> FinancialIndicatorQueryService:
    """
    创建生产环境的查询服务实例 - 重构版本

    Returns:
        配置好的查询服务实例
    """
    # 首先设置日志
    ProductionContainer._setup_logging()
    container = ProductionContainer()
    return container.financial_query_service()


def create_container() -> ProductionContainer:
    """
    创建完整的容器实例

    Returns:
        配置好的容器实例
    """
    # 首先设置日志
    ProductionContainer._setup_logging()
    return ProductionContainer()


def create_mcp_services():
    """
    创建MCP服务器所需的服务实例

    Returns:
        MCP服务元组 (financial_query_service, field_discovery_service)
    """
    # 首先设置日志
    ProductionContainer._setup_logging()
    container = ProductionContainer()
    return (
        container.financial_query_service(),
        container.field_discovery_service()
    )


def _create_cached_adapter_manager(cache_manager, stock_identifier):
    """创建带缓存装饰器的适配器管理器"""

    class CachedAdapterManager(AdapterManager):
        """带缓存装饰器的适配器管理器"""

        def __init__(self, stock_identifier=None):
            super().__init__(stock_identifier)
            self._cache_decorator = SmartCacheDecorator(
                cache_manager=cache_manager,
                prefix="adapter_query",
                ttl=3600  # 1小时缓存
            )

        def query(self, symbol: str, **kwargs):
            """重写query方法以应用缓存"""
            return self._cache_decorator(super().query)(symbol, **kwargs)

    return CachedAdapterManager(stock_identifier)