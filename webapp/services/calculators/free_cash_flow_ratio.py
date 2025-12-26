"""
自由现金流净利润比计算器

对应 components/free_cash_flow_ratio.py
"""

from typing import Dict, Tuple, List
import pandas as pd

from .. import data_service
from .common import calculate_free_cash_flow


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算自由现金流净利润比分析（包含数据获取）

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
    ratio_data, display_cols = _free_cash_flow_to_net_income_ratio(financial_data, market)
    ratio_data = ratio_data.sort_values("年份").reset_index(drop=True)

    # 计算指标
    positive_ratio_years = (ratio_data['自由现金流净利润比'] > 0).sum()
    total_years = len(ratio_data)

    metrics = {
        "avg_ratio": ratio_data['自由现金流净利润比'].mean(),
        "latest_ratio": ratio_data['自由现金流净利润比'].iloc[-1],
        "min_ratio": ratio_data['自由现金流净利润比'].min(),
        "max_ratio": ratio_data['自由现金流净利润比'].max(),
        "positive_years_ratio": (positive_ratio_years / total_years * 100) if total_years > 0 else 0,
        "cumulative_fcf": ratio_data['自由现金流'].sum(),
        "cumulative_net_income": ratio_data['净利润'].sum()
    }

    return ratio_data, display_cols, metrics


def _free_cash_flow_to_net_income_ratio(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
    """计算自由现金流净利润比（FCF / 净利润）

    自由现金流净利润比（自由现金流转换率）是衡量利润质量的重要指标：
    - > 1：说明公司不仅能将利润转化为现金,还有额外现金用于扩张
    - 0.8-1：利润质量良好
    - < 0.8：利润质量较差,大量利润被应收账款或存货占用

    Args:
        data: 包含利润表和现金流量表的字典
            {
                "income_statement": DataFrame,
                "cash_flow": DataFrame
            }
        market: 市场类型（A股/港股/美股）

    Returns:
        (添加了自由现金流净利润比字段的DataFrame, 显示列名列表)
    """
    # 先计算自由现金流
    fcf_data, _ = calculate_free_cash_flow(data, market)

    # 获取净利润数据
    income_df = data["income_statement"].copy()

    # 根据市场提取净利润字段
    if market == "A股":
        net_income_col = "五、净利润"
    elif market == "港股":
        net_income_col = "股东应占溢利"
    else:  # 美股
        net_income_col = "净利润"

    # 检查字段是否存在
    if net_income_col not in income_df.columns:
        raise ValueError(f"净利润字段 '{net_income_col}' 不存在")

    # 合并自由现金流和净利润
    result_df = pd.merge(
        fcf_data[["年份", "经营性现金流量净额", "资本支出", "自由现金流"]],
        income_df[["年份", net_income_col]],
        on="年份"
    )

    # 计算自由现金流净利润比
    result_df['自由现金流净利润比'] = (
        result_df['自由现金流'] /
        result_df[net_income_col].replace(0, pd.NA)
    ).round(2)

    # 重命名字段为通用名称
    result_df.rename(columns={
        net_income_col: "净利润"
    }, inplace=True)

    display_columns = [
        "年份",
        "净利润",
        "经营性现金流量净额",
        "资本支出",
        "自由现金流",
        "自由现金流净利润比"
    ]

    return result_df, display_columns


def calculate_investment_intensity_ratio(
    symbol: str,
    market: str,
    years: int
) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
    """计算投资强度比率分析（包含数据获取）

    投资强度比率是判断公司是否在为增长投入资金的重要指标：
    - 接近100%：公司在为维持现有业务的固定资产投资（维护性投资）
    - 远高于100%：公司在为增长进行投资（扩张性投资）
    - 低于100%：公司资本支出不足，可能影响未来竞争力

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
    ratio_data, display_cols = _investment_intensity_ratio(financial_data, market)
    ratio_data = ratio_data.sort_values("年份").tail(years).reset_index(drop=True)

    # 计算指标
    metrics = {
        "avg_ratio": ratio_data['投资强度比率'].mean(),
        "latest_ratio": ratio_data['投资强度比率'].iloc[-1],
        "min_ratio": ratio_data['投资强度比率'].min(),
        "max_ratio": ratio_data['投资强度比率'].max(),
        "cumulative_capex": ratio_data['资本支出'].sum(),
        "cumulative_depreciation": ratio_data['折旧'].sum()
    }

    return ratio_data, display_cols, metrics


def _investment_intensity_ratio(
    data: Dict[str, pd.DataFrame],
    market: str
) -> Tuple[pd.DataFrame, List[str]]:
    """计算投资强度比率（资本支出 ÷ 折旧 × 100）

    Args:
        data: 包含现金流量表的字典 {"cash_flow": DataFrame}
        market: 市场类型（A股/港股/美股）

    Returns:
        (添加了投资强度比率字段的DataFrame, 显示列名列表)
    """
    cashflow_df = data["cash_flow"].copy()

    # 根据市场提取资本支出和折旧字段
    if market == "A股":
        capex_col = "购建固定资产、无形资产和其他长期资产支付的现金"
        depreciation_col = "固定资产折旧、油气资产折耗、生产性生物资产折旧"
        # 检查字段是否存在
        if capex_col not in cashflow_df.columns:
            raise ValueError(f"资本支出字段 '{capex_col}' 不存在")
        if depreciation_col not in cashflow_df.columns:
            raise ValueError(f"折旧字段 '{depreciation_col}' 不存在")
        # 计算资本支出和折旧
        cashflow_df['资本支出'] = cashflow_df[capex_col].abs()
        cashflow_df['折旧'] = cashflow_df[depreciation_col].abs()

    elif market == "港股":
        capex_col = "购建固定资产"
        depreciation_col = "加:折旧及摊销"
        # 检查字段是否存在
        if capex_col not in cashflow_df.columns:
            raise ValueError(f"资本支出字段 '{capex_col}' 不存在")
        if depreciation_col not in cashflow_df.columns:
            raise ValueError(f"折旧字段 '{depreciation_col}' 不存在")
        # 计算资本支出和折旧
        cashflow_df['资本支出'] = cashflow_df[capex_col].abs()
        cashflow_df['折旧'] = cashflow_df[depreciation_col].abs()

    else:  # 美股
        # 美股的资本支出 = 购买固定资产 + 购建无形资产及其他资产
        capex_col_1 = "购买固定资产"
        capex_col_2 = "购建无形资产及其他资产"
        depreciation_col = "折旧及摊销"
        # 检查字段是否存在
        if depreciation_col not in cashflow_df.columns:
            raise ValueError(f"折旧字段 '{depreciation_col}' 不存在")
        # 计算资本支出和折旧
        capex_1 = cashflow_df.get(capex_col_1, 0).abs()
        capex_2 = cashflow_df.get(capex_col_2, 0).abs()
        cashflow_df['资本支出'] = (capex_1 + capex_2).fillna(0)
        cashflow_df['折旧'] = cashflow_df[depreciation_col].abs()

    # 计算投资强度比率（资本支出 / 折旧 * 100）
    cashflow_df['投资强度比率'] = (
        cashflow_df['资本支出'] /
        cashflow_df['折旧'].replace(0, pd.NA) * 100
    ).round(2)

    display_columns = [
        "年份",
        "资本支出",
        "折旧",
        "投资强度比率"
    ]

    return cashflow_df, display_columns
