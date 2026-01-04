"""
ROIC计算器

对应 components/roic.py
"""

from typing import Dict, Tuple, List
import pandas as pd
import requests

from .. import data_service
from .common import calculate_ebit, calculate_interest_bearing_debt


def calculate(
    symbol: str,
    market: str,
    years: int
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[str], List[str], List[str], Dict[str, float], Dict[str, float], Dict[str, str]]:
    """计算投入资本回报率分析（包含数据获取，同时计算普通ROIC和运营ROIC及拆解）

    Args:
        symbol: 股票代码
        market: 市场类型（A股/港股/美股）
        years: 查询年数

    Returns:
        (普通ROIC数据, 运营ROIC数据, ROIC拆解数据, 普通ROIC显示列, 运营ROIC显示列, 拆解显示列, 普通ROIC指标, 运营ROIC指标, 剔除说明)

    Raises:
        data_service.SymbolNotFoundError: 股票代码未找到
        data_service.APIServiceUnavailableError: API服务不可用
        data_service.DataServiceError: 其他数据错误
    """
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

    # 计算普通ROIC
    roic_data, roic_display_cols = _roic(financial_data, market)
    roic_data = roic_data.sort_values("年份").reset_index(drop=True)

    # 计算运营ROIC
    operating_roic_data, operating_display_cols, exclusion_info = _operating_roic(financial_data, market)
    operating_roic_data = operating_roic_data.sort_values("年份").reset_index(drop=True)

    # 计算ROIC拆解（杜邦分析）
    # ROIC = NOPAT利润率 × 资本周转率
    # NOPAT利润率 = NOPAT / 收入
    # 资本周转率 = 收入 / 投入资本
    dupont_data = roic_data[["年份", "NOPAT", "投入资本"]].copy()
    # 从收入数据中获取收入字段（已经在roic计算中获取）
    income_df, _ = calculate_ebit(financial_data, market)
    dupont_data = pd.merge(
        dupont_data,
        income_df[["年份", "收入"]],
        on="年份"
    )

    # 转换为数值类型（处理非数值类型，如None、空字符串等）
    dupont_data["NOPAT"] = pd.to_numeric(dupont_data["NOPAT"], errors="coerce")
    dupont_data["投入资本"] = pd.to_numeric(dupont_data["投入资本"], errors="coerce")
    dupont_data["收入"] = pd.to_numeric(dupont_data["收入"], errors="coerce")

    dupont_data["NOPAT利润率"] = (
        dupont_data["NOPAT"] / dupont_data["收入"].replace(0, pd.NA) * 100
    )
    # 处理无穷值并填充0
    dupont_data["NOPAT利润率"] = dupont_data["NOPAT利润率"].replace([float('inf'), -float('inf')], 0)
    dupont_data["NOPAT利润率"] = pd.to_numeric(dupont_data["NOPAT利润率"], errors="coerce").fillna(0)

    dupont_data["资本周转率"] = (
        dupont_data["收入"] / dupont_data["投入资本"].replace(0, pd.NA)
    )
    # 处理无穷值并填充0
    dupont_data["资本周转率"] = dupont_data["资本周转率"].replace([float('inf'), -float('inf')], 0)
    dupont_data["资本周转率"] = pd.to_numeric(dupont_data["资本周转率"], errors="coerce").fillna(0)

    dupont_data["ROIC验证"] = dupont_data["NOPAT利润率"] * dupont_data["资本周转率"]
    dupont_display_cols = ["年份", "NOPAT利润率", "资本周转率", "ROIC验证"]

    # 计算普通ROIC指标
    roic_metrics = {
        "avg_roic": roic_data['ROIC'].mean(),
        "latest_roic": roic_data['ROIC'].iloc[-1],
        "min_roic": roic_data['ROIC'].min(),
        "max_roic": roic_data['ROIC'].max(),
        "avg_nopat": roic_data['NOPAT'].mean(),
        "avg_capital": roic_data['投入资本'].mean()
    }

    # 计算运营ROIC指标
    operating_roic_metrics = {
        "avg_operating_roic": operating_roic_data['运营ROIC'].mean(),
        "latest_operating_roic": operating_roic_data['运营ROIC'].iloc[-1],
        "min_operating_roic": operating_roic_data['运营ROIC'].min(),
        "max_operating_roic": operating_roic_data['运营ROIC'].max(),
        "avg_operating_capital": operating_roic_data['运营投入资本'].mean()
    }

    # 计算ROIC拆解指标
    dupont_metrics = {
        "avg_nopat_margin": dupont_data['NOPAT利润率'].mean(),
        "avg_capital_turnover": dupont_data['资本周转率'].mean(),
        "latest_nopat_margin": dupont_data['NOPAT利润率'].iloc[-1],
        "latest_capital_turnover": dupont_data['资本周转率'].iloc[-1]
    }

    # 将拆解指标合并到普通ROIC指标中
    roic_metrics.update(dupont_metrics)

    return (
        roic_data,
        operating_roic_data,
        dupont_data,
        roic_display_cols,
        operating_display_cols,
        dupont_display_cols,
        roic_metrics,
        operating_roic_metrics,
        exclusion_info
    )


