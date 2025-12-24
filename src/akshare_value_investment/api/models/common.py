"""
通用API模型

定义可在多个响应中复用的通用模型。
遵循DRY原则，避免重复定义。
"""

from typing import List
from pydantic import BaseModel, Field


class MarketInfo(BaseModel):
    """市场信息模型"""
    value: str = Field(..., description="市场枚举值")
    name: str = Field(..., description="市场显示名称")
    query_types: List[str] = Field(..., description="支持的查询类型列表")


class QueryTypeInfo(BaseModel):
    """查询类型信息模型"""
    value: str = Field(..., description="查询类型枚举值")
    display_name: str = Field(..., description="查询类型显示名称")
    market: str = Field(..., description="所属市场")
