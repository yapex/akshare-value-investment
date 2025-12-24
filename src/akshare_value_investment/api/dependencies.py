"""
FastAPI依赖注入

整合现有dependency-injector容器与FastAPI依赖系统。
严格遵循SOLID原则，保持适配器模式。
"""

from typing import Annotated
from fastapi import Depends

from ..container import create_container, ProductionContainer
from ..business.financial_query_service import FinancialQueryService
from ..business.field_discovery_service import FieldDiscoveryService


def get_container() -> ProductionContainer:
    """
    获取依赖注入容器实例

    Returns:
        ProductionContainer: 配置好的容器实例
    """
    return create_container()


def get_financial_service(
    container: Annotated[ProductionContainer, Depends(get_container)]
) -> FinancialQueryService:
    """
    获取财务查询服务实例

    Args:
        container: 依赖注入容器

    Returns:
        FinancialQueryService: 财务查询服务实例
    """
    return FinancialQueryService(container)


def get_field_service(
    container: Annotated[ProductionContainer, Depends(get_container)]
) -> FieldDiscoveryService:
    """
    获取字段发现服务实例

    Args:
        container: 依赖注入容器

    Returns:
        FieldDiscoveryService: 字段发现服务实例
    """
    return FieldDiscoveryService(container)


# 类型别名，便于在路由中使用
FinancialServiceDep = Annotated[FinancialQueryService, Depends(get_financial_service)]
FieldServiceDep = Annotated[FieldDiscoveryService, Depends(get_field_service)]
ContainerDep = Annotated[ProductionContainer, Depends(get_container)]
