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