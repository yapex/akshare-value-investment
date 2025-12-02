"""
MCP Schema模块

定义MCP工具的请求和响应Schema，提供类型定义和验证规则。
"""

from .query_schemas import (
    FinancialQueryRequest,
    GetAvailableFieldsRequest,
    ValidateFieldsRequest,
    DiscoverAllMarketFieldsRequest
)

from .response_schemas import (
    FinancialQueryResponse,
    GetAvailableFieldsResponse,
    ValidateFieldsResponse,
    DiscoverAllMarketFieldsResponse
)

__all__ = [
    "FinancialQueryRequest",
    "GetAvailableFieldsRequest",
    "ValidateFieldsRequest",
    "DiscoverAllMarketFieldsRequest",
    "FinancialQueryResponse",
    "GetAvailableFieldsResponse",
    "ValidateFieldsResponse",
    "DiscoverAllMarketFieldsResponse"
]