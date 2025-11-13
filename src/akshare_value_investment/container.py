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
# 注意：AdapterManager已废弃，使用新的FinancialDataService
from .smart_cache import CacheConfig

# 导入新的Queryer架构
from .datasource.queryers.a_stock_queryers import (
    AStockIndicatorQueryer, AStockBalanceSheetQueryer,
    AStockIncomeStatementQueryer, AStockCashFlowQueryer
)
from .datasource.queryers.hk_stock_queryers import HKStockIndicatorQueryer, HKStockStatementQueryer
from .datasource.queryers.us_stock_queryers import USStockIndicatorQueryer, USStockStatementQueryer
from .services.financial_data_service import FinancialDataService
from .services.adapters.query_service_adapter import QueryServiceAdapter

# 导入业务层组件
from .business.processing.response_formatter import ResponseFormatter
from .business.processing.time_range_processor import TimeRangeProcessor
from .business.processing.data_processor import DataStructureProcessor

# 导入服务层组件
from .services.financial_query_service import FinancialIndicatorQueryService
from .services.field_discovery_service import FieldDiscoveryService

# 导入智能字段映射系统
from .business.mapping.unified_field_mapper import UnifiedFieldMapper
from .business.mapping.namespaced_config_loader import NamespacedMultiConfigLoader
from .business.mapping.interfaces import IConfigLoader, IFieldSearcher, IMarketInferrer
from .business.mapping.field_similarity_calculator import FieldSimilarityCalculator
from .business.mapping.candidate_ranker import CompositeRankingStrategy
from .business.mapping.field_searcher import DefaultFieldSearcher
from .business.mapping.market_inferrer import DefaultMarketInferrer

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
from .mcp.formatters import ResponseFormatter as MCPResponseFormatter
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

    # 新Queryer架构 - 遵循SOLID原则
    # A股Queryers
    a_stock_indicators = providers.Singleton(AStockIndicatorQueryer)
    a_stock_balance_sheet = providers.Singleton(AStockBalanceSheetQueryer)
    a_stock_income_statement = providers.Singleton(AStockIncomeStatementQueryer)
    a_stock_cash_flow = providers.Singleton(AStockCashFlowQueryer)

    # 港股Queryers
    hk_stock_indicators = providers.Singleton(HKStockIndicatorQueryer)
    hk_stock_statement = providers.Singleton(HKStockStatementQueryer)

    # 美股Queryers
    us_stock_indicators = providers.Singleton(USStockIndicatorQueryer)
    us_stock_statement = providers.Singleton(USStockStatementQueryer)

    # 财务数据聚合服务
    financial_data_service = providers.Singleton(
        FinancialDataService,
        a_stock_indicators=a_stock_indicators,
        a_stock_balance_sheet=a_stock_balance_sheet,
        a_stock_income_statement=a_stock_income_statement,
        a_stock_cash_flow=a_stock_cash_flow,
        hk_stock_indicators=hk_stock_indicators,
        hk_stock_statement=hk_stock_statement,
        us_stock_indicators=us_stock_indicators,
        us_stock_statement=us_stock_statement
    )

    # 查询服务适配器 - 确保向后兼容性
    query_service_adapter = providers.Singleton(
        QueryServiceAdapter,
        financial_service=financial_data_service
    )

    # 保留旧配置以兼容现有代码（已废弃标记）
    # adapter_manager = providers.Singleton(AdapterManager)  # 已废弃


  # 配置加载器 - 遵循依赖倒置原则
    config_loader = providers.Singleton(
        NamespacedMultiConfigLoader,
    )

    # 组件工厂 - 创建各个专门组件
    field_searcher = providers.Singleton(
        DefaultFieldSearcher,
        config_loader=config_loader
    )

    market_inferrer = providers.Singleton(
        DefaultMarketInferrer
    )

    # 统一字段映射器 - 最先进的SOLID架构实现
    field_mapper = providers.Singleton(
        UnifiedFieldMapper,
        config_loader=config_loader,
        field_searcher=field_searcher,
        market_inferrer=market_inferrer
    )
    response_formatter = providers.Singleton(ResponseFormatter)
    time_processor = providers.Singleton(TimeRangeProcessor)
    data_processor = providers.Singleton(DataStructureProcessor)
    field_discovery_service = providers.Singleton(
        FieldDiscoveryService,
        query_service=query_service_adapter  # 使用适配器确保接口兼容
    )

    # 核心财务指标查询服务 - 新架构
    financial_query_service = providers.Singleton(
        FinancialIndicatorQueryService,
        query_service=query_service_adapter,  # 使用适配器确保接口兼容
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
        MCPResponseFormatter,
        data_processor=mcp_smart_data_processor
    )

    # MCP服务器 - 使用依赖注入，避免直接依赖
    mcp_server = providers.Singleton(
        AkshareMCPServerV2,
        financial_service=financial_data_service,  # 修复：使用FinancialDataService而不是FinancialIndicatorQueryService
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
        MCP服务元组 (financial_data_service, field_discovery_service)
    """
    # 首先设置日志
    ProductionContainer._setup_logging()
    container = ProductionContainer()
    return (
        container.financial_data_service(),  # 修复：返回FinancialDataService
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