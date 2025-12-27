"""
可重用的基础计算函数

这些函数被多个计算器复用，包括：
- EBIT计算
- 自由现金流计算
- CAGR计算
- 有息债务计算
"""

from typing import Dict, Tuple, List
import pandas as pd


def calculate_cagr(series: pd.Series) -> float:
    """计算复合年增长率(CAGR)

    Args:
        series: 数据序列

    Returns:
        复合年增长率（百分比）

    Examples:
        >>> series = pd.Series([100, 110, 121])
        >>> calculate_cagr(series)
        10.0
    """
    if len(series) < 2:
        return 0.0
    first = series.iloc[0]
    last = series.iloc[-1]
    years = len(series) - 1
    if first <= 0:
        return 0.0
    return ((last / first) ** (1 / years) - 1) * 100


def calculate_interest_bearing_debt(balance_df: pd.DataFrame, market: str) -> pd.Series:
    """计算有息债务（统一的计算方法）

    有息债务是指需要支付利息的债务，包括：
    - 短期借款/短期债务
    - 长期借款/长期债务
    - 应付债券（A股特有）
    - 一年内到期的非流动负债

    Args:
        balance_df: 资产负债表DataFrame（需包含"年份"列）
        market: 市场类型（A股/港股/美股）

    Returns:
        有息债务的Series（与balance_df同长度）
    """
    # 根据市场映射字段
    if market == "A股":
        short_debt_col = "短期借款"
        long_debt_col = "长期借款"
        bonds_col = "应付债券"
        current_non_current_col = "一年内到期的非流动负债"
    elif market == "港股":
        short_debt_col = "短期贷款"
        long_debt_col = "长期贷款"
        bonds_col = None  # 港股可能没有单独的应付债券字段
        current_non_current_col = None  # 港股暂不统计
    else:  # 美股
        short_debt_col = "短期债务"
        long_debt_col = "长期负债"
        bonds_col = None  # 美股可能没有单独的应付债券字段
        current_non_current_col = "长期负债(本期部分)"

    # 计算有息债务
    interest_bearing_debt = (
        balance_df.get(short_debt_col, pd.Series([0] * len(balance_df))).fillna(0) +
        balance_df.get(long_debt_col, pd.Series([0] * len(balance_df))).fillna(0)
    )

    # 添加应付债券（如果存在）
    if bonds_col and bonds_col in balance_df.columns:
        interest_bearing_debt += balance_df[bonds_col].fillna(0)

    # 添加一年内到期的非流动负债（如果存在）
    if current_non_current_col and current_non_current_col in balance_df.columns:
        interest_bearing_debt += balance_df[current_non_current_col].fillna(0)

    return interest_bearing_debt


