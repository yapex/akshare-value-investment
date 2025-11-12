"""
模拟akshare API调用
用于验证缓存效果
"""

import random
from typing import Dict, Any

def mock_akshare_call(symbol: str, data_type: str = "financial") -> Dict[str, Any]:
    """模拟akshare API调用

    Args:
        symbol: 股票代码（可能包含年份和季度，如"600519_2020"或"600519_2024_Q1"）
        data_type: 数据类型

    Returns:
        模拟的财务数据
    """
    # 解析symbol获取基础股票代码
    # 支持格式："600519", "600519_2020", "600519_2024_Q1"
    base_symbol = symbol.split('_')[0]  # 提取基础股票代码

    # 基于完整symbol和时间戳生成稳定的数据
    # 确保相同参数返回相同数据
    data_hash = hash(f"{symbol}_{data_type}") % 1000000

    mock_data = {
        'symbol': base_symbol,  # 返回基础股票代码，符合真实业务逻辑
        'full_symbol': symbol,  # 保留完整查询标识
        'data_type': data_type,
        'revenue': 100000000 + data_hash * 10000,  # 稳定的营收数据
        'net_profit': 10000000 + data_hash * 1000,   # 稳定的净利润数据
        'data_hash': f"data_{symbol}_{data_hash}"
    }

    return mock_data