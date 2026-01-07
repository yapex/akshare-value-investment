"""
市场特定字段模块

本模块定义各市场的特定字段,通过继承StandardFields自动获得标准字段。
"""

from .a_stock_fields import AStockMarketFields
from .hk_stock_fields import HKStockMarketFields
from .us_stock_fields import USStockMarketFields

__all__ = [
    'AStockMarketFields',
    'HKStockMarketFields',
    'USStockMarketFields',
]