def calculate_ebit(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
    """计算EBIT和EBIT利润率

    计算公式：
    - A股: EBIT = 净利润 + 所得税费用 + 利息费用
    - 港股: EBIT = 除税前溢利（已包含所得税和融资成本）
    - 美股: EBIT = 持续经营税前利润（已包含所得税）

    Args:
        data: 包含利润表的字典 {"income_statement": DataFrame}
        market: 市场类型（A股/港股/美股）

    Returns:
        (添加了计算结果的DataFrame, 显示列名列表)
    """
    income_df = data["income_statement"].copy()

    if market == "A股":
        # EBIT = 净利润 + 所得税费用 + 利息费用
        income_df["EBIT"] = (
            income_df["五、净利润"] +
            income_df["减：所得税费用"] +
            income_df["其中：利息费用"]
        )
        # 创建通用名称字段（不使用inplace修改）
        income_df["净利润"] = income_df["五、净利润"]
        income_df["所得税费用"] = income_df["减：所得税费用"]
        income_df["利息费用"] = income_df["其中：利息费用"]
        income_df["收入"] = income_df["其中：营业收入"]
        display_columns = ["年份", "净利润", "所得税费用", "利息费用", "收入", "EBIT"]

    elif market == "港股":
        income_df["EBIT"] = income_df["除税前溢利"]
        income_df["收入"] = income_df["营业额"]
        display_columns = ["年份", "除税前溢利", "收入", "EBIT"]

    else:  # 美股
        income_df["EBIT"] = income_df["持续经营税前利润"]
        # 美股收入字段可能为"营业收入"或"收入总额"（如保险公司BRK.B）
        if "营业收入" in income_df.columns:
            income_df["收入"] = income_df["营业收入"]
        elif "收入总额" in income_df.columns:
            income_df["收入"] = income_df["收入总额"]
        else:
            raise ValueError("美股利润表缺少收入字段（需要'营业收入'或'收入总额'）")
        display_columns = ["年份", "持续经营税前利润", "收入", "EBIT"]

    # 计算EBIT利润率
    income_df["EBIT利润率"] = (income_df["EBIT"] / income_df["收入"] * 100).round(2)
    display_columns.append("EBIT利润率")

    return income_df, display_columns


def calculate_free_cash_flow(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
    """计算自由现金流（FCF = 经营活动现金流 - 资本支出）

    自由现金流是衡量公司真实盈利能力的重要指标：
    - 正值：公司有充足现金用于分红、回购、还债
    - 负值：公司需要外部融资来维持运营

    Args:
        data: 包含现金流量表的字典 {"cash_flow": DataFrame}
        market: 市场类型（A股/港股/美股）

    Returns:
        (添加了自由现金流字段的DataFrame, 显示列名列表)
    """
    cashflow_df = data["cash_flow"].copy()

    # 根据市场提取经营性现金流和资本支出字段
    if market == "A股":
        operating_cashflow_col = "经营活动产生的现金流量净额"
        capex_col = "购建固定资产、无形资产和其他长期资产支付的现金"
        # 检查字段是否存在
        if operating_cashflow_col not in cashflow_df.columns:
            raise ValueError(f"经营性现金流量净额字段 '{operating_cashflow_col}' 不存在")
        if capex_col not in cashflow_df.columns:
            raise ValueError(f"资本支出字段 '{capex_col}' 不存在")
        # 计算资本支出(取绝对值,因为不同市场符号可能不同)
        cashflow_df['资本支出'] = cashflow_df[capex_col].abs()

    elif market == "港股":
        operating_cashflow_col = "经营业务现金净额"
        capex_col_1 = "购建固定资产"
        capex_col_2 = "购建无形资产及其他资产"
        # 检查字段是否存在
        if operating_cashflow_col not in cashflow_df.columns:
            raise ValueError(f"经营性现金流量净额字段 '{operating_cashflow_col}' 不存在")
        # 港股的资本支出 = 购建固定资产 + 购建无形资产及其他资产(取绝对值)
        capex_1 = cashflow_df.get(capex_col_1, 0).abs()
        capex_2 = cashflow_df.get(capex_col_2, 0).abs()
        cashflow_df['资本支出'] = (capex_1 + capex_2).fillna(0)

    else:  # 美股
        operating_cashflow_col = "经营活动产生的现金流量净额"
        # 美股的资本支出 = 购买固定资产 + 购建无形资产及其他资产(取绝对值)
        capex_col_1 = "购买固定资产"
        capex_col_2 = "购建无形资产及其他资产"
        # 检查字段是否存在
        if operating_cashflow_col not in cashflow_df.columns:
            raise ValueError(f"经营性现金流量净额字段 '{operating_cashflow_col}' 不存在")
        # 计算资本支出
        capex_1 = cashflow_df.get(capex_col_1, 0).abs()
        capex_2 = cashflow_df.get(capex_col_2, 0).abs()
        cashflow_df['资本支出'] = (capex_1 + capex_2).fillna(0)

    # 计算自由现金流 = 经营现金流 - 资本支出
    cashflow_df['自由现金流'] = cashflow_df[operating_cashflow_col] - cashflow_df['资本支出']
    cashflow_df['自由现金流'] = cashflow_df['自由现金流'].round(2)

    # 重命名字段为通用名称
    cashflow_df.rename(columns={
        operating_cashflow_col: "经营性现金流量净额"
    }, inplace=True)

    display_columns = [
        "年份",
        "经营性现金流量净额",
        "资本支出",
        "自由现金流"
    ]

    return cashflow_df, display_columns
