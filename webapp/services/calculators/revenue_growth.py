"""
收入增长计算器

对应 components/revenue_growth.py
"""

from typing import Dict, Tuple
import pandas as pd

from .. import data_service
from .common import calculate_cagr


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """计算营业收入增长趋势（包含数据获取）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (收入数据DataFrame, 指标字典)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    financial_data = data_service.get_financial_statements(symbol, market, years)
    income_df = financial_data["income_statement"]

    # 获取收入字段名称
    if market == "A股":
        revenue_col = "其中：营业收入"
    elif market == "港股":
        # 港股收入字段可能为"营业额"或"经营收入总额"（如00388港交所）
        if "营业额" in income_df.columns:
            revenue_col = "营业额"
        elif "经营收入总额" in income_df.columns:
            revenue_col = "经营收入总额"
        else:
            raise ValueError("港股利润表缺少收入字段（需要'营业额'或'经营收入总额'）")
    else:  # 美股
        # 美股收入字段可能为"营业收入"或"收入总额"（如保险公司BRK.B）
        if "营业收入" in income_df.columns:
            revenue_col = "营业收入"
        elif "收入总额" in income_df.columns:
            revenue_col = "收入总额"
        else:
            raise ValueError("美股利润表缺少收入字段（需要'营业收入'或'收入总额'）")

    # 提取收入数据
    revenue_data = income_df[["年份", revenue_col]].copy()
    revenue_data = revenue_data.sort_values("年份").reset_index(drop=True)

    # 统一重命名为"收入"字段（便于后续处理）
    revenue_data["收入"] = revenue_data[revenue_col]

    # 计算增长率
    revenue_data['增长率'] = revenue_data["收入"].pct_change() * 100
    revenue_data['增长率'] = revenue_data['增长率'].round(2)

    # 计算指标
    years_count = len(revenue_data)
    metrics = {
        "cagr": calculate_cagr(revenue_data["收入"]),
        "avg_growth_rate": revenue_data['增长率'].mean(),
        "latest_revenue": revenue_data["收入"].iloc[-1],
        "avg_revenue": revenue_data["收入"].mean(),
        "years_count": years_count
    }

    return revenue_data, metrics
