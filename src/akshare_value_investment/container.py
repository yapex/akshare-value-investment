"""
依赖注入容器配置 - 简化版本

使用 dependency-injector 框架管理依赖关系 - 简化版本，不包含字段映射。
"""

from dependency_injector import containers, providers

from .models import MarketType
from .stock_identifier import StockIdentifier
from .adapters import AdapterManager
from .query_service import FinancialQueryService


class ProductionContainer(containers.DeclarativeContainer):
    """生产环境容器 - 简化版本"""

    # 配置
    config = providers.Configuration()

    # 核心组件
    stock_identifier = providers.Singleton(StockIdentifier)

    # 适配器管理器 - 简化版本，不需要字段映射器
    adapter_manager = providers.Singleton(AdapterManager)

    # 查询服务 - 简化版本，不需要字段映射器
    query_service = providers.Factory(
        FinancialQueryService,
        market_identifier=stock_identifier,
        adapter_manager=adapter_manager
    )


def create_production_service() -> FinancialQueryService:
    """
    创建生产环境的查询服务实例 - 简化版本

    Returns:
        配置好的查询服务实例
    """
    container = ProductionContainer()
    return container.query_service()


def create_container() -> ProductionContainer:
    """
    创建完整的容器实例

    Returns:
        配置好的容器实例
    """
    return ProductionContainer()