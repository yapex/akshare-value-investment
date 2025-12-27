"""
DCF估值计算器

对应 components/dcf_valuation.py
"""

from typing import Dict, List, Tuple
import pandas as pd
import requests

from .. import data_service


def calculate(
    symbol: str,
    market: str,
    years: int = 5,
    growth_rate: float = 0.05,
    discount_rate: float = 0.10,
    terminal_growth: float = 0.02
) -> Tuple[pd.DataFrame, List[str], Dict[str, any]]:
    """计算DCF估值（包含数据获取）

    Args:
        symbol: 股票代码
        market: 市场类型（A股、港股、美股）
        years: 预测年数，默认5年
        growth_rate: 现金流增长率，默认5%
        discount_rate: 折现率（WACC），默认10%
        terminal_growth: 永续增长率，默认2%

    Returns:
        (DataFrame, display_columns, stats_dict)
        - DataFrame: 包含预测现金流和折现值的详细数据
        - display_columns: 显示列名列表
        - stats: 包含估值结果的字典
    """
    # 查询类型映射
    query_type_map = {
        "A股": "a_financial_statements",
        "港股": "hk_financial_statements",
        "美股": "us_financial_statements"
    }

    query_type = query_type_map.get(market)
    if not query_type:
        raise ValueError(f"不支持的市场类型: {market}")

    # 调用FastAPI的财务三表查询端点
    response = requests.get(
        "http://localhost:8000/api/v1/financial/statements",
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

    # 转换为DataFrame并提取年份
    balance_df = pd.DataFrame(balance_sheet["data"])
    balance_df = data_service.extract_year_column(balance_df, market, symbol, "资产负债表")

    cashflow_df = pd.DataFrame(cash_flow["data"])
    cashflow_df = data_service.extract_year_column(cashflow_df, market, symbol, "现金流量表")

    # 确定字段映射（三地市场）
    if market == "A股":
        operating_cf_col = "经营活动产生的现金流量净额"
        capex_col = "购建固定资产、无形资产和其他长期资产支付的现金"
        short_debt_col = "短期借款"
        long_debt_col = "长期借款"
        cash_col = "货币资金"
        equity_col = "归属于母公司所有者权益合计"
    elif market == "港股":
        operating_cf_col = "经营业务现金净额"
        capex_col = "购建固定资产、无形资产及其他资产支付的现金"
        short_debt_col = "短期贷款"
        long_debt_col = "长期贷款"
        cash_col = "现金及等价物"
        equity_col = "股东权益合计"
    else:  # 美股
        operating_cf_col = "经营活动产生的现金流量净额"
        capex_col = "购建固定资产、无形资产和其他长期资产支付的现金"
        short_debt_col = "短期债务"
        long_debt_col = "长期负债"
        cash_col = "现金及现金等价物"
        equity_col = "股东权益合计"

    # 获取最新财务数据
    latest_balance = balance_df.iloc[0]
    latest_cashflow = cashflow_df.iloc[0]

    # 计算自由现金流（FCF = 经营现金流 - 资本支出）- 单位：亿元
    latest_fcf = latest_cashflow[operating_cf_col] - latest_cashflow.get(capex_col, 0)

    # 计算有息债务和净债务 - 单位：亿元
    interest_bearing_debt = latest_balance.get(short_debt_col, 0) + latest_balance.get(long_debt_col, 0)
    net_debt = interest_bearing_debt - latest_balance.get(cash_col, 0)

    # 获取股东权益 - 单位：亿元
    equity_value_bs = latest_balance.get(equity_col, 0)

    # DCF预测
    prediction_data = []
    current_fcf = latest_fcf
    present_value_fcf = 0

    for year in range(1, years + 1):
        # 现金流增长
        future_fcf = current_fcf * (1 + growth_rate) ** year
        # 折现到现值
        discount_factor = 1 / ((1 + discount_rate) ** year)
        pv_fcf = future_fcf * discount_factor
        present_value_fcf += pv_fcf

        prediction_data.append({
            "年份": f"第{year}年",
            "预测现金流": future_fcf,
            "折现因子": discount_factor,
            "折现现金流": pv_fcf
        })

    # 计算终值（Terminal Value）- 单位：亿元
    terminal_fcf = current_fcf * (1 + growth_rate) ** years * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount_rate) ** years)

    # 企业价值 = 预测期现值 + 终值现值 - 单位：亿元
    enterprise_value = present_value_fcf + pv_terminal

    # 股权价值 = 企业价值 - 净债务 - 单位：亿元
    equity_value_dcf = enterprise_value - net_debt

    # 计算估值溢价/折价
    valuation_premium = (equity_value_dcf - equity_value_bs) / equity_value_bs * 100 if equity_value_bs > 0 else 0

    # 构建结果DataFrame
    result_df = pd.DataFrame(prediction_data)

    # 添加汇总行
    summary_row = {
        "年份": "预测期合计",
        "预测现金流": result_df["预测现金流"].sum(),
        "折现因子": None,
        "折现现金流": present_value_fcf
    }
    result_df = pd.concat([result_df, pd.DataFrame([summary_row])], ignore_index=True)

    # 统计信息
    stats = {
        # 当前财务数据（单位：亿元）
        "current_fcf": latest_fcf,
        "net_debt": net_debt,
        "equity_value_bs": equity_value_bs,
        "interest_bearing_debt": interest_bearing_debt,
        "cash_balance": latest_balance.get(cash_col, 0),

        # DCF参数
        "growth_rate": growth_rate,
        "discount_rate": discount_rate,
        "terminal_growth": terminal_growth,
        "projection_years": years,

        # 估值结果（单位：亿元）
        "present_value_fcf": present_value_fcf,
        "terminal_value": terminal_value,
        "pv_terminal": pv_terminal,
        "enterprise_value": enterprise_value,
        "equity_value_dcf": equity_value_dcf,
        "equity_value_bs": equity_value_bs,
        "valuation_premium": valuation_premium,

        # 计算市场隐含增长率的方法
        "implied_growth_rate": lambda market_cap: _calculate_implied_growth_rate(
            market_cap, latest_fcf, net_debt, years, discount_rate, terminal_growth
        ) if market_cap > 0 else None,

        # 估值说明
        "valuation_summary": f"""
**估值模型**: DCF（折现现金流）模型
**预测期**: {years}年
**现金流增长率**: {growth_rate * 100:.1f}%
**折现率**: {discount_rate * 100:.1f}%
**永续增长率**: {terminal_growth * 100:.1f}%

**关键财务数据**（单位：亿元）:
- 当前自由现金流: {latest_fcf:.2f}
- 净债务: {net_debt:.2f}
- 账面股东权益: {equity_value_bs:.2f}

**DCF估值结果**（单位：亿元）:
- 预测期现值: {present_value_fcf:.2f}
- 终值现值: {pv_terminal:.2f}
- 企业价值: {enterprise_value:.2f}
- DCF股权价值: {equity_value_dcf:.2f}
- 账面股权价值: {equity_value_bs:.2f}
- 估值溢价/折价: {valuation_premium:+.1f}%

**投资建议**:
- 估值溢价 > 20%: 股价可能被高估，建议谨慎
- 估值溢价 ±20%: 股价相对合理
- 估值溢价 < -20%: 股价可能被低估，值得关注
            """
    }

    display_cols = [
        "年份",
        "预测现金流",
        "折现因子",
        "折现现金流"
    ]

    return result_df, display_cols, stats


