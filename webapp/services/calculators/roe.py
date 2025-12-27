"""
ROE和杜邦分析计算器

对应 components/roe.py
"""

from typing import Tuple
import pandas as pd
import requests

from .. import data_service


def calculate(symbol: str, market: str, years: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """计算ROE和杜邦分析（包含数据获取）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (ROE DataFrame, 杜邦分析 DataFrame)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
    # 获取财务指标数据（包含ROE）
    market_type_map = {
        "A股": "a_stock",
        "港股": "hk_stock",
        "美股": "us_stock"
    }
    market_type = market_type_map.get(market)

    response = requests.get(
        f"{data_service.API_BASE_URL}/api/v1/financial/indicators",
        params={
            "symbol": symbol,
            "market": market_type,
            "frequency": "annual"
        },
        timeout=30
    )

    if response.status_code != 200:
        raise data_service.APIServiceUnavailableError(f"API服务返回错误状态码: {response.status_code}")

    result = response.json()
    data_wrapper = result.get("data", {})
    records = data_wrapper.get("records", [])

    if not records:
        raise data_service.SymbolNotFoundError(f"{market}股票 {symbol} 没有财务指标数据")

    # 转换为DataFrame
    indicators_df = pd.DataFrame(records)

    # 提取年份（支持多种日期字段）
    if "报告期" in indicators_df.columns:
        date_col = "报告期"
    elif "REPORT_DATE" in indicators_df.columns:
        date_col = "REPORT_DATE"
    elif "date" in indicators_df.columns:
        date_col = "date"
    else:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 数据中缺少日期字段")

    indicators_df = indicators_df.copy()
    indicators_df["年份"] = pd.to_datetime(indicators_df[date_col]).dt.year

    # 根据市场选择ROE字段
    roe_field_map = {
        "A股": "净资产收益率-摊薄",
        "港股": "ROE_AVG",
        "美股": "ROE_AVG"
    }
    roe_field = roe_field_map.get(market)

    if roe_field not in indicators_df.columns:
        raise data_service.DataServiceError(f"{market}股票 {symbol} 没有{roe_field}字段")

    # 处理ROE值（可能是百分比字符串）
    def parse_roe_value(value):
        """解析ROE值，支持百分比字符串和数值"""
        if isinstance(value, str):
            # 移除百分号并转换为浮点数
            return float(value.replace("%", ""))
        elif pd.notna(value):
            return float(value)
        return None

    # 构建ROE数据（限制年数）
    roe_df = pd.DataFrame({
        "年份": indicators_df["年份"],
        "ROE": indicators_df[roe_field].apply(parse_roe_value)
    }).dropna().sort_values("年份")
    if years is not None:
        roe_df = roe_df.tail(years)
    roe_df = roe_df.reset_index(drop=True)

    # 获取财务三表数据用于杜邦分析
    financial_statements = data_service.get_financial_statements(symbol, market, years)
    income_df = financial_statements["income_statement"]

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

    # 根据市场映射字段（使用原始字段名，不做重命名）
    if market == "A股":
        net_income_col = "五、净利润"
        revenue_col = "其中：营业收入"
        total_assets_col = "资产合计"
        equity_col = "归属于母公司所有者权益合计"
    elif market == "港股":
        net_income_col = "股东应占溢利"
        revenue_col = "营业额"
        total_assets_col = "总资产"
        equity_col = "总权益"
    else:  # 美股
        net_income_col = "净利润"
        # 美股收入字段可能为"营业收入"或"收入总额"（如保险公司BRK.B）
        if "营业收入" in income_df.columns:
            revenue_col = "营业收入"
        elif "收入总额" in income_df.columns:
            revenue_col = "收入总额"
        else:
            raise ValueError("美股利润表缺少收入字段（需要'营业收入'或'收入总额'）")
        total_assets_col = "总资产"
        equity_col = "股东权益合计"

    # 合并利润表和资产负债表
    dupont_df = pd.merge(
        income_df.loc[:, ["年份", net_income_col, revenue_col]],
        balance_df.loc[:, ["年份", total_assets_col, equity_col]],
        on="年份"
    ).sort_values("年份").reset_index(drop=True)

    # 计算杜邦三要素
    dupont_df["净利润率"] = (dupont_df[net_income_col] / dupont_df[revenue_col] * 100).round(2)
    dupont_df["总资产周转率"] = (dupont_df[revenue_col] / dupont_df[total_assets_col]).round(2)
    dupont_df["权益乘数"] = (dupont_df[total_assets_col] / dupont_df[equity_col]).round(2)

    # 选择需要的列
    dupont_result = dupont_df[["年份", "净利润率", "总资产周转率", "权益乘数"]].copy()

    return roe_df, dupont_result
