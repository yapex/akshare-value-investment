"""
财务查询路由

提供财务数据查询相关的API端点，遵循SOLID原则和TDD开发流程。
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ...core.models import MarketType
from ...business.financial_types import FinancialQueryType, Frequency
from ..dependencies import FinancialServiceDep
from ..models.requests import FinancialQueryRequest

router = APIRouter(prefix="/api/v1/financial", tags=["财务查询"])


@router.post("/query", response_model=Dict[str, Any])
async def query_financial_data(
    request: FinancialQueryRequest,
    financial_service: FinancialServiceDep = FinancialServiceDep
) -> Dict[str, Any]:
    """
    统一财务数据查询接口

    Args:
        request: 财务查询请求
        financial_service: 财务查询服务（依赖注入）

    Returns:
        Dict[str, Any]: 查询结果或错误信息

    Notes:
        - fields为None时，返回所有可用字段（MCP模式下可能消耗大量token）
        - start_date和end_date均为None时，返回所有时间范围内的数据
        - 在MCP场景下，建议根据需要指定字段以减少token消耗

    Raises:
        HTTPException: 当参数无效或服务错误时
    """
    try:
        # 转换枚举字符串为枚举对象
        market_enum = MarketType(request.market)
        query_type_enum = FinancialQueryType(request.query_type)
        frequency_enum = Frequency(request.frequency)

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
                            "expected_query_types": [
                                qt.value for qt in FinancialQueryType.get_query_types_by_market(market_enum)
                            ]
                        }
                    }
                }
            )

        # 调用财务查询服务
        service_response = financial_service.query(
            market=market_enum,
            query_type=query_type_enum,
            symbol=request.symbol,
            fields=request.fields,
            start_date=request.start_date,
            end_date=request.end_date,
            frequency=frequency_enum
        )

        # 返回服务响应（已经是MCP格式）
        return service_response

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 处理其他异常
        raise HTTPException(
            status_code=500,
            detail=f"财务查询服务错误: {str(e)}"
        )