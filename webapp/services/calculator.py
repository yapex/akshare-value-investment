"""
财务指标计算服务

提供复杂财务指标的计算方法（一行代码能搞定的不封装）

设计原则：
- YAGNI：只包含当前需要的方法
- KISS：保持简单
"""

from typing import List, Tuple, Dict
import pandas as pd


class Calculator:
    """财务指标计算器"""

    @staticmethod
    def cagr(series: pd.Series) -> float:
        """计算复合年增长率(CAGR)

        Args:
            series: 数据序列

        Returns:
            复合年增长率（百分比）

        Examples:
            >>> import pandas as pd
            >>> series = pd.Series([100, 110, 121])
            >>> Calculator.cagr(series)
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

    @staticmethod
    def ebit(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
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
            # 重命名为通用名称
            income_df.rename(columns={
                "五、净利润": "净利润",
                "减：所得税费用": "所得税费用",
                "其中：利息费用": "利息费用",
                "其中：营业收入": "收入"
            }, inplace=True)
            display_columns = ["年份", "净利润", "所得税费用", "利息费用", "收入", "EBIT"]

        elif market == "港股":
            income_df["EBIT"] = income_df["除税前溢利"]
            income_df.rename(columns={"营业额": "收入"}, inplace=True)
            display_columns = ["年份", "除税前溢利", "收入", "EBIT"]

        else:  # 美股
            income_df["EBIT"] = income_df["持续经营税前利润"]
            income_df.rename(columns={"营业收入": "收入"}, inplace=True)
            display_columns = ["年份", "持续经营税前利润", "收入", "EBIT"]

        # 计算EBIT利润率
        income_df["EBIT利润率"] = (income_df["EBIT"] / income_df["收入"] * 100).round(2)
        display_columns.append("EBIT利润率")

        return income_df, display_columns

    @staticmethod
    def net_profit_cash_ratio(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
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

        # 计算累计值
        result_df = result_df.sort_values('年份').reset_index(drop=True)
        result_df['累计净利润'] = result_df[net_profit_col].cumsum()
        result_df['累计经营性现金流量净额'] = result_df[operating_cashflow_col].cumsum()

        # 计算净现比（累计经营性现金流 / 累计净利润）
        result_df['净现比'] = (
            result_df['累计经营性现金流量净额'] /
            result_df['累计净利润'].replace(0, pd.NA)
        ).round(2)

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
