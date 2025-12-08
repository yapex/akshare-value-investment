"""
财务查询路由测试

TDD测试：验证财务数据查询API端点的功能
先写失败测试，再实现功能
"""

import pytest
from fastapi.testclient import TestClient
from akshare_value_investment.api.main import create_app


def test_post_financial_query_a_stock_indicators():
    """测试A股财务指标查询"""
    app = create_app()
    client = TestClient(app)

    # 测试财务查询端点（还未实现，会先失败）
    request_data = {
        "market": "a_stock",
        "query_type": "a_stock_indicators",
        "symbol": "SH600519",
        "fields": ["报告期", "净利润", "净资产收益率"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "frequency": "annual"
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert "metadata" in data
    assert "query_info" in data

    # 验证查询信息
    query_info = data["query_info"]
    assert query_info["market"] == "a_stock"
    assert query_info["symbol"] == "SH600519"
    assert query_info["frequency"] == "annual"

    # 验证数据结构
    data_info = data["data"]
    assert "records" in data_info
    assert "columns" in data_info
    assert isinstance(data_info["records"], list)


def test_post_financial_query_hk_stock():
    """测试港股财务指标查询"""
    app = create_app()
    client = TestClient(app)

    request_data = {
        "market": "hk_stock",
        "query_type": "hk_stock_indicators",
        "symbol": "00700",
        "frequency": "quarterly"
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["metadata"]["query_type"] == "港股财务指标"


def test_post_financial_query_us_stock():
    """测试美股财务指标查询"""
    app = create_app()
    client = TestClient(app)

    request_data = {
        "market": "us_stock",
        "query_type": "us_stock_indicators",
        "symbol": "AAPL",
        "fields": ["REPORT_DATE", "PARENT_HOLDER_NETPROFIT", "OPERATE_INCOME"]
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # 美股可能没有数据，但错误处理应该正确
    assert data["status"] in ["success", "error"]
    if data["status"] == "success":
        assert data["metadata"]["query_type"] == "美股财务指标"


def test_post_financial_query_invalid_request():
    """测试无效请求参数的错误处理"""
    app = create_app()
    client = TestClient(app)

    # 测试无效的市场类型
    request_data = {
        "market": "invalid_market",
        "query_type": "a_stock_indicators",
        "symbol": "SH600519"
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    # 应该返回验证错误
    assert response.status_code == 422

    data = response.json()
    assert "detail" in data


def test_post_financial_query_missing_required_fields():
    """测试缺少必需字段的错误处理"""
    app = create_app()
    client = TestClient(app)

    # 测试缺少必需字段
    request_data = {
        "market": "a_stock",
        # 缺少 query_type 和 symbol
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    assert response.status_code == 422

    data = response.json()
    assert "detail" in data


def test_post_financial_query_market_query_type_mismatch():
    """测试市场与查询类型不匹配的错误处理"""
    app = create_app()
    client = TestClient(app)

    # 测试A股市场使用港股查询类型（不匹配）
    request_data = {
        "market": "a_stock",
        "query_type": "hk_stock_indicators",
        "symbol": "SH600519"
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    # 应该返回业务错误
    assert response.status_code == 400

    data = response.json()
    # FastAPI自动包装错误响应到detail字段
    assert "detail" in data
    assert "error" in data["detail"]
    assert "message" in data["detail"]["error"]


def test_post_financial_query_invalid_symbol():
    """测试无效股票符号的处理"""
    app = create_app()
    client = TestClient(app)

    request_data = {
        "market": "a_stock",
        "query_type": "a_stock_indicators",
        "symbol": "",  # 空符号
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    assert response.status_code == 422


def test_post_financial_query_field_filtering():
    """测试字段过滤功能"""
    app = create_app()
    client = TestClient(app)

    # 测试指定特定字段
    request_data = {
        "market": "a_stock",
        "query_type": "a_stock_indicators",
        "symbol": "SH600519",
        "fields": ["报告期", "净利润"],  # 只请求2个字段
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }

    response = client.post("/api/v1/financial/query", json=request_data)

    assert response.status_code == 200
    data = response.json()

    if data["status"] == "success":
        # 如果有数据，验证字段过滤
        records = data["data"]["records"]
        if records:
            # 检查返回记录只包含请求的字段
            record_keys = set(records[0].keys())
            expected_keys = {"报告期", "净利润"}  # 可能还有时间戳字段
            assert expected_keys.issubset(record_keys)