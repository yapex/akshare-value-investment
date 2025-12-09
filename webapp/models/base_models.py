"""
基础数据模型定义
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class MarketType(Enum):
    """市场类型枚举"""
    A_STOCK = "a_stock"
    HK_STOCK = "hk_stock"
    US_STOCK = "us_stock"


class ChecklistCategory(Enum):
    """检查清单分类"""
    ASSETS = "资产类项目"
    LIABILITIES = "负债与权益类项目"
    OVERALL = "整体分析指标"
    INCOME = "利润表及相关附注"
    CASHFLOW = "现金流量表及相关附注"


@dataclass
class SubQuestion:
    """子问题/追问数据结构"""
    question: str            # 追问内容
    passed: bool             # 通过/失败
    calculation: str         # 计算公式
    result: float            # 计算结果
    threshold: float         # 判断阈值
    details: Dict            # 详细数据
    report_guide: str        # 财报指引


@dataclass
class ChecklistItem:
    """检查清单项目数据结构"""
    question_id: str          # "1.1.1"
    question: str            # "货币资金是否安全？"
    category: ChecklistCategory  # 检查分类
    passed: bool             # True/False
    summary: str             # 检查总结
    calculation_details: Dict # 计算详细数据
    sub_questions: List[SubQuestion]  # 追问列表


@dataclass
class FinancialData:
    """财务数据容器"""
    balance_sheet: Dict       # 资产负债表数据
    income_statement: Dict    # 利润表数据
    cash_flow: Dict          # 现金流量表数据

    @property
    def is_empty(self) -> bool:
        """检查数据是否为空"""
        return (not self.balance_sheet and
                not self.income_statement and
                not self.cash_flow)