def _calculate_implied_growth_rate(
    market_cap: float,
    current_fcf: float,
    net_debt: float,
    years: int,
    discount_rate: float,
    terminal_growth: float,
    max_iterations: int = 100,
    tolerance: float = 0.0001
) -> float:
    """反向计算市场隐含增长率

    通过牛顿迭代法，从给定市值反推市场预期的现金流增长率。

    Args:
        market_cap: 市值（亿元）
        current_fcf: 当前自由现金流（亿元）
        net_debt: 净债务（亿元）
        years: 预测年数
        discount_rate: 折现率
        terminal_growth: 永续增长率
        max_iterations: 最大迭代次数
        tolerance: 收敛容差

    Returns:
        市场隐含增长率（小数形式，如0.08表示8%）
    """
    from scipy.optimize import fsolve

    def dcf_value(growth_rate_arr):
        """DCF估值函数"""
        g = growth_rate_arr[0]
        present_value_fcf = 0

        # 预测期现值
        for year in range(1, years + 1):
            future_fcf = current_fcf * (1 + g) ** year
            discount_factor = 1 / ((1 + discount_rate) ** year)
            present_value_fcf += future_fcf * discount_factor

        # 终值现值
        terminal_fcf = current_fcf * (1 + g) ** years * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth) if discount_rate > terminal_growth else 0
        pv_terminal = terminal_value / ((1 + discount_rate) ** years)

        # 企业价值和股权价值
        enterprise_value = present_value_fcf + pv_terminal
        equity_value = enterprise_value - net_debt

        return equity_value - market_cap

    # 使用 scipy 的 fsolve 求解
    try:
        # 初始猜测：使用 5% 作为起点
        initial_guess = [0.05]
        result = fsolve(dcf_value, initial_guess)

        # 验证结果合理性
        if -0.5 <= result[0] <= 0.5:  # 增长率在 -50% 到 50% 之间
            return result[0]
        else:
            return 0.0  # 如果结果不合理，返回0

    except Exception:
        # 如果求解失败，返回0
        return 0.0
