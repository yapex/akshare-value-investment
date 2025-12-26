"""
有息债务权益比计算器

对应 components/debt_to_equity.py
"""

from typing import Dict, Tuple, List
import pandas as pd
import requests

from .. import data_service
from .common import calculate_interest_bearing_debt


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算有息债务权益比（包含数据获取）

    计算公式：
    - 有息债务权益比 = 有息债务 ÷ 股东权益 × 100%
    - 有息债务 = 短期借款 + 长期借款 + 应付债券 + 一年内到期的非流动负债

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (有息债务权益比DataFrame, 显示列名列表, 关键指标字典)

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
        f"{data_service.API_BASE_URL}/api/v1/financial/statements",
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

    if not balance_sheet:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 没有资产负债表数据")

    # 转换资产负债表为DataFrame
    balance_df = pd.DataFrame(balance_sheet["data"])

    # 提取年份（支持多种日期字段）
    if "报告期" in balance_df.columns:
        date_col = "报告期"
    elif "REPORT_DATE" in balance_df.columns:
        date_col = "REPORT_DATE"
    elif "date" in balance_df.columns:
        date_col = "date"
    else:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 资产负债表数据中缺少日期字段")

    balance_df = balance_df.copy()
    balance_df["年份"] = pd.to_datetime(balance_df[date_col]).dt.year

    # 根据市场映射股东权益字段
    if market == "A股":
        equity_col = "所有者权益（或股东权益）合计"
    elif market == "港股":
        equity_col = "股东权益"
    else:  # 美股
        equity_col = "股东权益合计"

    # 使用统一方法计算有息债务
    interest_bearing_debt = calculate_interest_bearing_debt(balance_df, market)

    # 构建债务数据
    debt_data = pd.DataFrame({
        "年份": balance_df["年份"],
        "有息债务": interest_bearing_debt.values,
        "股东权益": balance_df[equity_col].fillna(0)
    })

    # 计算有息债务权益比
    debt_data["有息债务权益比"] = (
        debt_data["有息债务"] / debt_data["股东权益"] * 100
    ).replace([float('inf'), -float('inf')], 0).round(2)

    # 限制年数并排序
    debt_data = debt_data.sort_values("年份").tail(years).reset_index(drop=True)

    # 计算关键指标
    metrics = {
        "avg_debt_to_equity": debt_data['有息债务权益比'].mean(),
        "latest_debt_to_equity": debt_data['有息债务权益比'].iloc[-1],
        "max_debt_to_equity": debt_data['有息债务权益比'].max(),
        "min_debt_to_equity": debt_data['有息债务权益比'].min(),
        "latest_debt": debt_data['有息债务'].iloc[-1],
        "latest_equity": debt_data['股东权益'].iloc[-1]
    }

    # 显示列名
    display_cols = ["年份", "有息债务", "股东权益", "有息债务权益比"]

    return debt_data, display_cols, metrics
