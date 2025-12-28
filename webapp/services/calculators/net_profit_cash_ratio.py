"""
净利润现金比计算器

对应 components/net_profit_cash_ratio.py
"""

from typing import Dict, Tuple, List
import pandas as pd

from .. import data_service


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str]]:
    """计算净利润现金比分析（包含数据获取）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (结果DataFrame, 显示列名列表)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    financial_data = data_service.get_financial_statements(symbol, market, years)
    return _net_profit_cash_ratio(financial_data, market)


def _net_profit_cash_ratio(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
    """计算净利润现金比（累计净利润和累计经营性现金流量净额的比率）

    这是一个"利润是否为真"的重要指标：
    - 净利润现金比 > 1：说明利润质量好，有真实现金流支持
    - 净利润现金比 < 1：说明利润质量差，可能是应收账款或存货增加

    Args:
        data: 包含利润表和现金流量表的字典
            {
                "income_statement": DataFrame,
                "cash_flow": DataFrame
            }
        market: 市场类型（A股/港股/美股）

    Returns:
        (添加了计算结果的DataFrame, 显示列名列表)
    """
    income_df = data["income_statement"].copy()
    cashflow_df = data["cash_flow"].copy()

    # 根据市场提取净利润和经营性现金流量净额字段
    if market == "A股":
        net_profit_col = "五、净利润"
        operating_cashflow_col = "经营活动产生的现金流量净额"
    elif market == "港股":
        net_profit_col = "股东应占溢利"
        operating_cashflow_col = "经营业务现金净额"
    else:  # 美股
        net_profit_col = "净利润"
        operating_cashflow_col = "经营活动产生的现金流量净额"

    # 检查字段是否存在
    if net_profit_col not in income_df.columns:
        raise ValueError(f"净利润字段 '{net_profit_col}' 不存在")
    if operating_cashflow_col not in cashflow_df.columns:
        raise ValueError(f"经营性现金流量净额字段 '{operating_cashflow_col}' 不存在")

    # 按年份合并利润表和现金流量表
    result_df = pd.merge(
        income_df[["年份", net_profit_col]],
        cashflow_df[["年份", operating_cashflow_col]],
        on="年份"
    )

    # 转换为数值类型（处理非数值类型，如None、空字符串等）
    result_df[net_profit_col] = pd.to_numeric(result_df[net_profit_col], errors="coerce")
    result_df[operating_cashflow_col] = pd.to_numeric(result_df[operating_cashflow_col], errors="coerce")

    # 计算累计值
    result_df = result_df.sort_values('年份').reset_index(drop=True)
    result_df['累计净利润'] = result_df[net_profit_col].cumsum()
    result_df['累计经营性现金流量净额'] = result_df[operating_cashflow_col].cumsum()

    # 计算净现比（累计经营性现金流 / 累计净利润）
    result_df['净现比'] = (
        result_df['累计经营性现金流量净额'] /
        result_df['累计净利润'].replace(0, pd.NA)
    )
    # 处理无穷值
    result_df['净现比'] = result_df['净现比'].replace([float('inf'), -float('inf')], pd.NA)
    # 确保是数值类型后再round
    result_df['净现比'] = pd.to_numeric(result_df['净现比'], errors="coerce").round(2)

    # 重命名字段为通用名称
    result_df.rename(columns={
        net_profit_col: "净利润",
        operating_cashflow_col: "经营性现金流量净额"
    }, inplace=True)

    display_columns = [
        "年份",
        "净利润",
        "经营性现金流量净额",
        "累计净利润",
        "累计经营性现金流量净额",
        "净现比"
    ]

    return result_df, display_columns
