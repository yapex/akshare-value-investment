"""
财务指标计算服务

提供复杂财务指标的计算方法（一行代码能搞定的不封装）

设计原则：
- YAGNI：只包含当前需要的方法
- KISS：保持简单
- 单一职责：每个分析方法负责获取数据+计算，app.py只负责展示
"""

from typing import List, Tuple, Dict
import pandas as pd

from . import data_service


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

    @staticmethod
    def calculate_net_profit_cash_ratio(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str]]:
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
        return Calculator.net_profit_cash_ratio(financial_data, market)

    @staticmethod
    def calculate_revenue_growth(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, Dict[str, float]]:
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
            revenue_col = "营业额"
        else:  # 美股
            revenue_col = "营业收入"

        # 提取收入数据
        revenue_data = income_df[["年份", revenue_col]].copy()
        revenue_data = revenue_data.sort_values("年份").reset_index(drop=True)
        revenue_data['增长率'] = revenue_data[revenue_col].pct_change() * 100
        revenue_data['增长率'] = revenue_data['增长率'].round(2)

        # 计算指标
        years_count = len(revenue_data)
        metrics = {
            "cagr": Calculator.cagr(revenue_data[revenue_col]),
            "avg_growth_rate": revenue_data['增长率'].mean(),
            "latest_revenue": revenue_data[revenue_col].iloc[-1],
            "avg_revenue": revenue_data[revenue_col].mean(),
            "years_count": years_count
        }

        return revenue_data, metrics

    @staticmethod
    def calculate_ebit_margin(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
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
        ebit_data, display_cols = Calculator.ebit(financial_data, market)
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

    @staticmethod
    def free_cash_flow(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
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

    @staticmethod
    def free_cash_flow_to_net_income_ratio(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
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
        fcf_data, _ = Calculator.free_cash_flow(data, market)

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

    @staticmethod
    def calculate_free_cash_flow_to_net_income_ratio(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
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
        ratio_data, display_cols = Calculator.free_cash_flow_to_net_income_ratio(financial_data, market)
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

    @staticmethod
    def investment_intensity_ratio(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
        """计算投资强度比率（资本支出 ÷ 折旧 × 100）

        投资强度比率是判断公司是否在为增长投入资金的重要指标：
        - 接近100%：公司在为维持现有业务的固定资产投资（维护性投资）
        - 远高于100%：公司在为增长进行投资（扩张性投资）
        - 低于100%：公司资本支出不足，可能影响未来竞争力

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

    @staticmethod
    def calculate_investment_intensity_ratio(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
        """计算投资强度比率分析（包含数据获取）

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
        ratio_data, display_cols = Calculator.investment_intensity_ratio(financial_data, market)
        ratio_data = ratio_data.sort_values("年份").reset_index(drop=True)

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

    @staticmethod
    def roic(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
        """计算投入资本回报率（ROIC = NOPAT ÷ 投入资本）

        ROIC 是衡量公司资本使用效率的核心指标：
        - > 15%：优秀，公司资本利用效率很高
        - 10-15%：良好，公司资本利用效率较好
        - < 10%：一般，公司资本利用效率较低

        计算公式：
        - NOPAT（税后净营业利润）= EBIT × (1 - 税率)
        - 投入资本 = 股东权益 + 有息负债（短期借款 + 长期借款）
        - ROIC = NOPAT ÷ 投入资本 × 100%

        Args:
            data: 包含利润表和资产负债表的字典
                {
                    "income_statement": DataFrame,
                    "balance_sheet": DataFrame
                }
            market: 市场类型（A股/港股/美股）

        Returns:
            (添加了ROIC字段的DataFrame, 显示列名列表)
        """
        # 复用 ebit() 函数获取 EBIT
        income_df, _ = Calculator.ebit(data, market)
        balance_df = data["balance_sheet"].copy()

        # 根据市场提取权益字段并合并数据
        if market == "A股":
            equity_col = "归属于母公司所有者权益合计"
            short_debt_col = "短期借款"
            long_debt_col = "长期借款"
            tax_col = "所得税费用"
            # A股：合并利润表和资产负债表
            result_df = pd.merge(
                income_df.loc[:, ["年份", "EBIT", "收入", tax_col]],
                balance_df.loc[:, ["年份", equity_col, short_debt_col, long_debt_col]],
                on="年份"
            )
            # 计算实际税率
            result_df["实际税率"] = (result_df[tax_col] / result_df["EBIT"]).replace([float('inf'), -float('inf')], 0).fillna(0.25)

        elif market == "港股":
            equity_col = "股东权益"
            short_debt_col = "短期贷款"
            long_debt_col = "长期贷款"
            # 港股：合并利润表和资产负债表
            result_df = pd.merge(
                income_df.loc[:, ["年份", "EBIT", "收入"]],
                balance_df.loc[:, ["年份", equity_col, short_debt_col, long_debt_col]],
                on="年份"
            )
            # 港股使用固定税率
            result_df["实际税率"] = 0.165  # 香港利得税16.5%

        else:  # 美股
            equity_col = "股东权益合计"
            short_debt_col = "短期债务"
            long_debt_col = "长期负债"
            # 美股：合并利润表和资产负债表
            result_df = pd.merge(
                income_df.loc[:, ["年份", "EBIT", "收入"]],
                balance_df.loc[:, ["年份", equity_col, short_debt_col, long_debt_col]],
                on="年份"
            )
            # 美股使用固定税率
            result_df["实际税率"] = 0.21  # 美国联邦税率21%

        # 计算投入资本 = 股东权益 + 有息负债（短期借款 + 长期借款）
        result_df["投入资本"] = (
            result_df[equity_col].fillna(0) +
            result_df[short_debt_col].fillna(0) +
            result_df[long_debt_col].fillna(0)
        )

        # 计算 NOPAT（税后净营业利润）
        result_df["NOPAT"] = result_df["EBIT"] * (1 - result_df["实际税率"])

        # 计算 ROIC
        result_df["ROIC"] = (
            result_df["NOPAT"] /
            result_df["投入资本"].replace(0, pd.NA) * 100
        ).round(2)

        display_columns = [
            "年份",
            "EBIT",
            "实际税率",
            "NOPAT",
            "投入资本",
            "ROIC"
        ]

        return result_df, display_columns

    @staticmethod
    def calculate_roic(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, List[str], Dict[str, float]]:
        """计算投入资本回报率分析（包含数据获取）

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
        import requests

        # 获取利润表数据
        income_data = data_service.get_financial_statements(symbol, market, years)

        # 单独获取资产负债表数据
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
        import pandas as pd
        balance_df = pd.DataFrame(balance_sheet["data"])

        # 提取年份
        date_col = "报告期" if "报告期" in balance_df.columns else "date"
        balance_df = balance_df.copy()
        balance_df["年份"] = pd.to_datetime(balance_df[date_col]).dt.year

        # 构建完整数据字典
        financial_data = {
            "income_statement": income_data["income_statement"],
            "balance_sheet": balance_df
        }

        roic_data, display_cols = Calculator.roic(financial_data, market)
        roic_data = roic_data.sort_values("年份").reset_index(drop=True)

        # 计算指标
        metrics = {
            "avg_roic": roic_data['ROIC'].mean(),
            "latest_roic": roic_data['ROIC'].iloc[-1],
            "min_roic": roic_data['ROIC'].min(),
            "max_roic": roic_data['ROIC'].max(),
            "avg_nopat": roic_data['NOPAT'].mean(),
            "avg_capital": roic_data['投入资本'].mean()
        }

        return roic_data, display_cols, metrics
