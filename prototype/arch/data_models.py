#!/usr/bin/env python3
"""
核心数据模型

定义通用的数据结构和枚举类型。
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from decimal import Decimal


class MarketType(Enum):
    """市场类型枚举"""
    A_STOCK = "CN"
    HK_STOCK = "HK"
    US_STOCK = "US"


class PeriodType(Enum):
    """报告期类型枚举"""
    ANNUAL = "年度"
    SEMI_ANNUAL = "半年度"
    QUARTERLY = "季度"


@dataclass
class FinancialIndicator:
    """统一财务指标数据模型"""
    symbol: str                                    # 股票代码
    market: MarketType                             # 市场类型
    company_name: str                              # 公司名称
    report_date: datetime                          # 报告日期
    period_type: PeriodType                        # 报告期类型
    currency: str                                  # 货币单位
    indicators: Dict[str, Decimal]                 # 标准化财务指标字典
    raw_data: Optional[Dict[str, Any]] = None      # 原始数据（可选）


@dataclass
class QueryResult:
    """查询结果数据模型"""
    success: bool                                   # 查询是否成功
    data: list[FinancialIndicator]                 # 财务指标数据
    message: Optional[str] = None                  # 错误信息或提示
    total_records: int = 0                         # 记录总数


@dataclass
class MappingInfo:
    """字段映射信息"""
    unified_field: str                             # 统一字段名
    description: str                               # 字段描述
    a_stock_field: Optional[str] = None           # A股字段名
    hk_stock_field: Optional[str] = None          # 港股字段名
    us_stock_field: Optional[str] = None          # 美股字段名
    coverage_level: int = 1                        # 覆盖级别 (1=核心, 2=重要, 3=可选)
    available_markets: list = None                 # 可用市场列表

    def __post_init__(self):
        if self.available_markets is None:
            self.available_markets = []
            if self.a_stock_field:
                self.available_markets.append(MarketType.A_STOCK)
            if self.hk_stock_field:
                self.available_markets.append(MarketType.HK_STOCK)
            if self.us_stock_field:
                self.available_markets.append(MarketType.US_STOCK)