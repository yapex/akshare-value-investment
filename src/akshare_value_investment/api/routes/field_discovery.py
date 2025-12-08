"""
字段发现路由

提供字段发现相关的API端点，遵循SOLID原则和TDD开发流程。
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
from datetime import datetime

from ...core.models import MarketType
from ...business.financial_types import FinancialQueryType
from ..dependencies import FieldServiceDep

router = APIRouter(prefix="/api/v1/financial/fields", tags=["字段发现"])


def _get_fields_from_service(field_service, query_type: FinancialQueryType) -> list:
    """
    适配器函数：根据查询类型调用相应的字段发现方法

    Args:
        field_service: 字段发现服务实例
        query_type: 查询类型枚举

    Returns:
        list: 可用字段列表
    """
    # 映射查询类型到具体的服务方法
    method_mapping = {
        # A股
        FinancialQueryType.A_STOCK_INDICATORS: field_service.discover_a_stock_indicator_fields,
        FinancialQueryType.A_STOCK_BALANCE_SHEET: field_service.discover_a_stock_balance_sheet_fields,
        FinancialQueryType.A_STOCK_INCOME_STATEMENT: field_service.discover_a_stock_income_statement_fields,
        FinancialQueryType.A_STOCK_CASH_FLOW: field_service.discover_a_stock_cash_flow_fields,

        # 港股
        FinancialQueryType.HK_STOCK_INDICATORS: field_service.discover_hk_stock_indicator_fields,
        FinancialQueryType.HK_STOCK_STATEMENTS: field_service.discover_hk_stock_statement_fields,

        # 美股
        FinancialQueryType.US_STOCK_INDICATORS: field_service.discover_us_stock_indicator_fields,
        FinancialQueryType.US_STOCK_BALANCE_SHEET: field_service.discover_us_stock_balance_sheet_fields,
        FinancialQueryType.US_STOCK_INCOME_STATEMENT: field_service.discover_us_stock_income_statement_fields,
        FinancialQueryType.US_STOCK_CASH_FLOW: field_service.discover_us_stock_cash_flow_fields,
    }

    discovery_method = method_mapping.get(query_type)
    if not discovery_method:
        raise ValueError(f"不支持的查询类型: {query_type}")

    return discovery_method()


@router.get("/{market}/{query_type}", response_model=Dict[str, Any])
async def get_available_fields(
    market: str = Path(..., description="市场类型"),
    query_type: str = Path(..., description="查询类型"),
    field_service: FieldServiceDep = FieldServiceDep
) -> Dict[str, Any]:
    """
    获取指定市场查询类型的可用字段列表

    Args:
        market: 市场类型 (a_stock, hk_stock, us_stock)
        query_type: 查询类型 (a_stock_indicators, hk_stock_indicators, etc.)
        field_service: 字段发现服务（依赖注入）

    Returns:
        Dict[str, Any]: 包含字段信息的响应

    Raises:
        HTTPException: 当参数无效或服务错误时
    """
    try:
        # 参数验证和转换
        try:
            market_enum = MarketType(market)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"无效的市场类型: {market}。支持的类型: {[m.value for m in MarketType]}"
            )

        try:
            query_type_enum = FinancialQueryType(query_type)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"无效的查询类型: {query_type}"
            )

        # 验证市场与查询类型的匹配
        if query_type_enum.get_market() != market_enum:
            raise HTTPException(
                status_code=400,
                detail=f"查询类型 {query_type} 与市场 {market} 不匹配"
            )

        # 调用适配器获取字段
        available_fields = _get_fields_from_service(field_service, query_type_enum)

        # 构建响应格式
        response_data = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "records": [],
                "columns": available_fields,
                "shape": (0, len(available_fields)),
                "empty": True
            },
            "metadata": {
                "market": market_enum.value,
                "query_type": query_type_enum.get_display_name(),
                "available_fields": available_fields,
                "field_count": len(available_fields)
            },
            "query_info": {
                "market": market_enum.value,
                "query_type": query_type_enum.value
            }
        }

        return response_data

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"字段发现服务错误: {str(e)}"
        )