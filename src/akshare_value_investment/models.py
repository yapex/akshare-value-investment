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
    A_STOCK = "a_stock"
    HK_STOCK = "hk_stock"
    US_STOCK = "us_stock"


class PeriodType(Enum):
    """报告期类型枚举"""
    ANNUAL = "annual"
    QUARTERLY = "quarterly"


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