"""
核心数据模型

定义通用的数据结构和枚举类型。
"""

from enum import Enum


class MarketType(Enum):
    """市场类型枚举"""
    A_STOCK = "a_stock"
    HK_STOCK = "hk_stock"
    US_STOCK = "us_stock"
