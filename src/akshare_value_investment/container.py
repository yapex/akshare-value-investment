"""
依赖注入容器配置 - 重构版本

使用 dependency-injector 框架管理依赖关系，支持新的服务层架构。
"""

from dependency_injector import containers, providers

from .core.models import MarketType
from .core.stock_identifier import StockIdentifier
from .datasource.adapters import AdapterManager

# 导入业务层组件
from .business.processing.response_formatter import ResponseFormatter
from .business.processing.time_range_processor import TimeRangeProcessor
from .business.processing.data_processor import DataStructureProcessor

# 导入服务层组件
from .services.financial_query_service import FinancialIndicatorQueryService
from .services.field_discovery_service import FieldDiscoveryService

# 导入智能字段映射系统
from .business.mapping.field_mapper import FinancialFieldMapper


class ProductionContainer(containers.DeclarativeContainer):
    """生产环境容器 - 重构版本"""

    # 配置
    config = providers.Configuration()

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


def create_production_service() -> FinancialIndicatorQueryService:
    """
    创建生产环境的查询服务实例 - 重构版本

    Returns:
        配置好的查询服务实例
    """
    container = ProductionContainer()
    return container.financial_query_service()


def create_container() -> ProductionContainer:
    """
    创建完整的容器实例

    Returns:
        配置好的容器实例
    """
    return ProductionContainer()


def create_mcp_services():
    """
    创建MCP服务器所需的服务实例

    Returns:
        MCP服务元组 (financial_query_service, field_discovery_service)
    """
    container = ProductionContainer()
    return (
        container.financial_query_service(),
        container.field_discovery_service()
    )