"""
计算器模块

按 components 目录结构拆分的财务指标计算器，每个计算器对应一个组件。

架构设计：
- common.py: 可重用的基础计算函数
- *.py: 各组件专用计算器（与 components 一一对应）
"""

from .common import (
    calculate_ebit,
    calculate_free_cash_flow,
    calculate_cagr,
    calculate_interest_bearing_debt,
)

__all__ = [
    "calculate_ebit",
    "calculate_free_cash_flow",
    "calculate_cagr",
    "calculate_interest_bearing_debt",
]
