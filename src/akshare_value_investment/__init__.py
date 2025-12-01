"""
akshare-value-investment: 基于akshare的价值投资分析系统 - 简化版

提供跨市场（A股、港股、美股）财务指标原始数据访问功能。
简化版本：专注于核心查询器功能，支持SQLite智能缓存。
"""

__version__ = "0.1.0"
__author__ = "akshare-value-investment team"

# 导出主要接口
from .core.models import MarketType
from .container import create_container, create_production_service

__all__ = [
    "create_container",
    "create_production_service",
    "MarketType",
]
