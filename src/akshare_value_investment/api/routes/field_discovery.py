"""
字段发现路由

提供字段发现相关的API端点，遵循SOLID原则和TDD开发流程。
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
from datetime import datetime

from ...core.models import MarketType
from ...business.financial_types import FinancialQueryType, Frequency
from ..dependencies import FieldServiceDep, FinancialServiceDep

router = APIRouter(prefix="/api/v1/financial/fields", tags=["字段发现"])

# 财务指标查询类型
INDICATORS_TYPES = {
    FinancialQueryType.A_STOCK_INDICATORS,
    FinancialQueryType.HK_STOCK_INDICATORS,
    FinancialQueryType.US_STOCK_INDICATORS,
}

# 财务三表聚合查询类型
AGGREGATION_TYPES = {
    FinancialQueryType.A_FINANCIAL_STATEMENTS,
    FinancialQueryType.HK_FINANCIAL_STATEMENTS,
    FinancialQueryType.US_FINANCIAL_STATEMENTS,
}


def _get_indicator_fields(field_service, query_type: FinancialQueryType) -> list:
    """
    获取财务指标字段列表

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
        # 港股
        FinancialQueryType.HK_STOCK_INDICATORS: field_service.discover_hk_stock_indicator_fields,
        # 美股
        FinancialQueryType.US_STOCK_INDICATORS: field_service.discover_us_stock_indicator_fields,
    }

    discovery_method = method_mapping.get(query_type)
    if not discovery_method:
        raise ValueError(f"不支持的查询类型: {query_type}")

    return discovery_method()


def _get_statements_fields(financial_service, query_type: FinancialQueryType, symbol: str = "SH600519") -> Dict[str, list]:
    """
    通过聚合查询获取财务三表字段列表

    Args:
        financial_service: 财务查询服务实例
        query_type: 财务三表聚合查询类型
        symbol: 股票代码（用于查询，默认使用SH600519）

    Returns:
        Dict[str, list]: 三张表字段列表 {'balance_sheet': [...], 'income_statement': [...], 'cash_flow': [...]}
    """
    # 调用聚合查询服务，limit=1仅获取结构信息
    result = financial_service.query_financial_statements(
        query_type=query_type,
        symbol=symbol,
        frequency=Frequency.ANNUAL,
        limit=1
    )

    # 提取字段信息
    fields_dict = {}
    for statement_name, df in result.items():
        if not df.empty:
            fields_dict[statement_name] = list(df.columns)
        else:
            fields_dict[statement_name] = []

    return fields_dict


@router.get("/{market}/{query_type}", response_model=Dict[str, Any])
async def get_available_fields(
    market: str = Path(..., description="市场类型"),
    query_type: str = Path(..., description="查询类型"),
    field_service: FieldServiceDep = FieldServiceDep,
    financial_service: FinancialServiceDep = FinancialServiceDep
) -> Dict[str, Any]:
    """
    获取指定市场查询类型的可用字段列表

    支持财务指标和财务三表聚合查询的字段发现。

    Args:
        market: 市场类型 (a_stock, hk_stock, us_stock)
        query_type: 查询类型（财务指标或财务三表聚合类型）
        field_service: 字段发现服务（依赖注入）
        financial_service: 财务查询服务（依赖注入，用于财务三表）

    Returns:
        Dict[str, Any]: 包含字段信息的响应

    Raises:
        HTTPException: 当参数无效或服务错误时

    Examples:
        财务指标字段发现:
        GET /api/v1/financial/fields/a_stock/a_stock_indicators

        财务三表字段发现:
        GET /api/v1/financial/fields/a_stock/a_financial_statements
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

        # 根据查询类型获取字段
        if query_type_enum in INDICATORS_TYPES:
            # 财务指标字段发现
            available_fields = _get_indicator_fields(field_service, query_type_enum)

            # 构建财务指标响应格式
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

        elif query_type_enum in AGGREGATION_TYPES:
            # 财务三表字段发现 - 使用聚合查询
            # 根据市场选择代表性股票代码
            sample_symbols = {
                MarketType.A_STOCK: "SH600519",
                MarketType.HK_STOCK: "00700",
                MarketType.US_STOCK: "AAPL"
            }
            sample_symbol = sample_symbols[market_enum]

            # 调用聚合查询获取字段
            fields_dict = _get_statements_fields(financial_service, query_type_enum, sample_symbol)

            # 构建财务三表响应格式
            response_data = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "balance_sheet": {
                        "columns": fields_dict.get("balance_sheet", []),
                        "field_count": len(fields_dict.get("balance_sheet", []))
                    },
                    "income_statement": {
                        "columns": fields_dict.get("income_statement", []),
                        "field_count": len(fields_dict.get("income_statement", []))
                    },
                    "cash_flow": {
                        "columns": fields_dict.get("cash_flow", []),
                        "field_count": len(fields_dict.get("cash_flow", []))
                    }
                },
                "metadata": {
                    "market": market_enum.value,
                    "query_type": query_type_enum.get_display_name(),
                    "sample_symbol": sample_symbol,
                    "note": "字段列表通过查询样本股票数据获得"
                },
                "query_info": {
                    "market": market_enum.value,
                    "query_type": query_type_enum.value
                }
            }

        else:
            # 不支持的查询类型
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "type": "invalid_query_type",
                        "message": f"不支持的查询类型: {query_type}",
                        "details": {
                            "provided_query_type": query_type,
                            "supported_types": {
                                "indicators": ["a_stock_indicators", "hk_stock_indicators", "us_stock_indicators"],
                                "statements": ["a_financial_statements", "hk_financial_statements", "us_financial_statements"]
                            }
                        }
                    }
                }
            )

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