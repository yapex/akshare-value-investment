"""
工具函数 - 简化版，主要用于向后兼容
"""

# 重新导出核心函数，保持向后兼容
from webapp.core.data_accessor import (
    format_accounting,
    parse_amount,
    get_field_value,
    StockAnalyzer
)

# 保持原有函数名的别名
_parse_amount = parse_amount
_get_field_value = get_field_value

__all__ = [
    'format_accounting',
    'parse_amount',
    '_parse_amount',
    'get_field_value',
    '_get_field_value',
    'StockAnalyzer'
]