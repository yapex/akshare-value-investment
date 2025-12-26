"""
EBIT利润率计算器

对应 components/ebit_margin.py
"""

from typing import Dict, Tuple, List
import pandas as pd

from .. import data_service
from .common import calculate_ebit


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算EBIT利润率分析（包含数据获取）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (结果DataFrame, 显示列名列表, 指标字典)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    financial_data = data_service.get_financial_statements(symbol, market, years)
    ebit_data, display_cols = calculate_ebit(financial_data, market)
    ebit_data = ebit_data.sort_values("年份").reset_index(drop=True)
    ebit_data['利润率增长率'] = ebit_data['EBIT利润率'].pct_change() * 100
    ebit_data['利润率增长率'] = ebit_data['利润率增长率'].round(2)

    # 计算指标
    metrics = {
        "avg_margin": ebit_data['EBIT利润率'].mean(),
        "latest_margin": ebit_data['EBIT利润率'].iloc[-1],
        "max_margin": ebit_data['EBIT利润率'].max(),
        "min_margin": ebit_data['EBIT利润率'].min(),
        "avg_growth_rate": ebit_data['利润率增长率'].mean()
    }

    return ebit_data, display_cols, metrics
