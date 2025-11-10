"""
akshare-value-investment: 基于akshare的价值投资分析系统 - 简化版

提供跨市场（A股、港股、美股）财务指标原始数据访问功能。
简化版本：直接返回akshare原始数据，不进行字段映射。
"""

__version__ = "0.1.0"
__author__ = "akshare-value-investment team"

# 导出主要接口 - 简化版本
from .models import MarketType, FinancialIndicator, QueryResult, PeriodType
from .container import create_production_service

__all__ = [
    "create_production_service",
    "MarketType",
    "FinancialIndicator",
    "QueryResult",
    "PeriodType",
]
