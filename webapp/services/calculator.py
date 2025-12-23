"""
财务指标计算服务

提供复杂财务指标的计算方法（一行代码能搞定的不封装）

设计原则：
- YAGNI：只包含当前需要的方法
- KISS：保持简单
"""

from typing import List, Tuple
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
    def ebit(df: pd.DataFrame, market: str) -> Tuple[pd.DataFrame, List[str]]:
        """计算EBIT和EBIT利润率

        计算公式：
        - A股: EBIT = 净利润 + 所得税费用 + 利息费用
        - 港股: EBIT = 除税前溢利（已包含所得税和融资成本）
        - 美股: EBIT = 持续经营税前利润（已包含所得税）

        Args:
            df: 原始数据DataFrame（需包含年份列）
            market: 市场类型（A股/港股/美股）

        Returns:
            (添加了计算结果的DataFrame, 显示列名列表)
        """
        result_df = df.copy()

        if market == "A股":
            # EBIT = 净利润 + 所得税费用 + 利息费用
            result_df["EBIT"] = (
                result_df["五、净利润"] +
                result_df["减：所得税费用"] +
                result_df["其中：利息费用"]
            )
            # 重命名为通用名称
            result_df.rename(columns={
                "五、净利润": "净利润",
                "减：所得税费用": "所得税费用",
                "其中：利息费用": "利息费用",
                "其中：营业收入": "收入"
            }, inplace=True)
            display_columns = ["年份", "净利润", "所得税费用", "利息费用", "收入", "EBIT"]

        elif market == "港股":
            result_df["EBIT"] = result_df["除税前溢利"]
            result_df.rename(columns={"营业额": "收入"}, inplace=True)
            display_columns = ["年份", "除税前溢利", "收入", "EBIT"]

        else:  # 美股
            result_df["EBIT"] = result_df["持续经营税前利润"]
            result_df.rename(columns={"营业收入": "收入"}, inplace=True)
            display_columns = ["年份", "持续经营税前利润", "收入", "EBIT"]

        # 计算EBIT利润率
        result_df["EBIT利润率"] = (result_df["EBIT"] / result_df["收入"] * 100).round(2)
        display_columns.append("EBIT利润率")

        return result_df, display_columns
