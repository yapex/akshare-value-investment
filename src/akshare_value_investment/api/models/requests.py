"""
API请求模型

定义FastAPI的请求Pydantic模型，确保类型安全和数据验证。
严格遵循SOLID原则，每个模型单一职责。
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from ...core.models import MarketType
from ...business.financial_types import FinancialQueryType, Frequency


class FinancialQueryRequest(BaseModel):
    """
    财务查询请求模型

    封装财务数据查询的所有参数，确保类型安全和数据验证。
    """
    market: MarketType = Field(..., description="市场类型")
    query_type: FinancialQueryType = Field(..., description="查询类型")
    symbol: str = Field(..., min_length=1, description="股票代码")
    start_date: Optional[str] = Field(None, description="开始日期，YYYY-MM-DD格式，为None时不限制开始时间")
    end_date: Optional[str] = Field(None, description="结束日期，YYYY-MM-DD格式，为None时不限制结束时间")
    frequency: Frequency = Field(Frequency.ANNUAL, description="时间频率")

    model_config = ConfigDict(
        use_enum_values=True
    )


class FinancialStatementsAggregationRequest(BaseModel):
    """
    财务三表聚合查询请求模型

    专门用于财务三表聚合查询，支持limit参数。
    """
    query_type: FinancialQueryType = Field(
        ...,
        description="聚合查询类型（a_financial_statements/hk_financial_statements/us_financial_statements）"
    )
    symbol: str = Field(..., min_length=1, description="股票代码")
    frequency: Frequency = Field(Frequency.ANNUAL, description="时间频率（年度数据/报告期数据）")
    limit: Optional[int] = Field(None, ge=1, description="限制每个DataFrame返回的记录数")

    model_config = ConfigDict(
        use_enum_values=True
    )


class FieldDiscoveryRequest(BaseModel):
    """
    字段发现请求模型

    用于获取指定查询类型的可用字段列表。
    """
    market: MarketType = Field(..., description="市场类型")
    query_type: FinancialQueryType = Field(..., description="查询类型")

    model_config = ConfigDict(
        use_enum_values=True
    )
