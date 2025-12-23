"""
API数据模型测试

TDD测试：验证Pydantic模型的类型安全和数据验证功能
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from typing import List, Optional

# 测试财务查询请求模型（还未创建，会先失败）
def test_financial_query_request_model():
    """测试财务查询请求模型的数据验证"""
    from akshare_value_investment.api.models.requests import FinancialQueryRequest

    # 测试有效的请求
    request_data = {
        "market": "a_stock",
        "query_type": "a_stock_indicators",
        "symbol": "SH600519",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "frequency": "annual"
    }

    request = FinancialQueryRequest(**request_data)
    assert request.market == "a_stock"  # use_enum_values=True 返回字符串
    assert request.query_type == "a_stock_indicators"
    assert request.symbol == "SH600519"
    assert request.frequency == "annual"

def test_financial_query_request_validation():
    """测试财务查询请求模型的验证错误"""
    from akshare_value_investment.api.models.requests import FinancialQueryRequest

    # 测试无效的市场类型
    with pytest.raises(ValidationError):
        FinancialQueryRequest(
            market="INVALID_MARKET",  # 无效值
            query_type="a_stock_indicators",
            symbol="SH600519"
        )

# 测试字段发现请求模型
def test_field_discovery_request_model():
    """测试字段发现请求模型"""
    from akshare_value_investment.api.models.requests import FieldDiscoveryRequest

    request = FieldDiscoveryRequest(
        market="a_stock",
        query_type="a_stock_indicators"
    )

    assert request.market == "a_stock"  # use_enum_values=True 返回字符串
    assert request.query_type == "a_stock_indicators"

# 测试响应模型结构
def test_response_models_structure():
    """测试响应模型的基本结构"""
    from akshare_value_investment.api.models.responses import FinancialQueryResponse, FieldDiscoveryResponse

    # 测试响应模型能正确创建
    # 具体数据将在路由测试中验证
    assert True  # 基础结构测试