def _calculate_invested_capital_base(
    data: Dict[str, pd.DataFrame],
    market: str
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """计算投入资本的基础数据（共用方法）

    计算投入资本和NOPAT的统一方法，供普通ROIC和运营ROIC共用。

    Args:
        data: 包含利润表和资产负债表的字典
            {
                "income_statement": DataFrame,
                "balance_sheet": DataFrame
            }
        market: 市场类型（A股/港股/美股）

    Returns:
        (包含投入资本、NOPAT等基础字段的DataFrame, 字段映射字典)
    """
    # 获取原始利润表和资产负债表
    raw_income_df = data["income_statement"].copy()
    balance_df = data["balance_sheet"].copy()

    # 使用 calculate_ebit 方法获取 EBIT 和收入（已重命名字段）
    income_df, _ = calculate_ebit(data, market)

    # 根据市场提取字段
    if market == "A股":
        equity_col = "归属于母公司所有者权益合计"
        tax_col = "减：所得税费用"

        # A股：从原始利润表中获取所得税费用（避免字段重命名问题）
        result_df = pd.merge(
            income_df.loc[:, ["年份", "EBIT", "收入"]],
            raw_income_df.loc[:, ["年份", tax_col]],
            on="年份"
        )
        result_df = pd.merge(
            result_df,
            balance_df.loc[:, ["年份", equity_col]],
            on="年份"
        )

        # 转换为数值类型（处理非数值类型，如None、空字符串等）
        result_df[tax_col] = pd.to_numeric(result_df[tax_col], errors="coerce")
        result_df["EBIT"] = pd.to_numeric(result_df["EBIT"], errors="coerce")

        # 计算实际税率
        result_df["实际税率"] = (
            result_df[tax_col] / result_df["EBIT"].replace(0, pd.NA)
        )
        # 处理无穷值
        result_df["实际税率"] = result_df["实际税率"].replace([float('inf'), -float('inf')], 0)
        # 确保是数值类型
        result_df["实际税率"] = pd.to_numeric(result_df["实际税率"], errors="coerce").fillna(0.25)

    elif market == "港股":
        # 港股权益字段可能为"股东权益"、"总权益"或"股东权益合计"
        if "股东权益" in balance_df.columns:
            equity_col = "股东权益"
        elif "总权益" in balance_df.columns:
            equity_col = "总权益"
        elif "股东权益合计" in balance_df.columns:
            equity_col = "股东权益合计"
        else:
            raise ValueError("港股资产负债表缺少权益字段（需要'股东权益'、'总权益'或'股东权益合计'）")

        # 港股：合并利润表和资产负债表
        result_df = pd.merge(
            income_df.loc[:, ["年份", "EBIT", "收入"]],
            balance_df.loc[:, ["年份", equity_col]],
            on="年份"
        )
        # 港股使用固定税率
        result_df["实际税率"] = 0.165  # 香港利得税16.5%

    else:  # 美股
        equity_col = "股东权益合计"

        # 美股：合并利润表和资产负债表
        result_df = pd.merge(
            income_df.loc[:, ["年份", "EBIT", "收入"]],
            balance_df.loc[:, ["年份", equity_col]],
            on="年份"
        )
        # 美股使用固定税率
        result_df["实际税率"] = 0.21  # 美国联邦税率21%

    # 使用统一方法计算有息债务
    # 先给balance_df添加年份列用于merge
    balance_df_with_year = balance_df.copy()
    if "报告期" in balance_df.columns:
        date_col = "报告期"
    elif "REPORT_DATE" in balance_df.columns:
        date_col = "REPORT_DATE"
    elif "date" in balance_df.columns:
        date_col = "date"
    else:
        date_col = list(balance_df.columns)[1]  # 假设第二列是日期

    balance_df_with_year["年份"] = pd.to_datetime(balance_df_with_year[date_col]).dt.year

    # 计算有息债务
    interest_bearing_debt = calculate_interest_bearing_debt(balance_df_with_year, market)

    # 通过merge将有息债务关联到result_df
    debt_df = pd.DataFrame({
        "年份": balance_df_with_year["年份"],
        "有息债务": interest_bearing_debt.values
    })
    result_df = pd.merge(result_df, debt_df, on="年份", how="left")

    # 转换为数值类型（处理非数值类型，如None、空字符串等）
    result_df[equity_col] = pd.to_numeric(result_df[equity_col], errors="coerce")
    result_df["有息债务"] = pd.to_numeric(result_df["有息债务"], errors="coerce")
    result_df["EBIT"] = pd.to_numeric(result_df["EBIT"], errors="coerce")
    result_df["实际税率"] = pd.to_numeric(result_df["实际税率"], errors="coerce")

    # 计算投入资本 = 股东权益 + 有息债务
    result_df["投入资本"] = (
        result_df[equity_col].fillna(0) +
        result_df["有息债务"]
    )

    # 计算 NOPAT（税后净营业利润）
    result_df["NOPAT"] = result_df["EBIT"] * (1 - result_df["实际税率"])

    # 确保是数值类型
    result_df["投入资本"] = pd.to_numeric(result_df["投入资本"], errors="coerce")
    result_df["NOPAT"] = pd.to_numeric(result_df["NOPAT"], errors="coerce")

    # 返回字段映射
    field_mapping = {
        "equity_col": equity_col
    }

    return result_df, field_mapping


def _roic(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str]]:
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
    # 使用统一的基础方法计算投入资本和NOPAT
    result_df, _ = _calculate_invested_capital_base(data, market)

    # 转换为数值类型（处理非数值类型，如None、空字符串等）
    result_df["NOPAT"] = pd.to_numeric(result_df["NOPAT"], errors="coerce")
    result_df["投入资本"] = pd.to_numeric(result_df["投入资本"], errors="coerce")

    # 计算 ROIC
    result_df["ROIC"] = (
        result_df["NOPAT"] /
        result_df["投入资本"].replace(0, pd.NA) * 100
    )
    # 处理无穷值
    result_df["ROIC"] = result_df["ROIC"].replace([float('inf'), -float('inf')], pd.NA)
    # 确保是数值类型后再round
    result_df["ROIC"] = pd.to_numeric(result_df["ROIC"], errors="coerce").round(2)

    display_columns = [
        "年份",
        "EBIT",
        "实际税率",
        "NOPAT",
        "投入资本",
        "ROIC"
    ]

    return result_df, display_columns


