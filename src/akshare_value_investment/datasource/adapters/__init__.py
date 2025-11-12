"""
市场适配器模块 - 拆分版本

提供市场特定的财务数据适配器，遵循单一职责原则。
每个适配器专注于单一市场的数据获取和处理。
"""

# 导入拆分后的适配器
from .a_stock_adapter import AStockAdapter
from .hk_stock_adapter import HKStockAdapter
from .us_stock_adapter import USStockAdapter
from .adapter_manager import AdapterManager

# 导出接口
__all__ = [
    'AStockAdapter',
    'HKStockAdapter',
    'USStockAdapter',
    'AdapterManager'
]