"""
净利润估值计算器

基于三年后预估净利润的PE倍数估值法

对应 components/net_income_valuation.py
"""

from typing import Dict, List, Tuple
import pandas as pd
import requests

from .. import data_service


def calculate(
    symbol: str,
    market: str,
    years: int = 10,
    growth_rate: float = 0.10,
    pe_multiple: float = 25.0
) -> Tuple[pd.DataFrame, List[str], Dict[str, any]]:
    """计算净利润估值（PE倍数法，包含数据获取）

    估值公式：
    企业价值 = 三年后预估净利润 × PE倍数
    三年后预估净利润 = 当前净利润 × (1 + 增长率)^3

    Args:
        symbol: 股票代码
        market: 市场类型（A股、港股、美股）
        years: 查询历史年数（用于获取当前净利润），默认10年
        growth_rate: 净利润增长率，默认10%
        pe_multiple: PE倍数，默认25倍

    Returns:
        (DataFrame, display_columns, stats_dict)
        - DataFrame: 包含净利润历史数据和预测数据的详细数据
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
    income_statement = data_dict.get("income_statement")

    if not income_statement:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 没有利润表数据")

    # 转换为DataFrame并提取年份
    income_df = pd.DataFrame(income_statement["data"])
    income_df = data_service.extract_year_column(income_df, market, symbol, "利润表")

    # 确定净利润字段映射（三地市场）
    if market == "A股":
        net_income_col = "五、净利润"
    elif market == "港股":
        net_income_col = "股东应占溢利"
    else:  # 美股
        net_income_col = "净利润"

    # 检查字段是否存在
    if net_income_col not in income_df.columns:
        raise ValueError(f"净利润字段 '{net_income_col}' 不存在")

    # 获取最新净利润数据（单位：亿元）
    latest_net_income = income_df.iloc[0][net_income_col]

    # 构建历史数据DataFrame（用于展示趋势）
    history_df = income_df[["年份", net_income_col]].copy()
    history_df = history_df.sort_values("年份").reset_index(drop=True)
    history_df.rename(columns={net_income_col: "历史净利润"}, inplace=True)

    # 计算历史增长率
    if len(history_df) >= 2:
        first_income = history_df["历史净利润"].iloc[-1]
        historical_growth_rate = (latest_net_income / first_income) ** (1 / (len(history_df) - 1)) - 1
    else:
        historical_growth_rate = 0.0

    # 构建预测数据
    prediction_data = []
    for year in range(1, 4):  # 预测未来3年
        future_net_income = latest_net_income * (1 + growth_rate) ** year
        prediction_data.append({
            "年份": f"第{year}年",
            "预测净利润": future_net_income
        })

    prediction_df = pd.DataFrame(prediction_data)

    # 三年后预估净利润
    year3_net_income = latest_net_income * (1 + growth_rate) ** 3

    # 计算各年预测净利润（用于stats）
    year1_net_income = latest_net_income * (1 + growth_rate) ** 1
    year2_net_income = latest_net_income * (1 + growth_rate) ** 2

    # 企业价值 = 三年后预估净利润 × PE倍数（单位：亿元）
    enterprise_value = year3_net_income * pe_multiple

    # 统计信息
    stats = {
        # 当前财务数据（单位：亿元）
        "current_net_income": latest_net_income,
        "historical_growth_rate": historical_growth_rate,

        # 估值参数
        "growth_rate": growth_rate,
        "pe_multiple": pe_multiple,
        "projection_years": 3,

        # 预测数据（单位：亿元）
        "year1_net_income": year1_net_income,
        "year2_net_income": year2_net_income,
        "year3_net_income": year3_net_income,

        # 估值结果（单位：亿元）
        "enterprise_value": enterprise_value,

        # 计算市场隐含增长率的方法
        "implied_growth_rate": lambda market_cap: _calculate_implied_growth_rate(
            market_cap, latest_net_income, pe_multiple
        ) if market_cap > 0 else None,

        # 估值说明
        "valuation_summary": f"""
**估值模型**: PE倍数法（三年后净利润）
**预测期**: 3年
**净利润增长率**: {growth_rate * 100:.1f}%
**PE倍数**: {pe_multiple:.0f}倍

**关键财务数据**（单位：亿元）:
- 当前净利润: {latest_net_income:.2f}
- 历史平均增长率: {historical_growth_rate * 100:.1f}%

**预测净利润**（单位：亿元）:
- 第1年: {year1_net_income:.2f}
- 第2年: {year2_net_income:.2f}
- 第3年: {year3_net_income:.2f}

**估值结果**（单位：亿元）:
- 三年后预估净利润: {year3_net_income:.2f}
- 企业价值: {enterprise_value:.2f}

**投资建议**:
- 估值适合盈利稳定、增长可预测的成熟企业
- 建议结合DCF、市盈率等多种估值方法综合判断
- 注意：PE倍数法对增长率和PE倍数假设非常敏感
        """
    }

    display_cols_history = ["年份", "历史净利润"]
    display_cols_prediction = ["年份", "预测净利润"]

    return history_df, prediction_df, display_cols_history, display_cols_prediction, stats


def _calculate_implied_growth_rate(
    market_cap: float,
    current_net_income: float,
    pe_multiple: float,
    max_iterations: int = 100,
    tolerance: float = 0.0001
) -> float:
    """反向计算市场隐含增长率

    从给定市值反推市场预期的净利润增长率。

    估值公式：
    企业价值 = 三年后净利润 × PE倍数
    三年后净利润 = 当前净利润 × (1 + g)^3

    因此：
    市值 = 当前净利润 × (1 + g)^3 × PE倍数
    g = (市值 / (当前净利润 × PE倍数))^(1/3) - 1

    Args:
        market_cap: 市值（亿元）
        current_net_income: 当前净利润（亿元）
        pe_multiple: PE倍数
        max_iterations: 最大迭代次数（保留参数以兼容接口）
        tolerance: 收敛容差（保留参数以兼容接口）

    Returns:
        市场隐含增长率（小数形式，如0.08表示8%）
    """
    if current_net_income <= 0 or pe_multiple <= 0:
        return 0.0

    # 直接求解：g = (市值 / (当前净利润 × PE倍数))^(1/3) - 1
    ratio = market_cap / (current_net_income * pe_multiple)
    implied_rate = ratio ** (1 / 3) - 1

    # 限制合理范围：-50% 到 100%
    if implied_rate < -0.5:
        return -0.5
    elif implied_rate > 1.0:
        return 1.0
    else:
        return implied_rate