def _operating_roic(data: Dict[str, pd.DataFrame], market: str) -> Tuple[pd.DataFrame, List[str], Dict[str, str]]:
    """计算运营投入资本回报率（剔除非经营性资产）

    运营ROIC剔除了不直接参与业务运营的资产：
    - A股：剔除货币资金（商誉字段缺失）
    - 港股：剔除现金及等价物（商誉字段缺失）
    - 美股：剔除商誉 + 现金及现金等价物

    计算公式：
    - 运营投入资本 = 投入资本 - 非经营性资产
    - 运营ROIC = NOPAT ÷ 运营投入资本 × 100%

    Args:
        data: 包含利润表和资产负债表的字典
            {
                "income_statement": DataFrame,
                "balance_sheet": DataFrame
            }
        market: 市场类型（A股/港股/美股）

    Returns:
        (添加了运营ROIC字段的DataFrame, 显示列名列表, 剔除说明字典)

    Raises:
        ValueError: 所需字段不存在
    """
    balance_df = data["balance_sheet"].copy()

    # 根据市场提取非经营性资产字段
    if market == "A股":
        cash_col = "货币资金"
        goodwill_col = None
    elif market == "港股":
        cash_col = "现金及等价物"
        goodwill_col = None
    else:  # 美股
        cash_col = "现金及现金等价物"
        # 商誉字段可能不存在（例如拼多多）
        if "商誉" in balance_df.columns:
            goodwill_col = "商誉"
        else:
            goodwill_col = None

    # 验证非经营性资产字段是否存在
    if cash_col not in balance_df.columns:
        raise ValueError(f"{market}资产负债表字段 '{cash_col}' 不存在")
    if goodwill_col and goodwill_col not in balance_df.columns:
        raise ValueError(f"{market}资产负债表字段 '{goodwill_col}' 不存在")

    # 使用统一的基础方法计算投入资本和NOPAT
    result_df, _ = _calculate_invested_capital_base(data, market)

    # 合并非经营性资产字段
    asset_cols = ["年份", cash_col]
    if goodwill_col:
        asset_cols.append(goodwill_col)

    result_df = pd.merge(
        result_df,
        balance_df.loc[:, asset_cols],
        on="年份"
    )

    # 转换为数值类型（处理非数值类型，如None、空字符串等）
    result_df[cash_col] = pd.to_numeric(result_df[cash_col], errors="coerce")
    if goodwill_col:
        result_df[goodwill_col] = pd.to_numeric(result_df[goodwill_col], errors="coerce")

    # 计算非经营性资产总额
    non_operating_assets = result_df[cash_col].fillna(0)
    if goodwill_col:
        non_operating_assets += result_df[goodwill_col].fillna(0)

    result_df["非经营性资产"] = pd.to_numeric(non_operating_assets, errors="coerce")

    # 计算运营投入资本 = 投入资本 - 非经营性资产
    result_df["运营投入资本"] = result_df["投入资本"] - result_df["非经营性资产"]

    # 转换为数值类型（处理非数值类型，如None、空字符串等）
    result_df["NOPAT"] = pd.to_numeric(result_df["NOPAT"], errors="coerce")
    result_df["运营投入资本"] = pd.to_numeric(result_df["运营投入资本"], errors="coerce")
    result_df["投入资本"] = pd.to_numeric(result_df["投入资本"], errors="coerce")

    # 计算运营ROIC
    result_df["运营ROIC"] = (
        result_df["NOPAT"] /
        result_df["运营投入资本"].replace(0, pd.NA) * 100
    )
    # 处理无穷值
    result_df["运营ROIC"] = result_df["运营ROIC"].replace([float('inf'), -float('inf')], pd.NA)
    # 确保是数值类型后再round
    result_df["运营ROIC"] = pd.to_numeric(result_df["运营ROIC"], errors="coerce").round(2)

    # 计算普通ROIC（用于对比）
    result_df["ROIC"] = (
        result_df["NOPAT"] /
        result_df["投入资本"].replace(0, pd.NA) * 100
    )
    # 处理无穷值
    result_df["ROIC"] = result_df["ROIC"].replace([float('inf'), -float('inf')], pd.NA)
    # 确保是数值类型后再round
    result_df["ROIC"] = pd.to_numeric(result_df["ROIC"], errors="coerce").round(2)

    # 构建剔除说明
    if market == "A股":
        exclusion_note = "剔除：货币资金（注：商誉字段缺失，未剔除）"
    elif market == "港股":
        exclusion_note = "剔除：现金及等价物（注：商誉字段缺失，未剔除）"
    else:  # 美股
        if goodwill_col:
            exclusion_note = "剔除：商誉 + 现金及现金等价物"
        else:
            exclusion_note = "剔除：现金及现金等价物（注：商誉字段缺失，未剔除）"

    exclusion_info = {
        "exclusion_note": exclusion_note,
        "goodwill_field": goodwill_col if goodwill_col else "无",
        "cash_field": cash_col
    }

    display_columns = [
        "年份",
        "投入资本",
        "非经营性资产",
        "运营投入资本",
        "NOPAT",
        "运营ROIC"
    ]

    return result_df, display_columns, exclusion_info
