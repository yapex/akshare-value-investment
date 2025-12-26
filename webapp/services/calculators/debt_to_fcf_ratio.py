"""
有息债务与自由现金流比率计算器

对应 components/debt_to_fcf_ratio.py
"""

from typing import Dict, Tuple, List
import pandas as pd
import requests

from .. import data_service
from .common import calculate_interest_bearing_debt, calculate_free_cash_flow


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算有息债务与自由现金流比率（包含数据获取）

    计算公式：
    - 有息债务与自由现金流比率 = 有息债务 ÷ 自由现金流
    - 有息债务 = 短期借款 + 长期借款 + 应付债券 + 一年内到期的非流动负债
    - 自由现金流 = 经营活动现金流净额 - 资本支出

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (有息债务与自由现金流比率DataFrame, 显示列名列表, 关键指标字典)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    # 获取财务三表数据
    query_type_map = {
        "A股": "a_financial_statements",
        "港股": "hk_financial_statements",
        "美股": "us_financial_statements"
    }
    query_type = query_type_map.get(market)

    response = requests.get(
        f"{data_service.API_BASE_URL}{data_service.FINANCIAL_STATEMENTS_ENDPOINT}",
        params={
            "symbol": symbol,
            "query_type": query_type,
            "frequency": "annual"
        },
        timeout=30
    )

    if response.status_code != 200:
        raise data_service.APIServiceUnavailableError(f"API服务返回错误状态码: {response.status_code}")

    result = response.json()
    data_dict = result.get("data", {})
    balance_sheet = data_dict.get("balance_sheet")
    cash_flow = data_dict.get("cash_flow")

    if not balance_sheet:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 没有资产负债表数据")
    if not cash_flow:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 没有现金流量表数据")

    # 转换资产负债表为DataFrame并提取年份
    balance_df = pd.DataFrame(balance_sheet["data"])
    balance_df = data_service.extract_year_column(balance_df, market, symbol, "资产负债表")

    # 计算有息债务
    interest_bearing_debt = calculate_interest_bearing_debt(balance_df, market)

    # 构建债务数据DataFrame
    debt_df = pd.DataFrame({
        "年份": balance_df["年份"],
        "有息债务": interest_bearing_debt.values
    })

    # 转换现金流量表为DataFrame并提取年份
    cashflow_df = pd.DataFrame(cash_flow["data"])
    cashflow_df = data_service.extract_year_column(cashflow_df, market, symbol, "现金流量表")

    # 计算自由现金流
    cashflow_data, _ = calculate_free_cash_flow({"cash_flow": cashflow_df}, market)

    # 构建自由现金流数据DataFrame
    fcf_df = pd.DataFrame({
        "年份": cashflow_data["年份"],
        "自由现金流": cashflow_data["自由现金流"].values
    })

    # 合并债务和自由现金流数据
    ratio_data = pd.merge(debt_df, fcf_df, on="年份", how="inner")

    # 计算有息债务与自由现金流比率
    ratio_data["有息债务与自由现金流比率"] = (
        ratio_data["有息债务"] / ratio_data["自由现金流"].replace(0, float('inf'))
    ).replace([float('inf'), -float('inf'), float('nan')], None).round(2)

    # 限制年数并排序
    ratio_data = ratio_data.sort_values("年份").tail(years).reset_index(drop=True)

    # 计算关键指标
    valid_ratios = ratio_data["有息债务与自由现金流比率"].dropna()
    metrics = {
        "avg_ratio": valid_ratios.mean() if len(valid_ratios) > 0 else None,
        "latest_ratio": ratio_data["有息债务与自由现金流比率"].iloc[-1] if len(ratio_data) > 0 else None,
        "min_ratio": valid_ratios.min() if len(valid_ratios) > 0 else None,
        "max_ratio": valid_ratios.max() if len(valid_ratios) > 0 else None,
        "latest_debt": ratio_data["有息债务"].iloc[-1] if len(ratio_data) > 0 else None,
        "latest_fcf": ratio_data["自由现金流"].iloc[-1] if len(ratio_data) > 0 else None,
        "positive_fcf_years": (ratio_data["自由现金流"] > 0).sum(),
        "total_years": len(ratio_data)
    }

    # 显示列名
    display_cols = ["年份", "有息债务", "自由现金流", "有息债务与自由现金流比率"]

    return ratio_data, display_cols, metrics
