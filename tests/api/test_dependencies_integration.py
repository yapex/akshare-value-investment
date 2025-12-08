"""
依赖注入集成测试

TDD测试：验证FastAPI依赖注入与现有容器的完整集成
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# 测试依赖注入提供者（还未创建，会先失败）
def test_financial_service_dependency():
    """测试财务查询服务的依赖注入"""
    from akshare_value_investment.api.dependencies import get_financial_service, get_container

    # 先获取容器，再获取服务
    container = get_container()
    service = get_financial_service(container)

    assert service is not None
    assert hasattr(service, 'query')
    assert hasattr(service, 'get_available_fields')

def test_field_service_dependency():
    """测试字段发现服务的依赖注入"""
    from akshare_value_investment.api.dependencies import get_field_service, get_container

    # 先获取容器，再获取服务
    container = get_container()
    service = get_field_service(container)

    assert service is not None
    assert hasattr(service, 'discover_a_stock_indicator_fields')
    assert hasattr(service, 'discover_all_fields')

def test_container_dependency():
    """测试容器依赖"""
    from akshare_value_investment.api.dependencies import get_container

    # 测试能正确获取容器实例
    container = get_container()

    assert container is not None
    # 验证容器有必要的查询器
    assert hasattr(container, 'a_stock_indicators')
    assert hasattr(container, 'hk_stock_indicators')
    assert hasattr(container, 'us_stock_indicators')

def test_dependency_integration_with_routes():
    """测试依赖注入与路由的集成"""
    from akshare_value_investment.api.main import create_app

    app = create_app()
    client = TestClient(app)

    # 测试能通过依赖注入访问服务
    # 这个测试会在路由实现后完善
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"