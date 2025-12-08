"""
字段发现路由测试

TDD测试：验证字段发现API端点的功能
先写失败测试，再实现功能
"""

import pytest
from fastapi.testclient import TestClient
from akshare_value_investment.api.main import create_app


def test_get_available_fields_a_stock():
    """测试获取A股财务指标可用字段"""
    app = create_app()
    client = TestClient(app)

    # 测试字段发现端点（还未实现，会先失败）
    response = client.get("/api/v1/financial/fields/a_stock/a_stock_indicators")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "metadata" in data
    assert "query_info" in data

    # 验证元数据
    metadata = data["metadata"]
    assert metadata["market"] == "a_stock"
    assert "field_count" in metadata
    assert isinstance(metadata["field_count"], int)

    # 验证数据结构
    data_info = data["data"]
    assert "columns" in data_info
    assert "fields" in data_info or "available_fields" in metadata


def test_get_available_fields_hk_stock():
    """测试获取港股财务指标可用字段"""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/financial/fields/hk_stock/hk_stock_indicators")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["metadata"]["market"] == "hk_stock"


def test_get_available_fields_us_stock():
    """测试获取美股财务指标可用字段"""
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/financial/fields/us_stock/us_stock_indicators")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["metadata"]["market"] == "us_stock"


def test_get_available_fields_invalid_market():
    """测试无效市场类型的错误处理"""
    app = create_app()
    client = TestClient(app)

    # 测试无效的市场类型
    response = client.get("/api/v1/financial/fields/invalid_market/a_stock_indicators")

    assert response.status_code == 422  # 验证错误

    data = response.json()
    assert "detail" in data


def test_get_available_fields_invalid_query_type():
    """测试无效查询类型的错误处理"""
    app = create_app()
    client = TestClient(app)

    # 测试无效的查询类型
    response = client.get("/api/v1/financial/fields/a_stock/invalid_query_type")

    assert response.status_code == 422  # 验证错误


def test_get_available_fields_market_query_type_mismatch():
    """测试市场与查询类型不匹配的错误处理"""
    app = create_app()
    client = TestClient(app)

    # 测试A股市场使用港股查询类型（不匹配）
    response = client.get("/api/v1/financial/fields/a_stock/hk_stock_indicators")

    # 这应该返回错误，因为查询类型与市场不匹配
    assert response.status_code in [400, 422]  # 业务错误或验证错误

    data = response.json()
    assert "error" in data or "detail" in data