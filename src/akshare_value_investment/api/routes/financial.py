"""
财务查询路由

提供财务数据查询相关的API端点，遵循SOLID原则和TDD开发流程。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
import pandas as pd

from ...core.models import MarketType
from ...business.financial_types import FinancialQueryType, Frequency
from ..dependencies import FinancialServiceDep
from ..models.requests import FinancialQueryRequest, FinancialStatementsAggregationRequest

router = APIRouter(prefix="/api/v1/financial", tags=["财务查询"])

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


@router.post("/indicators", response_model=Dict[str, Any])
async def query_financial_indicators(
    request: FinancialQueryRequest,
    financial_service: FinancialServiceDep = FinancialServiceDep
) -> Dict[str, Any]:
    """
    财务指标查询接口

    查询A股、港股、美股的财务指标数据。

    Args:
        request: 财务查询请求
        financial_service: 财务查询服务（依赖注入）

    Returns:
        Dict[str, Any]: 查询结果或错误信息

    Raises:
        HTTPException: 当参数无效或服务错误时

    Examples:
        ```python
        import requests

        response = requests.post(
            "http://localhost:8000/api/v1/financial/indicators",
            json={
                "market": "a_stock",
                "query_type": "a_stock_indicators",
                "symbol": "SH600519",
                "frequency": "annual",
                "limit": 5
            }
        )
        result = response.json()
        ```
    """
    try:
        # 转换枚举字符串为枚举对象
        market_enum = MarketType(request.market)
        query_type_enum = FinancialQueryType(request.query_type)
        frequency_enum = Frequency(request.frequency)

        # 验证是否为财务指标查询类型
        if query_type_enum not in INDICATORS_TYPES:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "type": "invalid_query_type",
                        "message": f"查询类型 {request.query_type} 不是财务指标查询类型",
                        "details": {
                            "provided_query_type": request.query_type,
                            "supported_indicators_types": [
                                "a_stock_indicators",
                                "hk_stock_indicators",
                                "us_stock_indicators"
                            ],
                            "note": "如需查询财务三表，请使用 /api/v1/financial/statements 接口"
                        }
                    }
                }
            )

        # 验证市场与查询类型的匹配
        if query_type_enum.get_market() != market_enum:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "type": "invalid_query_type",
                        "message": f"查询类型 {request.query_type} 与市场 {request.market} 不匹配",
                        "details": {
                            "provided_market": request.market,
                            "provided_query_type": request.query_type,
                        }
                    }
                }
            )

        # 调用财务查询服务
        service_response = financial_service.query(
            market=market_enum,
            query_type=query_type_enum,
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            frequency=frequency_enum
        )

        # 返回服务响应（已经是标准格式）
        return service_response

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"财务指标查询服务错误: {str(e)}"
        )


@router.post("/statements", response_model=Dict[str, Any])
async def query_financial_statements(
    request: FinancialStatementsAggregationRequest,
    financial_service: FinancialServiceDep = FinancialServiceDep
) -> Dict[str, Any]:
    """
    财务三表聚合查询接口（唯一的财务三表查询入口）

    返回包含资产负债表、利润表、现金流量表的字典结构。

    Args:
        request: 财务三表聚合查询请求
        financial_service: 财务查询服务（依赖注入）

    Returns:
        Dict[str, Any]: 包含三表数据的字典
            {
                "status": "success",
                "data": {
                    "balance_sheet": DataFrame数据,
                    "income_statement": DataFrame数据,
                    "cash_flow": DataFrame数据
                },
                "metadata": {
                    "symbol": "股票代码",
                    "query_type": "查询类型显示名称",
                    "frequency": "时间频率显示名称",
                    "record_counts": {
                        "balance_sheet": 记录数,
                        "income_statement": 记录数,
                        "cash_flow": 记录数
                    }
                }
            }

    Raises:
        HTTPException: 当参数无效或服务错误时

    Examples:
        ```python
        import requests

        response = requests.post(
            "http://localhost:8000/api/v1/financial/statements",
            json={
                "query_type": "a_financial_statements",
                "symbol": "SH600519",
                "frequency": "annual",
                "limit": 3
            }
        )
        result = response.json()
        ```

    Notes:
        - 这是财务三表查询的唯一接口
        - 支持A股、港股、美股三个市场
        - 返回三张表的完整数据
        - 可通过limit参数限制返回记录数
    """
    try:
        # 转换枚举字符串为枚举对象
        query_type_enum = FinancialQueryType(request.query_type)
        frequency_enum = Frequency(request.frequency)

        # 验证是否为聚合查询类型
        aggregation_types = {
            FinancialQueryType.A_FINANCIAL_STATEMENTS,
            FinancialQueryType.HK_FINANCIAL_STATEMENTS,
            FinancialQueryType.US_FINANCIAL_STATEMENTS,
        }

        if query_type_enum not in aggregation_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "type": "invalid_query_type",
                        "message": f"查询类型 {request.query_type} 不是财务三表聚合查询类型",
                        "details": {
                            "provided_query_type": request.query_type,
                            "supported_aggregation_types": [
                                "a_financial_statements",
                                "hk_financial_statements",
                                "us_financial_statements"
                            ]
                        }
                    }
                }
            )

        # 调用财务三表聚合查询服务
        result = financial_service.query_financial_statements(
            query_type=query_type_enum,
            symbol=request.symbol,
            frequency=frequency_enum,
            limit=request.limit
        )

        # 提取单位映射（如果存在，仅A股有）
        unit_map = result.pop("unit_map", {})

        # 构建响应数据
        # 将DataFrame转换为字典格式以便JSON序列化
        data_dict = {}
        record_counts = {}

        for statement_name, df in result.items():
            if df.empty:
                data_dict[statement_name] = {
                    "columns": [],
                    "data": [],
                    "record_count": 0
                }
                record_counts[statement_name] = 0
            else:
                data_dict[statement_name] = {
                    "columns": list(df.columns),
                    "data": df.to_dict(orient='records'),
                    "record_count": len(df)
                }
                record_counts[statement_name] = len(df)

        # 构建元数据
        metadata = {
            "symbol": request.symbol,
            "query_type": query_type_enum.get_display_name(),
            "frequency": frequency_enum.get_display_name(),
            "record_counts": record_counts,
            "limit": request.limit
        }

        # 如果有单位映射，添加到元数据中
        if unit_map:
            metadata["unit_info"] = unit_map
            metadata["default_unit"] = "亿元"

        # 构建响应
        return {
            "status": "success",
            "data": data_dict,
            "metadata": metadata
        }

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except ValueError as e:
        # 处理ValueError（如无效的查询类型）
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "type": "invalid_request",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"财务三表聚合查询服务错误: {str(e)}"
        )


@router.get("/indicators", response_model=Dict[str, Any])
async def get_financial_indicators(
    symbol: str = Query(..., description="股票代码"),
    market: str = Query("a_stock", description="市场类型"),
    frequency: str = Query("annual", description="数据频率"),
    financial_service: FinancialServiceDep = FinancialServiceDep
) -> Dict[str, Any]:
    """
    财务指标查询接口（GET方法，支持浏览器URL访问）

    通过URL查询参数查询财务指标数据。

    Args:
        symbol: 股票代码（如：SH600519, 00700, AAPL）
        market: 市场类型（a_stock, hk_stock, us_stock）
        frequency: 数据频率（annual, quarterly）
        financial_service: 财务查询服务（依赖注入）

    Returns:
        Dict[str, Any]: 查询结果或错误信息

    Examples:
        浏览器访问:
        http://localhost:8000/api/v1/financial/indicators?symbol=SH600519&market=a_stock&frequency=annual

        查询港股:
        http://localhost:8000/api/v1/financial/indicators?symbol=00700&market=hk_stock&frequency=annual

        查询美股:
        http://localhost:8000/api/v1/financial/indicators?symbol=AAPL&market=us_stock&frequency=annual
    """
    try:
        # 转换枚举字符串为枚举对象
        market_enum = MarketType(market)
        frequency_enum = Frequency(frequency)

        # 根据市场确定查询类型
        query_type_map = {
            MarketType.A_STOCK: FinancialQueryType.A_STOCK_INDICATORS,
            MarketType.HK_STOCK: FinancialQueryType.HK_STOCK_INDICATORS,
            MarketType.US_STOCK: FinancialQueryType.US_STOCK_INDICATORS,
        }

        query_type_enum = query_type_map.get(market_enum)
        if not query_type_enum:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的市场类型: {market}"
            )

        # 调用财务查询服务
        service_response = financial_service.query(
            market=market_enum,
            query_type=query_type_enum,
            symbol=symbol,
            fields=None,
            start_date=None,
            end_date=None,
            frequency=frequency_enum
        )

        # 返回服务响应（已经是标准格式）
        return service_response

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"财务指标查询服务错误: {str(e)}"
        )


@router.get("/statements", response_model=Dict[str, Any])
async def get_financial_statements(
    symbol: str = Query(..., description="股票代码"),
    query_type: str = Query(..., description="查询类型（a_financial_statements/hk_financial_statements/us_financial_statements）"),
    frequency: str = Query("annual", description="数据频率（annual, quarterly）"),
    limit: Optional[int] = Query(None, ge=1, description="限制返回记录数"),
    financial_service: FinancialServiceDep = FinancialServiceDep
) -> Dict[str, Any]:
    """
    财务三表聚合查询接口（GET方法，支持浏览器URL访问）

    通过URL查询参数查询财务三表数据。

    Args:
        symbol: 股票代码（如：SH600519, 00700, AAPL）
        query_type: 查询类型（a_financial_statements, hk_financial_statements, us_financial_statements）
        frequency: 数据频率（annual, quarterly）
        limit: 限制返回记录数
        financial_service: 财务查询服务（依赖注入）

    Returns:
        Dict[str, Any]: 包含三表数据的字典

    Examples:
        查询A股财务三表（最近10年）:
        http://localhost:8000/api/v1/financial/statements?symbol=SH600519&query_type=a_financial_statements&frequency=annual&limit=10

        查询港股财务三表:
        http://localhost:8000/api/v1/financial/statements?symbol=00700&query_type=hk_financial_statements&frequency=annual

        查询美股财务三表:
        http://localhost:8000/api/v1/financial/statements?symbol=AAPL&query_type=us_financial_statements&frequency=annual
    """
    try:
        # 转换枚举字符串为枚举对象
        query_type_enum = FinancialQueryType(query_type)
        frequency_enum = Frequency(frequency)

        # 验证是否为聚合查询类型
        if query_type_enum not in AGGREGATION_TYPES:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "type": "invalid_query_type",
                        "message": f"查询类型 {query_type} 不是财务三表聚合查询类型",
                        "details": {
                            "provided_query_type": query_type,
                            "supported_aggregation_types": [
                                "a_financial_statements",
                                "hk_financial_statements",
                                "us_financial_statements"
                            ]
                        }
                    }
                }
            )

        # 调用财务三表聚合查询服务
        result = financial_service.query_financial_statements(
            query_type=query_type_enum,
            symbol=symbol,
            frequency=frequency_enum,
            limit=limit
        )

        # 提取单位映射（如果存在，仅A股有）
        unit_map = result.pop("unit_map", {})

        # 构建响应数据
        data_dict = {}
        record_counts = {}

        for statement_name, df in result.items():
            if df.empty:
                data_dict[statement_name] = {
                    "columns": [],
                    "data": [],
                    "record_count": 0
                }
                record_counts[statement_name] = 0
            else:
                data_dict[statement_name] = {
                    "columns": list(df.columns),
                    "data": df.to_dict(orient='records'),
                    "record_count": len(df)
                }
                record_counts[statement_name] = len(df)

        # 构建元数据
        metadata = {
            "symbol": symbol,
            "query_type": query_type_enum.get_display_name(),
            "frequency": frequency_enum.get_display_name(),
            "record_counts": record_counts,
            "limit": limit
        }

        # 如果有单位映射，添加到元数据中
        if unit_map:
            metadata["unit_info"] = unit_map
            metadata["default_unit"] = "亿元"

        # 构建响应
        return {
            "status": "success",
            "data": data_dict,
            "metadata": metadata
        }

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except ValueError as e:
        # 处理ValueError（如无效的查询类型）
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "type": "invalid_request",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"财务三表聚合查询服务错误: {str(e)}"
        )